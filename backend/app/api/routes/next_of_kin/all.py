from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.app.api.routes.auth.deps import CurrentUser
from backend.app.api.services.next_of_kin import get_user_nex_of_kins
from backend.app.core.db import get_session
from backend.app.core.logging import get_logger
from backend.app.next_of_kin.schema import NextOfKinReadSchema

logger = get_logger()

router = APIRouter(prefix="/next-of-kin", tags=["Next of Kin"])


@router.get(
    "/all",
    response_model=list[NextOfKinReadSchema],
    status_code=status.HTTP_200_OK,
    description="Get all next of kins for an authenticated user",
)
async def lis_next_of_kins(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> list[NextOfKinReadSchema]:
    try:
        next_of_kins = await get_user_nex_of_kins(user_id=current_user.id, session=session)
        return [NextOfKinReadSchema.model_validate(kin) for kin in next_of_kins]
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Failed to get next of kins for usesr: {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to get next of kins",
                "action": "Please try again later"
                },
        )