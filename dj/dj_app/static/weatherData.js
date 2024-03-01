// This is where the section starts. Seems like the html up above loads then comes down here.
// Once here

document.addEventListener("DOMContentLoaded", function () {
  // This loads up right away

  const url = `weather_data/{{ airport }}/`;
  // This is where the data is pulled from the views function data_v. This is the first point of access.

  fetch(url)
    .then(response => response.json())
    .then(data => {
      // data is a variable that pulls in data_v's bulk_flight_deet dictionary
      // weather_data is the dictionary provided from views.py essentially a type of
      // bulk_flight_deets.
      const weather_data = data.dep_weather;
      function createWeatherRows(weather_data, weather_origin) {
        var tableBody = document.getElementById(weather_origin);
        Object.entries(weather_data).forEach(([weather_key, weather_value]) => {
          // console.log('in func')
          var row = document.createElement("tr");
          var cell = document.createElement("td");
          let zt = weather_value[0];
          let actual_data = weather_value[1];
          // The first section- has zulu time and type of weather
          // console.log(zt,actual_data)
          cell.innerHTML = `${weather_key} <span class="small-text">${zt}</span>`;
          row.appendChild(cell);
          tableBody.appendChild(row);
          // This is the second section - has the weather itself
          var row = document.createElement("tr");
          var cellMessage = document.createElement("td");
          cellMessage.style.textAlign = "left";
          cellMessage.style.fontFamily = "Menlo, monospace";
          cellMessage.innerHTML = actual_data;
          row.appendChild(cellMessage);
          tableBody.appendChild(row);
        });
      }
      // departure weather calls
      createWeatherRows(weather_data, "weather_DataBody_departure");
      // destination weather calls
      createWeatherRows(weather_data, "weather_DataBody_destination");
    })
    .catch(error => console.error("Error Console:", error));
});
