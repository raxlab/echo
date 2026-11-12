"""Regression checks against the published saviialib 1.21.0 API signatures."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, create_autospec, patch

import pytest
import voluptuous as vol
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from saviialib import SaviiaAPI, SaviiaAPIConfig

from custom_components.saviia import async_setup_entry
from custom_components.saviia.config_flow import SaviiaConfigFlow
from custom_components.saviia.const import ServicesParams
from custom_components.saviia.services.backup_service import BackupService
from custom_components.saviia.services.system_service import SystemService
from custom_components.saviia.services.thies_service import ThiesService

CLOUD = {
    "databricks_host_url": "https://example.azuredatabricks.net",
    "databricks_api_key": "test-token",
    "cloud_provider_destination_path": "/Volumes/catalog/schema/telemetry",
}
FTP = {
    "ftp_port": 8888,
    "ftp_host": "localhost",
    "ftp_user": "anonymous",
    "ftp_password": "test-password",
}


@pytest.fixture
def context() -> SimpleNamespace:
    """Use real API instances as autospecs so removed arguments raise TypeError."""
    real_api = SaviiaAPI(
        SaviiaAPIConfig(
            databricks_host_url=CLOUD["databricks_host_url"],
            databricks_api_key=CLOUD["databricks_api_key"],
            logger=logging.getLogger(__name__),
            local_backup_path="/media/backup_local",
        )
    )
    thies = create_autospec(real_api.get("thies"), instance=True)
    backup = create_autospec(real_api.get("backup"), instance=True)
    thies.get_thies_data.return_value = {
        "status": 200,
        "metadata": {"data": {"need_to_sync": True, "need_to_backup": True}},
    }
    thies.post_thies_data.return_value = {"status": 200}
    backup.export_files.return_value = {"status": 200}
    api = MagicMock()
    api.get.side_effect = {"thies": thies, "backup": backup}.__getitem__
    entry = SimpleNamespace(
        entry_id="existing-entry",
        data={**CLOUD, "local_backup_source_path": "/media/backup_local"},
    )
    hass = SimpleNamespace(
        data={"saviia": {entry.entry_id: {"api": api}}},
        config_entries=SimpleNamespace(async_entries=lambda _: [entry]),
    )
    return SimpleNamespace(entry=entry, hass=hass, thies=thies, backup=backup)


def service_call(context: SimpleNamespace, data: dict) -> SimpleNamespace:
    """Create the portion of a Home Assistant service call consumed by the handlers."""
    return SimpleNamespace(hass=context.hass, data=data)


@pytest.mark.asyncio
async def test_get_uses_databricks_signature(context: SimpleNamespace) -> None:
    """The service forwards the configured destination and preserves nested data."""
    result = await ThiesService().async_get_thies_data(service_call(context, FTP))
    context.thies.get_thies_data.assert_awaited_once_with(
        **FTP, cloud_provider_destination_path=CLOUD["cloud_provider_destination_path"]
    )
    assert result["metadata"]["data"]["need_to_sync"] is True
    assert result["entry_id"] == context.entry.entry_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "flags", [{}, {"need_to_sync": False}, {"need_to_backup": False}]
)
async def test_post_reads_nested_flags(
    context: SimpleNamespace, flags: dict[str, bool]
) -> None:
    """Automatic planning reads metadata.data without replacing explicit false flags."""
    await ThiesService().async_post_thies_data(service_call(context, {**FTP, **flags}))
    context.thies.post_thies_data.assert_awaited_once_with(
        **FTP,
        need_to_sync=flags.get("need_to_sync", True),
        need_to_backup=flags.get("need_to_backup", True),
        cloud_provider_destination_path=CLOUD["cloud_provider_destination_path"],
        ftp_server_folders_path=["/ARCH_AV1", "/ARCH_EX1"],
    )


@pytest.mark.asyncio
async def test_post_with_both_flags_skips_planning(context: SimpleNamespace) -> None:
    """Custom FTP paths and destinations are passed through with explicit flags."""
    data = {
        **FTP,
        "need_to_sync": False,
        "need_to_backup": True,
        "cloud_provider_destination_path": "/Volumes/catalog/schema/override",
        "ftp_server_folders_path": ["/custom/ARCH_AV1", "/custom/ARCH_EX1"],
    }
    await ThiesService().async_post_thies_data(service_call(context, data))
    context.thies.get_thies_data.assert_not_awaited()
    context.thies.post_thies_data.assert_awaited_once_with(**data)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        {"status": 500, "metadata": {"error": "FTP unavailable"}},
        {"status": 200, "metadata": {"data": {}}},
    ],
)
async def test_failed_or_incomplete_status_does_not_post(
    context: SimpleNamespace, response: dict
) -> None:
    """A failed lookup must not be reported as a successful no-op."""
    context.thies.get_thies_data.return_value = response
    with pytest.raises(HomeAssistantError, match="Unable to determine"):
        await ThiesService().async_post_thies_data(service_call(context, FTP))
    context.thies.post_thies_data.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("override", [None, "/Volumes/catalog/schema/override"])
async def test_export_uses_databricks_signature(
    context: SimpleNamespace, override: str | None
) -> None:
    """Backup exports accept default and per-call Databricks destinations."""
    data = {"local_folder_path": "thies/EXT"}
    if override:
        data["cloud_provider_destination_path"] = override
    await BackupService().async_export_files(service_call(context, data))
    context.backup.export_files.assert_awaited_once_with(
        local_folder_path="thies/EXT",
        cloud_provider_destination_path=override
        or CLOUD["cloud_provider_destination_path"],
    )


@pytest.mark.asyncio
async def test_missing_databricks_credentials_requests_reauth(
    context: SimpleNamespace,
) -> None:
    """Existing SharePoint entries request new settings before API initialization."""
    context.entry.data = {"sharepoint_client_id": "legacy-client"}
    with pytest.raises(ConfigEntryAuthFailed, match="Databricks"):
        await async_setup_entry(context.hass, context.entry)


@pytest.mark.asyncio
async def test_setup_initializes_the_published_databricks_api(
    context: SimpleNamespace,
) -> None:
    """Home Assistant setup creates all APIs with Databricks settings."""
    context.hass.data["saviia"].update(
        services_registered=True, websocket_registered=True
    )
    context.hass.config_entries.async_forward_entry_setups = AsyncMock()
    coordinator = SimpleNamespace(
        name="netcamera_rates_coordinator", async_config_entry_first_refresh=AsyncMock()
    )
    with (
        patch(
            "custom_components.saviia.NetcameraRatesCoordinator",
            return_value=coordinator,
        ),
        patch("custom_components.saviia.SaviiaStorage"),
    ):
        assert await async_setup_entry(context.hass, context.entry)
    api = context.hass.data["saviia"][context.entry.entry_id]["api"]
    assert api.get("thies").config.databricks_host_url == CLOUD["databricks_host_url"]
    assert api.get("backup").config.databricks_api_key == CLOUD["databricks_api_key"]
    assert api.get("thies").config.local_backup_path == "/media/backup_local"
    assert set(api.list_available()) == {"thies", "backup", "netcamera", "tasks"}


@pytest.mark.asyncio
async def test_new_setup_collects_databricks_fields() -> None:
    """New entries use the three Databricks fields and a local backup root."""
    flow = SaviiaConfigFlow()
    result = await flow.async_step_user(CLOUD)
    assert result["type"] == "create_entry"
    assert result["data"]["databricks_host_url"] == CLOUD["databricks_host_url"]
    assert result["data"]["local_backup_source_path"] == "/media/backup_local"
    assert not any(key.startswith("sharepoint_") for key in result["data"])


@pytest.mark.asyncio
async def test_reauth_preserves_existing_settings(context: SimpleNamespace) -> None:
    """Migration updates the original entry and retains local/task/email settings."""
    previous = {
        "local_backup_source_path": "/media/existing-backup",
        "latitude": -46.2,
        "longitude": -73.4,
        "bot_token": "test-discord-token",
        "task_channel_id": "test-channel",
        "email_address": "test@example.com",
        "email_password": "test-email-password",
    }
    context.entry.data = {**previous, "sharepoint_client_id": "legacy-client"}
    flow = SaviiaConfigFlow()
    with (
        patch.object(flow, "_get_reauth_entry", return_value=context.entry),
        patch.object(
            flow, "async_update_reload_and_abort", return_value={"type": "abort"}
        ) as update,
    ):
        form = await flow.async_step_reauth(context.entry.data)
        assert form["step_id"] == "reauth_confirm"
        await flow.async_step_reauth_confirm(CLOUD)
    update.assert_called_once_with(context.entry, data={**previous, **CLOUD})


@pytest.mark.asyncio
async def test_config_service_does_not_expose_token(context: SimpleNamespace) -> None:
    """The public get_config_value service must reject the Databricks token."""
    with pytest.raises(HomeAssistantError, match="not allowed"):
        await SystemService().async_get_config_value(
            service_call(context, {"key": "databricks_api_key"})
        )


def test_service_schema_rejects_removed_post_override() -> None:
    """Do not silently ignore an override that saviialib no longer supports."""
    with pytest.raises(vol.Invalid):
        ServicesParams.SERVICE_POST_THIES_DATA_SCHEMA(
            {**FTP, "local_backup_source_path": "/other/backup"}
        )


@pytest.mark.asyncio
async def test_reauth_rejects_invalid_volume_without_updating(
    context: SimpleNamespace,
) -> None:
    """A legacy SharePoint path must not be reused as a Databricks volume."""
    flow = SaviiaConfigFlow()
    with (
        patch.object(flow, "_get_reauth_entry", return_value=context.entry),
        patch.object(flow, "async_update_reload_and_abort") as update,
    ):
        result = await flow.async_step_reauth_confirm(
            {**CLOUD, "cloud_provider_destination_path": "Shared Documents/THIES"}
        )
    assert result["errors"] == {"base": "invalid_schema"}
    update.assert_not_called()
