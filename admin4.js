// Fetch and display courses dynamically based on selected schema
const schemaSelect = document.getElementById('schema-select');
schemaSelect.addEventListener('change', async function () {
    const semester = 1; // Default semester, can be updated dynamically
    const response = await fetch(`/get_courses/${schema_name}/${semester}`);
    const data = await response.json();
    displayCourses(data.courses);
});

// Trigger search on button click
function searchCourses() {
    const semester = document.getElementById('semester-input').value.trim();
    const schemaName = document.getElementById('schema-name-input').value.trim();

    console.log("Sending search for:", { schema_name: schemaName, semester: parseInt(semester) }); // Log input

    if (!semester || !schemaName) {
        alert('Please fill in both Schema Name and Semester.');
        return;
    }

    fetch('/search_courses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema_name: schemaName, semester: parseInt(semester) })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Fetched courses:", data); // 🔍 Check response data
        if (data.error) {
            console.error(data.error);
            alert(data.error);
            return;
        }
        displayCourses(data);
    })
    .catch(error => console.error("Error fetching courses:", error));
}

function submitCourseEdit() {
    const courseId = document.getElementById("editCourseForm").dataset.courseId;

    const updatedCourse = {
        course_title: document.getElementById("edit_course_title").value,
        course_type: document.getElementById("edit_course_type").value,
        semester: parseInt(document.getElementById("edit_semester").value)
    };

    fetch(`/update_course/${courseId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedCourse)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Course updated successfully!');
            closeCourseModal();
            location.reload(); // Reload to reflect changes
        } else {
            alert('Failed to update course: ' + data.error);
        }
    })
    .catch((error) => console.error("Error updating course:", error));
}

function closeCourseModal() {
    document.getElementById("editCourseModal").style.display = "none";
}


// Fetch and display courses dynamically
function fetchCourses(edit_schema_name, semester) {
    fetch(`/get_courses/${schema_name}/${semester}`)
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text); });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error(data.error);
                alert(data.error);
                return;
            }
            displayCourses(data.courses);
        })
        .catch(error => console.error("Error fetching courses:", error));
}

function displayCourses(courses) {
    const tableBody = document.querySelector('#schema-table tbody');
    tableBody.innerHTML = ''; // Clear previous data

    if (!courses.length) {
        alert("No courses found for the given schema and semester.");
        return;
    }

    // Make the table visible
    document.querySelector('.schema-table-section').style.display = 'block';

    courses.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.schema_name || ''}</td>
            <td>${course.dept_code || ''}</td>
            <td>${course.details?.univ_code || ''}</td>
            <td>${course.course_code || ''}</td>
            <td>${course.course_title || ''}</td>
            <td>${course.course_type || ''}</td>
            <td>${course.semester || ''}</td>
            <td>
                <button class="edit-btn" onclick="editCourse('${course._id}')">Edit</button>
                <button class="delete-btn" onclick="deleteCourse('${course._id}')">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}


function editCourse(courseId) {
    fetch(`/get_course/${courseId}`)
        .then((response) => response.json())
        .then((data) => {
            console.log(data); // Check the structure in the console
            document.getElementById("edit_course_code").value = data.course_code;
            document.getElementById("edit_course_name").value = data.course_title;
            document.getElementById("edit_course_type").value = data.course_type;
            document.getElementById("edit_dept_code").value = data.dept_code;
            document.getElementById("edit_semester").value = data.semester;
            document.getElementById("edit_schema_name").value = data.schema_name; // Display schema_name
            document.getElementById("editCourseForm").dataset.courseId = data._id; // Set course ID
            document.getElementById("editModal").style.display = "block"; // Show the modal
        })
        .catch((error) => console.error("Error fetching course:", error));
}

// Handle form submission for course update
document.getElementById("editCourseForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const courseId = document.getElementById("editCourseForm").dataset.courseId;
    const updatedData = {
        course_name: document.getElementById("edit_course_name").value,
        course_code: document.getElementById("edit_course_code").value,
        course_type: document.getElementById("edit_course_type").value,
        dept_code: document.getElementById("edit_dept_code").value,
        semester: document.getElementById("edit_semester").value,
        schema_name: document.getElementById("edit_schema_name").value
    };

    fetch(`/update_course/${courseId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedData),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.message) {
            alert("Course updated successfully!");
            location.reload(); // Refresh the page after successful update
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch((error) => console.error("Error updating course:", error));
});

// Function to close the modal
function closeEditCourseModal() {
    document.getElementById("editModal").style.display = "none";
}

// Delete Course Function
async function deleteCourse(courseId) {
    if (confirm('Are you sure you want to delete this course?')) {
        const response = await fetch(`/delete_course/${courseId}`, { method: 'DELETE' });
        if (response.ok) {
            alert('Course deleted successfully!');
            location.reload();
        } else {
            alert('Failed to delete course.');
        }
    }
}

// Export Schema Data to CSV
function exportSchema() {
    let csvContent = "data:text/csv;charset=utf-8,";
    const rows = document.querySelectorAll('table tr');
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => col.innerText);
        csvContent += rowData.join(',') + "\n";
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'schema_courses.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


function downloadTemplate() {
    const csvContent = "course_code,course_title,course_type,semester,dept_code,schema_name\n"; // CSV header
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "course_upload_template.csv");
    link.click();
}