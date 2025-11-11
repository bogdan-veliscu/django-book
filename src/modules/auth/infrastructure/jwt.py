"""JWT authentication service."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.config import Settings
from src.core.domain.exceptions import ValidationException


class JWTService:
    """Service for creating and validating JWT tokens."""

    def __init__(self, settings: Settings) -> None:
        """Initialize JWT service.

        Args:
            settings: Application settings.
        """
        self._secret_key = settings.secret_key
        self._algorithm = settings.algorithm
        self._access_token_expire_minutes = settings.access_token_expire_minutes

    def create_access_token(self, user_id: int, email: str) -> str:
        """Create a new access token.

        Args:
            user_id: The user's ID.
            email: The user's email.

        Returns:
            The encoded JWT token.
        """
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=self._access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": now,
            "exp": expire,
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate an access token.

        Args:
            token: The JWT token to decode.

        Returns:
            The decoded payload.

        Raises:
            ValidationException: If the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError as e:
            raise ValidationException("Invalid or expired token") from e

    def get_user_id_from_token(self, token: str) -> int:
        """Extract user ID from a token.

        Args:
            token: The JWT token.

        Returns:
            The user's ID.

        Raises:
            ValidationException: If the token is invalid or expired.
        """
        payload = self.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValidationException("Token missing user ID")
        return int(user_id)
