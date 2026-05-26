"""Task-related SAVIIA services."""

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
    LogClientArgs(client_name="logging", service_name="services", class_name="tasks")
)


class TaskService:
    """Task service methods."""

    async def async_update_task(self, call: ServiceCall) -> ServiceResponse:
        """Update a Task in a Discord channel."""
        logclient.method_name = "async_update_task"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
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

    async def async_delete_task(self, call: ServiceCall) -> ServiceResponse:
        """Delete a Task in a Discord channel."""
        logclient.method_name = "async_delete_task"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
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

    async def async_create_task(self, call: ServiceCall) -> ServiceResponse:
        """Create a Task in a Discord channel."""
        logclient.method_name = "async_create_task"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
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

    async def async_get_tasks(self, call: ServiceCall) -> ServiceResponse:
        """Get all the tasks stored in the Discord channel."""
        logclient.method_name = "async_get_tasks"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
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

    async def async_get_pending_tasks(self, call: ServiceCall) -> ServiceResponse:
        """Get all the pending tasks."""
        logclient.method_name = "async_get_pending_tasks"
        logclient.debug(DebugArgs(status=LogStatus.STARTED))
        _ensure_domain_setup(call.hass)
        api: SaviiaAPI = _check_api_in_entry(call.hass)
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
