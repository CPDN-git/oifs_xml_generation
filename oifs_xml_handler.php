<?php

//  OpenIFS XML generation handler
//  Original Sarah Sparrow
//  Mods: Glenn Carver & GPT6.

require_once(__DIR__ . '/../../project/oifs_xml_common.inc');

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    oifs_xml_error(405, 'Please submit the ensemble generation form.');
}

// Preserve metadata as data; escape only when displaying it in HTML.
$form_data = array();
$fields = array(
    'BatchProj', 'BatchName', 'BatchDesc', 'BatchOwner', 'BatchTechInfo',
    'model_class', 'model_config', 'start_dates', 'start_umid', 'n_analysis',
    'n_ens', 's_ens', 'upload_loc', 'exptid', 'fclen', 'fclen_units',
    'fullpos_namelist', 'SO4_file', 'Rad_file', 'GHG_file', 'climate_data_file'
);
foreach ($fields as $field) {
    if (!isset($_POST[$field]) || !is_string($_POST[$field]) || strpos($_POST[$field], "\0") !== false) {
        oifs_xml_error(400, 'Missing or invalid form field: ' . $field . '.');
    }
    $form_data[$field] = $_POST[$field];
    if (!in_array($field, array('BatchDesc', 'BatchTechInfo'), true) && trim($form_data[$field]) === '') {
        oifs_xml_error(400, 'Please complete the form field: ' . $field . '.');
    }
}
foreach (array('n_analysis', 'n_ens', 's_ens', 'fclen') as $field) {
    if (filter_var($form_data[$field], FILTER_VALIDATE_INT, array('options' => array('min_range' => 1))) === false) {
        oifs_xml_error(400, 'Please enter a positive whole number for ' . $field . '.');
    }
}
if (!preg_match('/\A[A-Za-z0-9]{4}\z/', $form_data['exptid']) ||
    !preg_match('/\A[A-Za-z0-9]{4}\z/', $form_data['start_umid'])) {
    oifs_xml_error(400, 'The experiment ID and starting UMID must each contain four letters or digits.');
}
// The backend incorporates the batch name into its output filename.
if (strpbrk($form_data['BatchName'], "/\\") !== false) {
    oifs_xml_error(400, 'The batch name must not contain directory separators.');
}
$dates = explode(',', $form_data['start_dates']);
foreach ($dates as &$date) {
    $date = trim($date);
    if (!preg_match('/\A[0-9]{10}\z/', $date) ||
        !checkdate((int)substr($date, 4, 2), (int)substr($date, 6, 2), (int)substr($date, 0, 4)) ||
        (int)substr($date, 8, 2) > 23) {
        oifs_xml_error(400, 'Start dates must be valid YYYYMMDDHH values separated by commas.');
    }
}
unset($date);
$form_data['start_dates'] = implode(',', $dates);
if (!in_array($form_data['fclen_units'], array('days', 'hours'), true) ||
    !in_array($form_data['upload_loc'], array('upload2', 'upload3', 'upload4',
        'upload5', 'upload6', 'upload7', 'upload8', 'upload9', 'upload10', 'upload11', 'upload12'), true)) {
    oifs_xml_error(400, 'Invalid forecast units or upload location.');
}

// Recheck every filename against the server's allowed selections, not just POST.
try {
    foreach (oifs_xml_directories() as $field => $directory) {
        if (!in_array($form_data[$field], oifs_xml_files($directory), true)) {
            oifs_xml_error(400, 'Please select an available file for ' . $field . '.');
        }
    }
} catch (Throwable $error) {
    error_log('Ensemble file selection: ' . $error->getMessage());
    oifs_xml_error(500, 'The model or ancillary file selections are unavailable.');
}

$payload = json_encode($form_data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if ($payload === false) {
    oifs_xml_error(400, 'The form contains text that could not be encoded. Please use UTF-8 text.');
}
$script = rtrim($oifs_repo_root, '/') . '/oifs_xml_generation/create_basic_xml_webform.py';
$availability_errors = array();
if (!is_file($python_env)) {
    $availability_errors[] = 'The configured Python executable was not found or is not a regular file: '
        . $python_env . '. Check $python_env in html/project/batch_site_config.inc and parent-directory permissions.';
} elseif (!is_executable($python_env)) {
    $availability_errors[] = 'The PHP worker cannot execute the configured Python interpreter: '
        . $python_env . '. Check executable permissions and directory access for the PHP worker account.';
}
if (!is_file($script)) {
    $availability_errors[] = 'The XML generator script was not found or is not a regular file: '
        . $script . '. Check $oifs_repo_root in html/project/batch_site_config.inc, the repository location, and parent-directory permissions.';
} elseif (!is_readable($script)) {
    $availability_errors[] = 'The PHP worker cannot read the XML generator script: '
        . $script . '. Check file permissions and directory access for the PHP worker account.';
}
if (!is_callable('exec')) {
    $availability_errors[] = 'PHP exec() is unavailable. Check disable_functions in the web worker PHP configuration (PHP-FPM or Apache), which may differ from command-line PHP.';
}
if ($availability_errors) {
    error_log('Ensemble generator unavailable: ' . implode(' ', $availability_errors));
    oifs_xml_error(500, implode(' ', $availability_errors));
}
// Quote each positional argument separately, using the configured Python environment.
// Scope the environment setting to this child process, not the PHP worker.
$command = 'OIFS_CONFIG_DIR=' . escapeshellarg($oifs_config_dir) . ' '
    . 'OIFS_REPO_ROOT=' . escapeshellarg($oifs_repo_root) . ' '
    . implode(' ', array_map('escapeshellarg', array($python_env, $script, $payload)));
$output = array();
$exit_status = 1;
try {
    exec($command . ' 2>&1', $output, $exit_status);
} catch (Throwable $error) {
    error_log('Ensemble generator could not start: ' . $error->getMessage());
    oifs_xml_error(500, 'Unable to start XML generation using ' . $python_env . ' and ' . $script
        . ': ' . $error->getMessage());
}
if ($exit_status !== 0) {
    http_response_code(500);
    error_log('Ensemble generation failed (exit status ' . $exit_status . ') using ' . $python_env
        . ' and ' . $script . ': ' . implode("\n", $output));
}
oifs_xml_page_start('OpenIFS@home Ensemble Generation Result');
echo '<p>' . ($exit_status === 0 ? 'XML generation completed.' :
    'XML generation failed (exit status ' . $exit_status . '). See the generator output below and contact the server administrator before retrying.') . '</p>';
if ($exit_status !== 0) {
    echo '<p>Python interpreter: ' . oifs_xml_escape($python_env)
        . '<br>Generator script: ' . oifs_xml_escape($script) . '</p>';
}
echo '<pre>' . oifs_xml_escape(implode("\n", $output)) . '</pre>';
echo '<p><a href="/project/oifs_xml_generation.php">Return to the ensemble form</a></p>';
oifs_xml_page_end();
