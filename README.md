# oifs_xml_generation

Scripts and webpages for generating OpenIFS@home submission XML files.

## Webpage deployment

Run `./do_deploy.sh` on the server. It deploys:

- `oifs_xml_generation.php` and `oifs_xml_handler.php` to `/storage/www/cpdnboinc/html/user/project`.
- `include/oifs_xml_common.inc` to `/storage/www/cpdnboinc/html/project`.

All `.inc` files are routed to `html/project`.

The script uses the same comparison rules as `cpdn_webpages`: identical files
are skipped, newer deployed files are retained, older deployed files are
replaced, and differing files with equal timestamps are retained with a message.
Missing files are copied. Destination symbolic links, including broken links,
stop deployment without changing the link or its target. Comparison errors retain
the underlying diagnostic and stop deployment; earlier files may already have been
deployed. File arrays contain one filename per line.

The following shared files, owned and deployed by `cpdn_webpages`, must already
exist in `html/project`:

- `cpdn_web_bootstrap.inc`, providing shared startup for each PHP page.
- `batch_site_config.inc`, supplying the host-specific `$project_path`,
  `$oifs_config_dir`, `$ancil_base_path`, `$oifs_repo_root`, and `$python_env` settings.
- `allowed_uploaders.inc`, supplying the `$allowed_uploaders` email array.

BOINC libraries remain in `html/inc`. Each PHP page loads the bootstrap at page
scope to change working directory to `html/user`, load site configuration and
define include paths. It then loads `oifs_xml_common.inc` through `PROJECT_INC`;
that helper retains XML-specific configuration checks and uploader authorization.
The bootstrap is deployed by `cpdn_webpages`, not copied by this repository. Error
reporting and logging are controlled by the server configuration.

The form and handler read model configurations from `$oifs_config_dir`. On aurai,
set this in the server's `html/project/batch_site_config.inc`:

```php
$oifs_repo_root = '/home/boinc/cpdnboinc/';
$oifs_config_dir = $oifs_repo_root . 'oifs_workgen/configs/oifs';
```

Ancillary selections remain under `$ancil_base_path/oifs_ancil_files`. All selection
directories and files must be readable by PHP. The handler uses the configured
Python executable to run `$oifs_repo_root/oifs_xml_generation/create_basic_xml_webform.py`. This deployment
script does not copy or execute Python files.

The handler passes two child-process environment variables to Python:

- `OIFS_CONFIG_DIR` from `$oifs_config_dir`, used by `CreateFort4` to read model XML.
- `OIFS_REPO_ROOT` from `$oifs_repo_root`, used by both generators to locate
  `oifs_workgen/xml_staging`.

Deploy the updated Python scripts and `create_xml_funcs.py` alongside the PHP
changes. For command-line generation, export both variables explicitly; there is
no fallback to hostname-based paths or the old `config_dir` directory.

On aurai, submission XML is written to
`/home/boinc/cpdnboinc/oifs_workgen/xml_staging`. Both generators print
`XML file written: <full path>` only after successfully writing and closing the
file. This occurs before the `fort.4` preview is generated; a later preview failure
does not remove the XML already written.

Namelist templates are read from `namelists/oifs` in the same `oifs_workgen`
repository as `configs/oifs`. For the aurai configuration above, this resolves to
`/home/boinc/cpdnboinc/oifs_workgen/namelists/oifs`; template filenames come from
the selected model XML. No separate template-directory setting is required.

## Backend follow-up

Model configuration lookup is now shared between PHP and Python. Before treating
the complete generation flow as ready on aurai, the following separate Python
issues still need review:

- `create_basic_xml_webform.py` strips backslashes and uses `literal_eval` on the JSON
  payload. Quotes, backslashes and multiline metadata can fail or be altered;
  the backend should decode the JSON supplied by PHP directly.

The GitHub form defaults are retained. The server-only sensitivity experiment
fields are intentionally absent.
