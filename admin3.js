
// Add Student Form Submission
document.getElementById("addStudentForm").addEventListener("submit", function (event) {
    event.preventDefault();

    let studentData = {
        univ_no: document.getElementById("univ_no").value,
        name: document.getElementById("name").value,
        reg_no: document.getElementById("reg_no").value,
        batch: document.getElementById("batch").value,
        dept_code:document.getElementById("dept_code").value
    };

    fetch("/submit_student_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(studentData),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                alert("Student added successfully!");
                location.reload(); // Refresh the page
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch((error) => console.error("Error adding student:", error));
});

function sendstudentData(data) {
    fetch('/submit_student_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ students: data })
    })
    .then(response => response.json())
    .then(data => console.log('Data submitted successfully:', data))
    .catch(error => console.error('Error submitting data:', error));
}


// Search Students
function searchStudents() {
    const batch = document.querySelector('input[name="batch"]').value;
    const dept_code = document.querySelector('input[name="dept_code"]').value;
    const clg_id = document.querySelector('input[name="clg_id"]').value;

    fetch(`/search_students?batch=${batch}&dept_code=${dept_code}&clg_id=${clg_id}`)
        .then((response) => response.json())
        .then((data) => {
            const resultsDiv = document.getElementById("student-results");
            resultsDiv.innerHTML = "";

            if (data.length === 0) {
                resultsDiv.innerHTML = "<p>No students found.</p>";
                return;
            }

            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>University No</th>
                        <th>Name</th>
                        <th>Registration No</th>
                        <th>Batch</th>
                        <th>Semester</th>
                    </tr>
                </thead>
                <tbody>
                    ${data
                        .map(
                            (student) => `
                        <tr>
                            <td>${student.univ_no}</td>
                            <td>${student.name}</td>
                            <td>${student.reg_no}</td>
                            <td>${student.batch}</td>
                            <td>${student.semester}</td>
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            `;
            resultsDiv.appendChild(table);
        })
        .catch((error) => console.error("Error searching students:", error));
}

// Edit Student
function editstudent(studentId) {
    fetch(`/get_student/${studentId}`)
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("edit_univ_no").value = data.univ_no;
            document.getElementById("edit_name").value = data.name;
            document.getElementById("edit_reg_no").value = data.reg_no;
            document.getElementById("edit_batch").value = data.batch;
            document.getElementById("edit_dept_code").value = data.dept_code;
            document.getElementById("editStudentForm").dataset.studentId = data._id; // Store ID
            document.getElementById("editModal").style.display = "block";
        })
        .catch((error) => console.error("Error fetching student:", error));
}


// Save Edited Student
document.getElementById("editStudentForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const studentId = document.getElementById("editStudentForm").dataset.studentId; // Get the MongoDB ID
    const updatedData = {
        name: document.getElementById("edit_name").value,
        reg_no: document.getElementById("edit_reg_no").value,
        batch: document.getElementById("edit_batch").value,
        dept_code: document.getElementById("edit_dept_code").value,
        univ_no: document.getElementById("edit_univ_no").value,
    };

    fetch(`/update_student/${studentId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedData),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                alert("Student updated successfully!");
                location.reload(); // Refresh the page
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch((error) => console.error("Error updating student:", error));
});

// Delete Student
function deletestudent(studentId) {
    if (confirm("Are you sure you want to delete this student?")) {
        fetch(`/delete_student/${studentId}`, {
            method: "DELETE",
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.message) {
                    alert("Student deleted successfully!");
                    location.reload(); // Refresh the page
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch((error) => console.error("Error deleting student:", error));
    }
}

function savestudent() {
    const studentId = document.getElementById('student-id').value;
    const updatedData = {
        reg_no: document.getElementById('edit-reg-no').value,
        name: document.getElementById('edit-name').value,
        dept_code: document.getElementById('edit-dept-code').value,
        batch: document.getElementById('edit-batch').value,
        univ_no: document.getElementById('edit-univ-no').value,
        univ_code: document.getElementById('edit-univ-code').value,
        clg_id: document.getElementById('edit-clg-id').value
    };

    fetch(`/update_student/${studentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Faculty updated successfully!");
            location.reload();
        } else {
            alert("Error updating student.");
        }
    })
    .catch(error => console.error("Error updating faculty:", error));
}


// Close Edit Modal
function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}

// Download CSV Template
function downloadTemplate() {
    const csvContent = "univ_no,name,reg_no,batch,dept_code\n"; // CSV header
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "student_upload_template.csv");
    link.click();
}