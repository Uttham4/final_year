$('#add-student-form').submit(function (event) {
    event.preventDefault();
    showLoader()
    const studentData = {
        first_name: $('#first-name').val(),
        last_name: $('#last-name').val(),
        reg_num: $('#reg-num').val(),
        roll_num: $('#roll-num').val(),
        type: $('#type').val()
    };
    const backendUrl = "https://4n87vpnms5.execute-api.us-east-2.amazonaws.com/prod";


    $.ajax({
        url: `${backendUrl}/student/add`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(studentData),
        success: function () {
            hideLoader();
            Swal.fire({
                title: 'Success!',
                text: 'Student added successfully!',
                icon: 'success',
                confirmButtonText: 'OK',
                backdrop: true,
            });
            $('#add-student-form')[0].reset();
        },
        error: function () {
            hideLoader();
            Swal.fire({
                title: 'Failed!',
                text: 'Failed to add student. Please try again!',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        }
    });
});



$(document).ready(function () {
    const element = document.getElementById("add-user");
    const admin = localStorage.getItem('admin');

    // Since admin is "0", let's ensure it stays hidden
    element.style.display = "none";
    element.classList.add("hidden");

    // Only show for admin="1"
    if (admin === "1") {
        element.style.display = "";
        element.classList.remove("hidden");
    }
});