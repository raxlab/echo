"""System-related SAVIIA services."""

from __future__ import annotations

from homeassistant.core import ServiceCall, ServiceResponse
from homeassistant.exceptions import HomeAssistantError

from custom_components.saviia.const import ServicesParams
from custom_components.saviia.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .common import _get_config_entry_data
from .storage_service import StorageService

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="system")
)


class SystemService:
    """System service methods."""

    def __init__(self, storage_service: StorageService | None = None) -> None:
        self._storage_service = storage_service or StorageService()

    async def async_get_config_value(self, call: ServiceCall) -> ServiceResponse:
        """Return a whitelisted config entry value."""
        logclient.method_name = "async_get_config_value"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        key = call.data.get("key")

        if key not in ServicesParams.ALLOWED_CONFIG_KEYS:
            error_message = (
                f"The requested key '{key}' is not allowed. "
                "This service only exposes a safe whitelist of config keys."
            )
            logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": error_message},
                )
            )
            raise HomeAssistantError(error_message)

        config_data = _get_config_entry_data(call.hass)
        if key not in config_data:
            error_message = f"Key '{key}' was not found in SAVIIA config entry data"
            logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": error_message},
                )
            )
            raise HomeAssistantError(error_message)

        return {"key": key, "value": config_data[key]}

    async def async_add_person(self, call: ServiceCall) -> ServiceResponse:
        """Store a person in local SAVIIA storage."""
        return await self._storage_service.async_add_person(call)

    async def async_delete_person(self, call: ServiceCall) -> ServiceResponse:
        """Delete a person from local SAVIIA storage."""
        return await self._storage_service.async_delete_person(call)
