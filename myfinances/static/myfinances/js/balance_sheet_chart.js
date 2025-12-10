document.addEventListener("DOMContentLoaded", function () {
  if (typeof chartData === "undefined") return;

  const canvas = document.getElementById("balanceSheetChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  // Detect dark mode
  const isDarkMode = window.matchMedia &&
                     window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Text and grid colors depending on mode
  const textColor = isDarkMode ? "#f8f9fa" : "#212529"; // light vs dark
  const gridColor = isDarkMode ? "#444" : "#ccc";

  // Dataset colors (bold but visible in both modes)
  const labelColors = {
    Income: "#1e7e34",      // dark green
    Expense: "#c82333",     // dark red
    Asset: "#004085",       // dark blue
    Liability: "#7a3e00",   // dark brown/orange
    Equity: "#4b0082",      // indigo
    Other: "#6c757d"        // medium gray
  };

  const allMonths = Array.from(
    new Set(Object.values(chartData).map(labelObj => Object.keys(labelObj)).flat())
  ).sort();

const datasets = Object.keys(chartData).map(label => ({
  label: label,
  data: allMonths.map(month => {
    const val = chartData[label][month] || 0;
    // Keep Income as-is, flip all others to positive
    return label === "Income" ? val : Math.abs(val);
  }),
  borderColor: labelColors[label] || textColor,
  backgroundColor: labelColors[label] || textColor,
  fill: false,
  tension: 0.25
}));

// Add a new dataset for Income - Expense
const incomeExpenseDiff = {
  label: "Income - Expense",
  data: allMonths.map(month => {
    const income = chartData["Income"] ? (chartData["Income"][month] || 0) : 0;
    const expense = chartData["Expense"] ? (chartData["Expense"][month] || 0) : 0;
    return income - Math.abs(expense); // subtract expense (converted to positive)
  }),
  borderColor: "#ff9900",   // orange line for visibility
  backgroundColor: "#ff9900",
  borderDash: [5, 5],       // dashed line to distinguish
  fill: false,
  tension: 0.25
};

// Push the difference dataset into the list
datasets.push(incomeExpenseDiff);

  new Chart(ctx, {
    type: "line",
    data: {
      labels: allMonths,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: "Monthly Totals by Label",
          color: textColor
        },
        legend: {
          position: "bottom",
          labels: {
            color: textColor
          }
        },
        annotation: {
          annotations: {
            baseline: {
              type: "line",
              yMin: 0,
              yMax: 0,
              borderColor: textColor,
              borderWidth: 2,
              label: {
                enabled: true,
                content: "Zero baseline",
                color: textColor,
                backgroundColor: isDarkMode ? "#343a40" : "#e9ecef"
              }
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Month",
            color: textColor
          },
          ticks: {
            color: textColor,
            callback: function (value) {
              const raw = this.getLabelForValue(value);
              const [year, month] = raw.split("-");
              const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
              return monthNames[parseInt(month, 10) - 1] + "/" + year;
            }
          },
          grid: {
            color: gridColor
          }
        },
        y: {
          title: {
            display: true,
            text: "Total Amount",
            color: textColor
          },
          ticks: {
            color: textColor,
            callback: function (value) {
              return "$" + value.toLocaleString();
            }
          },
          grid: {
            color: gridColor
          }
        }
      }
    }
  });
});