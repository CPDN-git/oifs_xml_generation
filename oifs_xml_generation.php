<?php
// This file is part of BOINC.
// http://boinc.berkeley.edu
// Copyright (C) 2008 University of California
//
// BOINC is free software; you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License
// as published by the Free Software Foundation,
// either version 3 of the License, or (at your option) any later version.
//
// BOINC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with BOINC.  If not, see <http://www.gnu.org/licenses/>.

//require_once("../inc/util.inc");
//require_once("../inc/user.inc");
//require_once("../inc/oifs_uploaders.inc");
//require_once("../inc/batch_site_config.inc");

//page_head("OpenIFS Ancil upload form");

echo <<<EOH
<html>
<head>
<title>OpenIFS@home Ensemble Generation</title>
<META NAME="ROBOTS" CONTENT="NOINDEV, NOFOLLOW">
<script type="text/javascript" src="jquery/jquery-latest.js"></script>
<script type="text/javascript" src="jquery/jquery.tablesorter.js"></script>
<script type="text/javascript">
                        $(document).ready(function() {
                                $("#myTable").tablesorter();
                        });
                </script>
<style type="text/css">
                        #sortedtable thead th {
                                color: #00f;
                                font-weight: bold;
                                text-decoration: underline;
                        }
                </style>
<link rel="stylesheet" href="cpdn.css">
</head>
<body>
EOH;

echo '<div class="wrap" style="width:100%">';
echo '<div style="width:100%">';
echo '<img src="img/OIFS_Home_logo.png" alt="OpenIFS@home" style="width:200px">';
echo '<img src="img/CPDN_abbrv_logo.png" alt="CPDN" style="width:250px; float:right;">';
echo '</div>';
echo '<div style="clear: both;"></div>';
echo '</div>';
echo '<hr>';
echo '<h2>To generate a submission xml enter the following information about your experiment file(s).</h2>';

//$user = get_logged_in_user();
if (1){//in_array($user->email_addr,$allowed_uploaders)){
	//echo "<p>$user->name is logged in</p>";
	?>
	<p><b>Use comma separated lists to enter mutliple values of fields (e.g. start date and batch owner) if required.</b></p>
	<form id="oifs_xml_form" name="oifs_xml_form"  action="oifs_xml_handler.php" method="post" enctype="multipart/form-data">
	
	<div id="BatchInfo" name="BatchInfo">
        <h3>Batch Information</h3>
	<table width="100%" border="0" style="border:none;">
	<tr class="nohover"><td Width=22%>Batch Project:</td><td width=78%><input type="text" name="BatchProj" value="OpenIFSATHOME"></td></tr>
	<tr class="nohover"><td>Batch Name:</td><td><textarea id="BatchName" name="BatchName" rows="1" cols="80"></textarea></td></tr>
	<tr class="nohover"><td>Batch Description:</td><td><textarea id="BatchDesc" name="BatchDesc" rows="3" cols="80"></textarea></td></tr>
	<tr class="nohover"><td>Batch Owner(s). Enter as Name (e-mail):</td><td><textarea id="BatchOwner" name="BatchOwner" rows="1" cols="80"></textarea></td></tr>
	<tr class="nohover"><td>Batch Technical Information:</td><td><textarea id="BatchTechInfo" name="BatchTechInfo" rows="3" cols="80"></textarea></td></tr>
	</table>
	</div>
	
	<div id="config" name="config">
	<h3>Model Configuration Details</h3>
	<table width="100%" border="0" style="border:none;">
	<tr class="nohover"><td width=22%>Model Class:</td><td width=78%><input type="text" name="model_class" value="openifs"></td></tr>
	<tr class="nohover"><td>Model Configuration File:</td><td><select id="model_config" name="model_config" class="dropdown">
	<?php 
	$files = array_slice(scandir($base_path.'/oifs_workgen/config_dir'), 2);	
	foreach ($files as $file) {
	if ($file=="40r1_T159.xml"){
	echo "<option selected=\"selected\" value=\"" .$file."\">" . $file. "</option>";
	} else {
    	echo "<option value=\"" .$file."\">" . $file. "</option>";
	}
	}
	?>
	</select></td></tr>
	</table>
	</div>

	<div id="setup" name="setup">
        <h3>Ensemble Setup</h3>
	<table width="100%" border="0" style="border:none;">
	<tr class="nohover"><td width=22%>Start date(s) as YYYYMMDDHH:</td><td width=78%><textarea id="start_dates" name="start_dates" rows="1" cols="80"></textarea></td></tr>
	<tr class="nohover"><td>Starting UMID:</td><td><input type="text" name="start_umid" value="a000"></td></tr>
	<tr class="nohover"><td>Number of analyses (per start date):</td><td><input type="text" name="n_analysis"></td></tr>
	<tr class="nohover"><td>Number of ensemble members (per analysis):</td><td><input type="text" name="n_ens"></td></tr>
	<tr class="nohover"><td>Starting ensemble member number:</td><td><input type="text" name="s_ens" value="1"></td></tr>
	<tr class="nohover"><td>Upload Location:</td><td><select id="upload_loc" name="upload_loc" class="dropdown">
                <option value="0">Select...</option>
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

	<div id="ens_config" name="ens_config">
        <h3>Ensemble Configuration</h3>
	<table width="100%" border="0" style="border:none;">
	<tr class="nohover"><td Width=22%>ECMWF Experiment ID:</td><td width=78%><input type="text" name="exptid"></td></tr>
        <tr class="nohover"><td>Forecast Length:</td><td><input type="text" name="fclen">
	<select id="fclen_units" name="fclen_units" class="dropdown">
                <option value="days">Days</option>
                <option value="hours">Hours</option>
                </select></td></tr>
        <tr class="nohover"><td>FullPos Namelist File:</td><td><select id="fullpos_namelist" name="fullpos_namelist" class="dropdown" style="width: 25%;">
        <option value="0">Select</option>
        <?php
        $files = array_slice(scandir($ancil_base_path.'/oifs_ancil_files/fullpos_namelist'), 2);
        foreach ($files as $file)
        {
        echo "<option value=\"" .$file."\">" . $file . "</option>";
        }
        ?>
        </select></td></tr>
	</table>
        </div>

	<div id="ifsdata" name="ifsdata">
	<h3>IFS data</h3>
	<table width="100%" border="0" style="border:none;">
        <tr class="nohover"><td Width=22%>SO4 File:</td><td width=78%><select id="SO4_file" name="SO4_file" class="dropdown" style="width: 25%;">
        <?php
        $files = array_slice(scandir($ancil_base_path.'/oifs_ancil_files/ifsdata/SO4_files'), 2);
        foreach ($files as $file) {
        if ($file=="SO4.zip"){
        echo "<option selected=\"selected\" value=\"" .$file."\">" . $file. "</option>";
        } else {
        echo "<option value=\"" .$file."\">" . $file. "</option>";
        }
        }
        ?>
        </select></td></tr>
        <tr class="nohover"><td>Other radiation File:</td><td width=78%><select id="Rad_file" name="Rad_file" class="dropdown" style="width: 25%;">
        <?php
        $files = array_slice(scandir($ancil_base_path.'/oifs_ancil_files/ifsdata/other_radiation_files'), 2);
        foreach ($files as $file) {
        if ($file=="other_radiation.zip"){
        echo "<option selected=\"selected\" value=\"" .$file."\">" . $file. "</option>";
        } else {
        echo "<option value=\"" .$file."\">" . $file. "</option>";
        }
        }
        ?>
        <tr class="nohover"><td>GHG File:</td><td width=78%><select id="GHG_file" name="GHG_file" class="dropdown" style="width: 25%;">
        <?php
        $files = array_slice(scandir($ancil_base_path.'/oifs_ancil_files/ifsdata/GHG_files'), 2);
        foreach ($files as $file) {
        if ($file=="GHG.zip"){
        echo "<option selected=\"selected\" value=\"" .$file."\">" . $file. "</option>";
        } else {
        echo "<option value=\"" .$file."\">" . $file. "</option>";
        }
        }
        ?>
	</table>
        </div>

	<div id="climate_data" name="climate_data">
        <h3>Climate Data</h3>
        <table width="100%" border="0" style="border:none;">
	<tr class="nohover"><td Width=22%>Climate Data File:</td><td width=78%><select id="climate_data_file" name="climate_data_file" class="dropdown" style="width: 25%;">
        <?php
        $files = array_slice(scandir($ancil_base_path.'/oifs_ancil_files/climate_data'), 2);
        foreach ($files as $file) {
        if ($file=="climate_data.zip"){
        echo "<option selected=\"selected\" value=\"" .$file."\">" . $file. "</option>";
        } else {
        echo "<option value=\"" .$file."\">" . $file. "</option>";
        }
        }
        ?>
        </table>
	</div>

        <div id="sensitivity_exp" name="sensitivity_exp">
        <h3>Sensitivity Experiment</h3>
        <table width="100%" border="0" style="border:none;">
        <tr class="nohover"><td Width=22%>Number samples:</td><td width=78%><input type="text" name="persamp">
	<tr class="nohover"><td Width=22%>Perturbed parameters:</td><td width=78%><input type="text" name="perpara">
        <tr class="nohover"><td Width=22%>Corresponding Boundaries:</td><td width=78%><input type="text" name="perboun">
        </table>
	</div>

	<br>
	<br>
	<input class="button" type="submit" name="submit" value="Create" />	
<form>

<?php 
}
else {
	echo "You are not allowed to visit this page";
	}

?>
