// clinic_dash_pro\static\clinic_dash_pro\js\expenses_monthly_yoy_chart.js


document.addEventListener("DOMContentLoaded", function () {

    console.log("📊 YOY Chart JS Loaded");

    const rawJson = document.getElementById("report-data-json")?.textContent;

    console.log("Raw JSON from template:", rawJson);

    let reportData = null;

    try {
        reportData = JSON.parse(rawJson);
        console.log("Parsed reportData:", reportData);
    } catch (err) {
        console.error("❌ JSON.parse failed:", err);
    }

    if (!reportData || reportData.length === 0) {
        console.error("❌ reportData is empty or null — chart cannot render.");
        return;
    }

    // Extract months and values
    const months = reportData.map(row => row.period_month);
    const expenses = reportData.map(row => row.expense_amount);
    const assets = reportData.map(row => row.asset_amount);
    const combined = reportData.map(row => row.operational_total);

    console.log("Months:", months);
    console.log("Expenses:", expenses);
    console.log("Assets:", assets);
    console.log("Combined:", combined);

    const canvas = document.getElementById('expenses_monthly_yoy_chart');

    if (!canvas) {
        console.error("❌ Canvas element not found!");
        return;
    }

    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Expenses',
                    data: expenses,
                    borderColor: '#d9534f',
                    backgroundColor: 'rgba(217,83,79,0.2)',
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Assets',
                    data: assets,
                    borderColor: '#5bc0de',
                    backgroundColor: 'rgba(91,192,222,0.2)',
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: 'Combined',
                    data: combined,
                    borderColor: '#5cb85c',
                    backgroundColor: 'rgba(92,184,92,0.2)',
                    borderWidth: 2,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    ticks: {
                        callback: value => '$' + value.toLocaleString()
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.raw;
                            return context.dataset.label + ': $' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });

    console.log("✅ Chart rendered successfully");
});
