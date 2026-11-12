"""Config flow for SAVIIA integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector
import voluptuous as vol
from homeassistant import config_entries

from custom_components.saviia.const import ConfigDefaultsParams, GeneralParams

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

from custom_components.saviia.libs.log_client import (
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

logclient = LogClient(
    LogClientArgs(
        client_name="logging", service_name="config_flow", class_name="config_flow"
    )
)


class SaviiaConfigFlow(config_entries.ConfigFlow, domain=GeneralParams.DOMAIN):
    """Config flow for Thies Data Logger."""

    VERSION = 1

    def _get_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                **self._get_cloud_schema().schema,
                vol.Required(
                    "local_backup_source_path",
                    default=ConfigDefaultsParams.DEFAULT_LOCAL_BACKUP_PATH,
                ): cv.string,
                vol.Optional("latitude"): cv.latitude,
                vol.Optional("longitude"): cv.longitude,
                # Task Creation Parameters
                vol.Optional("bot_token", default=""): cv.string,
                vol.Optional("task_channel_id", default=""): cv.string,
                # Email client notification
                vol.Optional("email_address", default=""): cv.string,
                vol.Optional("email_password", default=""): cv.string,
            }
        )

    def _get_cloud_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("databricks_host_url"): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                ),
                vol.Required("databricks_api_key"): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required("cloud_provider_destination_path"): str,
            }
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:  # noqa: ARG002
        """Collect Databricks settings for an existing SharePoint entry."""
        return await self.async_step_reauth_confirm()

    @staticmethod
    def _validate_cloud_data(data: dict[str, Any]) -> None:
        """Validate Databricks configuration on the backend."""
        validation_schema = vol.Schema(
            {
                vol.Required("databricks_host_url"): cv.url,
                vol.Required("databricks_api_key"): vol.All(
                    cv.string, vol.Length(min=1)
                ),
                vol.Required("cloud_provider_destination_path"): vol.All(
                    cv.string,
                    vol.Match(r"^/Volumes/[^/]+/[^/]+/[^/]+(?:/.*)?$"),
                ),
            },
            extra=vol.ALLOW_EXTRA,
        )

        validation_schema(data)

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Update the same entry, retaining local paths and notification settings."""
        entry = self._get_reauth_entry()
        errors = {}
        if user_input is not None:
            try:
                cloud_data = self._get_cloud_schema()(user_input)
                self._validate_cloud_data(cloud_data)
            except vol.Invalid:
                errors["base"] = "invalid_schema"
            else:
                data = {
                    key: value
                    for key, value in entry.data.items()
                    if not key.startswith("sharepoint_")
                }
                data.update(cloud_data)
                return self.async_update_reload_and_abort(entry, data=data)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=self._get_cloud_schema(),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                data = self._get_schema()(user_input)
                self._validate_cloud_data(data)

                return self.async_create_entry(
                    title="SAVIIA Credentials",
                    data=data,
                )
            except ValueError as e:
                logclient.error(
                    ErrorArgs(
                        status=LogStatus.ERROR,
                        metadata={"msg": f"Value error during config flow: {e}"},
                    )
                )
                errors["base"] = "invalid_input"
            except vol.Invalid as e:
                logclient.error(
                    ErrorArgs(
                        status=LogStatus.ERROR,
                        metadata={"msg": f"Schema validation error: {e}"},
                    )
                )
                errors["base"] = "invalid_schema"
            except OSError as e:
                logclient.error(
                    ErrorArgs(
                        status=LogStatus.ERROR,
                        metadata={"msg": f"OS error during config flow: {e}"},
                    )
                )
                errors["base"] = "os_error"
            except RuntimeError as e:
                logclient.error(
                    ErrorArgs(
                        status=LogStatus.ERROR,
                        metadata={"msg": f"Runtime error during config flow: {e}"},
                    )
                )
                errors["base"] = "runtime_error"

        return self.async_show_form(
            step_id="user", data_schema=self._get_schema(), errors=errors
        )
