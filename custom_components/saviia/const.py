"""Constants variables."""

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_NAME, Platform


class GeneralParams:
    """General variables."""

    DOMAIN = "saviia"
    MANUFACTURER = "raxlab"
    CONFIG_SCHEMA = vol.Schema(
        {
            DOMAIN: vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=DOMAIN): cv.string,
                }
            )
        },
        extra=vol.ALLOW_EXTRA,
    )
    LOGGER = logging.getLogger(__package__)
    PLATFORMS = [Platform.SENSOR]


class ServicesParams:
    """Services parameters."""

    ALLOWED_CONFIG_KEYS = frozenset(
        {
            "sharepoint_tenant_name",
            "sharepoint_site_name",
            "sharepoint_avg_backup_folder_name",
            "sharepoint_ext_backup_folder_name",
            "local_backup_source_path",
            "sharepoint_backup_base_url",
            "latitude",
            "longitude",
        }
    )

    SERVICE_GET_THIES_DATA = "get_thies_data"
    SERVICE_GET_THIES_DATA_SCHEMA = vol.Schema(
        {
            vol.Required("ftp_port"): int,
            vol.Required("ftp_host"): cv.string,
            vol.Required("ftp_user"): cv.string,
            vol.Required("ftp_password"): cv.string,
            vol.Optional("sharepoint_destination_path"): cv.string,
        }
    )

    SERVICE_EXPORT_FILES = "export_files"
    SERVICE_EXPORT_FILES_SCHEMA = vol.Schema(
        {
            vol.Required("local_folder_path"): cv.string,
            vol.Optional("sharepoint_destination_path"): cv.string,
        }
    )

    SERVICE_POST_THIES_DATA = "post_thies_data"
    SERVICE_POST_THIES_DATA_SCHEMA = vol.Schema(
        {
            vol.Required("ftp_port"): int,
            vol.Required("ftp_host"): cv.string,
            vol.Required("ftp_user"): cv.string,
            vol.Required("ftp_password"): cv.string,
            vol.Optional("need_to_sync"): bool,
            vol.Optional("need_to_backup"): bool,
            vol.Optional("sharepoint_destination_path"): cv.string,
            vol.Optional("ftp_server_folders_path"): list,
            vol.Optional("local_backup_source_path"): cv.string,
        }
    )

    SERVICE_GET_NETCAMERA_RATES = "get_netcamera_rates"
    SERVICE_GET_NETCAMERA_RATES_SCHEMA = vol.Schema(
        {
            vol.Optional("latitude"): cv.latitude,
            vol.Optional("longitude"): cv.longitude,
        }
    )
    SERVICE_UPDATE_TASK = "update_task"
    SERVICE_UPDATE_TASK_SCHEMA = vol.Schema(
        {
            vol.Required("task"): dict,
            vol.Required("completed"): bool,
        }
    )
    SERVICE_DELETE_TASK = "delete_task"
    SERVICE_DELETE_TASK_SCHEMA = vol.Schema(
        {
            vol.Required("task_id"): cv.string,
        }
    )
    SERVICE_CREATE_TASK = "create_task"
    SERVICE_CREATE_TASK_SCHEMA = vol.Schema(
        {
            vol.Required("task"): dict,
            vol.Optional("images"): list,
        }
    )

    SERVICE_GET_TASKS = "get_tasks"
    SERVICE_GET_TASKS_SCHEMA = vol.Schema(
        {
            vol.Optional("params"): dict,
        }
    )
    SERVICE_GET_PENDING_TASKS = "get_pending_tasks"
    SERVICE_GET_PENDING_TASKS_SCHEMA = vol.Schema(
        {
            vol.Optional("download"): bool,
            vol.Optional("notify"): bool,
        }
    )

    SERVICE_DETECT_FAILURES = "detect_failures"
    SERVICE_DETECT_FAILURES_SCHEMA = vol.Schema(
        {
            vol.Required("local_backup_source_path"): str,
            vol.Required("n_days"): int,
            vol.Optional("db_driver"): str,
            vol.Optional("db_host"): str,
            vol.Optional("db_name"): str,
            vol.Optional("user"): str,
            vol.Optional("pwd"): str,
        }
    )

    SERVICE_GET_CONFIG_VALUE = "get_config_value"
    SERVICE_GET_CONFIG_VALUE_SCHEMA = vol.Schema(
        {
            vol.Required("key"): cv.string,
        }
    )

    SERVICE_ADD_PERSON = "add_person"
    SERVICE_ADD_PERSON_SCHEMA = vol.Schema(
        {
            vol.Required("person"): vol.Schema(
                {
                    vol.Required("id"): cv.string,
                    vol.Required("name"): cv.string,
                    vol.Required("email"): cv.string,
                    vol.Optional("discord"): cv.string,
                }
            ),
        }
    )

    SERVICE_DELETE_PERSON = "delete_person"
    SERVICE_DELETE_PERSON_SCHEMA = vol.Schema(
        {
            vol.Required("id"): cv.string,
        }
    )


class ConfigDefaultsParams:
    """Config flow default parameters."""

    # - THIES Data Logger Synchronization
    DEFAULT_SHAREPOINT_THIES_AVG_FOLDER = (
        "Shared%20Documents/General/Test_Raspberry/THIES/AVG"
    )
    DEFAULT_SHAREPOINT_THIES_EXT_FOLDER = (
        "Shared%20Documents/General/Test_Raspberry/THIES/EXT"
    )

    DEFAULT_FTP_PATH_AVG = "/ARCH_AV1"
    DEFAULT_FTP_PATH_EXT = "/ARCH_EX1"

    # - Local Backup
    DEFAULT_SHAREPOINT_BASE_URL = "/sites/uc365_CentrosyEstacionesRegionalesUC/Shared%20Documents/General/Test_Raspberry"
    DEFAULT_LOCAL_BACKUP_PATH = "/media/backup_local"
