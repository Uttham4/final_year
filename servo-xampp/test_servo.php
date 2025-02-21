<?php

$hostname = "localhost";
$username = "root";
$password = "";
$database = "sensor_db";

$conn = mysqli_connect($hostname, $username, $password, $database);

if (!$conn) {
	die("Connection failed: " . mysqli_connect_error());
}

echo "Database connection is OK<br>";

if (isset($_POST["PIN_OUT"]) && isset($_POST["DEGREE"])) {

	$t = $_POST["PIN_OUT"];
	$h = $_POST["DEGREE"];

	$sql = "INSERT INTO servo_table (PIN_OUT, DEGREE) VALUES (" . $t . ", " . $h . ")";

	if (mysqli_query($conn, $sql)) {
		echo "\nNew record created successfully";
	} else {
		echo "Error: " . $sql . "<br>" . mysqli_error($conn);
	}
}

?>