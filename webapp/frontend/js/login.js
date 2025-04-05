document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    // Show the loader immediately after the form is submitted
    document.getElementById('loader').style.display = 'block';

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const backendUrl = "http://127.0.0.1:5000";

    try {
        const response = await fetch(`${backendUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();
        console.log(result)
        const message = document.getElementById('login-message');

        // Hide the loader after the response is received
        document.getElementById('loader').style.display = 'none';

        if (response.ok) {
            message.textContent = "Login successful!";
            message.classList.remove('text-danger');
            message.classList.add('text-success');
            localStorage.setItem('token', result.token);
            localStorage.setItem('admin', result.admin);

            window.location.href = 'index.html';
        } else {
            message.textContent = `Error: ${result.error}`;
            message.classList.remove('text-success');
            message.classList.add('text-danger');
        }
    } catch (error) {
        // Hide the loader if there's an error
        document.getElementById('loader').style.display = 'none';
        const message = document.getElementById('login-message');
        message.textContent = "An error occurred. Please try again.";
        message.classList.remove('text-success');
        message.classList.add('text-danger');
    }
});