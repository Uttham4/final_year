$('#add-user-form').submit(function (event) {
    event.preventDefault();
    showLoader();

    const userData = {
        username: $('#username').val(),
        password: $('#password').val(),
        admin: $('#admin').val() === 'true'
    };


    $.ajax({
        url: `${backendUrl}/users/add_user`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(userData),
        success: function () {
            hideLoader();
            Swal.fire({
                title: 'Success!',
                text: 'User added successfully!',
                icon: 'success',
                confirmButtonText: 'OK',
                backdrop: true,
            });
            $('#add-user-form')[0].reset();
        },
        error: function () {
            hideLoader();
            Swal.fire({
                title: 'Failed!',
                text: 'Failed to add user. Please try again!',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        }
    });
});