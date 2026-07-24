from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.api.routes.auth.deps import CurrentUser
from backend.app.api.services.bank_account import create_bank_account
from backend.app.core.services.bank_account_created import send_account_created_email
from backend.app.core.db import get_session
from backend.app.core.logging import get_logger
from backend.app.bank_account.schema import BankAccountCreateSchema, BankAccountReadSchema

logger = get_logger()

router = APIRouter(prefix="/bank-account")

@router.post(
    "/create",
    response_model=BankAccountReadSchema,
    status_code=status.HTTP_201_CREATED,
    description="Create a new bank account. Requires complete profile and at least one next of kin. Maximum 3 accounts per user"
)
async def create_bank_account_route(
    current_user: CurrentUser,
    account_data: BankAccountCreateSchema,
    session: AsyncSession = Depends(get_session),
) -> BankAccountReadSchema:
    account = await create_bank_account(
        user_id=current_user.id,
        account_data=account_data,
        session=session
    )
    try:
        if not account.account_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "messsage": "Account number not generated"
                }
            )

        try:
            await send_account_created_email(
                email=current_user.email,
                full_name=current_user.full_name,
                account_number=account.account_number,
                account_name=account.account_name,
                account_type=account.account_type,
                currency=account.currency.value,
                identification_type=current_user.profile.means_of_identification.value
            )
        except Exception as e:
            logger.error(f"failed to send account creation email: {e}")
        logger.info(F"Created account for user: {current_user.email}")
        return BankAccountReadSchema.model_validate(account)

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to create bank account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to create bank account",
                "action": "Please try later"
            }
        )


