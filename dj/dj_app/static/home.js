document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.querySelector('.search-form');
  const searchButton = document.getElementById("searchButton");
  const loadingSpinner = document.getElementById("loadingSpinner");

  searchForm.addEventListener('submit', function(event) {
      event.preventDefault();
      performSearch();
  });

  searchButton.addEventListener("click", function (event) {
      event.preventDefault();
      performSearch();
  });

  function performSearch() {
      searchButton.style.display = "none";
      loadingSpinner.style.display = "block";
      setTimeout(function () {
          searchForm.submit();
      }, 10);
  }

  const scrollingTexts = document.querySelectorAll('.scrolling-text');
  let currentTextIndex = parseInt(localStorage.getItem('currentTextIndex')) || 0;
  currentTextIndex = (currentTextIndex + 1) % scrollingTexts.length;
  localStorage.setItem('currentTextIndex', currentTextIndex);

  scrollingTexts.forEach((text, index) => {
      if (index === currentTextIndex) {
          text.classList.add('active');
          text.classList.remove('hidden');
      } else {
          text.classList.remove('active');
          text.classList.add('hidden');
      }
  });

  function rotateText() {
      const currentText = scrollingTexts[currentTextIndex];
      const nextTextIndex = (currentTextIndex + 1) % scrollingTexts.length;
      const nextText = scrollingTexts[nextTextIndex];
      currentText.classList.remove('active');
      currentText.classList.add('hidden');
      nextText.classList.remove('hidden');
      nextText.classList.add('active');
      currentTextIndex = nextTextIndex;
      localStorage.setItem('currentTextIndex', currentTextIndex);
  }

  setInterval(rotateText, 8000);
});