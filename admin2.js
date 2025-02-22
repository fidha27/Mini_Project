let facultyData = [];

document.getElementById("faculty-form").addEventListener("submit", function(event) {
    event.preventDefault();  // Stop default form submission

    // Extract form data
    let facultyData = {
        name: document.getElementById("name").value,
        pen_no: document.getElementById("pen_no").value,
        dept_code: document.getElementById("dept_code").value,
        designation: document.getElementById("designation").value,
    };

    // Send data to Flask backend
    fetch('/submit_faculty_data', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"  // Ensure JSON format
        },
        body: JSON.stringify(facultyData)  // Convert data to JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert("Faculty added successfully!");
            refreshFacultyList();  // Refresh faculty list after adding
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(error => console.error("Error submitting faculty data:", error));
});


function downloadTemplate() {
    const csvContent = "pen_no,name,dept_code,designation\n"; // CSV header
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'faculty_upload_template.csv');
    link.click();
}


// Send faculty data to Flask function
function sendFacultyData(data) {
    fetch('/submit_faculty_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ faculty: data })
    })
    .then(response => response.json())
    .then(data => console.log('Data submitted successfully:', data))
    .catch(error => console.error('Error submitting data:', error));
}

// Render faculty table
function renderFacultyTable() {
    const tbody = document.querySelector('#faculty-table tbody');
    tbody.innerHTML = '';
    facultyData.forEach((faculty, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${faculty.penNo}</td>
            <td>${faculty.name}</td>
            <td>${faculty.deptCode}</td>
            <td>${faculty.designation}</td>
            <td>${faculty.univCode}</td>
            <td>${faculty.clgId}</td>
            <td>${faculty.password || 'Not Generated'}</td>
            <td>
                <button class="edit-btn" onclick="editFaculty(${index})">Edit</button>
                <button class="delete-btn" onclick="deleteFaculty(${index})">Delete</button>
                <button class="generate-btn" onclick="generatePassword(${index}, '${faculty.penNo}')">Generate Password</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function editFaculty(facultyId) {
    fetch(`/get_faculty/${facultyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Populate form with existing data
            document.getElementById('editFacultyId').value = facultyId;
            document.getElementById('editPen').value = data.pen_no;
            document.getElementById('editName').value = data.name;
            document.getElementById('editDeptCode').value = data.dept_code;
            document.getElementById('editDesignation').value = data.designation;

            // Show modal
            document.getElementById('editModal').style.display = 'block';
        })
        .catch(error => console.error('Error fetching faculty:', error));
}

// Function to close modal
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// Submit updated data
document.getElementById('editFacultyForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const facultyId = document.getElementById('editFacultyId').value;
    const updatedData = {
        pen_no: document.getElementById('editPen').value,
        name: document.getElementById('editName').value,
        dept_code: document.getElementById('editDeptCode').value,
        designation: document.getElementById('editDesignation').value
    };

    fetch(`/update_faculty/${facultyId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            closeEditModal();
            location.reload(); // Refresh the page to reflect changes
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error updating faculty:', error));
});



function deleteFaculty(facultyId) {
    console.log("Deleting faculty with ID:", facultyId);

    if (!facultyId) {
        console.error("Faculty ID is undefined!");
        return;
    }

    // Show confirmation before deleting
    if (!confirm("Are you sure you want to delete this faculty member?")) {
        return; // Exit if the user cancels the confirmation
    }

    fetch(`/delete_faculty/${facultyId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            console.log("Delete response:", data);

            // Display success or error message on the page
            const messageDiv = document.getElementById('message');
            if (data.message) {
                messageDiv.innerHTML = `<p style="color: green;">${data.message}</p>`;
                
                // Remove the faculty row from the table if it exists
                const facultyRow = document.getElementById(`faculty-row-${facultyId}`);
                if (facultyRow) {
                    facultyRow.remove();
                }
            } else if (data.error) {
                messageDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
            }
        })
        .catch(error => {
            console.error("Error deleting faculty:", error);
            document.getElementById('message').innerHTML = `<p style="color: red;">An error occurred while deleting.</p>`;
        });
}



function generatePassword(facultyId) {
    fetch(`http://127.0.0.1:5000/generate_password/${facultyId}`, {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => console.log("Generated password:", data.password))
    .catch(error => console.error("Error generating password:", error));
}

function generateAllPasswords() {
    fetch('/generate_all_passwords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log("Generated passwords:", data);
        for (const facultyId in data) {
            const passwordCell = document.getElementById(`password-${facultyId}`);
            if (passwordCell) {
                passwordCell.textContent = data[facultyId];
            }
        }
        alert("Passwords generated successfully!");
    })
    .catch(error => {
        console.error("Error generating passwords:", error);
        alert("Failed to generate passwords. Please try again.");
    });
}

// Search Faculty
function searchFaculty() {
    let departmentCode = document.getElementById("search-dept").value;
    let penNo = document.getElementById("search-pen_no").value;

    fetch(`/search_faculty?department_code=${departmentCode}&pen_no=${penNo}`)
        .then(response => response.json())
        .then(data => {
            let resultContainer = document.getElementById("faculty-results");
            resultContainer.innerHTML = "";

            if (data.length === 0) {
                resultContainer.innerHTML = "<p>No results found.</p>";
                return;
            }

            let table = `<table>
                            <tr>
                                <th>PEN No</th>
                                <th>Name</th>
                                <th>Department Code</th>
                                <th>Designation</th>
                                <th>College ID</th>
                                <th>University Code</th>
                            </tr>`;
            
            data.forEach(faculty => {
                table += `<tr>
                            <td>${faculty.pen_no}</td>
                            <td>${faculty.name}</td>
                            <td>${faculty.dept_code}</td>
                            <td>${faculty.designation}</td>
                            <td>${faculty.clg_id}</td>
                            <td>${faculty.univ_code}</td>
                          </tr>`;
            });

            table += `</table>`;
            resultContainer.innerHTML = table;
        })
        .catch(error => console.error("Error:", error));
}

// Save edited faculty
function saveFaculty() {
    const facultyId = document.getElementById('faculty-id').value;
    const updatedData = {
        pen_no: document.getElementById('edit-pen-no').value,
        name: document.getElementById('edit-name').value,
        dept_code: document.getElementById('edit-dept-code').value,
        designation: document.getElementById('edit-designation').value,
        univ_code: document.getElementById('edit-univ-code').value,
        clg_id: document.getElementById('edit-clg-id').value
    };

    fetch(`/update_faculty/${facultyId}`, {
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
            alert("Error updating faculty.");
        }
    })
    .catch(error => console.error("Error updating faculty:", error));
}

// Cancel edit
function cancelEdit() {
    document.getElementById('edit-faculty-form').style.display = 'none';
}


