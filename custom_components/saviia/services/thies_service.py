"""THIES-related services."""

from __future__ import annotations

from homeassistant.core import ServiceCall, ServiceResponse
from saviialib import SaviiaAPI

from custom_components.saviia.libs.log_client import (
    DebugArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .common import (
    _ensure_domain_setup,
    _format_multi_entry_response,
    _iter_config_entry_contexts,
    _resolve_thies_call_data,
)

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="thies")
)


class ThiesService:
    """THIES service methods."""

    async def async_get_thies_data(self, call: ServiceCall) -> ServiceResponse:
        """Return the THIES sync/backup state using the configured credentials."""
        logclient.method_name = "async_get_thies_data"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)

        results: list[dict] = []
        for config_entry, entry_data in _iter_config_entry_contexts(call.hass):
            api: SaviiaAPI = entry_data["api"]
            thies_service = api.get("thies")
            request_data = _resolve_thies_call_data(config_entry, call)
            result = await thies_service.get_thies_data(
                ftp_port=request_data["ftp_port"],
                ftp_host=request_data["ftp_host"],
                ftp_user=request_data["ftp_user"],
                ftp_password=request_data["ftp_password"],
                sharepoint_destination_path=request_data["sharepoint_destination_path"],
            )
            results.append({"entry_id": config_entry.entry_id, **result})

        return _format_multi_entry_response(results)

    async def async_post_thies_data(self, call: ServiceCall) -> ServiceResponse:
        """Execute THIES backup and sync using precomputed state values."""
        logclient.method_name = "async_post_thies_data"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)

        results: list[dict] = []
        for config_entry, entry_data in _iter_config_entry_contexts(call.hass):
            api: SaviiaAPI = entry_data["api"]
            thies_service = api.get("thies")
            request_data = _resolve_thies_call_data(config_entry, call)

            need_to_sync = call.data.get("need_to_sync")
            need_to_backup = call.data.get("need_to_backup")
            if need_to_sync is None or need_to_backup is None:
                status_result = await thies_service.get_thies_data(
                    ftp_port=request_data["ftp_port"],
                    ftp_host=request_data["ftp_host"],
                    ftp_user=request_data["ftp_user"],
                    ftp_password=request_data["ftp_password"],
                    sharepoint_destination_path=request_data[
                        "sharepoint_destination_path"
                    ],
                )
                if need_to_sync is None:
                    need_to_sync = status_result.get("need_to_sync", False)
                if need_to_backup is None:
                    need_to_backup = status_result.get("need_to_backup", False)

            result = await thies_service.post_thies_data(
                ftp_port=request_data["ftp_port"],
                ftp_host=request_data["ftp_host"],
                ftp_user=request_data["ftp_user"],
                ftp_password=request_data["ftp_password"],
                need_to_sync=bool(need_to_sync),
                need_to_backup=bool(need_to_backup),
                sharepoint_destination_path=request_data["sharepoint_destination_path"],
                ftp_server_folders_path=request_data["ftp_server_folders_path"],
                local_backup_source_path=request_data["local_backup_source_path"],
            )
            results.append({"entry_id": config_entry.entry_id, **result})

        return _format_multi_entry_response(results)

    async def async_detect_failures(self, call: ServiceCall) -> ServiceResponse:
        """Detect failures in THIES backups based on local backup and DB params."""
        logclient.method_name = "async_detect_failures"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)

        results: list[dict] = []
        for config_entry, entry_data in _iter_config_entry_contexts(call.hass):
            api: SaviiaAPI = entry_data["api"]
            thies_service = api.get("thies")

            local_backup_source_path = call.data["local_backup_source_path"]
            n_days = call.data["n_days"]
            db_driver = call.data.get("db_driver")
            db_host = call.data.get("db_host")
            db_name = call.data.get("db_name")
            user = call.data.get("user")
            pwd = call.data.get("pwd")

            result = await thies_service.detect_failures(
                local_backup_source_path=local_backup_source_path,
                n_days=n_days,
                db_driver=db_driver,
                db_host=db_host,
                db_name=db_name,
                user=user,
                pwd=pwd,
            )
            results.append({"entry_id": config_entry.entry_id, **result})

        return _format_multi_entry_response(results)
