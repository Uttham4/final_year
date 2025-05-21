const saveStudentIdToLocalStorage = () => {
    const studentId = document.getElementById("student-id").value;
    localStorage.setItem("currentStudentID", studentId);
}



$('#student-form').submit(function (event) {
    event.preventDefault();
    showLoader();
    const studentId = $('#student-id').val();
    $.ajax({
        url: `${backendUrl}/students/student_details`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ id: studentId }),
        success: function (response) {
            console.log(response);
            hideLoader();
            try {
                
                if (response.message === "paid") {
                    console.log("paid");
                    console.log("Before Swal.fire");

                    // Show Swal alert
                    Swal.fire({
                        title: 'Student Paid Today',
                        text: `Student has already paid for menu: ${Object.keys(JSON.parse(response.menu)).join(", ")}`,
                        icon: 'info',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                    }).then((result) => {
                        console.log("Swal result:", result);

                        if (result.isConfirmed) {
                            console.log("User clicked OK, calling API...");

                            // Call API first
                            fetch(`${backendUrl}/payments/update_paid_status`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ id: studentId })
                            })
                                .then(response => response.json())
                                .then(data => {
                                    console.log('API Response:', data);

                                    // Now call makeControlServoRequest only after API response
                                    makeControlServoRequest();
                                })
                                .catch(error => console.error('Fetch Error:', error));
                        } else {
                            console.log("Swal closed without confirmation.");
                        }
                    });

                    console.log("After Swal.fire call in main thread");
                    return
                }

            } catch {
                (error => {
                    console.log("error", error);
                })
            }


            if (response.message === "Already marked today") {
                Swal.fire({
                    title: 'Failed!',
                    text: "Student has already been marked for today!",
                    icon: 'warning',
                    confirmButtonText: 'OK',
                    backdrop: true,
                }).then((result) => {
                    console.log("Student marked for today!");
                });

                return;
            }
            

            if (Array.isArray(response) && response.length > 0) {
                const data = response[0];

                $('#roll-num').text(data.roll_num ?? 'N/A');
                $('#reg-num').text(data.reg_num ?? 'N/A');
                $('#year').text(data.year ?? 'N/A');
                $('#semester').text(data.semester ?? 'N/A');
                $('#department').text(data.department ?? 'N/A');
                $('#section').text(data.section ?? 'N/A');
                $('#full-name').text(`${data.first_name ?? 'Unknown'} ${data.last_name ?? ''}`.trim());
                $('#age').text(data.age ?? 'N/A');
                $('#type').text(data.type ?? 'N/A');
                $('#address').text(data.address ?? 'N/A');
                $('#contact_number').text(data.contact_number ?? 'N/A');
                $('#email').text(data.email ?? 'N/A');
                $('#student-image').attr('src', '../backend/local_backend/' + data.image ?? '');
                $('#history').text(data.history ?? 'No history available.');

                $('#student-info').fadeIn();

                if ((data.type ?? '').toLowerCase() === "day scholar") {
                    if (data.paid) {
                        console.log("paid");
                    } else {

                        $('#payment-section').fadeIn();
                    }
                } else {
                    console.log("payment visible");
                    $('#payment-section').fadeOut();
                    makeControlServoRequest();
                }
            } else {
                // hideLoader();
                Swal.fire({
                    title: 'Failed!',
                    text: 'No student data found!',
                    icon: 'error',
                    confirmButtonText: 'OK',
                    backdrop: true,
                });

            }
        },
        error: function () {
            hideLoader();
            Swal.fire({
                title: 'Failed!',
                text: 'Error fetching student data!',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        }
    });
});

const makeControlServoRequest = () => {
    fetch("http://192.168.216.104/control_servo?status=open", {
        method: "GET"
    })
        .then(response => response.text()) // Get the plain text response
        .then(data => {
            console.log("Response from ESP32:", data);

            if (data == "No object detected within 5 seconds") {
                return Swal.fire({
                    title: 'Plate not detected!',
                    text: 'Please contact help, No plate detected!',
                    icon: 'warning',
                    showConfirmButton: true,
                }).then(() => {
                    console.log("Plate not detected");
                });
            }

            // Show success message
            Swal.fire({
                title: 'Take the Plate',
                text: 'Please take the plate!',
                icon: 'info',
                showConfirmButton: true,
            });

            // Proceed with student update
            return fetch(`${backendUrl}/students/update_today`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: localStorage.getItem('currentStudentID') })
            });

        })
        .then(response => {
            if (!response || !response.ok) {  // Ensure response is valid before using it
                throw new Error(`HTTP Error: ${response ? response.status : 'Unknown'}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Student update successful:', data);
            localStorage.removeItem("currentStudentID");
            localStorage.removeItem("totalCost");
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Failed!',
                text: error.message || 'Error occurred!',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        });
};


document.getElementById('pay-btn').onclick = function () {
    const studentId = $('#student-id').val();
    console.log("studentId", studentId);

    if (!studentId) {
        Swal.fire({
            title: 'Failed!',
            text: 'Please provide a student ID',
            icon: 'error',
            confirmButtonText: 'OK',
            backdrop: true,
        });
        return;
    }



    // Create order first
    fetch(`${backendUrl}/payments/create_order`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            amount: (localStorage.getItem("totalCost") > 0) ? localStorage.getItem("totalCost") : localStorage.getItem("currentMenuTotalCost"),
            currency: 'INR',
            student_id: studentId  // Include student ID in order creation
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(orderData => {
            if (!orderData.id) {
                throw new Error('Order ID not received from server');
            }

            const options = {
                key: "rzp_test_L3zRDHReH9Csk5",
                amount :(localStorage.getItem("totalCost") > 0) ? localStorage.getItem("totalCost") : localStorage.getItem("currentMenuTotalCost"),
                currency: "INR",
                name: "Rit",
                description: "Test Transaction",
                order_id: orderData.id,  // Set order ID received from server
                handler: function (response) {
                    console.log('Payment response:', response);

                    if (!response.razorpay_payment_id || !response.razorpay_order_id || !response.razorpay_signature) {
                        throw new Error('Missing required Razorpay parameters');
                    }

                    return fetch(`${backendUrl}/payments/verify_payment`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_signature: response.razorpay_signature,
                            student_id: studentId
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Verification response:', data);
                            if (data.status === 'success') {
                                Swal.fire({
                                    title: 'Success!',
                                    text: 'Payment successful!',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                    backdrop: true,
                                });

                                // Make a POST request to the /paid route
                                return fetch(`${backendUrl}/payments/payment_handler`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        student_id: studentId,
                                        menu: localStorage.getItem(`menu_${localStorage.getItem("currentStudentID")}`) || localStorage.getItem('currentMenu'),
                                        amount: (localStorage.getItem("totalCost") > 0) ? localStorage.getItem("totalCost") : localStorage.getItem("currentMenuTotalCost"),
                                    })
                                });
                            } else {
                                throw new Error(data.message || 'Payment verification failed');
                            }
                        })
                        .then(response => response.json())
                        .then(paidData => {
                            console.log('Paid route response:', paidData);
                            makeControlServoRequest();
                        });
                },
                prefill: {
                    name: "Test User",
                    email: "test@example.com",
                    contact: "9999999999"
                },
                theme: {
                    color: "#3399cc"
                }
            };

            const rzp1 = new Razorpay(options);
            rzp1.open();
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Failed!',
                text: error.message || 'An error occurred during payment processing',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        });
};



document.getElementById('count-btn').addEventListener('click', function (event) {
    event.preventDefault();

    fetch(`${backendUrl}/students/count_student`, {
        method: 'GET',  // Use GET method
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('API response:', data);

            if (data) {

                Swal.fire({
                    title: 'Count Retrieved!',
                    text: `The count of students eating today is: ${data.total_count} and count of hosteller : ${data.hosteller_count} and count of day scholer ${data.day_scholar_count}`,
                    icon: 'info',
                    confirmButtonText: 'OK',
                    backdrop: true,
                });
            } else {
                // Handle case where there's no count or error
                Swal.fire({
                    title: 'Failed!',
                    text: 'Failed to retrieve count',
                    icon: 'error',
                    confirmButtonText: 'OK',
                    backdrop: true,
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error!',
                text: 'An error occurred while calling the API',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        });
});

$(document).ready(function () {
    let studentID = localStorage.getItem("currentStudentID");
    let form = document.getElementById("student-form");

    if (form) { // Ensure the form exists
        document.getElementById("student-id").value = studentID;
        form.requestSubmit();
    } else {
        console.error("Form with ID 'submit-form' not found.");
    }

    const element1 = document.getElementById("count-btn");
    const admin = localStorage.getItem('admin');

    console.log("admin", admin);

    if (admin === "1") {
        console.log("admin");
        element1?.classList.remove("hidden");
    }
});

