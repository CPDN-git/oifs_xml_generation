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
  `$oifs_config_dir`, `$ancil_base_path`, `$oifs_path`, and `$python_env` settings.
- `oifs_uploaders.inc`, supplying the `$allowed_uploaders` email array.

BOINC libraries remain in `html/inc`. The PHP pages change working directory to
`html/user` before loading site configuration and BOINC. Error reporting and
logging are controlled by the server configuration.

The form and handler read model configurations from `$oifs_config_dir`. On aurai,
set this in the server's `html/project/batch_site_config.inc`:

```php
$oifs_config_dir = '/home/boinc/cpdnboinc/oifs_workgen/configs/oifs';
```

Ancillary selections remain under `$ancil_base_path/oifs_ancil_files`. All selection
directories and files must be readable by PHP. The handler uses the configured
Python executable to run `$oifs_path/oifs_xml_generation/create_basic_xml_webform.py`. This deployment
script does not copy or execute Python files.

The handler passes `$oifs_config_dir` to Python as the child-process environment
variable `OIFS_CONFIG_DIR`. `CreateFort4` uses it to read the selected model XML,
so PHP and Python use the same directory. Deploy the updated `create_xml_funcs.py`
alongside the PHP changes. For command-line Python generation, export
`OIFS_CONFIG_DIR` explicitly; there is no fallback to the old `config_dir` path.

## Backend follow-up

Model configuration lookup is now shared between PHP and Python. Before treating
the complete generation flow as ready on aurai, the following separate Python
issues still need review:

- `create_basic_xml_webform.py` strips backslashes and uses `literal_eval` on the JSON
  payload. Quotes, backslashes and multiline metadata can fail or be altered;
  the backend should decode the JSON supplied by PHP directly.
- `create_xml_funcs.py` still hard-codes `/storage/www/cpdnboinc_dev/` for namelist
  template lookup in `CreateFort4`. Model XML lookup now uses `OIFS_CONFIG_DIR`.

The GitHub form defaults are retained. The server-only sensitivity experiment
fields are intentionally absent.
