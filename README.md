# oifs_xml_generation

Scripts and webpages for generating OpenIFS@home submission XML files.

## Webpage deployment

Run `./do_deploy.sh` on the server. It deploys:

- `oifs_xml_generation.php` and `oifs_xml_handler.php` to `/storage/www/cpdnboinc/html/user/project`.
- `include/oifs_xml_common.inc` to `/storage/www/cpdnboinc/html/project`.

All `.inc` files are routed to `html/project`.

The script uses the same comparison rules as `oifs_webpages`: identical files
are skipped, newer deployed files are retained, older deployed files are
replaced, and differing files with equal timestamps are retained with a message.
Missing files are copied. File arrays contain one filename per line.

The following site-managed files must already exist in `html/project`:

- `batch_site_config.inc`, supplying the host-specific `$project_path`,
  `$base_path`, `$ancil_base_path`, `$oifs_path`, and `$python_env` settings.
- `oifs_uploaders.inc`, supplying the `$allowed_uploaders` email array.

BOINC libraries remain in `html/inc`. The PHP pages change working directory to
`html/user` before loading site configuration and BOINC. Error reporting and
logging are controlled by the server configuration.

The form reads configurations from `$base_path/oifs_workgen/config_dir` and
ancillary selections from `$ancil_base_path/oifs_ancil_files`. These existing
backend directory conventions are retained; the directories and selected files
must be readable by PHP. The handler uses the configured Python executable to
run `$oifs_path/oifs_xml_generation/create_basic_xml_webform.py`. This deployment
script does not copy or execute Python files.

## Backend follow-up

The PHP and deployment refactor leaves Python code unchanged. Before treating
the complete generation flow as ready on aurai, review:

- `create_basic_xml_webform.py` selects a project directory for `caerus`,
  `hesperus`, and `pandia`, but not `aurai`.
- Its argument decoder strips backslashes and uses `literal_eval` on the JSON
  payload. Quotes, backslashes and multiline metadata can fail or be altered;
  the backend should decode the JSON supplied by PHP directly.
- `create_xml_funcs.py` hard-codes `/storage/www/cpdnboinc_dev/` and legacy
  configuration/namelist directories in `CreateFort4`.

The GitHub form defaults are retained. The server-only sensitivity experiment
fields are intentionally absent.
