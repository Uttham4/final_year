CREATE TABLE esp32_data.servo_data (  
    `S.NO` INT AUTO_INCREMENT PRIMARY KEY,
    PIN_OUT INT NOT NULL,
    DEGREE INT NOT NULL,
    POSITION VARCHAR(255) DEFAULT NULL,
    CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
    MODIFIED_AT DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    DELETED_AT DATETIME DEFAULT NULL
);


CREATE TABLE student_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_num VARCHAR(20) NOT NULL, -- Roll number of the student
    reg_num VARCHAR(20) NOT NULL, -- Registration number of the student
    year INT, -- Current academic year
    semester INT, -- Current semester
    department VARCHAR(50), -- Department (e.g., CSE, ECE)
    section CHAR(1), -- Section (e.g., 'A', 'B')
    first_name VARCHAR(50) NOT NULL, -- Student's first name
    last_name VARCHAR(50) NOT NULL, -- Student's last name
    age INT, -- Student's age
    type ENUM('Day Scholar', 'Hosteller') NOT NULL, -- Type of student
    passout_year INT, -- Expected or actual year of graduation
    contact_number VARCHAR(15), -- Optional: Student's contact number
    email VARCHAR(100), -- Optional: Student's email address
    address TEXT, -- Optional: Student's home address
    guardian_name VARCHAR(100), -- Optional: Name of the guardian/parent
    guardian_contact VARCHAR(15), -- Optional: Guardian's contact number
    image VARCHAR(255), -- URL or file path to the student's image
    history TEXT, -- Stores the student's history
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Record creation time
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Record last update time
    today BOOLEAN DEFAULT FALSE, -- Indicates if the student is present today
    paid BOOLEAN DEFAULT FALSE, -- Indicates if the student is present today
    not_available_from DATE, -- Start date for unavailability
    not_available_to DATE, -- End date for unavailability
    last_menu jSON
);


DELIMITER $$

CREATE EVENT reset_student_details
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    UPDATE datadb.student_details
    SET paid = FALSE, today = FALSE,last_menu=None;
END$$

DELIMITER ;




SET GLOBAL event_scheduler = ON;


 mysql -h data.cjgsuu0i0kma.us-east-2.rds.amazonaws.com -u root -p



INSERT INTO student_details (
    roll_num,
    reg_num,
    year,
    semester,
    department,
    section,
    first_name,
    last_name,
    age,
    type,
    passout_year,
    contact_number,
    email,
    address,
    guardian_name,
    guardian_contact,
    image,
    history,
    today,
    not_available_from,
    not_available_to
) VALUES (
    '202102100',                  -- roll_num
    '211721106100',                 -- reg_num
    2023,                        -- year
    1,                           -- semester
    'Computer Science',          -- department
    'A',                         -- section
    'John',                      -- first_name
    'Doe',                       -- last_name
    21,                          -- age
    'Day Scholar',               -- type
    2027,                        -- passout_year
    '1234567890',                -- contact_number
    'john.doe@example.com',      -- email
    '123 Main St, Springfield',  -- address
    'Jane Doe',                  -- guardian_name
    '987654321',                -- guardian_contact
    'https://example.com/image.jpg', -- image
    'No history available.',     -- history
    FALSE,                       -- today (initially set to FALSE)
    '2024-12-25',                -- not_available_from (e.g., start date of unavailability)
    '2024-12-31'                 -- not_available_to (e.g., end date of unavailability)
);


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    admin BOOLEAN DEFAULT FALSE,
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



UPDATE student_details 
SET paid = 0, today = 0;
