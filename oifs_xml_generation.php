<?php

// OpenIFS batch XML generation
// Original Sarah Sparrow.
// Mods: Glenn Carver & GPT6.

require_once(__DIR__ . '/../../project/oifs_xml_common.inc');

// Check all external selection directories before sending the form HTML.
$file_lists = array();
try {
    foreach (oifs_xml_directories() as $field => $directory) {
        $file_lists[$field] = oifs_xml_files($directory);
        if (count($file_lists[$field]) === 0) {
            throw new RuntimeException('No selectable files in: ' . $directory);
        }
    }
} catch (Throwable $error) {
    error_log('Ensemble form: ' . $error->getMessage());
    oifs_xml_error(500, 'The model or ancillary file selections are unavailable. Please contact the server administrator.');
}

oifs_xml_page_start('OpenIFS@home Ensemble Generation');
echo '<p>' . oifs_xml_escape($user->name) . ' is logged in</p>';
echo '<p>Enter the following information to generate submission XML.</p>';
?>
    <p><b>Use comma separated lists to enter multiple values of fields (e.g. start date and batch owner) if required.</b></p>
    <form id="oifs_xml_form" name="oifs_xml_form"  action="/project/oifs_xml_handler.php" method="post" enctype="multipart/form-data">

    <div id="BatchInfo">
        <h3>Batch Information</h3>
    <table width="100%" border="0" style="border:none;">
    <tr class="nohover"><td style="width:22%">Batch Project:</td><td style="width:78%"><input type="text" name="BatchProj" required value="OpenIFSATHOME"></td></tr>
    <tr class="nohover"><td>Batch Name:</td><td><textarea id="BatchName" name="BatchName" required rows="1" cols="80"></textarea></td></tr>
    <tr class="nohover"><td>Batch Description:</td><td><textarea id="BatchDesc" name="BatchDesc" rows="3" cols="80"></textarea></td></tr>
    <tr class="nohover"><td>Batch Owner(s). Enter as Name (e-mail):</td><td><textarea id="BatchOwner" name="BatchOwner" required rows="1" cols="80"></textarea></td></tr>
    <tr class="nohover"><td>Batch Technical Information:</td><td><textarea id="BatchTechInfo" name="BatchTechInfo" rows="3" cols="80"></textarea></td></tr>
    </table>
    </div>

    <div id="config">
    <h3>Model Configuration Details</h3>
    <table width="100%" border="0" style="border:none;">
    <tr class="nohover"><td style="width:22%">Model Class:</td><td style="width:78%"><input type="text" name="model_class" required value="openifs"></td></tr>
    <tr class="nohover"><td>Model Configuration File:</td><td><select id="model_config" name="model_config" required class="dropdown">
    <?php oifs_xml_options($file_lists['model_config'], '43r3_t159l91.xml'); ?>
    </select></td></tr>
    </table>
    </div>

    <div id="setup">
        <h3>Ensemble Setup</h3>
    <table width="100%" border="0" style="border:none;">
    <tr class="nohover"><td style="width:22%">Start date(s) as YYYYMMDDHH:</td><td style="width:78%"><textarea id="start_dates" name="start_dates" required rows="1" cols="80"></textarea></td></tr>
    <tr class="nohover"><td>Starting UMID:</td><td><input type="text" name="start_umid" required value="a000"></td></tr>
    <tr class="nohover"><td>Number of analyses (per start date):</td><td><input type="number" min="1" step="1" name="n_analysis" required></td></tr>
    <tr class="nohover"><td>Number of ensemble members (per analysis):</td><td><input type="number" min="1" step="1" name="n_ens" required></td></tr>
    <tr class="nohover"><td>Starting ensemble member number:</td><td><input type="number" min="1" step="1" name="s_ens" required value="1"></td></tr>
    <tr class="nohover"><td>Upload Location:</td><td><select id="upload_loc" name="upload_loc" required class="dropdown">
                <option value="">Select...</option>
                <option value="alpha">Alpha</option>
                <option value="dev">Dev</option>
                <option value="upload2">Upload2</option>
                <option value="upload3">Upload3</option>
                <option value="upload4">Upload4</option>
                <option value="upload5">Upload5</option>
                <option value="upload6">Upload6</option>
                <option value="upload7">Upload7</option>
                <option value="upload8">Upload8</option>
                <option value="upload9">Upload9</option>
                <option value="upload10">Upload10</option>
                <option value="upload11">Upload11</option>
                <option value="upload12">Upload12</option>
                </select></td></tr>
    </table>
        </div>

    <div id="ens_config">
        <h3>Ensemble Configuration</h3>
    <table width="100%" border="0" style="border:none;">
    <tr class="nohover"><td style="width:22%">ECMWF Experiment ID:</td><td style="width:78%"><input type="text" name="exptid" required></td></tr>
        <tr class="nohover"><td>Forecast Length:</td><td><input type="number" min="1" step="1" name="fclen" required>
    <select id="fclen_units" name="fclen_units" required class="dropdown">
                <option value="days">Days</option>
                <option value="hours">Hours</option>
                </select></td></tr>
        <tr class="nohover"><td>FullPos Namelist File:</td><td><select id="fullpos_namelist" name="fullpos_namelist" required class="dropdown" style="width: 25%;">
        <?php oifs_xml_options($file_lists['fullpos_namelist'], ''); ?>
        </select></td></tr>
    </table>
        </div>

    <div id="ifsdata">
    <h3>IFS data</h3>
    <table width="100%" border="0" style="border:none;">
        <tr class="nohover"><td style="width:22%">SO4 File:</td><td style="width:78%"><select id="SO4_file" name="SO4_file" required class="dropdown" style="width: 25%;">
        <?php oifs_xml_options($file_lists['SO4_file'], 'SO4_159l_2.zip'); ?>
        </select></td></tr>
        <tr class="nohover"><td>Other radiation File:</td><td style="width:78%"><select id="Rad_file" name="Rad_file" required class="dropdown" style="width: 25%;">
        <?php oifs_xml_options($file_lists['Rad_file'], 'other_radiation_159l_2.zip'); ?>
        </select></td></tr>
        <tr class="nohover"><td>GHG File:</td><td style="width:78%"><select id="GHG_file" name="GHG_file" required class="dropdown" style="width: 25%;">
        <?php oifs_xml_options($file_lists['GHG_file'], 'GHG_159l_2.zip'); ?>
        </select></td></tr>
    </table>
        </div>

    <div id="climate_data">
        <h3>Climate Data</h3>
        <table width="100%" border="0" style="border:none;">
    <tr class="nohover"><td style="width:22%">Climate Data File:</td><td style="width:78%"><select id="climate_data_file" name="climate_data_file" required class="dropdown" style="width: 25%;">
        <?php oifs_xml_options($file_lists['climate_data_file'], 'climate.v015_159l_2.zip'); ?>
        </select></td></tr>
        </table>
    </div>
    <br>
    <br>
    <input class="button" type="submit" name="submit" value="Create" />
</form>
<?php oifs_xml_page_end(); ?>
