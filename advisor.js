document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("course-form").addEventListener("submit", function (event) {
      event.preventDefault();

      let subject = document.getElementById("subject").value;
      let teacher = document.getElementById("teacher").value;
      let department = document.getElementById("department").value;

      if (subject && teacher && department) {
          let formData = new FormData();
          formData.append("subject", subject);
          formData.append("teacher", teacher);
          formData.append("department", department);

          fetch("save_course.php", {
              method: "POST",
              body: formData
          })
          .then(response => response.text())
          .then(data => {
              alert(data); // Show success message
              document.getElementById("course-form").reset(); // Reset form
              location.reload(); // Refresh the page
          })
          .catch(error => console.error("Error:", error));
      } else {
          alert("Please fill in all fields before saving.");
      }
  });
  document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("course-mapping-link").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent default <a> behavior
        window.location.href = "courses-mapping.html"; // Redirect to Course Mapping page
    });
});

        

});
