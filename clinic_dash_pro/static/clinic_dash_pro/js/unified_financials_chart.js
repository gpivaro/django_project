// clinic_dash_pro\static\clinic_dash_pro\js\unified_financials_chart.js

document.addEventListener("DOMContentLoaded", function () {

    console.log("📊 Unified Financials Chart Loaded");

    const rawJson = document.getElementById("unified-financials-json")?.textContent;

    let data = null;

    try {
        data = JSON.parse(rawJson);
    } catch (err) {
        console.error("❌ Failed to parse unified financials JSON:", err);
        return;
    }

    if (!data || data.length === 0) {
        console.error("❌ unified_financials is empty — cannot render chart.");
        return;
    }

    const months = data.map(row => row.period_month);
    const revenue = data.map(row => row.revenue);
    const payroll = data.map(row => row.payroll);
    const operational = data.map(row => row.operational_total);
    const net = data.map(row => row.real_profit);

    const canvas = document.getElementById("unified_financials_chart");
    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: months,
            datasets: [
                {
                    label: "Revenue",
                    data: revenue,
                    borderColor: "#5cb85c",
                    backgroundColor: "rgba(92,184,92,0.2)",
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "Payroll",
                    data: payroll,
                    borderColor: "#d9534f",
                    backgroundColor: "rgba(217,83,79,0.2)",
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "Operational",
                    data: operational,
                    borderColor: "#5bc0de",
                    backgroundColor: "rgba(91,192,222,0.2)",
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "Net Income",
                    data: net,
                    borderColor: "#f0ad4e",
                    backgroundColor: "rgba(240,173,78,0.2)",
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
                        callback: value => "$" + value.toLocaleString()
                    },
                    grid: {
                        color: (ctx) => ctx.tick.value === 0 ? "#000" : "#ddd",
                        lineWidth: (ctx) => ctx.tick.value === 0 ? 2 : 1
                    }

                }
            },
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.raw.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });

    console.log("✅ Unified Financials Chart rendered");
});
