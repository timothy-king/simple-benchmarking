<?php
ini_set('display_errors', 'On');
error_reporting(E_ALL);

$server=trim(file_get_contents("../config/host"));
$user=trim(file_get_contents("../config/user"));
$password=trim(file_get_contents("../config/password"));
$database=trim(file_get_contents("../config/database"));
?>
