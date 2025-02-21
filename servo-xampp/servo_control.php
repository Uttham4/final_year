<?php
// Database configuration
$host = "localhost";
$db = "sensor_db";
$user = "root";
$pass = "";

// Create connection
$conn = new mysqli($host, $user, $pass, $db);

// Check connection
if ($conn->connect_error) {
	die("Connection failed: " . $conn->connect_error);
}

// Debug incoming data
$debugLog = "=== DEBUG START ===\n";
$debugLog .= "POST Data:\n" . print_r($_POST, true);
$debugLog .= "Raw Input: " . file_get_contents('php://input') . "\n";
$debugLog .= "Server Data:\n" . print_r($_SERVER, true);
file_put_contents("debug_log.txt", $debugLog, FILE_APPEND);

// Check if ID is provided
if (!isset($_POST['id'])) {
	parse_str(file_get_contents('php://input'), $_POST); // Fallback to raw POST body
}

if (!isset($_POST['id'])) {
	echo json_encode(["status" => "error", "message" => "ID not provided"]);
	exit();
}

$id = $_POST['id'];

// Debug ID value
file_put_contents("debug_log.txt", "ID Received: " . $id . "\n", FILE_APPEND);

// Query to verify ID
$sql = "SELECT * FROM users WHERE id_card = '$id'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
	// Debug database match
	file_put_contents("debug_log.txt", "Database Match Found\n", FILE_APPEND);

	// Output all matching rows for debugging
	while ($row = $result->fetch_assoc()) {
		file_put_contents("debug_log.txt", "Row: " . json_encode($row) . "\n", FILE_APPEND);
	}

	// Send command to ESP32
	$espUrl = "http://192.168.234.104/control_servo?status=open";
	$response = file_get_contents($espUrl);

	if ($response === false) {
		file_put_contents("debug_log.txt", "ESP32 Communication Failed\n", FILE_APPEND);
		echo json_encode(["status" => "error", "message" => "Failed to communicate with ESP32"]);
	} else {
		file_put_contents("debug_log.txt", "ESP32 Response: " . $response . "\n", FILE_APPEND);
		echo json_encode(["status" => "success", "message" => "Servo controlled", "esp_response" => $response]);
	}
} else {
	// Debug no match found
	file_put_contents("debug_log.txt", "No Matching Records Found\n", FILE_APPEND);
	echo json_encode(["status" => "error", "message" => "ID Not Found"]);
}

$conn->close();
?>