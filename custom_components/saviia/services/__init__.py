"""Service registration for SAVIIA."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, SupportsResponse

from custom_components.saviia.const import GeneralParams, ServicesParams

from .backup_service import BackupService
from .netcamera_service import NetcameraService
from .storage_service import StorageService
from .system_service import SystemService
from .task_service import TaskService
from .thies_service import ThiesService

__all__ = ["async_setup_services", "async_unload_services"]


class SaviiaServiceRegistry:
    """Register and unload SAVIIA services by domain."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._task_service = TaskService()
        self._thies_service = ThiesService()
        self._backup_service = BackupService()
        self._netcamera_service = NetcameraService()
        self._storage_service = StorageService()
        self._system_service = SystemService(self._storage_service)

    def _register(self, service_name: str, handler, schema) -> None:
        self._hass.services.async_register(
            GeneralParams.DOMAIN,
            service_name,
            handler,
            schema=schema,
            supports_response=SupportsResponse.ONLY,
        )

    def _remove(self, service_name: str) -> None:
        self._hass.services.async_remove(GeneralParams.DOMAIN, service_name)

    async def async_setup(self) -> None:
        """Set up the integration services."""
        self._register(
            ServicesParams.SERVICE_GET_THIES_DATA,
            self._thies_service.async_get_thies_data,
            ServicesParams.SERVICE_GET_THIES_DATA_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_POST_THIES_DATA,
            self._thies_service.async_post_thies_data,
            ServicesParams.SERVICE_POST_THIES_DATA_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_EXPORT_FILES,
            self._backup_service.async_export_files,
            ServicesParams.SERVICE_EXPORT_FILES_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_GET_NETCAMERA_RATES,
            self._netcamera_service.async_get_netcamera_rates,
            ServicesParams.SERVICE_GET_NETCAMERA_RATES_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_UPDATE_TASK,
            self._task_service.async_update_task,
            ServicesParams.SERVICE_UPDATE_TASK_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_DELETE_TASK,
            self._task_service.async_delete_task,
            ServicesParams.SERVICE_DELETE_TASK_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_CREATE_TASK,
            self._task_service.async_create_task,
            ServicesParams.SERVICE_CREATE_TASK_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_GET_TASKS,
            self._task_service.async_get_tasks,
            ServicesParams.SERVICE_GET_TASKS_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_GET_PENDING_TASKS,
            self._task_service.async_get_pending_tasks,
            ServicesParams.SERVICE_GET_PENDING_TASKS_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_GET_CONFIG_VALUE,
            self._system_service.async_get_config_value,
            ServicesParams.SERVICE_GET_CONFIG_VALUE_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_ADD_PERSON,
            self._system_service.async_add_person,
            ServicesParams.SERVICE_ADD_PERSON_SCHEMA,
        )
        self._register(
            ServicesParams.SERVICE_DELETE_PERSON,
            self._system_service.async_delete_person,
            ServicesParams.SERVICE_DELETE_PERSON_SCHEMA,
        )

    async def async_unload(self) -> None:
        """Unload integration services."""
        for service_name in (
            ServicesParams.SERVICE_GET_THIES_DATA,
            ServicesParams.SERVICE_POST_THIES_DATA,
            ServicesParams.SERVICE_EXPORT_FILES,
            ServicesParams.SERVICE_GET_NETCAMERA_RATES,
            ServicesParams.SERVICE_UPDATE_TASK,
            ServicesParams.SERVICE_DELETE_TASK,
            ServicesParams.SERVICE_CREATE_TASK,
            ServicesParams.SERVICE_GET_TASKS,
            ServicesParams.SERVICE_GET_PENDING_TASKS,
            ServicesParams.SERVICE_GET_CONFIG_VALUE,
            ServicesParams.SERVICE_ADD_PERSON,
            ServicesParams.SERVICE_DELETE_PERSON,
        ):
            self._remove(service_name)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the integration services."""
    await SaviiaServiceRegistry(hass).async_setup()


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload integration services."""
    await SaviiaServiceRegistry(hass).async_unload()
