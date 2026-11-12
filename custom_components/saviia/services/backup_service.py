"""Backup-related services."""

from __future__ import annotations

from homeassistant.core import ServiceCall, ServiceResponse
from homeassistant.exceptions import HomeAssistantError
from saviialib import SaviiaAPI

from custom_components.saviia.libs.log_client import (
    DebugArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .common import _ensure_domain_setup, _iter_config_entry_contexts

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="backup")
)


class BackupService:
    """Backup service methods."""

    async def async_export_files(self, call: ServiceCall) -> ServiceResponse:
        """Export a local folder to Databricks using the backup API."""
        logclient.method_name = "async_export_files"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)

        local_folder_path = call.data["local_folder_path"]
        results: list[dict] = []
        for config_entry, entry_data in _iter_config_entry_contexts(call.hass):
            api: SaviiaAPI = entry_data["api"]
            backup_service = api.get("backup")
            cloud_provider_destination_path = call.data.get(
                "cloud_provider_destination_path"
            ) or config_entry.data.get("cloud_provider_destination_path")
            if not cloud_provider_destination_path:
                msg = "No Databricks destination path available for the backup service"
                raise HomeAssistantError(msg)
            result = await backup_service.export_files(
                local_folder_path=local_folder_path,
                cloud_provider_destination_path=cloud_provider_destination_path,
            )
            results.append({"entry_id": config_entry.entry_id, **result})

        if len(results) == 1:
            return results[0]
        return {"results": results}
