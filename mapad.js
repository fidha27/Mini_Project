document.addEventListener('DOMContentLoaded', function () {
    // Use the data passed from Flask
    const faculties = window.faculties || [];
    const schemas = window.schemas || [];
    const courses = window.courses || [];

    console.log('Faculties:', faculties); // Debugging
    console.log('Schemas:', schemas);     // Debugging
    console.log('Courses:', courses);    // Debugging

    // Map Advisor Logic
    const addBatchBtn = document.getElementById('add-batch-btn');
    const advisorTable = document.getElementById('advisor-table');

    // Add Batch Row
    addBatchBtn.addEventListener('click', function () {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" class="new-batch-id" placeholder="Enter Batch ID"></td>
            <td>
                <select class="advisor-select">
                    ${faculties.map(faculty => `<option value="${faculty.name}">${faculty.name}</option>`).join('')}
                </select>
            </td>
            <td>
                <button class="save-btn">Save</button>
                <button class="delete-btn">Delete</button>
            </td>
        `;
        advisorTable.appendChild(newRow);

        // Reattach event listeners for the new row
        const saveBtn = newRow.querySelector('.save-btn');
        const deleteBtn = newRow.querySelector('.delete-btn');

        saveBtn.addEventListener('click', saveBatchHandler);
        deleteBtn.addEventListener('click', deleteBatchHandler);
    });

    // Save Batch Handler
    function saveBatchHandler() {
        const row = this.closest('tr');
        const batchId = row.querySelector('.new-batch-id').value;
        const advisorSelect = row.querySelector('.advisor-select');
        const newAdvisor = advisorSelect.value;

        fetch('/add_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                batch_id: batchId,
                advisor_name: newAdvisor
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Batch added successfully') {
                row.innerHTML = `
                    <td>${batchId}</td>
                    <td>
                        <span class="advisor-name">${newAdvisor}</span>
                        <select class="advisor-select hidden">
                            ${faculties.map(faculty => `<option value="${faculty.name}">${faculty.name}</option>`).join('')}
                        </select>
                    </td>
                    <td>
                        <button class="edit-btn" data-batch-id="${batchId}">Edit</button>
                        <button class="save-btn hidden" data-batch-id="${batchId}">Save</button>
                        <button class="delete-btn" data-batch-id="${batchId}">Delete</button>
                    </td>
                `;

                // Reattach event listeners for the new buttons
                const editBtn = row.querySelector('.edit-btn');
                const saveBtn = row.querySelector('.save-btn');
                const deleteBtn = row.querySelector('.delete-btn');

                editBtn.addEventListener('click', editBatchHandler);
                saveBtn.addEventListener('click', saveBatchHandler);
                deleteBtn.addEventListener('click', deleteBatchHandler);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Edit Batch Handler
    function editBatchHandler() {
        const row = this.closest('tr');
        const advisorNameSpan = row.querySelector('.advisor-name');
        const advisorSelect = row.querySelector('.advisor-select');
        const saveButton = row.querySelector('.save-btn');

        advisorNameSpan.classList.add('hidden');
        advisorSelect.classList.remove('hidden');
        this.classList.add('hidden');
        saveButton.classList.remove('hidden');
    }

    // Delete Batch Handler
    function deleteBatchHandler() {
        const row = this.closest('tr');
        const batchId = this.getAttribute('data-batch-id');

        fetch('/delete_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                batch_id: batchId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Batch deleted successfully') {
                row.remove();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Map Module Coordinator Logic
    const addModuleBtn = document.getElementById('add-module-btn');
    const moduleTable = document.getElementById('module-table');

    // Add Module Row
    addModuleBtn.addEventListener('click', function () {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" class="new-module-name" placeholder="Enter Module Name"></td>
            <td>
                <select class="mc-select">
                    ${faculties.map(faculty => `<option value="${faculty.name}">${faculty.name}</option>`).join('')}
                </select>
            </td>
            <td>
                <select class="schema-select">
                    ${schemas.map(schema => `<option value="${schema.schema_name}">${schema.schema_name}</option>`).join('')}
                </select>
            </td>
            <td>
                <select class="course-select" multiple>
                    ${courses.map(course => `<option value="${course.details.code}">${course.details.title}</option>`).join('')}
                </select>
            </td>
            <td>
                <button class="save-mc-btn">Save</button>
                <button class="delete-mc-btn">Delete</button>
            </td>
        `;
        moduleTable.appendChild(newRow);

        // Reattach event listeners for the new row
        const saveMcBtn = newRow.querySelector('.save-mc-btn');
        const deleteMcBtn = newRow.querySelector('.delete-mc-btn');

        saveMcBtn.addEventListener('click', saveModuleHandler);
        deleteMcBtn.addEventListener('click', deleteModuleHandler);
    });

    // Save Module Handler
    function saveModuleHandler() {
        const row = this.closest('tr');
        const moduleName = row.querySelector('.new-module-name').value;
        const mcSelect = row.querySelector('.mc-select');
        const newMcName = mcSelect.value;
        const schemaSelect = row.querySelector('.schema-select');
        const schemaName = schemaSelect.value;
        const courseSelect = row.querySelector('.course-select');
        const selectedCourses = Array.from(courseSelect.selectedOptions).map(option => option.value);

        fetch('/add_module', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                module_name: moduleName,
                mc_name: newMcName,
                schema_name: schemaName,
                courses: selectedCourses
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Module added successfully') {
                row.innerHTML = `
                    <td>${moduleName}</td>
                    <td>
                        <span class="mc-name">${newMcName}</span>
                        <select class="mc-select hidden">
                            ${faculties.map(faculty => `<option value="${faculty.name}">${faculty.name}</option>`).join('')}
                        </select>
                    </td>
                    <td>
                        <select class="schema-select">
                            ${schemas.map(schema => `<option value="${schema.schema_name}">${schema.schema_name}</option>`).join('')}
                        </select>
                    </td>
                    <td>
                        <select class="course-select" multiple>
                            ${courses.map(course => `<option value="${course.details.code}">${course.details.title}</option>`).join('')}
                        </select>
                    </td>
                    <td>
                        <button class="edit-mc-btn" data-module-id="${moduleName}">Edit</button>
                        <button class="save-mc-btn hidden" data-module-id="${moduleName}">Save</button>
                        <button class="delete-mc-btn" data-module-id="${moduleName}">Delete</button>
                    </td>
                `;

                // Reattach event listeners for the new buttons
                const editMcBtn = row.querySelector('.edit-mc-btn');
                const saveMcBtn = row.querySelector('.save-mc-btn');
                const deleteMcBtn = row.querySelector('.delete-mc-btn');

                editMcBtn.addEventListener('click', editModuleHandler);
                saveMcBtn.addEventListener('click', saveModuleHandler);
                deleteMcBtn.addEventListener('click', deleteModuleHandler);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Edit Module Handler
    function editModuleHandler() {
        const row = this.closest('tr');
        const mcNameSpan = row.querySelector('.mc-name');
        const mcSelect = row.querySelector('.mc-select');
        const saveMcBtn = row.querySelector('.save-mc-btn');

        mcNameSpan.classList.add('hidden');
        mcSelect.classList.remove('hidden');
        this.classList.add('hidden');
        saveMcBtn.classList.remove('hidden');
    }

    // Delete Module Handler
    function deleteModuleHandler() {
        const row = this.closest('tr');
        const moduleName = this.getAttribute('data-module-id');

        fetch('/delete_module', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                module_name: moduleName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Module deleted successfully') {
                row.remove();
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
