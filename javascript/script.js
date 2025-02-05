document.getElementById("htmlForm").addEventListener("submit", function (event) {
  event.preventDefault();

  const htmlInput = document.getElementById("htmlInput").value;
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlInput, "text/html");

  const jsonOutput = extractWeekData(doc);
  document.getElementById("jsonOutput").textContent = JSON.stringify(jsonOutput, null, 2);
});

function extractWeekData(doc) {
  const weeks = [];
  const weekElements = doc.querySelectorAll(".is-header");

  weekElements.forEach(weekElement => {
      const dateSpans = weekElement.querySelectorAll("span");
      const weekNumberSpan = weekElement.querySelector(".is-soft");

      let weekNumber = "";
      let year = "";
      if (weekNumberSpan) {
          const weekText = weekNumberSpan.textContent.trim();
          const matches = weekText.match(/Week (\d+)( (\d{4}))?/);
          if (matches) {
              weekNumber = matches[1];
              year = matches[3] || new Date().getFullYear().toString();
          }
      }

      const startDateStr = dateSpans[0]?.textContent.trim() || "";
      const endDateStr = dateSpans[1]?.textContent.trim() || "";

      if (!startDateStr || !endDateStr) return; // Geen geldige data

      const startDate = parseDate(startDateStr, parseInt(year));
      const endDate = parseDate(endDateStr, parseInt(year));

      if (!startDate || !endDate) return;

      const days = generateWeekDays(startDate);
      
      weeks.push({
          dateRange: {
              start: startDateStr,
              end: endDateStr
          },
          weekNumber,
          year,
          days
      });
  });

  return weeks;
}

function parseDate(dateStr, year) {
  const months = {
      "januari": 0, "februari": 1, "maart": 2, "april": 3,
      "mei": 4, "juni": 5, "juli": 6, "augustus": 7,
      "september": 8, "oktober": 9, "november": 10, "december": 11
  };

  const dateParts = dateStr.split(" ");
  if (dateParts.length < 2) return null;

  const day = parseInt(dateParts[0], 10);
  const month = months[dateParts[1].toLowerCase()];

  if (isNaN(day) || month === undefined) return null;

  return new Date(year, month, day);
}

function generateWeekDays(startDate) {
  const dayNames = ["ma", "di", "wo", "do", "vr", "za", "zo"];
  return dayNames.map((name, index) => {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + index);

      return {
          name,
          date: date.toISOString().split("T")[0], // YYYY-MM-DD
          hours: "0u",
          remarks: "No log for this day."
      };
  });
}
