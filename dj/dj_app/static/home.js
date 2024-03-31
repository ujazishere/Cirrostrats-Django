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


  const scrollingTexts = document.querySelectorAll('.scrolling-text');
  let currentTextIndex = 0;

  function rotateText() {
      const currentText = scrollingTexts[currentTextIndex];
      const nextTextIndex = (currentTextIndex + 1) % scrollingTexts.length;
      const nextText = scrollingTexts[nextTextIndex];

      currentText.classList.remove('active');
      currentText.classList.add('hidden');

      nextText.classList.remove('hidden');
      nextText.classList.add('active');

      currentTextIndex = nextTextIndex;
  }

  setInterval(rotateText, 8000); // Change text every 3 seconds



function search() {
  // Hide the button
  document.getElementById("searchButton").style.display = "none";
  
  // Optionally, you might want to show a loading spinner
  document.getElementById("loadingSpinner").style.display = "block";

  // Perform your search operation here
  // For example, submit the form
  document.querySelector('.search-form').submit();
}