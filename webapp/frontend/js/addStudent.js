$('#add-student-form').submit(function (event) {
    event.preventDefault();
    showLoader();

    let formData = new FormData();
    formData.append('first_name', $('#first-name').val());
    formData.append('last_name', $('#last-name').val());
    formData.append('reg_num', $('#reg-num').val());
    formData.append('roll_num', $('#roll-num').val());
    formData.append('type', $('#type').val());
    formData.append('year', $('#year').val());
    formData.append('semester', $('#semester').val());
    formData.append('department', $('#department').val());
    formData.append('section', $('#section').val());
    formData.append('age', $('#age').val());

    // Add image file if selected
    let imageFile = $('#image')[0].files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    $.ajax({
        url: `${backendUrl}/students/add_student`,
        method: 'POST',
        processData: false,
        contentType: false,
        data: formData,
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

    element.style.display = "none";
    element.classList.add("hidden");

    if (admin === "1") {
        element.style.display = "";
        element.classList.remove("hidden");
    }
});
