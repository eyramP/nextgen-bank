from uuid import UUID
from datetime import timezone, datetime
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.core.logging import get_logger
from backend.app.bank_account.models import BankAccount
from backend.app.bank_account.schema import BankAccountCreateSchema
from backend.app.bank_account.enums import AccountStatusEnum
from backend.app.bank_account.utils import generate_account_number
from backend.app.core.config import settings
from backend.app.auth.models import User

logger = get_logger()

async def get_primary_bank_account(user_id: UUID, session) -> BankAccount | None:
    """Below is the same as BankAccount.is_primary == True"""
    statement = select(BankAccount).where(
        BankAccount.user_id == user_id,
        BankAccount.is_primary
    )

    result = await session.exec(statement)
    return result.first()

async def validate_user_kyc(user: User) -> bool:
    if not user.profile:
        return False
    if not user.next_of_kins or len(user.next_of_kins) == 0:
        return False
    return True

async def create_bank_account(
    user_id: UUID,
    account_data: BankAccountCreateSchema,
    session: AsyncSession
) -> BankAccount:
    try:
        statement = select(User).where(User.id == user_id)
        result = await session.exec(statement)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "User not found"
                }
            )

        # This is to load the the user profile and prefetch the user's next of kings
        # An optimization technique
        await session.refresh(user, ["profile", "next_of_kins"])

        if not await validate_user_kyc(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "KYC requirements not met",
                    "action": "Please complete your profile and add at least one next of kin",
                }
            )

        statement = select(BankAccount).where(BankAccount.user_id == user_id)
        result = await session.exec(statement)
        existing_accounts = result.all()
        if len(existing_accounts) >= settings.MAX_BANK_ACCOUNTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Maximum number of accounts reached.",
                }
            )

        if account_data.is_primary:
            primary_exists = any(account.is_primary for account in existing_accounts)

            if primary_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": "error",
                        "message": "A primary account already exists",
                        "action": "Please unset the existing primary account first"
                    }
                )

        # Check if the user does not have any account already
        elif len(existing_accounts) == 0:
            # If the above is no then set this current account ben created to the primary account
            account_data.is_primary = True

        """Use the generate account number function to generate a new account number"""
        """We are converting all the account data the user field into a python dictionary
               Excluding the account number because that is generated automatically above
            """
        account_number = generate_account_number(account_data.currency)
        new_account = BankAccount(
            **account_data.model_dump(exclude={"account_number"}),
            user_id=user_id,
            account_number=account_number
        )

        """Add new account
           Commit the changes
           & refresh the database account table
           making the just added account accessible instatnly
        """
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)

        """We return the newly created
           Because we refreshed earlier
           the account can be accessed instantly
        """
        return new_account

    except HTTPException as http_ex:
        """We roll back the sesion so the account is not created if something"""
        await session.rollback()
        raise http_ex
    except Exception as e:
        """We roll back the sesion so the account is not created if something"""
        await session.rollback()
        logger.error(f"Failed to created bank account for user: {user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to create account",
                "action": "Please try again"
            }
        )


async def actiavte_bank_account(
    account_id: UUID,
    verified_by: UUID,
    session: AsyncSession
) -> tuple[BankAccount, User]:
    try:

        """Prepare statement here"""
        statement = (
            select(BankAccount, User)
            .join(User)
            .where(BankAccount.id == account_id, BankAccount.user_id != verified_by)
        )

        """execute statement"""
        result = await session.exec(statement)
        account_user_tuple = result.first()

        """Raise a 404 if account tuple is not found"""
        if not account_user_tuple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "Bank account not found"
                }
            )

        """Unpack the tuple"""
        account, user = account_user_tuple

        """
        Check if the account is activated already and send a 400 bad request to the user
        Notifyig himm/her that the account already activated
        """
        if account.account_status == AccountStatusEnum.Active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Bank account activated already"
                }
            )

        """Activate the account now"""
        account.kyc_submitted = True
        account.kyc_verified = True
        account.kyc_verified_on = datetime.now(timezone.utc)
        account.account_status = AccountStatusEnum.Active
        account.kyc_verified_by = verified_by

        """Save the changes to the database and refesh to get the latest state"""
        session.add(account)
        await session.commit()
        await session.refresh(account)

        """Return activated account and user tuple"""
        return account, user
    except HTTPException as http_ex:
        """Raise an exception and rollback the transaction if anything goes wrong"""
        await session.rollback()
        raise http_ex
    except Exception as e:
        """Raise an exception and rollback the transaction if anything goes wrong"""
        await session.rollback()
        logger.error(f"Failed to activate account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to activate account bank account",
                "message": "Try again later"
            }
        )
