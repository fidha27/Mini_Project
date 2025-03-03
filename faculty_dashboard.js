document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/faculty")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Faculty not found or unauthorized access.");
                document.getElementById("faculty-name").textContent = "Faculty Not Found";
                return;
            }

            // Update faculty name and advisor status
            document.getElementById("faculty-name").textContent = data.name;
            document.getElementById("advisor-status").textContent = `Advisor Status: ${data.is_advisor ? "Yes" : "No"}`;

            // Show advisor tab if the faculty is an advisor
            if (data.is_advisor) {
                document.getElementById("advisor-tab").style.display = "block";
            }

            // Ensure teaching batches are displayed
            const batchContainer = document.getElementById("teaching-batches");
            batchContainer.innerHTML = ""; // Clear previous content

            if (data.teaching_batches.length > 0) {
                data.teaching_batches.forEach(batch => {
                    let batchCard = document.createElement("div");
                    batchCard.classList.add("batch-card");

                    batchCard.innerHTML = `
                        <h3>Batch ${batch.batch}</h3>
                        <p>Course: ${batch.course_title}</p>
                        <a href="/view_batch/${batch.batch}" class="view-batch-btn">View Batch</a>
                    `;

                    batchContainer.appendChild(batchCard);
                });
            } else {
                batchContainer.innerHTML = "<p>No assigned batches found.</p>";
            }
        })
        .catch(error => console.error("Error fetching faculty data:", error));
});


document.addEventListener("DOMContentLoaded", function () {
    // Select all "View Batch" buttons
    const viewBatchButtons = document.querySelectorAll(".view-batch-btn");

    viewBatchButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default navigation

            const semester = this.getAttribute("href"); // Get URL from the button
            console.log("Navigating to:", semester);

            // Navigate smoothly to the batch dashboard
            window.location.href = semester;
        });
    });

    // Optional: Add hover effects for better UX
    const batchCards = document.querySelectorAll(".batch-card");

    batchCards.forEach(card => {
        card.addEventListener("mouseover", function () {
            this.style.transform = "scale(1.05)";
            this.style.transition = "0.3s ease-in-out";
        });

        card.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
        });
    });

    // Optional: Filter batches (if you add a search/filter input)
    const searchInput = document.getElementById("batch-search");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const searchText = searchInput.value.toLowerCase();
            batchCards.forEach(card => {
                const courseName = card.querySelector("p").textContent.toLowerCase();
                if (courseName.includes(searchText)) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }
});


function viewBatch(courseCode) {
    alert(`Navigating to batch ${courseCode}`);
    // Implement navigation to batch details page
}

