// Use the miniproject database
use("miniproject");

// Insert students
db.getCollection('students').insertMany([
    { "university_id": "UNIV001", "name": "John Doe", "admission_no": "A001" },
    { "university_id": "UNIV001", "name": "Jane Smith", "admission_no": "A002" },
    { "university_id": "UNIV001", "name": "Alice Johnson", "admission_no": "A003" }
]);

// Insert advisors
db.getCollection('advisor').insertMany([
    { "batch_id": "CS 2022-2026", "advisor_id": "PEN001", "adname": "Dr. Smitha" },
    { "batch_id": "CS 2021-2025", "advisor_id": "PEN002", "adname": "Sam" },
    { "batch_id": "CS 2023-2027", "advisor_id": "PEN003", "adname": "Dr. Varun" },
    { "batch_id": "CS 2020-2024", "advisor_id": "PEN004", "adname": "Dr. Priya" }
]);

// Insert admin records
db.getCollection('admin').insertMany([
    { "admin_id": "ADMIN001", "univ_code": "UNIV001", "clg_id": "CLG001" },
    { "admin_id": "ADMIN002", "univ_code": "UNIV001", "clg_id": "CLG002" },
    { "admin_id": "ADMIN003", "univ_code": "UNIV001", "clg_id": "CLG003" }
]);

// Insert colleges
db.getCollection('college').insertMany([
    { "college_id": "CLG001", "univ_code": "UNIV001", "name": "College of Science" },
    { "college_id": "CLG002", "univ_code": "UNIV001", "name": "College of Arts" },
    { "college_id": "CLG003", "univ_code": "UNIV001", "name": "College of Engineering" }
]);

// Insert departments
db.getCollection("schemas").insertMany([
    {
        "schema_name": "2015",
        "univ_code": "UNIV456",
        "clg_id": "CLG123",
        "admin_id": ObjectId("67c5fbb6e6605343d1d41eb7")
    },
    {
        "schema_name": "2019",
        "univ_code": "UNIV456",
        "clg_id": "CLG123",
        "admin_id": ObjectId("67c5fbb6e6605343d1d41eb7")
    }
]);

// Insert courses
db.getCollection('courses').insertMany([
    { "schema_name": "2019", "details": { "course_code": "cst201", "course_title": "Data Structures", "dept_code": "cse", "semester": "3", "univ_code": "UNIV001", "course_type": "theory" } },
    { "schema_name": "2015", "details": { "course_code": "cst202", "course_title": "Operating Systems", "dept_code": "cse", "semester": "4", "univ_code": "UNIV001", "course_type": "theory" } },
    { "schema_name": "2019", "details": { "course_code": "cst203", "course_title": "Database Management Systems", "dept_code": "cse", "semester": "5", "univ_code": "UNIV001", "course_type": "theory" } },
    { "schema_name": "2015", "details": { "course_code": "cst204", "course_title": "Computer Networks", "dept_code": "cse", "semester": "6", "univ_code": "UNIV001", "course_type": "theory" } },
    { "schema_name": "2019", "details": { "course_code": "cst205", "course_title": "Software Engineering", "dept_code": "cse", "semester": "5", "univ_code": "UNIV001", "course_type": "theory" } }
]);

// Insert departments
db.getCollection('departments').insertMany([
    {
        "dept_name": "Computer Science",
        "dept_code": "cse",
        "hod_username": "hodcse",
        "hod_password": "123",
        "admin_id": "67c5fbb6e6605343d1d41eb7"
    },
    {
        "dept_name": "Mechanical Engineering",
        "dept_code": "me",
        "hod_username": "hodme",
        "hod_password": "456",
        "admin_id": "67c5fbb6e6605343d1d41eb7"
    },
    {
        "dept_name": "Electrical Engineering",
        "dept_code": "ee",
        "hod_username": "hodee",
        "hod_password": "789",
        "admin_id": "67c5fbb6e6605343d1d41eb7"
    }
]);

// Insert faculty members
db.getCollection('faculty').insertMany([
    {
        "pen_no": "PEN001",
        "name": "Dr. Smitha",
        "dept_code": "cse",
        "designation": "Professor",
        "univ_code": "UNIV001",
        "clg_id": "CLG003",
        "password": "123",
        "admin_id": "67c5fbb6e6605343d1d41eb7",
        "pen": "PEN001",
        "role": {
            "advisor": ["2023"],
            "mc": true
        }
    },
    {
        "pen_no": "PEN002",
        "name": "Sam",
        "dept_code": "cse",
        "designation": "Associate Professor",
        "univ_code": "UNIV001",
        "clg_id": "CLG003",
        "password": "456",
        "admin_id": "67c5fbb6e6605343d1d41eb7",
        "pen": "PEN002",
        "role": {
            "advisor": ["2024"],
            "mc": false
        }
    },
    {
        "pen_no": "PEN003",
        "name": "Dr. Varun",
        "dept_code": "me",
        "designation": "Assistant Professor",
        "univ_code": "UNIV001",
        "clg_id": "CLG003",
        "password": "789",
        "admin_id": "67c5fbb6e6605343d1d41eb7",
        "pen": "PEN003",
        "role": {
            "advisor": ["2023", "2025"],
            "mc": true
        }
    },
    {
        "pen_no": "PEN004",
        "name": "Dr. Priya",
        "dept_code": "me",
        "designation": "Assistant Professor",
        "univ_code": "UNIV001",
        "clg_id": "CLG003",
        "password": "321",
        "admin_id": "67c5fbb6e6605343d1d41eb7",
        "pen": "PEN004",
        "role": {
            "advisor": ["2022"],
            "mc": false
        }
    },
    {
        "pen_no": "PEN005",
        "name": "Dr. Ann",
        "dept_code": "cse",
        "designation": "Assistant Professor",
        "univ_code": "UNIV001",
        "clg_id": "CLG003",
        "password": "654",
        "admin_id": "67c5fbb6e6605343d1d41eb7",
        "pen": "PEN005",
        "role": {
            "advisor": ["2024"],
            "mc": true
        }
    }
]);

// Insert batch details
db.getCollection('batch').insertMany([
    { "batch_id": "CS 2022-2026", "dept_code": "cse", "advisor_id": "PEN001", "adname": "Dr. Smitha" },
    { "batch_id": "CS 2021-2025", "dept_code": "cse", "advisor_id": "PEN002", "adname": "Sam" },
    { "batch_id": "CS 2023-2027", "dept_code": "cse", "advisor_id": "PEN003", "adname": "Dr. Varun" },
    { "batch_id": "CS 2020-2024", "dept_code": "cse", "advisor_id": "PEN004", "adname": "Dr. Priya" }
]);

// Insert threshold values
db.getCollection('threshold').insertMany([
    {
        "direct_threshold": 60,
        "indirect_threshold": 40,
        "co_attainment": {
            "level3": 80,
            "level2": 60,
            "level1": 40
        }
    }
]);

// Insert modules
db.getCollection('modules').insertMany([
    {
        "module_name": "Data Structures",
        "mc_name": "Dr. Smitha",
        "schema_name": "2019",
        "courses": ["cst201", "cst202"]
    },
    {
        "module_name": "Operating Systems",
        "mc_name": "Sam",
        "schema_name": "2019",
        "courses": ["cst203", "cst204"]
    }
]);
