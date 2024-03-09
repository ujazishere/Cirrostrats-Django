document.getElementById("searchButton").addEventListener("click", function (event) {
  // Prevent the default form submission behavior
  event.preventDefault();

  // Show the loading spinner
  document.getElementById("loadingSpinner").style.display = "block";

  // Submit the form after a short delay to allow the loading spinner to be displayed
  setTimeout(function () {
    document.querySelector(".search-form").submit();
  }, 500); // Adjust the delay as needed
});