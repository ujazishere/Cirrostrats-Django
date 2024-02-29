// This is where the section starts. Seems like the html up above loads then comes down here.
// Once here
document.addEventListener("DOMContentLoaded", function () {
  // This loads up right away

  console.log("INSIDE SUMMARY BOX");
  var airport = "{{ airport }}";
  var url = "summary_box/" + airport + "/";
  // This is where the data is pulled from the views function data_v. This is the first point of access.
  fetch(url)
    .then(response => response.json())
    .then(data => {
      // data is a variable that pulls in data_v's bulk_flight_deet dictionary
      let bulk_flight_deets = data;
      console.log(bulk_flight_deets);
      let flt_num = bulk_flight_deets.flight_number;
      let registration = bulk_flight_deets.registration;
      let departure_ID = bulk_flight_deets.departure_ID;
      let destination_ID = bulk_flight_deets.destination_ID;
      let departure_gate = bulk_flight_deets.departure_gate;
      let arrival_gate = bulk_flight_deets.arrival_gate;
      let scheduled_departure_time = bulk_flight_deets.scheduled_departure_time;
      let scheduled_arrival_time = bulk_flight_deets.scheduled_arrival_time;
      let scheduled_out = bulk_flight_deets.scheduled_out;
      let scheduled_in = bulk_flight_deets.scheduled_in;
      let estimated_out = bulk_flight_deets.estimated_out;
      let estimated_in = bulk_flight_deets.estimated_in;

      function summary_box(bulk_flight_deets) {
        console.log("here in summary box", departure_ID);

        var summary_box_js = document.getElementById("summary_box_js");

        // this is for flight_num and registration //
        var thead = document.createElement("thead");
        var tr = document.createElement("tr");
        var th = document.createElement("th");
        var span = document.createElement("span");
        var tbody_summary_box = document.createElement("tbody");
        span.className = "small-text";
        span.innerHTML = registration;
        th.innerHTML = flt_num;
        th.colSpan = "2";
        th.appendChild(span);
        tr.appendChild(th);
        thead.appendChild(tr);
        summary_box_js.appendChild(thead);
        summary_box_js.appendChild(tbody_summary_box);

        function tr_td_section(tr_class_name, td1_class_name, td2_class_name, td1_displays, td2_displays) {
          var tr_item = document.createElement("tr");

          var td_spacer_cell1 = document.createElement("td");
          var td_spacer_cell2 = document.createElement("td");

          tr_item.className = tr_class_name;

          td_spacer_cell1.className = td1_class_name;
          td_spacer_cell2.className = td2_class_name;

          td_spacer_cell1.innerHTML = td1_displays;
          td_spacer_cell2.innerHTML = td2_displays;

          tr_item.appendChild(td_spacer_cell1);
          tr_item.appendChild(td_spacer_cell2);

          return tr_item;
        }

        function spacer_section() {
          var spacer_section = tr_td_section(
            (tr_class_name = "spacer-row"),
            (td1_class_name = "spacer-cell"),
            (td2_class_name = "spacer-cell"),
            (td1_displays = "&nbsp;"),
            (td2_displays = "&nbsp;")
          );

          return spacer_section;
        }

        airportID_section = tr_td_section(
          (tr_class_name = ""),
          (td1_class_name = "table-cell"),
          (td2_class_name = "table-cell text-align-right"),
          (td1_displays = departure_ID),
          (td2_displays = destination_ID)
        );
        tbody_summary_box.appendChild(airportID_section);

        tbody_summary_box.appendChild(spacer_section());

        gate_title = tr_td_section(
          (tr_class_name = "info-row"),
          (td1_class_name = "info-cell"),
          (td2_class_name = "info-cell"),
          (td1_displays = "Gate"),
          (td2_displays = "Gate")
        );
        tbody_summary_box.appendChild(gate_title);

        gate_section = tr_td_section(
          (tr_class_name = "gate-row"),
          (td1_class_name = "gate-cell"),
          (td2_class_name = "gate-cell"),
          (td1_displays = departure_gate),
          (td2_displays = arrival_gate)
        );
        tbody_summary_box.appendChild(gate_section);

        tbody_summary_box.appendChild(spacer_section());

        scheduled_section = tr_td_section(
          (tr_class_name = "scheduled-row"),
          (td1_class_name = "scheduled-cell"),
          (td2_class_name = "scheduled-cell"),
          (td1_displays = "Scheduled Local"),
          (td2_displays = "Scheduled Local")
        );
        tbody_summary_box.appendChild(scheduled_section);

        scheduled__row_section = tr_td_section(
          (tr_class_name = "scheduled-time-row"),
          (td1_class_name = "scheduled-time-cell"),
          (td2_class_name = "scheduled-time-cell"),
          (td1_displays = scheduled_departure_time),
          (td2_displays = scheduled_arrival_time)
        );
        tbody_summary_box.appendChild(scheduled__row_section);

        tbody_summary_box.appendChild(spacer_section());

        UTC_section = tr_td_section(
          (tr_class_name = "scheduled-row"),
          (td1_class_name = "scheduled-cell"),
          (td2_class_name = "scheduled-cell"),
          (td1_displays = "UTC"),
          (td2_displays = "UTC")
        );
        tbody_summary_box.appendChild(UTC_section);

        flight_aware_UTC = tr_td_section(
          (tr_class_name = "flight-status-row"),
          (td1_class_name = "flight-status-cell"),
          (td2_class_name = "flight-status-cell"),
          (td1_displays = "STD " + scheduled_out + "<br>" + "ETD " + estimated_out),
          (td2_displays = "STD " + scheduled_in + "<br>" + "ETD " + estimated_in)
        );

        tbody_summary_box.appendChild(flight_aware_UTC);
      }

      // To use the function you have to use this

      summary_box(bulk_flight_deets);
    })
    .catch(error => console.error("Error Console:", error));
});
