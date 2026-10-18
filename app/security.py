import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import settings

# Define la cabecera X-Device-Token (Swagger mostrará un botón "Authorize")
api_key_header = APIKeyHeader(name="X-Device-Token", auto_error=False)


def verificar_token(token: str | None = Depends(api_key_header)) -> None:
    if not token or not secrets.compare_digest(
        token.encode(), settings.DEVICE_TOKEN.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de dispositivo inválido o ausente",
        )