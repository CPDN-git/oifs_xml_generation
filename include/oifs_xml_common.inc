<?php

// The calling page loads cpdn_web_bootstrap.inc before this XML-specific helper.
foreach (array('project_path', 'oifs_config_dir', 'ancil_base_path', 'oifs_repo_root', 'python_env') as $setting) {
    if (!isset($$setting) || !is_string($$setting) || $$setting === '') {
        error_log('Missing XML generation configuration setting: ' . $setting);
        http_response_code(500);
        exit('Batch site configuration is incomplete for this host.');
    }
}

require_once(BOINC_INC . 'util.inc');
require_once(BOINC_INC . 'user.inc');
require_once(PROJECT_INC . 'allowed_uploaders.inc');

// Return to the complete /project URL after login, including for handler requests.
$user = get_logged_in_user(false);
if (!$user) {
    header('Location: /login_form.php?next_url=' . rawurlencode('project/oifs_xml_generation.php'));
    exit;
}
if (!isset($allowed_uploaders) || !is_array($allowed_uploaders)) {
    http_response_code(500);
    exit('Uploader access configuration is unavailable.');
}
if (!in_array($user->email_addr, $allowed_uploaders, true)) {
    http_response_code(403);
    exit('You are not allowed to visit this page.');
}

function oifs_xml_escape($value)
{
    return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function oifs_xml_page_start($title)
{
    header('Content-Type: text/html; charset=utf-8');
    $title_html = oifs_xml_escape($title);
    echo <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<title>$title_html</title>
<link rel="stylesheet" href="/cpdn.css">
</head>
<body>
<div class="wrap" style="width:100%">
    <img src="/img/OIFS_Home_logo.png" alt="OpenIFS@home" style="width:200px">
    <img src="/img/CPDN_abbrv_logo.png" alt="CPDN" style="width:250px; float:right;">
    <div style="clear:both;"></div>
</div>
<hr>
<h1>$title_html</h1>
HTML;
}

function oifs_xml_page_end()
{
    echo '</body></html>';
}

function oifs_xml_error($status, $message)
{
    http_response_code($status);
    oifs_xml_page_start('OpenIFS ensemble generation error');
    echo '<p>' . oifs_xml_escape($message) . '</p>';
    echo '<p><a href="/project/oifs_xml_generation.php">Return to the ensemble form</a></p>';
    oifs_xml_page_end();
    exit;
}

function oifs_xml_directories()
{
    global $oifs_config_dir, $ancil_base_path;
    $ancils = rtrim($ancil_base_path, '/') . '/oifs_ancil_files/';
    return array(
        'model_config' => rtrim($oifs_config_dir, '/'),
        'fullpos_namelist' => $ancils . 'fullpos_namelist',
        'SO4_file' => $ancils . 'ifsdata/SO4_files',
        'Rad_file' => $ancils . 'ifsdata/other_radiation_files',
        'GHG_file' => $ancils . 'ifsdata/GHG_files',
        'climate_data_file' => $ancils . 'climate_data'
    );
}

function oifs_xml_files($directory)
{
    if (!is_dir($directory) || !is_readable($directory)) {
        throw new RuntimeException('Selection directory unavailable: ' . $directory);
    }
    $entries = scandir($directory);
    if ($entries === false) {
        throw new RuntimeException('Unable to list selection directory: ' . $directory);
    }
    $files = array();
    foreach ($entries as $file) {
        if ($file !== '.' && $file !== '..' &&
            is_file($directory . '/' . $file) && is_readable($directory . '/' . $file)) {
            $files[] = $file;
        }
    }
    return $files;
}

function oifs_xml_options($files, $default = '')
{
    echo '<option value="">Select...</option>';
    foreach ($files as $file) {
        $selected = $file === $default ? ' selected' : '';
        $file_html = oifs_xml_escape($file);
        echo '<option value="' . $file_html . '"' . $selected . '>' . $file_html . '</option>';
    }
}
