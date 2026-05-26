"""Config flow for SAVIIA integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from custom_components.saviia.const import GeneralParams

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
                vol.Required(
                    "sharepoint_client_id",
                ): str,
                vol.Required(
                    "sharepoint_client_secret",
                ): str,
                vol.Required(
                    "sharepoint_tenant_id",
                ): str,
                vol.Required(
                    "sharepoint_tenant_name",
                ): str,
                vol.Required(
                    "sharepoint_site_name",
                ): str,  # THIES Data Logger Parameters
                vol.Required("sharepoint_avg_backup_folder_name"): str,
                vol.Required(
                    "sharepoint_ext_backup_folder_name"
                ): str,  # Local Backup Parameters
                vol.Required("local_backup_source_path"): str,
                vol.Required("sharepoint_backup_base_url"): str,
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                return self.async_create_entry(
                    title="SAVIIA Credentials", data=user_input
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
