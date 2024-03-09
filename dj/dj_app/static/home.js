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
    "Want to know the weather at a particular airport? Look it up.",
  ];

  // Get a random index within the range of the array length
  const randomIndex = Math.floor(Math.random() * h3Contents.length);

  // Get the h3 element
  const randomH3 = document.getElementById("randomH3");

  // Set the content of the h3 element to the randomly chosen content
  randomH3.innerHTML = `
        <svg class="bi me-2" width="16" height="16" fill="currentColor">
          <use xlink:href="#info-fill"/>
        </svg>
        ${h3Contents[randomIndex]}
      `;

  // Add the animation class to make the h3 visible with animation
  randomH3.classList.add("visible");
});
