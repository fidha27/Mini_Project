document.addEventListener('DOMContentLoaded', function () {
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
                    {% for faculty in faculties %}
                    <option value="{{ faculty.name }}">{{ faculty.name }}</option>
                    {% endfor %}
                </select>
            </td>
            <td>
                <button class="save-btn">Save</button>
                <button class="delete-btn">Delete</button>
            </td>
        `;
        advisorTable.querySelector('tbody').appendChild(newRow);

        // Attach event listeners to the new row
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
                            {% for faculty in faculties %}
                            <option value="{{ faculty.name }}">{{ faculty.name }}</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td>
                        <button class="edit-btn">Edit</button>
                        <button class="save-btn hidden">Save</button>
                        <button class="delete-btn">Delete</button>
                    </td>
                `;

                // Reattach event listeners
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
        const batchId = row.getAttribute('data-batch-id');

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
                    {% for faculty in faculties %}
                    <option value="{{ faculty.name }}">{{ faculty.name }}</option>
                    {% endfor %}
                </select>
            </td>
            <td>
                <select class="schema-select">
                    {% for schema in schemas %}
                    <option value="{{ schema.schema_name }}">{{ schema.schema_name }}</option>
                    {% endfor %}
                </select>
            </td>
            <td>
                <select class="course-select" multiple>
                    {% for course in courses %}
                    <option value="{{ course.code }}">{{ course.title }}</option>
                    {% endfor %}
                </select>
            </td>
            <td>
                <button class="save-mc-btn">Save</button>
                <button class="delete-mc-btn">Delete</button>
            </td>
        `;
        moduleTable.querySelector('tbody').appendChild(newRow);

        // Attach event listeners to the new row
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
                            {% for faculty in faculties %}
                            <option value="{{ faculty.name }}">{{ faculty.name }}</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td>
                        <select class="schema-select">
                            {% for schema in schemas %}
                            <option value="{{ schema.schema_name }}">{{ schema.schema_name }}</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td>
                        <select class="course-select" multiple>
                            {% for course in courses %}
                            <option value="{{ course.code }}">{{ course.title }}</option>
                            {% endfor %}
                        </select>
                    </td>
                    <td>
                        <button class="edit-mc-btn">Edit</button>
                        <button class="save-mc-btn hidden">Save</button>
                        <button class="delete-mc-btn">Delete</button>
                    </td>
                `;

                // Reattach event listeners
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
        const moduleName = row.getAttribute('data-module-id');

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
