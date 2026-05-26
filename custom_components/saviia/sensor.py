from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import GeneralParams
from .coordinator import NetcameraRatesCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SAVIIA sensor based on a config entry."""
    netcamera_rates_coordinator = hass.data[GeneralParams.DOMAIN][
        config_entry.entry_id
    ]["netcamera_rates_coordinator"]

    sensors = [
        SaviiaNetcameraRatesSensor(netcamera_rates_coordinator, config_entry),
    ]
    async_add_entities(sensors, update_before_add=True)


class SaviiaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for SAVIIA coordinator-backed sensors."""

    def __init__(
        self,
        coordinator: NetcameraRatesCoordinator,
        config_entry: ConfigEntry,
        attribute: str,
        name_suffix: str,
        icon: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_{attribute}"
        self._attr_name = f"{config_entry.title} - {name_suffix}"
        self._attribute = attribute
        self._attr_icon = icon or "mdi:file"
        self.coordinator = coordinator

    @property
    def data(self) -> dict[str, Any]:
        if isinstance(self.coordinator.data, dict):
            return self.coordinator.data
        return {}

    @property
    def metadata(self) -> dict[str, Any]:
        return self.data.get("metadata", {}).get("data", {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {
            "last_update": self.coordinator.last_update,
            "error": self.data.get("metadata", {}).get("error", {}),
        }


class SaviiaNetcameraRatesSensor(SaviiaBaseSensor):
    """Sensor to display netcamera time rates."""

    def __init__(self, coordinator, config_entry):
        super().__init__(
            coordinator,
            config_entry,
            attribute="netcamera_rates",
            name_suffix="Netcamera Time Rates",
            icon="mdi:camera-timer",
        )

    @property
    def metadata(self) -> dict[str, Any]:
        return self.data.get("metadata", {})

    @property
    def native_value(self) -> str | None:
        return self.data.get("metadata", {}).get("status", None)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        base = super().extra_state_attributes or {}
        return {
            **base,
            "photo_rate": self.metadata.get("photo_rate", -1),
            "video_rate": self.metadata.get("video_rate", -1),
            "precipitation": self.metadata.get("precipitation", -1),
            "precipitation_prob": self.metadata.get("precipitation_probability", -1),
        }
