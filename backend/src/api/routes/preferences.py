"""
User preferences endpoints for Event-Driven Todo Chatbot.

Implements GET and PUT endpoints for managing user preferences.
Uses Dapr State API for persistence.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
import logging

from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.models.preferences import UserPreferences
from ...shared.models.task import TaskPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/preferences", tags=["preferences"])

# Temporary user ID for MVP (no authentication yet)
TEMP_USER_ID = "user-001"


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating user preferences."""
    notificationChannels: List[str] | None = None
    reminderAdvanceTime: int | None = Field(None, ge=1, le=168)
    defaultPriority: TaskPriority | None = None
    timezone: str | None = None
    emailAddress: EmailStr | None = None


@router.get("", response_model=UserPreferences)
async def get_user_preferences() -> UserPreferences:
    """
    Get user preferences.

    Returns:
        UserPreferences: Current user preferences

    Raises:
        HTTPException: If preferences cannot be retrieved
    """
    try:
        dapr_client = DaprClientWrapper()

        # Generate state key for user preferences
        state_key = f"chat-api.preferences.user.{TEMP_USER_ID}"

        # Retrieve preferences from Dapr State API
        preferences_data = await dapr_client.get_state(state_key)

        # If no preferences exist, return defaults
        if not preferences_data:
            logger.info(f"No preferences found for user {TEMP_USER_ID}, returning defaults")
            default_preferences = UserPreferences(
                userId=TEMP_USER_ID,
                notificationChannels=["in-app", "email"],
                reminderAdvanceTime=24,
                defaultPriority=TaskPriority.MEDIUM,
                timezone="UTC",
                emailAddress="user@example.com",
                updatedAt=datetime.utcnow().isoformat()
            )

            # Save default preferences
            await dapr_client.save_state(state_key, default_preferences.model_dump())

            return default_preferences

        # Parse and return existing preferences
        preferences = UserPreferences(**preferences_data)
        logger.info(f"Retrieved preferences for user {TEMP_USER_ID}")

        return preferences

    except Exception as e:
        logger.error(f"Error retrieving user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user preferences: {str(e)}"
        )


@router.put("", response_model=UserPreferences)
async def update_user_preferences(request: UpdatePreferencesRequest) -> UserPreferences:
    """
    Update user preferences.

    Args:
        request: Preferences update request with optional fields

    Returns:
        UserPreferences: Updated user preferences

    Raises:
        HTTPException: If preferences cannot be updated
    """
    try:
        dapr_client = DaprClientWrapper()

        # Generate state key for user preferences
        state_key = f"chat-api.preferences.user.{TEMP_USER_ID}"

        # Retrieve existing preferences
        preferences_data = await dapr_client.get_state(state_key)

        # If no preferences exist, create defaults
        if not preferences_data:
            logger.info(f"No existing preferences for user {TEMP_USER_ID}, creating new")
            current_preferences = UserPreferences(
                userId=TEMP_USER_ID,
                notificationChannels=["in-app", "email"],
                reminderAdvanceTime=24,
                defaultPriority=TaskPriority.MEDIUM,
                timezone="UTC",
                emailAddress="user@example.com",
                updatedAt=datetime.utcnow().isoformat()
            )
        else:
            current_preferences = UserPreferences(**preferences_data)

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)

        if "notificationChannels" in update_data:
            current_preferences.notificationChannels = update_data["notificationChannels"]
            logger.info(f"Updated notification channels: {update_data['notificationChannels']}")

        if "reminderAdvanceTime" in update_data:
            current_preferences.reminderAdvanceTime = update_data["reminderAdvanceTime"]
            logger.info(f"Updated reminder advance time: {update_data['reminderAdvanceTime']}")

        if "defaultPriority" in update_data:
            current_preferences.defaultPriority = update_data["defaultPriority"]
            logger.info(f"Updated default priority: {update_data['defaultPriority']}")

        if "timezone" in update_data:
            current_preferences.timezone = update_data["timezone"]
            logger.info(f"Updated timezone: {update_data['timezone']}")

        if "emailAddress" in update_data:
            current_preferences.emailAddress = update_data["emailAddress"]
            logger.info(f"Updated email address: {update_data['emailAddress']}")

        # Update timestamp
        current_preferences.updatedAt = datetime.utcnow().isoformat()

        # Save updated preferences to Dapr State API
        await dapr_client.save_state(state_key, current_preferences.model_dump())

        logger.info(f"Updated preferences for user {TEMP_USER_ID}")

        return current_preferences

    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}"
        )
