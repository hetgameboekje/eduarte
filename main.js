function parseAndPost() {
    const inputHTML = document.getElementById("htmlInput").value;
    const parser = new DOMParser();
    const doc = parser.parseFromString(inputHTML, "text/html");

    let databaseRows = [];

    const weekContainers = doc.querySelectorAll(".content--part");

    weekContainers.forEach(container => {
        const weekHeader = container.querySelector(".is-header");
        if (!weekHeader) return;

        const weekSpans = weekHeader.querySelectorAll("span");
        const startDay = weekSpans[0]?.textContent.trim();
        const endDay = weekSpans[1]?.textContent.trim();
        const weekNumber = weekSpans[3]?.textContent.trim(); // Weeknummer
        const givenYear = parseInt(weekSpans[4]?.textContent.trim(), 10); // Gegeven jaartal in HTML

        if (!startDay || !endDay || !weekNumber || isNaN(givenYear)) return;

        const startDate = parseDate(startDay, givenYear);
        const weekPlanElements = container.querySelectorAll(".week-plan");

        weekPlanElements.forEach((weekPlan, index) => {
            const dayName = weekPlan.querySelector(".week-plan--title")?.textContent.trim();
            const taskElement = weekPlan.querySelector(".task p span");
            const durationElement = weekPlan.querySelector(".task--summary-meta span");

            let rawDuration = durationElement ? durationElement.textContent.trim() : "0u";
            let durationInSeconds = convertToSeconds(rawDuration);

            if (durationInSeconds > 0) {
                databaseRows.push({
                    date: formatDate(startDate, index + 1),
                    week_number: parseInt(weekNumber, 10),
                    day: dayName,
                    task: taskElement ? taskElement.textContent.trim() : "Geen taak",
                    duration_seconds: durationInSeconds
                });
            }
        });
    });

    if (databaseRows.length > 0) {
        sendToServer(databaseRows);
    } else {
        document.getElementById("output").textContent = "Geen relevante data om te verzenden.";
    }
}

function sendToServer(data) {
    fetch("chatgpt8.html", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById("output").textContent = "Server Response: " + JSON.stringify(result, null, 4);
    })
    .catch(error => {
        document.getElementById("output").textContent = "Fout bij verzenden: " + error;
    });
}

function parseDate(dayMonth, givenYear) {
    const months = {
        "januari": 0, "februari": 1, "maart": 2, "april": 3, "mei": 4, "juni": 5,
        "juli": 6, "augustus": 7, "september": 8, "oktober": 9, "november": 10, "december": 11
    };
    const parts = dayMonth.split(" ");
    if (parts.length !== 2) return null;

    const day = parseInt(parts[0], 10);
    const month = months[parts[1].toLowerCase()];
    if (isNaN(day) || month === undefined) return null;

    return new Date(givenYear, month, day);
}

function formatDate(startDate, dayOffset) {
    let date = new Date(startDate);
    date.setDate(startDate.getDate() + dayOffset);
    return date.toISOString().split("T")[0];
}

function convertToSeconds(durationText) {
    let hours = 0;
    let minutes = 0;

    const hourMatch = durationText.match(/(\d+)u/);
    const minuteMatch = durationText.match(/(\d+)m/);

    if (hourMatch) {
        hours = parseInt(hourMatch[1], 10);
    }

    if (minuteMatch) {
        minutes = parseInt(minuteMatch[1], 10);
    }

    return (hours * 3600) + (minutes * 60);
}