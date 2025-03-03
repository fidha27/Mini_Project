document.addEventListener('DOMContentLoaded', function () {
    const toolTableBody = document.getElementById('tool-table-body');
    const addToolBtn = document.getElementById('add-tool-btn');
    const calculateBtn = document.getElementById('calculate-btn');
    const previewSection = document.getElementById('preview-section');
    const previewTableBody = document.querySelector('#preview-table tbody');
    const confirmBtn = document.getElementById('confirm-btn');

    let toolsList = [];
    let previewData = [];

    const coList = JSON.parse(document.getElementById('co-list-data').textContent);
    fetchTools();
    loadSavedTools()
    

     // Fetch available tools
    function fetchTools() {
        fetch('/get-tools-for-course')
            .then(response => response.json())
            .then(data => {
                toolsList = data.tools;
                console.log("Available tools:", toolsList);
            })
            .catch(error => console.error('Error fetching tools:', error));
    }
    // Load saved tool data
    async function loadSavedTools() {
        try {
            const response = await fetch('/get-saved-tool-data');
            const data = await response.json();
            console.log("📌 Raw Saved Tools Data:", data);
            
            
            displayToolRows(data);
        } catch (error) {
            console.error('❌ Error fetching saved config:', error);
        }
    }
    

    function displayToolRows(savedTools) {
        toolTableBody.innerHTML = ''; // Clear existing table data
    
        // Ensure savedTools is an array before checking its length
        if (savedTools.length === 0) {
            console.log("⚠ No saved tools found.");
            return;
        }
    
        console.log("✅ Displaying Saved Tools:", savedTools);
    
        savedTools.forEach(({ tool_name, tool_number, thresholds }) => {
            console.log("➡ Adding row for:", tool_name, tool_number, thresholds);
            addToolRow(tool_name, tool_number, thresholds);
        });
    }
    
    

    function addToolRow(selectedTool = '', selectedNumber = '', thresholdValues = []) {
        const newRow = document.createElement('tr');

        const toolSelect = document.createElement('select');
        toolSelect.classList.add('tool-dropdown');

        const defaultOption = document.createElement('option');
        defaultOption.textContent = 'Select Tool';
        defaultOption.value = '';
        toolSelect.appendChild(defaultOption);

        toolsList.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool.tool_name;
            option.textContent = tool.tool_name;
            if (tool.tool_name === selectedTool) option.selected = true;
            toolSelect.appendChild(option);
        });

        const toolNumberSelect = document.createElement('select');
        toolNumberSelect.classList.add('tool-number-dropdown');

        for (let i = 1; i <= 5; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Tool ${i}`;
            if (i == selectedNumber) option.selected = true;
            toolNumberSelect.appendChild(option);
        }

        newRow.innerHTML = `
            <td></td>
            ${coList.map((co, index) => `<td><input type="number" class="threshold" value="${thresholdValues[index] || ''}" placeholder="Threshold for CO${co}"></td>`).join('')}
            <td><button class="delete-btn">Delete</button></td>
        `;

        const firstTd = newRow.querySelector('td');
        firstTd.appendChild(toolSelect);
        firstTd.appendChild(toolNumberSelect);

        toolTableBody.appendChild(newRow);
    }

    addToolBtn.addEventListener('click', function () {
        addToolRow();
    });

    toolTableBody.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-btn')) {
            e.target.closest('tr').remove();
        }
    });

    calculateBtn.addEventListener('click', function () {
        previewTableBody.innerHTML = '';
        previewSection.classList.remove('hidden');
        previewData = [];

        const rows = toolTableBody.querySelectorAll('tr');
        let columnSums = new Array(coList.length).fill(0);
        let isValid = true;

        rows.forEach(row => {
            const toolSelect = row.querySelector('.tool-dropdown');
            const toolName = toolSelect.value;
            const toolNumberSelect = row.querySelector('.tool-number-dropdown');
            const toolNumber = toolNumberSelect.value;
            const thresholds = Array.from(row.querySelectorAll('.threshold')).map(th => parseFloat(th.value) || 0);

            if (!toolName || !toolNumber) {
                alert('Please select a tool and specify its number.');
                isValid = false;
                return;
            }

            thresholds.forEach((value, index) => columnSums[index] += value);
            previewData.push({ tool_name: toolName, tool_number: toolNumber, thresholds });

            const previewRow = document.createElement('tr');
            previewRow.innerHTML = `
                <td>${toolName} (${toolNumber})</td>
                ${thresholds.map(value => `<td><input type="number" class="preview-threshold" value="${value}"></td>`).join('')}
                <td><button class="delete-preview-btn">Delete</button></td>
            `;
            previewTableBody.appendChild(previewRow);
        });

        if (!isValid) return;

        for (let i = 0; i < columnSums.length; i++) {
            if (columnSums[i] !== 100) {
                alert(`Total threshold for CO${coList[i]} must be 100%. Currently, it is ${columnSums[i]}%.`);
                return;
            }
        }
    });

    confirmBtn.addEventListener('click', function () {
        let updatedData = [];
        let columnSums = new Array(coList.length).fill(0);
        let isValid = true;

        const previewRows = previewTableBody.querySelectorAll('tr');

        previewRows.forEach(row => {
            const toolInfo = row.cells[0].textContent.split(' (');
            const toolName = toolInfo[0];
            const toolNumber = toolInfo[1].replace(')', '');
            const thresholds = Array.from(row.querySelectorAll('.preview-threshold')).map(th => parseFloat(th.value) || 0);

            thresholds.forEach((value, index) => columnSums[index] += value);
            updatedData.push({ tool_name: toolName, tool_number: toolNumber, thresholds });
        });

        for (let i = 0; i < columnSums.length; i++) {
            if (columnSums[i] !== 100) {
                alert(`Total threshold for CO${coList[i]} must be 100%. Currently, it is ${columnSums[i]}%.`);
                isValid = false;
                break;
            }
        }

        if (!isValid) return;

        fetch('/save-tool-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ toolData: updatedData })
        })
        .then(response => response.json())
        .then(() => {
            alert('Configuration saved successfully!');
            showEditButton();
        })
        .catch(error => console.error('Error saving tool data:', error));
    });

    

    previewTableBody.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-preview-btn')) {
            e.target.closest('tr').remove();
        }
    });

    document.getElementById("home-btn").addEventListener("click", function () {
        // Retrieve semester from session storage or a predefined value
        const semester = sessionStorage.getItem("selectedSemester") || "defaultSemester"; 
        window.location.href = `/view_batch/${semester}`;
    });
    
    
});


