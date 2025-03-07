document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("uploadButton").addEventListener("click", function () {
        uploadFile();
    });
});


function uploadFile() {
    const fileInput = document.getElementById("fileUpload");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file to upload.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload-marks", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("File uploaded and marks processed successfully!");
        }
    })
    .catch(error => console.error("Error uploading file:", error));
}



document.getElementById("fileUpload").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        fetch("/upload-marks", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("File uploaded and marks processed successfully!");
            }
        })
        .catch(error => console.error("Error uploading file:", error));
    }
});

function selectTool() {
    const toolName = document.getElementById("toolSelect").value;
    const numParts = document.getElementById("numParts").value;
    const toolDetails = {
        tool_name: toolName,
        parts: []
    };

    for (let i = 1; i <= numParts; i++) {
        const part = {
            part_label: String.fromCharCode(64 + i),
            questions: []
        };

        const partDiv = document.getElementById(`part${i}`);
        const questionRows = partDiv.querySelectorAll(".question-row");

        questionRows.forEach((row, index) => {
            part.questions.push({
                question_no: index + 1,
                co: row.querySelector(".co-value").value,
                total_marks: row.querySelector(".total-marks").value,
                compulsory: row.querySelector(".compulsory").checked
            });
        });

        toolDetails.parts.push(part);
    }

    fetch("/store-tool-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toolDetails)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Tool details saved successfully!");
        }
    })
    .catch(error => console.error("Error saving tool config:", error));
}

function generateCSV() {
    const toolName = document.getElementById("examType").value; // Get selected tool

    if (!toolName) {
        alert("Please select a tool before generating the CSV.");
        return;
    }

    fetch(`/generate-csv?tool_name=${encodeURIComponent(toolName)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                return;
            }
            alert("CSV generated successfully!");
            let link = document.getElementById("csvDownloadLink");
            link.href = data.file_url;
            link.style.display = "block";
            link.innerText = "Download CSV";
        })
        .catch(error => {
            console.error("Error fetching CSV:", error);
            alert("Failed to generate CSV. Please check console for details.");
        });
}


document.getElementById("numParts").addEventListener("change", function () {
    const numParts = parseInt(this.value);
    const partsContainer = document.getElementById("partsContainer");
    partsContainer.innerHTML = ""; // Clear existing parts

    for (let i = 1; i <= numParts; i++) {
        const partDiv = document.createElement("div");
        partDiv.className = "part-section";
        partDiv.id = `part${i}`;

        partDiv.innerHTML = `
            <h4>Part ${String.fromCharCode(64 + i)}</h4>
            <label for="numQuestions${i}">Number of Questions:</label>
            <input type="number" id="numQuestions${i}" min="1">
            <div class="questions-container" id="questionsContainer${i}"></div>
        `;

        partsContainer.appendChild(partDiv);

        // Attach event listener dynamically
        document.getElementById(`numQuestions${i}`).addEventListener("change", function () {
            generateQuestions(i);
        });
    }
});
function generateParts() {
    const numParts = parseInt(document.getElementById("numParts").value);
    const partsContainer = document.getElementById("partsContainer");
    partsContainer.innerHTML = ""; // Clear previous content

    if (isNaN(numParts) || numParts < 1) {
        return; // Stop execution if invalid input
    }

    for (let i = 1; i <= numParts; i++) {
        const partDiv = document.createElement("div");
        partDiv.className = "part-section";
        partDiv.id = `part${i}`;

        partDiv.innerHTML = `
            <h4>Part ${String.fromCharCode(64 + i)}</h4>
            <label for="numQuestions${i}">Number of Questions:</label>
            <input type="number" id="numQuestions${i}" min="1">
            <div class="questions-container" id="questionsContainer${i}"></div>
        `;

        partsContainer.appendChild(partDiv);

        // Attach event listener dynamically to each "numQuestions" input
        document.getElementById(`numQuestions${i}`).addEventListener("change", function () {
            generateQuestions(i);
        });
    }
}

function generateQuestions(partIndex) {
    const numQuestions = parseInt(document.getElementById(`numQuestions${partIndex}`).value);
    const questionsContainer = document.getElementById(`questionsContainer${partIndex}`);
    questionsContainer.innerHTML = ""; // Clear previous questions

    if (isNaN(numQuestions) || numQuestions < 1) {
        return; // Stop execution if invalid input
    }

    for (let j = 1; j <= numQuestions; j++) {
        const questionDiv = document.createElement("div");
        questionDiv.className = "question-row";

        questionDiv.innerHTML = `
            <label>Q${j} - CO:</label>
            <input type="text" class="co-value" placeholder="Enter CO" required>
            
            <label>Total Marks:</label>
            <input type="number" class="total-marks" required>

            <label>Compulsory:</label>
            <input type="checkbox" class="compulsory">
        `;

        questionsContainer.appendChild(questionDiv);
    }
}


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("numParts").addEventListener("change", function () {
        generateParts();
    });
});

window.enterMark = function () {
    console.log("Entering marks...");
};
function enterMark() {
    const studentRoll = document.getElementById("studentRoll").value;
    const marks = document.getElementById("marks").value;

    if (!studentRoll || !marks) {
        alert("Please enter student roll number and marks.");
        return;
    }

    fetch("/enter-marks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_roll: studentRoll, marks: marks })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Marks entered successfully!");
        }
    })
    .catch(error => console.error("Error entering marks:", error));
}

function confirmEntries() {
    const toolName = document.getElementById("examType").value;
    const numParts = document.getElementById("numParts").value;

    if (!toolName || !numParts) {
        alert("Please select a tool and enter the number of parts.");
        return;
    }

    const toolDetails = {
        tool_name: toolName,
        batch: "", 
        course_name: "", 
        parts: []
    };

    for (let i = 1; i <= numParts; i++) {
        const part = {
            part_label: String.fromCharCode(64 + i),
            questions: []
        };

        const partDiv = document.getElementById(`part${i}`);
        const questionRows = partDiv.querySelectorAll(".question-row");

        questionRows.forEach((row, index) => {
            part.questions.push({
                question_no: index + 1,
                co: row.querySelector(".co-value").value,
                total_marks: row.querySelector(".total-marks").value,
                compulsory: row.querySelector(".compulsory").checked
            });
        });

        toolDetails.parts.push(part);
    }

    fetch("/confirm-tool-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toolDetails)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Tool details confirmed and saved successfully!");
        }
    })
    .catch(error => console.error("Error saving tool config:", error));
}
