const logout = () => {
    Swal.fire({
        title: 'Attention!',
        text: 'You have been logged out!',
        icon: 'info',
        confirmButtonText: 'OK',
        backdrop: true,
    });

    setTimeout(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('admin');
        window.location.href = 'login.html';
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    try {
        // Decode the token
        const decoded = jwt_decode(token);
        console.log('Decoded Token:', decoded);

        // Check for expiration
        const now = Math.floor(Date.now() / 1000);
        if (decoded.exp < now) {
            console.error('Token has expired');
            window.location.href = 'login.html';
            return;
        }

        // Token is valid, proceed with your logic
        console.log('Token is valid');
    } catch (error) {
        console.error('Invalid token:', error);
        window.location.href = 'login.html';
    }
});

var backendUrl = "https://4n87vpnms5.execute-api.us-east-2.amazonaws.com/prod";

const addStudent = () => {
    window.location.href = 'addStudent.html';
}
const home = () => {
    window.location.href = 'index.html';
}

const addUser = () => {
    window.location.href = 'addUser.html';
}

const inventory = () => {
    window.location.href = 'inventory.html';
}

$(document).ready(function () {
    const element1 = document.getElementById("add-user");
    const element2 = document.getElementById("inventory");
    const element3 = document.getElementById("add-student");
    const admin = localStorage.getItem('admin');
    console.log("admin", admin);

    // Hide elements
    element1?.style.setProperty('display', 'none');
    element1?.classList.add("hidden");
    element3?.style.setProperty('display', 'none');
    element3?.classList.add("hidden");
    element2?.style.setProperty('display', 'none');
    element2?.classList.add("hidden");

    // Show for admin="1"
    if (admin === "1") {
        console.log("admin");
        element1?.style.removeProperty('display');
        element1?.classList.remove("hidden");
        element2?.style.removeProperty('display');
        element2?.classList.remove("hidden");
        element3?.style.removeProperty('display');
        element3?.classList.remove("hidden");
    }
});
function showLoader() { document.getElementById('loader').classList.remove('hidden'); }
function hideLoader() { document.getElementById('loader').classList.add('hidden'); }