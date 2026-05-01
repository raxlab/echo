"""Provides services for SAVIIA integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import (
        HomeAssistant,
        ServiceCall,
        ServiceResponse,
    )


from http import HTTPStatus

from homeassistant.core import (
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError
from saviialib import SaviiaAPI

from custom_components.saviia.const import (
    GeneralParams,
    ServicesParams,
)
from custom_components.saviia.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    InfoArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
)

logclient = LogClient(
    LogClientArgs(client_name="logging", service_name="services", class_name="services")
)


def _ensure_domain_setup(hass) -> None:
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


def _check_api_in_entry(hass) -> SaviiaAPI:
    api_exists = False
    api: SaviiaAPI
    for entry_data in hass.data[GeneralParams.DOMAIN].values():
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


def _get_config_entry_data(hass) -> dict:
    """Get config entry data for the integration."""
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


async def async_get_config_value(call: ServiceCall) -> ServiceResponse:
    """Return a safe config flow value from config entry data."""
    logclient.method_name = "async_get_config_value"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)

    key = call.data.get("key")
    if key not in ServicesParams.ALLOWED_CONFIG_KEYS:
        error_message = (
            f"The requested key '{key}' is not allowed. "
            "This service only exposes a safe whitelist of config keys."
        )
        logclient.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": error_message},
            )
        )
        raise HomeAssistantError(error_message)

    config_data = _get_config_entry_data(call.hass)
    if key not in config_data:
        error_message = f"Key '{key}' was not found in SAVIIA config entry data"
        logclient.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": error_message},
            )
        )
        raise HomeAssistantError(error_message)

    return {
        "key": key,
        "value": config_data[key],
    }


async def async_sync_thies_files(call: ServiceCall) -> None:
    """File synchronization."""
    logclient.method_name = "async_sync_thies_files"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    hass = call.hass
    _ensure_domain_setup(hass)

    for entry_id in hass.data[GeneralParams.DOMAIN]:
        if entry_id == "services_registered":
            continue

        coordinator = hass.data[GeneralParams.DOMAIN][entry_id]["thies_coordinator"]
        if not coordinator:
            continue
        try:
            success = await coordinator.async_request_refresh()
            logclient.info(
                InfoArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": "File sync successful"},
                )
            )
            if success:
                metadata = coordinator.data.get("metadata")
                logclient.debug(
                    DebugArgs(
                        status=LogStatus.SUCCESSFUL,
                        metadata={"msg": f"Metadata: {metadata}"},
                    )
                )

        except Exception as e:
            logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": e.__str__()},
                )
            )
            raise


async def async_detect_failures(call: ServiceCall) -> ServiceResponse:
    logclient.method_name = "async_detect_failures"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    thies_service = api.get("thies")
    try:
        local_backup_source_path, n_days, db_driver, db_host, db_name, user, pwd = (
            call.data.get("local_backup_source_path"),
            call.data.get("n_days"),
            call.data.get("db_driver", ""),
            call.data.get("db_host", ""),
            call.data.get("db_name", ""),
            call.data.get("user", ""),
            call.data.get("pwd", ""),
        )
        result = await thies_service.detect_failures(
            local_backup_source_path, n_days, db_driver, db_host, db_name, user, pwd
        )
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
                        "msg": f"The validation for thies sensors was successful: {result.get('metadata')}"
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
                metadata={"msg": f"Error during the thies sensor validation: {e}"},
            )
        )
        raise


async def async_local_backup(call: ServiceCall) -> None:
    logclient.method_name = "async_local_backup"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    hass = call.hass
    _ensure_domain_setup(hass)

    for entry_id in hass.data[GeneralParams.DOMAIN]:
        if entry_id == "services_registered":
            continue
        coordinator = hass.data[GeneralParams.DOMAIN][entry_id][
            "local_backup_coordinator"
        ]
        try:
            success = await coordinator.async_request_refresh()
            logclient.info(
                InfoArgs(
                    status=LogStatus.SUCCESSFUL,
                    metadata={"msg": "Local backup successful"},
                )
            )
            if success:
                metadata = coordinator.data.get("metadata")
                logclient.debug(
                    DebugArgs(
                        status=LogStatus.SUCCESSFUL,
                        metadata={"msg": f"Metadata: {metadata}"},
                    )
                )
        except Exception as e:
            logclient.error(
                ErrorArgs(
                    status=LogStatus.ERROR,
                    metadata={"msg": e.__str__()},
                )
            )
            raise


async def async_get_netcamera_rates(call: ServiceCall) -> ServiceResponse:
    """Get camera rates service."""
    logclient.method_name = "async_get_netcamera_rates"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    camera_services = api.get("netcamera")
    try:
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


async def async_update_task(call: ServiceCall) -> ServiceResponse:
    """Update a Task in a Discord channel."""
    logclient.method_name = "async_update_task"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    task_service = api.get("tasks")
    try:
        task, completed = call.data.get("task"), call.data.get("completed")
        result = await task_service.update_task(task, completed)
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
                        "msg": f"Task updated successfully: {result.get('metadata')}"
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
                metadata={"msg": f"Error updating task: {e}"},
            )
        )
        raise


async def async_delete_task(call: ServiceCall) -> ServiceResponse:
    """Delete a Task in a Discord channel."""
    logclient.method_name = "async_delete_task"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    task_service = api.get("tasks")
    try:
        task_id = call.data.get("task_id")
        result = await task_service.delete_task(task_id)
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
                        "msg": f"Task deleted successfully: {result.get('metadata')}"
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
                metadata={"msg": f"Error deleting task: {e}"},
            )
        )
        raise


async def async_create_task(call: ServiceCall) -> ServiceResponse:
    """Create a Task in a Discord channel."""
    logclient.method_name = "async_create_task"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    task_service = api.get("tasks")
    try:
        task, images = call.data.get("task"), call.data.get("images", [])
        result = await task_service.create_task(task, images)
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
                        "msg": f"Task created successfully: {result.get('metadata')}"
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
                metadata={"msg": f"Error creating task: {e}"},
            )
        )
        raise


async def async_get_tasks(call: ServiceCall) -> ServiceResponse:
    """Get all the tasks stored in the Discord channel."""
    logclient.method_name = "async_get_tasks"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    task_service = api.get("tasks")
    try:
        params = call.data.get("params", {})
        result = await task_service.get_tasks(params)
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
                        "msg": f"Tasks fetched successfully: {result.get('metadata')}"
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
                metadata={"msg": f"Error creating task: {e}"},
            )
        )
        raise


async def async_get_pending_tasks(call: ServiceCall) -> ServiceResponse:
    """Get all the pending tasks."""
    logclient.method_name = "async_get_pending_tasks"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    api = _check_api_in_entry(call.hass)
    task_service = api.get("tasks")
    try:
        download = call.data.get("download", False)
        notify = call.data.get("notify", False)
        result = await task_service.get_pending_tasks(download, notify)
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
                        "msg": f"Pending tasks fetched successfully: {result.get('metadata')}"
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
                metadata={"msg": f"Error while retrieving the pending task: {e}"},
            )
        )
        raise


async def async_add_person(call: ServiceCall) -> ServiceResponse:
    """Store a person in local SAVIIA storage."""
    logclient.method_name = "async_add_person"
    logclient.debug(DebugArgs(status=LogStatus.STARTED))
    _ensure_domain_setup(call.hass)
    person = call.data["person"]

    for entry_id in call.hass.data[GeneralParams.DOMAIN]:
        if entry_id in {"services_registered", "websocket_registered"}:
            continue
        storage = call.hass.data[GeneralParams.DOMAIN][entry_id]["storage"]
        await storage.async_add_person(person)

    logclient.info(
        InfoArgs(
            status=LogStatus.SUCCESSFUL,
            metadata={"msg": f"Person '{person['id']}' added successfully"},
        )
    )
    return {
        "status": "success",
        "person": person,
    }


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the SAVIIA integration."""
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_SYNC_FILES,
        async_sync_thies_files,
        schema=ServicesParams.SERVICE_SYNC_FILES_SCHEMA,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_LOCAL_BACKUP,
        async_local_backup,
        schema=ServicesParams.SERVICE_LOCAL_BACKUP_SCHEMA,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_GET_NETCAMERA_RATES,
        async_get_netcamera_rates,
        schema=ServicesParams.SERVICE_GET_NETCAMERA_RATES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_UPDATE_TASK,
        async_update_task,
        schema=ServicesParams.SERVICE_UPDATE_TASK_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_DELETE_TASK,
        async_delete_task,
        schema=ServicesParams.SERVICE_DELETE_TASK_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_CREATE_TASK,
        async_create_task,
        schema=ServicesParams.SERVICE_CREATE_TASK_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_GET_TASKS,
        async_get_tasks,
        schema=ServicesParams.SERVICE_GET_TASKS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_DETECT_FAILURES,
        async_detect_failures,
        schema=ServicesParams.SERVICE_DETECT_FAILURES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_GET_PENDING_TASKS,
        async_get_pending_tasks,
        schema=ServicesParams.SERVICE_GET_PENDING_TASKS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_GET_CONFIG_VALUE,
        async_get_config_value,
        schema=ServicesParams.SERVICE_GET_CONFIG_VALUE_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        GeneralParams.DOMAIN,
        ServicesParams.SERVICE_ADD_PERSON,
        async_add_person,
        schema=ServicesParams.SERVICE_ADD_PERSON_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for the SAVIIA integration."""
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_SYNC_FILES)
    hass.services.async_remove(
        GeneralParams.DOMAIN, ServicesParams.SERVICE_LOCAL_BACKUP
    )
    hass.services.async_remove(
        GeneralParams.DOMAIN, ServicesParams.SERVICE_GET_NETCAMERA_RATES
    )
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_UPDATE_TASK)
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_DELETE_TASK)
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_CREATE_TASK)
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_GET_TASKS)
    hass.services.async_remove(
        GeneralParams.DOMAIN, ServicesParams.SERVICE_GET_PENDING_TASKS
    )
    hass.services.async_remove(
        GeneralParams.DOMAIN, ServicesParams.SERVICE_DETECT_FAILURES
    )
    hass.services.async_remove(
        GeneralParams.DOMAIN, ServicesParams.SERVICE_GET_CONFIG_VALUE
    )
    hass.services.async_remove(GeneralParams.DOMAIN, ServicesParams.SERVICE_ADD_PERSON)
