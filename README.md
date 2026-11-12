# ECHO

### *Edge Computing & Hardware Orchestration*

Home Assistant integration for remote data extraction, processing, and orchestration for  UC Centers and Field Stations Network (RCER UC). 

![ECHO](images/icon.png)


## Installation via HACS

1. The **ECHO integration** is not part of the HACS Store. To install it, you will need to add it as a *custom repository* by following this guide: [HACS Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories/).
2. Download the integration by entering the repository URL and adding it. Then, go to HACS and install it.
3. Once the installation is complete, **restart** Home Assistant.
4. After restarting, navigate to the **Integrations page** to configure the service.


## Service Configuration

ECHO 8.0.0 uses `saviialib==1.21.0` for THIES extraction, local backups,
Databricks synchronization, and alert/task orchestration.

### Databricks configuration

- **databricks_host_url**: Workspace URL, e.g. `https://your-workspace.azuredatabricks.net`.
- **databricks_api_key**: API token with access to the destination volume.
- **cloud_provider_destination_path**: Volume base path, e.g. `/Volumes/catalog/schema/volume`.
- **local_backup_source_path**: Existing local backup root, e.g. `/media/backup_local`.

The integration also accepts **latitude**, **longitude**, **bot_token**,
**task_channel_id**, **email_address**, and **email_password** for camera scheduling,
Discord tasks, and Gmail SMTP notifications. Cloud credentials are not returned by
`saviia.get_config_value`.

### Upgrading from SharePoint

After installing 8.0.0 and restarting Home Assistant, existing SharePoint entries
request new Databricks settings through the integration's reauthentication dialog.
Enter the workspace URL, token, and volume base path. The existing entry is updated;
its local backup path, location, Discord/email settings, and entry ID are retained.
Old SharePoint settings are removed after submission. Existing cloud files are not
moved or copied by this configuration step.

Update automations as follows:

- Replace `sharepoint_destination_path` with `cloud_provider_destination_path`
  in `get_thies_data`, `post_thies_data`, and `export_files`. Omit it to use the
  configured volume base path.
- Remove `local_backup_source_path` from `post_thies_data`: version 1.21.0 uses
  the local root configured on the API. The separate `detect_failures` action
  still accepts its own local path.
- Read sync flags from `response.metadata.data.need_to_sync` and
  `response.metadata.data.need_to_backup`. If either flag is omitted from
  `post_thies_data`, the integration fetches the status and fills it in;
  explicit `false` values are retained. A failed status lookup stops the action.

Example export action:

```yaml
action: saviia.export_files
data:
  local_folder_path: thies/EXT
  cloud_provider_destination_path: /Volumes/catalog/schema/volume
```

THIES appends `<backup-root-name>/thies/AVG` and `<backup-root-name>/thies/EXT`
to the volume base path. For example, `/media/backup_local` produces
`/Volumes/catalog/schema/volume/backup_local/thies/AVG`.
In saviialib 1.21.0, `export_files` instead appends the resolved local path with
its leading slash removed: the example above with `/media/backup_local`
exports to `/Volumes/catalog/schema/volume/media/backup_local/thies/EXT`.
These layouts differ when the local backup root is absolute; choose destinations
accordingly to avoid duplicate cloud trees. This integration does not change the
library's path construction.

The automatic THIES status lookup in 1.21.0 inspects `/ARCH_AV1` and `/ARCH_EX1`.
Custom `ftp_server_folders_path` values apply to the post operation; the status
API does not accept a folder override. For custom FTP layouts, supply both flags
explicitly or adjust the library before relying on automatic planning.

## Activating Debugging

If you need to debug the integration flow and view detailed results, you can enable debug logging:

1. Enable debugging directly in the Integrations UI.
2. Alternatively, add the following to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.echo: debug
```


## Inspired by

* [Meteo Lt](https://github.com/Brunas/meteo_lt)
* [AI Agent HA](https://github.com/sbenodiz/ai_agent_ha)

## EchoLib

The integration of Echo is based on the echo-lib API library. All the services that Echo offers in Home Assistant are methods defined by this API. For more information about this API, visit https://github.com/pedrozavalat/echo-lib and consult the README file.
