// script.js

let schemaData = []; // Example: [{ schemaName: "Schema 1" }, { schemaName: "Schema 2" }]
let toolData = []; // Example: [{ schemaName: "Schema 1", toolName: "Tool A", toolDescription: "Description A" }]

// Populate schema select options
function updateSchemaSelect() {
    const schemaSelect = document.getElementById('schema-select');
    schemaSelect.innerHTML = '';
    schemaData.forEach(schema => {
        const option = document.createElement('option');
        option.value = schema.schemaName;
        option.textContent = schema.schemaName;
        schemaSelect.appendChild(option);
    });
}

// Handle tool form submission
document.getElementById('tool-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const tool = {
        schemaName: formData.get('schema-select'),
        toolName: formData.get('tool-name'),
        toolDescription: formData.get('tool-description'),
    };
    toolData.push(tool);
    renderToolsTable();
    e.target.reset();
});

// Render tools table
function renderToolsTable() {
    const tbody = document.querySelector('#tools-table tbody');
    tbody.innerHTML = '';
    schemaData.forEach(schema => {
        const schemaRow = document.createElement('tr');
        schemaRow.innerHTML = `
            <td>${schema.schemaName}</td>
            <td colspan="3"></td>
        `;
        tbody.appendChild(schemaRow);

        toolData.filter(tool => tool.schemaName === schema.schemaName).forEach(tool => {
            const toolRow = document.createElement('tr');
            toolRow.innerHTML = `
                <td></td>
                <td>${tool.toolName}</td>
                <td>${tool.toolDescription}</td>
                <td>
                    <button class="edit-btn" onclick="editTool('${tool.toolName}')">Edit</button>
                    <button class="delete-btn" onclick="deleteTool('${tool.toolName}')">Delete</button>
                </td>
            `;
            tbody.appendChild(toolRow);
        });
    });
}

// Edit tool
function editTool(toolName) {
    const tool = toolData.find(t => t.toolName === toolName);
    if (tool) {
        document.getElementById('tool-name').value = tool.toolName;
        document.getElementById('tool-description').value = tool.toolDescription;
        document.getElementById('schema-select').value = tool.schemaName;
        toolData = toolData.filter(t => t.toolName !== toolName);
        renderToolsTable();
    }
}

// Delete tool
function deleteTool(toolName) {
    toolData = toolData.filter(t => t.toolName !== toolName);
    renderToolsTable();
}

// Initialize schema data (example)
schemaData = [
    { schemaName: "Schema 1" },
    { schemaName: "Schema 2" },
];
updateSchemaSelect();