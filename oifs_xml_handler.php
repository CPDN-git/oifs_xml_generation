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

require_once("../inc/util.inc");
require_once("../inc/user.inc");
require_once("../inc/boinc_db.inc");
require_once("../inc/oifs_uploaders.inc");
require_once("../inc/batch_site_config.inc");

//page_head("OpenIFS Ensemble Creation");

echo <<<EOH
<html>
<head>
<title>OpenIFS@home Ancil upload form</title>
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

$user = get_logged_in_user();

if (in_array($user->email_addr,$allowed_uploaders)){
        echo "$user->name is logged in<br>";
        echo 'Form was submitted, here are the form values: <pre>';
	foreach ($_POST as $key => $value){
		$_POST[$key] = htmlspecialchars($value,ENT_QUOTES, "UTF-8");
        }
	print_r($_POST);
        echo "</pre>";
	$arr= json_encode($_POST);
	$escaped_arr=escapeshellarg($arr);
	$r = escapeshellcmd( $python_env.' '.$oifs_path.'oifs_xml_generation/create_basic_xml_webform.py '.$escaped_arr); 
        $output = shell_exec($r.' 2>&1');
	echo "<pre>$output</pre>";
}
else {
        die("You are not allowed to visit this page");
        } ?>

