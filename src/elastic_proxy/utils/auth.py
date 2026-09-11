from fastapi import Header, HTTPException, status

from ..config import settings


async def validate_private_key(
    private_key: str = Header(
        ...,
        alias="PRIVATE-KEY",
        description="Private key to access",
        examples=["795364a26ba34c8b365864bb4ed4c665"]
    ),
) -> str:
    if private_key != settings.PRIVATE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé privée invalide ou manquante",
        )
    return private_key
