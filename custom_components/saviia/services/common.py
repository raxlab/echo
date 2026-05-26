"""Shared helpers for SAVIIA services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from saviialib import SaviiaAPI

from custom_components.saviia.const import GeneralParams
from custom_components.saviia.libs.log_client import (
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="common")
)


def _ensure_domain_setup(hass: HomeAssistant) -> None:
    logclient.method_name = "_ensure_domain_setup"
    if GeneralParams.DOMAIN not in hass.data:
        error_message = (
            f"[service] No data found for {GeneralParams.DOMAIN}. "
            "Ensure the integration is properly set up before calling this service."
        )
        logclient.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": error_message},
            )
        )
        raise ValueError(error_message)


def _check_api_in_entry(hass: HomeAssistant) -> SaviiaAPI:
    api_exists = False
    api: SaviiaAPI
    for _, entry_data in _iter_domain_entries(hass):
        try:
            if entry_data.get("api"):
                api_exists = True
                api = entry_data["api"]
                break
        except AttributeError:
            continue
    if not api_exists:
        error_message = "No API instance found in any config entry"
        logclient.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": error_message},
            )
        )
        raise ValueError(error_message)
    return api


def _iter_domain_entries(hass: HomeAssistant) -> Iterable[tuple[str, dict[str, Any]]]:
    domain_data = hass.data[GeneralParams.DOMAIN]
    for entry_id, entry_data in domain_data.items():
        if not isinstance(entry_data, dict):
            continue
        if entry_id in {"services_registered", "websocket_registered"}:
            continue
        yield entry_id, entry_data


def _iter_config_entry_contexts(
    hass: HomeAssistant,
) -> Iterable[tuple[ConfigEntry, dict[str, Any]]]:
    domain_data = hass.data[GeneralParams.DOMAIN]
    for config_entry in hass.config_entries.async_entries(GeneralParams.DOMAIN):
        entry_data = domain_data.get(config_entry.entry_id)
        if not isinstance(entry_data, dict):
            continue
        yield config_entry, entry_data


def _get_config_entry_data(hass: HomeAssistant) -> dict[str, Any]:
    """Get config flow data from the first config entry."""
    logclient.method_name = "_get_config_entry_data"
    entries = hass.config_entries.async_entries(GeneralParams.DOMAIN)
    if not entries:
        error_message = "No config entry found for SAVIIA"
        logclient.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": error_message},
            )
        )
        raise HomeAssistantError(error_message)

    return dict(entries[0].data)


def _resolve_thies_call_data(
    config_entry: ConfigEntry, call: ServiceCall
) -> dict[str, Any]:
    config_data = config_entry.data
    sharepoint_destination_path = call.data.get(
        "sharepoint_destination_path"
    ) or config_data.get("sharepoint_avg_backup_folder_name")
    if not sharepoint_destination_path:
        msg = "No SharePoint destination path available for the THIES service"
        raise HomeAssistantError(msg)

    return {
        "ftp_port": call.data["ftp_port"],
        "ftp_host": call.data["ftp_host"],
        "ftp_user": call.data["ftp_user"],
        "ftp_password": call.data["ftp_password"],
        "sharepoint_destination_path": sharepoint_destination_path,
        "ftp_server_folders_path": call.data.get(
            "ftp_server_folders_path",
            [
                config_data["thies_ftp_server_avg_path"],
                config_data["thies_ftp_server_ext_path"],
            ],
        ),
        "local_backup_source_path": call.data.get(
            "local_backup_source_path",
            config_data["local_backup_source_path"],
        ),
    }


def _format_multi_entry_response(results: list[dict[str, Any]]) -> dict[str, Any]:
    if len(results) == 1:
        return results[0]
    return {"results": results}
