$('#student-form').submit(function (event) {
    event.preventDefault();
    showLoader();
    const studentId = $('#student-id').val();
    const backendUrl = "https://4n87vpnms5.execute-api.us-east-2.amazonaws.com/prod";

    $.ajax({
        url: `${backendUrl}/student`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ id: studentId }),
        success: function (response) {
            console.log(response);
            hideLoader();
            if (response.message === "paid") {
                Swal.fire({
                    title: 'Student Paid Today',
                    text: "Student has already paid!",
                    icon: 'info',
                    confirmButtonText: 'OK',
                    backdrop: true,
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Make API call when OK is clicked
                        fetch(`${backendUrl}/mark-paid`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ id: studentId })
                        })
                            .then(response => response.json())
                            .then(data => {
                                console.log('API Response:', data);
                            })
                            .catch(error => {
                                console.error('Error:', error);
                            });
                    }
                });
                makeControlServoRequest(180);

                return;
            }

            if (response.message === "Already marked today") {
                Swal.fire({
                    title: 'Failed!',
                    text: "Student has already been marked for today!",
                    icon: 'warning',
                    confirmButtonText: 'OK',
                    backdrop: true,
                }).then((result) => {
                    if (result.isConfirmed) {
                        makeControlServoRequest(180);
                    }
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
                $('#student-image').attr('src', data.image ?? 'placeholder.png');
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
                text: 'Student not found!',
                icon: 'error',
                confirmButtonText: 'OK',
                backdrop: true,
            });
        }
    });
});


const makeControlServoRequest = (degree) => {
    const payload = {
        "servo_degree": degree
    };

    Swal.fire({
        title: degree === 180 ? 'Take the Plate' : 'Close the Door',
        text: degree === 180 ? 'Please take the plate!' : 'Please close the door!',
        icon: 'info',
        showConfirmButton: true,
    }).then(() => {
        // Make the control_servo POST request
        fetch('http://18.218.182.119:5000/control_servo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
            .then(response => {
                console.log(response);
                // Check if the response is a text response
                if (response.ok) {
                    return response.text();  // Parse as plain text
                } else {
                    throw new Error(`HTTP Error: ${response.status}`);
                }
            })
            .then(data => {
                // Log the response as plain text (it's not JSON)
                console.log('Servo control successful:', data);

                // After the first request (180 degrees), wait for 5 seconds, then do the second request (90 degrees)
                if (degree === 180) {
                    setTimeout(() => {
                        makeControlServoRequest(0);  // Call with 90 degrees after 5 seconds
                    }, 5000);  // 5-second delay between requests
                }
            })
            .catch(error => {
                console.error('Error controlling servo:', error);
                Swal.fire({
                    title: 'Failed!',
                    text: 'Error controlling the servo!',
                    icon: 'error',
                    confirmButtonText: 'OK',
                    backdrop: true,
                });
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
    fetch('http://18.218.182.119:5000/create_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            amount: 100,  // amount in paise
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
                amount: "100",
                currency: "INR",
                name: "Your Company",
                description: "Test Transaction",
                order_id: orderData.id,  // Set order ID received from server
                handler: function (response) {
                    console.log('Payment response:', response);

                    if (!response.razorpay_payment_id || !response.razorpay_order_id || !response.razorpay_signature) {
                        throw new Error('Missing required Razorpay parameters');
                    }

                    return fetch('http://18.218.182.119:5000/verify_payment', {
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
                                return fetch(`${backendUrl}/paid`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        student_id: studentId
                                    })
                                });
                            } else {
                                throw new Error(data.message || 'Payment verification failed');
                            }
                        })
                        .then(response => response.json())
                        .then(paidData => {
                            console.log('Paid route response:', paidData);
                            makeControlServoRequest(180);
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
    event.preventDefault();  // Prevent the button's default behavior (e.g., form submission)
    const apiUrl = 'https://4n87vpnms5.execute-api.us-east-2.amazonaws.com/prod';  // Replace with your actual API URL

    // Make the API call (using fetch in this example)
    fetch(`${apiUrl}/count`, {
        method: 'GET',  // Use GET method
        headers: {
            'Content-Type': 'application/json',  // Still including this, even though it's not strictly required for GET
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('API response:', data);

            if (data) {
                // Update UI with the count result (this can be customized as needed)
                Swal.fire({
                    title: 'Count Retrieved!',
                    text: `The count of students eating today is: ${data.count}`,
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
    const element1 = document.getElementById("count-btn");
    const admin = localStorage.getItem('admin');
    console.log("admin", admin);



    // Show for admin="1"
    if (admin === "1") {
        console.log("admin");
        element1?.classList.remove("hidden");
    }
});