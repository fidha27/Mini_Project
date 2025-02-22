document.addEventListener("DOMContentLoaded", function () {
    const courseForm = document.getElementById("course-form");
    if (!courseForm) {
        console.error("Course form not found!");
        return;
    }

     // Add event listeners to existing Edit and Delete buttons on page load
    document.querySelectorAll("#course-mapping-table tr").forEach(row => {
        const mappingId = row.getAttribute("data-id");
        if(!mappingId) return;
        const editButton = row.querySelector(".edit-btn");
        const deleteButton = row.querySelector(".delete-btn");

        if (editButton) {
            editButton.addEventListener("click", () => updateMapping(mappingId, row));
        }
        if (deleteButton) {
            deleteButton.addEventListener("click", () => deleteMapping(mappingId, row));
        }
    });

    courseForm.addEventListener("submit", function (event) {
        event.preventDefault();

        let subject = document.getElementById("subject").value;
        let teacher = document.getElementById("teacher").value;
        let department = document.getElementById("department").value;

        console.log("Subject:", subject);
        console.log("Teacher:", teacher);
        console.log("Department:", department);

        if (!subject || !teacher || !department) {
            alert("Please fill in all fields before saving.");
            return;
        }

        fetch("/course-mapping", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ subject, teacher, department })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                let successModal = new bootstrap.Modal(document.getElementById("successModal"));
                successModal.show();

                // Reset form and add to table with the received ID
                courseForm.reset();
                addMappingToTable(data.id, subject, teacher, department);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    function addMappingToTable(id, subject, teacher, department) {
        const tableBody = document.getElementById("course-mapping-table");

        if (!tableBody) {
            console.error("Table body not found!");
            return;
        }

        let newRow = document.createElement("tr");
        newRow.setAttribute("data-id", id); // Store the ID for reference

        // Correctly insert data into table row
        newRow.innerHTML = `
            <td>${subject}</td>
            <td>${teacher}</td>
            <td>${department}</td>
            <td>
                <button class="btn btn-warning btn-sm edit-btn">Edit</button>
                <button class="btn btn-danger btn-sm delete-btn">Delete</button>
            </td>
        `;

        // Add event listeners to buttons
        newRow.querySelector(".edit-btn").addEventListener("click", () => updateMapping(id, subject, teacher, department));
        newRow.querySelector(".delete-btn").addEventListener("click", () => deleteMapping(id, newRow));

        // Append new row to the table body
        tableBody.appendChild(newRow);
    }

    function updateMapping(id, subject, teacher, department) {
        let newSubject = prompt("Enter new subject:", subject);
        let newTeacher = prompt("Enter new teacher:", teacher);
        let newDepartment = prompt("Enter new department:", department);

        if (!newSubject || !newTeacher || !newDepartment) {
            alert("All fields are required!");
            return;
        }

        fetch(`/edit-mapping/${id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subject: newSubject, teacher: newTeacher, department: newDepartment })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Course mapping updated successfully!");

                // Update table row with new values
                let row = document.querySelector(`tr[data-id='${id}']`);
                if (row) {
                    row.cells[0].innerText = newSubject;
                    row.cells[1].innerText = newTeacher;
                    row.cells[2].innerText = newDepartment;
                }
            }
        })
        .catch(error => console.error("Error:", error));
    }

    function deleteMapping(id, rowElement) {
        if (!id || id === "null") {
            console.error("Invalid ID: Cannot delete.");
            alert("Error: Invalid course mapping ID.");
            return;
        }


        if (!confirm("Are you sure you want to delete this course mapping?")) return;

        fetch(`/delete-mapping/${id}`, { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("Course mapping deleted successfully!");
                rowElement.remove(); // Remove row from table
            }
        })
        .catch(error => console.error("Error:", error));
    }
});
