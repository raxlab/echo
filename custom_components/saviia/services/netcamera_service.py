"""Netcamera-related SAVIIA services."""

from __future__ import annotations

from http import HTTPStatus

from homeassistant.core import ServiceCall, ServiceResponse
from saviialib import SaviiaAPI

from custom_components.saviia.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    InfoArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .common import _check_api_in_entry, _ensure_domain_setup

logclient = LogClient(
    LogClientArgs(
        client_name="logging", service_name="services", class_name="netcamera"
    )
)


class NetcameraService:
    """Netcamera service methods."""

    async def async_get_netcamera_rates(self, call: ServiceCall) -> ServiceResponse:
        """Get camera rates service."""
        logclient.method_name = "async_get_netcamera_rates"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
        camera_services = api.get("netcamera")
        try:
            # The underlying API instance uses its configured latitude/longitude.
            # Ignore any latitude/longitude passed via the service call.
            result = await camera_services.get_camera_rates()
            if result.get("status") != HTTPStatus.OK.value:
                logclient.error(
                    ErrorArgs(
                        status=LogStatus.ERROR,
                        metadata={"msg": result["message"]},
                    )
                )
            else:
                logclient.info(
                    InfoArgs(
                        status=LogStatus.SUCCESSFUL,
                        metadata={
                            "msg": f"Camera rates retrieved: {result.get('metadata')}"
                        },
                    )
                )
            return {
                "api_status": result.get("status"),
                "api_message": result.get("message"),
                "api_metadata": result.get("metadata"),
            }
        except Exception as e:
            logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": f"Error retrieving camera rates: {e}"},
                )
            )
            raise
