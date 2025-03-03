document.addEventListener('DOMContentLoaded', function () {
    const addCoBtn = document.getElementById('add-co-btn');
    const coStatusBody = document.getElementById('co-status-body');
    const matrixContainer = document.getElementById("matrix-container");
    const matrixBody = document.getElementById("matrix-body");

    // Fetch and display COs on page load
    fetchCOs();
    fetchMatrix();

    addCoBtn.addEventListener('click', function () {
        const coNo = document.getElementById('co-no').value;
        const description = document.getElementById('description').value;
        const bloomLevel = document.getElementById('bloom-level').value;
        const threshold = document.getElementById('set-threshold').value;

        if (!coNo || !description || !bloomLevel || !threshold) {
            alert("Please fill all fields correctly.");
            return;
        }

        fetch('/add_co', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ co_no: coNo, description, bloom_level: bloomLevel, threshold })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchCOs();
        })
        .catch(error => console.error("Error:", error));
    });

    fetch("/select_course_batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ course_name: course, batch: batch })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            setTimeout(() => {  // Small delay before redirecting
                window.location.href = "/course_outcome";
            }, 500);  
        } else {
            alert("Failed to select course & batch");
        }
    });

    
    // Function to mark a cell when clicked
    function markCell(cell) {
        if (!cell.classList.contains("marked")) {
            cell.classList.add("marked");
            cell.querySelector(".cell-value").textContent = "✔️"; // Show a checkmark
        } else {
            cell.classList.remove("marked");
            cell.querySelector(".cell-value").textContent = ""; // Clear value
        }
    }
    
    function fetchMatrix() {
        console.log("Fetching Matrix...");
    
        fetch('/get_matrix')
        .then(response => response.json())
        .then(data => {
            console.log("Matrix fetched:", data);
    
            const matrixContainer = document.getElementById("matrix-container");
            const matrixBody = document.getElementById("matrix-body");
    
            if (data.length > 0) {
                matrixContainer.classList.remove("hidden");
                matrixBody.innerHTML = ""; // Clear existing rows
    
                data.forEach(co => {
                    let row = `<tr class="matrix-row">
                                <td>${co.co_number}</td>`;
                    for (let i = 1; i <= 12; i++) {
                        let value = co.po_correlations[`PO${i}`] || '-'; // Use stored value or "-"
                        let cellClass = value !== '-' ? 'marked' : ''; // Highlight marked cells
    
                        row += `<td class="matrix-cell ${cellClass}">
                                    <span class="cell-value">${value}</span>
                                </td>`;
                    }
                    row += `</tr>`;
                    matrixBody.innerHTML += row;
                });
    
                // Add click event to enable editing
                document.querySelectorAll(".matrix-cell").forEach(cell => {
                    cell.addEventListener("click", () => markCell(cell));
                });
            } else {
                matrixContainer.classList.add("hidden"); // Hide matrix if no data
            }
        })
        .catch(error => console.error("Error fetching CO-PO matrix:", error));
    }
    
    // Ensure fetchMatrix is called when the page loads
    document.addEventListener("DOMContentLoaded", fetchMatrix);
    
        // Function to generate values for marked cells
    
        function fetchCOs() {
            console.log("Fetching COs...");
            fetch('/get_cos')
                .then(response => response.json())
                .then(cos => {
                    console.log("COs fetched:", cos);
                    coStatusBody.innerHTML = ''; // Clear previous entries
                    cos.forEach(co => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${co.co_no}</td>
                            <td id="desc-${co._id}">${co.description}</td>
                            <td id="bloom-${co._id}">${co.bloom_level}</td>
                            <td id="threshold-${co._id}">${co.threshold}</td>
                            <td>${co.is_approved ? "✅ Approved" : "⏳ Pending"}</td>
                            <td>
                                <button onclick="window.editCO('${co._id}')">✏️ Edit</button>
                                <button onclick="window.deleteCO('${co._id}')">❌ Delete</button>
                            </td>
                        `;
                        coStatusBody.appendChild(row);
                    });
                })
                .catch(error => console.error("Error fetching COs:", error));
        }
        

});

window.editCO = function (coId) {
    console.log(`Editing CO: ${coId}`);  // Debugging

    const descElement = document.getElementById(`desc-${coId}`);
    const bloomElement = document.getElementById(`bloom-${coId}`);
    const thresholdElement = document.getElementById(`threshold-${coId}`);

    if (!descElement || !bloomElement || !thresholdElement) {
        console.error(`Error: Element not found for CO ${coId}`);
        alert("Error: Unable to find CO details. Please refresh and try again.");
        return;
    }

    const description = prompt("Enter new description:", descElement.textContent);
    const bloomLevel = prompt("Enter new Bloom's Level (1-6):", bloomElement.textContent);
    const threshold = prompt("Enter new Threshold:", thresholdElement.textContent);

    if (!description || !bloomLevel || !threshold) {
        alert("Fields cannot be empty!");
        return;
    }

    fetch('/edit_co', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ _id: coId, description, bloom_level: bloomLevel, threshold })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Edit response:", data);  // Debugging
        if (data.success) {
            alert(data.message || "CO updated successfully!");
            setTimeout(fetchCOs, 500);  // Small delay before refreshing
        } else {
            alert("Error updating CO. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
};

window.deleteCO = function (coId) {
    if (!confirm("Are you sure you want to delete this CO?")) return;

    fetch('/delete_co', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ _id: coId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchCOs();
    })
    .catch(error => console.error("Error:", error));
};


const calculateBtn = document.getElementById("calculate-btn");
if (calculateBtn) {
    calculateBtn.addEventListener("click", calculateCorrelation);
    console.log("Event Listener Added!"); // Debugging
} else {
    console.error("Calculate button not found!");
}

function calculateCorrelation() {
    console.log("Calculating Correlation...");

    const matrixBody = document.getElementById("matrix-body");
    const rows = matrixBody.getElementsByTagName("tr");
    
    let mappedMatrix = [];
    let dataToSend = [];

    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName("td");
        let rowValues = [];
        const coNumber = cells[0].textContent; // CO Number
        const coLevel = parseInt(document.getElementById("bloom-level").value) || 1;

        for (let j = 1; j < cells.length; j++) { // Skip CO Number column
            const cell = cells[j].querySelector(".cell-value");
            let correlationValue = 0;

            // Check if the cell is marked (has the "marked" class)
            if (cells[j].classList.contains("marked")) {
                const poLevel = j;
                const diff = Math.abs(coLevel - poLevel);

                if (diff === 0 || diff === 1) {
                    correlationValue = 3; // High correlation
                } else if (diff === 2 || diff === 3) {
                    correlationValue = 2; // Medium correlation
                } else if (diff === 4 || diff === 5) {
                    correlationValue = 1; // Low correlation
                }
            }

            rowValues.push(correlationValue);
            cell.textContent = correlationValue; // Set value in table

            // Prepare data for MongoDB
            dataToSend.push({
                co_number: coNumber,
                po_number: j,
                value: correlationValue
            });
        }

        mappedMatrix.push(rowValues);
    }

    console.log("Mapped Correlation Matrix:", mappedMatrix);
    console.log("Data to Send to MongoDB:", dataToSend);

    // Send to MongoDB

    fetch('/save_matrix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            matrix: dataToSend
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error("Error saving matrix:", error));
}







