# Changelog

## 8.0.0

- Require saviialib 1.21.0 and use Databricks for THIES and file exports.
- Replace SharePoint setup fields and service destination arguments with
  Databricks workspace/token/volume settings.
- Let existing entries collect Databricks settings while retaining local and
  notification configuration.
- Read automatic THIES flags from metadata.data, preserve explicit false flags,
  and stop when status lookup fails.
- Remove the unsupported post_thies_data local_backup_source_path override.

See README.md for automation changes and the library's destination path layouts.
