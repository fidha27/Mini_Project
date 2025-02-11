document.addEventListener("DOMContentLoaded", function () {
    const editButtons = document.querySelectorAll(".edit-btn");
    const saveButtons = document.querySelectorAll(".save-btn");

    editButtons.forEach((editBtn, index) => {
        editBtn.addEventListener("click", () => {
            const row = editBtn.closest("tr");
            const advisorName = row.querySelector(".advisor-name");
            const advisorSelect = row.querySelector(".advisor-select");

            // Hide the span, show dropdown and save button
            advisorName.classList.add("hidden");
            advisorSelect.classList.remove("hidden");
            editBtn.classList.add("hidden");
            saveButtons[index].classList.remove("hidden");
        });
    });

    saveButtons.forEach((saveBtn, index) => {
        saveBtn.addEventListener("click", () => {
            const row = saveBtn.closest("tr");
            const advisorName = row.querySelector(".advisor-name");
            const advisorSelect = row.querySelector(".advisor-select");

            // Update advisor name and hide dropdown
            advisorName.textContent = advisorSelect.value;
            advisorName.classList.remove("hidden");
            advisorSelect.classList.add("hidden");
            saveBtn.classList.add("hidden");
            editButtons[index].classList.remove("hidden");
        });
    });
});
