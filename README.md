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

ECHO enables automated data extraction from THIES stations, local processing, cloud backup (SharePoint), and alert/task orchestration.

During setup, you will be prompted to provide the following parameters:

### FTP Configuration (Data Source)

1. **ftp_host**: FTP server IP address or hostname (e.g., `localhost`).
2. **ftp_port**: FTP server port (default: `21`).
3. **ftp_user**: FTP username.
4. **ftp_password**: FTP password.


### SharePoint Configuration (Cloud Backup)

5. **sharepoint_client_id**: Application Client ID.
6. **sharepoint_client_secret**: Application Client Secret.
7. **sharepoint_tenant_id**: Microsoft 365 Tenant ID.
8. **sharepoint_tenant_name**: Organization tenant name (e.g., `myorg`).
9. **sharepoint_site_name**: SharePoint site name.


### Data Paths & Backup

10. **thies_ftp_server_avg_path**: Path to average data files in the FTP server.
11. **thies_ftp_server_ext_path**: Path to extended/raw data files in the FTP server.
12. **sharepoint_avg_backup_folder_name**: Destination folder for average data in SharePoint.
13. **sharepoint_ext_backup_folder_name**: Destination folder for extended data in SharePoint.
14. **local_backup_source_path**: Local directory used as backup source.
15. **sharepoint_backup_base_url**: Base URL for SharePoint backups.


### Location Configuration 

16. **latitude**: Latitude of the station.
17. **longitude**: Longitude of the station.

Used for georeferencing, contextual analysis, and future location-based features.


###  Task & Alert System

ECHO integrates with external services to generate alerts and manage operational tasks.

18. **bot_token**: Discord bot token used for sending alerts via the task system (e.g., Xavia Live).
19. **task_channel_id**: Discord channel ID where alerts and tasks will be posted.


### Email Notifications 

20. **email_address**: Email address used to send alerts and task notifications.
21. **email_password**: Application password (e.g., Google App Password).

> ⚠️ Note: Email delivery is currently configured for Gmail SMTP.



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
