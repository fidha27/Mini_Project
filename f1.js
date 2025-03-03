document.addEventListener("DOMContentLoaded", function () {
    // Fetch user details from the URL or session
    const urlParams = new URLSearchParams(window.location.search);
    const facultyName = urlParams.get("facultyName");
    const batchName = urlParams.get("batchName");
    const department = urlParams.get("department");
  
    document.addEventListener("DOMContentLoaded", function () {
        const advisorName = document.getElementById("advisor-name").textContent;
        const batchName = document.getElementById("batch-name").textContent;
        const department = document.getElementById("department").textContent;
    
        if (!advisorName || !batchName || !department) {
            alert("Batch details not found!");
        }
    });

  
    // Sidebar navigation
    const sidebarLinks = document.querySelectorAll("#sidebar ul li a");
    sidebarLinks.forEach(link => {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        const page = link.textContent.trim().toLowerCase();
  
        // Redirect to the respective page with user details
        switch (page) {
          case "co outcomes":  // ✅ Added this case
              window.location.href = `/course_outcome?facultyName=${facultyName}&batchName=${batchName}&department=${department}`;
              break;
          case "co attainment":
              window.location.href = `/co-attainment?facultyName=${facultyName}&batchName=${batchName}&department=${department}`;
              break;
          case "co calculation":
              window.location.href = `/external-marks?facultyName=${facultyName}&batchName=${batchName}&department=${department}`;
              break;
          case "tool selection":
              window.location.href = `/tool-selection?facultyName=${facultyName}&batchName=${batchName}&department=${department}`;
              break;
              case "mark upload":
                window.location.href = `/mark-upload?facultyName=${facultyName}&batchName=${batchName}&department=${department}`;
                break;
          default:
              alert("Page not found!");
      }

      });
    });
  
    document.addEventListener("DOMContentLoaded", function () {
        const courseCode = "{{ courses[0][0] }}"; // Get the course code from the template
        const matrixContainer = document.getElementById("matrix-container");
        const matrixBody = document.getElementById("matrix-body");
    
        // Fetch CO-PO matrix data
        fetch(`/get-matrix?course_code=${courseCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    matrixContainer.classList.remove("hidden");
                    matrixBody.innerHTML = ""; // Clear existing rows
    
                    data.forEach(co => {
                        let row = `<tr><td>${co.co_number}</td>`;
                        for (let i = 1; i <= 10; i++) {
                            row += `<td><input type="text" placeholder="0-3"></td>`;
                        }
                        row += `</tr>`;
                        matrixBody.innerHTML += row;
                    });
                }
            })
            .catch(error => console.error("Error fetching CO-PO matrix:", error));
    });
    document.getElementById("view-batch-btn").addEventListener("click", function () {
      const course = document.getElementById("course-dropdown").value;
      const batch = document.getElementById("batch-dropdown").value;
  
      if (!course || !batch) {
          alert("Please select a course and batch.");
          return;
      }
  
      fetch("/select_course_batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ course_name: course, batch: batch })
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              console.log("DEBUG: Course & Batch stored in session.");
              setTimeout(() => {
                  window.location.href = "/course_outcome";
              }, 500);
          } else {
              alert("Failed to select course & batch.");
          }
      });
  });
  
    
  });

  document.addEventListener("DOMContentLoaded", function() {
    console.log("Fetching CO-PO Matrix...");

    fetch('/get_matrix')  // Fetch stored matrix from Flask
        .then(response => response.json())
        .then(data => {
            console.log("Matrix fetched:", data);
            
            if (data.length > 0) {
                document.getElementById("matrix-container").classList.remove("hidden"); 
                const matrixBody = document.getElementById("matrix-body");
                matrixBody.innerHTML = ""; // Clear any existing rows

                data.forEach(co => {
                    let row = `<tr><td>${co.co_number}</td>`;

                    for (let i = 1; i <= 12; i++) {
                        let value = co.po_correlations[`PO${i}`] || '-';  // Show stored value or '-'
                        row += `<td>${value}</td>`;
                    }
                    
                    row += `</tr>`;
                    matrixBody.innerHTML += row;
                });
            }
        })
        .catch(error => console.error("Error fetching CO-PO matrix:", error));
});
  