from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from saviialib import SaviiaAPI

from custom_components.saviia.helpers.datetime_utils import datetime_to_str, today
from custom_components.saviia.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

from .const import GeneralParams


class SaviiaBaseCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: SaviiaAPI,
    ) -> None:
        """Set up the coordinator."""
        super().__init__(
            hass,
            GeneralParams.LOGGER,
            name=GeneralParams.MANUFACTURER,
            config_entry=config_entry,
            update_interval=None,
        )
        self.api = api
        self.config_entry = config_entry
        self.last_update: str | None = None
        self.data: dict[str, Any] = {}


class NetcameraRatesCoordinator(SaviiaBaseCoordinator):
    """Class to manage the Netcamera time rates fetching."""

    def __init__(self, hass, config_entry, api):
        super().__init__(hass, config_entry, api)
        self.name = "netcamera_rates_coordinator"
        self.latitude = config_entry.data["latitude"]
        self.longitude = config_entry.data["longitude"]
        self.update_interval = timedelta(minutes=10)
        self.camera_service = api.get("netcamera")
        self.logclient = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="coordinators",
                class_name="netcamera_rates_coordinator",
            )
        )

    async def _async_update_data(self) -> dict:
        """Fetch netcamera time rates based on latitude and longitude."""
        self.logclient.method_name = "_async_update_data"
        self.logclient.debug(
            DebugArgs(
                status=LogStatus.STARTED,
                metadata={"msg": "Netcamera rates fetching started"},
            )
        )
        try:
            netcamera_rates = await self.camera_service.get_camera_rates(
                latitude=self.latitude,
                longitude=self.longitude,
            )
            self.data = netcamera_rates
            self.last_update = datetime_to_str(today())
            self.logclient.debug(
                DebugArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={
                        "msg": f"Netcamera rates fetching completed. Data: {netcamera_rates}"
                    },
                )
            )
            return {"netcamera_rates": netcamera_rates}
        except Exception as e:
            self.logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": e.__str__()},
                )
            )
            raise
