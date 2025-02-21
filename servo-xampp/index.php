<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servo Control</title>
    <script>
        async function checkID() {
            const id = document.getElementById("idInput").value;

            if (!id) {
                alert("Please enter an ID.");
                return;
            }

            const response = await fetch("servo_control.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `id=${encodeURIComponent(id)}`,
            });
            console.log("id : ", id);

            const data = await response.json();
            alert(data.message);
        }
    </script>
</head>

<body>
    <h1>Servo Control Panel</h1>
    <label for="idInput">Enter or Scan ID:</label>
    <input type="text" id="idInput">
    <button onclick="checkID()">Submit</button>
</body>

</html>