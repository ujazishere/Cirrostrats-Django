// Add event listener to the search button
document
  .getElementById("searchButton")
  .addEventListener("click", function (event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Show the loading spinner
    document.getElementById("loadingSpinner").style.display = "block";

    // Submit the form after a short delay to allow the loading spinner to be displayed
    setTimeout(function () {
      document.querySelector(".search-form").submit();
    }, 10); // Adjust the delay as needed
  });




  window.addEventListener("load", function () {
    // Array of h3 tag contents
    const h3Contents = [
      "Want to know if your gate is occupied in Newark? Look up the gate. For example: 71x",
      "Hit the live map to see the HD weather radar",
      "Want to know the weather at a particular airport? Look it up the identifier. E.g: KEWR",
    ];

    // Get the h3 element
    const randomH3 = document.getElementById("randomH3");

    // Get the last displayed index from local storage or default to 0
    let index = parseInt(localStorage.getItem("lastDisplayedIndex")) || 0;

    function displayNextText() {
      // Set the content of the h3 element to the next content in the array
      randomH3.innerHTML = `
        <svg class="bi me-2" width="16" height="16" fill="currentColor">
          <use xlink:href="#info-fill"/>
        </svg>
        ${h3Contents[index]}
      `;

      // Add the animation class to make the h3 visible with animation
      randomH3.classList.add("visible");

      // Increment the index for next content
      index++;

      // If reached the end of content, reset index to 0
      if (index >= h3Contents.length) {
        index = 0;
      }

      // Store the index in local storage
      localStorage.setItem("lastDisplayedIndex", index.toString());
    }

    // Initial display
    displayNextText();


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