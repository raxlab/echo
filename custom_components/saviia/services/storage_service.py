"""Storage-related SAVIIA services."""

from __future__ import annotations

from homeassistant.core import ServiceCall, ServiceResponse

from custom_components.saviia.libs.log_client import (
    DebugArgs,
    InfoArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .common import _ensure_domain_setup, _iter_domain_entries

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="storage")
)


class StorageService:
    """Storage service methods."""

    async def async_add_person(self, call: ServiceCall) -> ServiceResponse:
        """Store a person in local SAVIIA storage."""
        logclient.method_name = "async_add_person"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        person = call.data["person"]

        for _, entry_data in _iter_domain_entries(call.hass):
            storage = entry_data["storage"]
            await storage.async_add_person(person)

        logclient.info(
            InfoArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Person '{person['id']}' added successfully"},
            )
        )
        return {"status": "success", "person": person}

    async def async_delete_person(self, call: ServiceCall) -> ServiceResponse:
        """Delete a person from local SAVIIA storage."""
        logclient.method_name = "async_delete_person"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        person_id = call.data["id"]

        for _, entry_data in _iter_domain_entries(call.hass):
            storage = entry_data["storage"]
            await storage.async_delete_person(person_id)

        logclient.info(
            InfoArgs(
                status=LogStatus.SUCCESSFUL,
                metadata={"msg": f"Person '{person_id}' deleted successfully"},
            )
        )
        return {"status": "success", "person_id": person_id}
