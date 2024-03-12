// This script is for departure/destination expand/collapse animation
function toggleAccordion(contentId) {
  var content = document.getElementById(contentId);
  var tbody = content.querySelector("tbody"); // Select the tbody element inside the content
  
  if (tbody.style.display === "none" || tbody.style.display === "") {
    tbody.style.display = "table-row-group"; // Show the content
  } else {
    tbody.style.display = "none"; // Hide the content
  }
}

document.getElementById("searchButton").addEventListener("click", function(event) {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Show the loading spinner
  document.getElementById("loadingSpinner").style.display = "block";

  // Submit the form after a short delay to allow the loading spinner to be displayed
  setTimeout(function() {
  document.querySelector(".search-form").submit();
  }, 500); // Adjust the delay as needed
  });

  function search() {
    // Hide the button
    document.getElementById("searchButton").style.display = "none";
    
    // Optionally, you might want to show a loading spinner
    document.getElementById("loadingSpinner").style.display = "block";

    // Perform your search operation here
    // For example, submit the form
    document.querySelector('.search-form').submit();
  }