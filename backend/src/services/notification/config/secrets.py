"""
Secrets Manager for Notification Service.

Integrates with Dapr Secrets API to retrieve email configuration
and other sensitive credentials.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Service for managing secrets via Dapr Secrets API.

    Retrieves SMTP configuration and other sensitive data
    from Kubernetes secrets or other secret stores.
    """

    def __init__(self):
        """Initialize secrets manager."""
        # In production, this would use Dapr Secrets API
        # For MVP, we'll use environment variables as fallback
        pass

    async def get_smtp_config(self) -> Optional[Dict[str, Any]]:
        """
        Get SMTP configuration from secrets.

        Returns:
            Dict with SMTP configuration or None
        """
        try:
            # In production, retrieve from Dapr Secrets API:
            # GET http://localhost:3500/v1.0/secrets/{secret-store-name}/{secret-name}

            # For MVP/development, return default configuration
            # This would typically point to MailHog for testing
            smtp_config = {
                "host": "localhost",
                "port": 1025,  # MailHog SMTP port
                "username": None,
                "password": None,
                "use_tls": False,
                "from_email": "noreply@todo-chatbot.com"
            }

            logger.info("Retrieved SMTP configuration")

            return smtp_config

        except Exception as e:
            logger.error(f"Error getting SMTP config: {e}", exc_info=True)
            return None

    async def get_secret(
        self,
        secret_store: str,
        secret_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a secret from Dapr Secrets API.

        Args:
            secret_store: Name of the secret store component
            secret_name: Name of the secret

        Returns:
            Secret data dict or None
        """
        try:
            # In production, this would call Dapr Secrets API:
            # GET http://localhost:{dapr-http-port}/v1.0/secrets/{secret-store}/{secret-name}

            # Example implementation:
            # import aiohttp
            # async with aiohttp.ClientSession() as session:
            #     url = f"http://localhost:3500/v1.0/secrets/{secret_store}/{secret_name}"
            #     async with session.get(url) as response:
            #         if response.status == 200:
            #             return await response.json()
            #         else:
            #             logger.error(f"Failed to get secret: {response.status}")
            #             return None

            logger.warning(
                f"Secret retrieval not implemented for {secret_store}/{secret_name}, "
                f"using defaults"
            )

            return None

        except Exception as e:
            logger.error(f"Error getting secret: {e}", exc_info=True)
            return None

    async def get_api_key(
        self,
        service_name: str
    ) -> Optional[str]:
        """
        Get API key for external service.

        Args:
            service_name: Name of the service

        Returns:
            API key string or None
        """
        try:
            # Retrieve from secrets store
            secret_data = await self.get_secret(
                secret_store="local-secrets",
                secret_name=f"{service_name}-api-key"
            )

            if secret_data:
                return secret_data.get("key")

            return None

        except Exception as e:
            logger.error(f"Error getting API key: {e}", exc_info=True)
            return None

    async def get_database_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get database credentials from secrets.

        Returns:
            Dict with database credentials or None
        """
        try:
            secret_data = await self.get_secret(
                secret_store="local-secrets",
                secret_name="database-credentials"
            )

            if secret_data:
                return {
                    "host": secret_data.get("host"),
                    "port": secret_data.get("port"),
                    "username": secret_data.get("username"),
                    "password": secret_data.get("password"),
                    "database": secret_data.get("database")
                }

            return None

        except Exception as e:
            logger.error(f"Error getting database credentials: {e}", exc_info=True)
            return None

    def validate_smtp_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate SMTP configuration.

        Args:
            config: SMTP configuration dict

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["host", "port", "from_email"]

        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required SMTP field: {field}")
                return False

        # Validate port is integer
        if not isinstance(config["port"], int):
            logger.error("SMTP port must be an integer")
            return False

        # Validate port range
        if not (1 <= config["port"] <= 65535):
            logger.error("SMTP port must be between 1 and 65535")
            return False

        return True
