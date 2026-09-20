document.addEventListener("DOMContentLoaded", function () {

    const rawJson = document.getElementById("therapist-profitability-json")?.textContent;

    let data = null;

    try {
        data = JSON.parse(rawJson);
    } catch (err) {
        console.error("❌ Failed to parse therapist profitability JSON:", err);
        return;
    }

    if (!data || data.length === 0) {
        console.error("❌ therapist_profitability is empty — cannot render chart.");
        return;
    }

    // Sort by month so lines appear correctly
    data.sort((a, b) => a.period_month.localeCompare(b.period_month));

    // Extract unique months
    const months = [...new Set(data.map(row => row.period_month))];

    // Extract unique therapist initials
    const therapists = [...new Set(data.map(row => row.employee_initials))];

    // Assign colors per therapist
    const palette = [
        "#5cb85c", "#d9534f", "#5bc0de", "#f0ad4e",
        "#9370DB", "#FF7F50", "#20B2AA", "#708090",
        "#8B0000", "#2E8B57", "#1E90FF"
    ];

    const colorMap = {};
    therapists.forEach((t, idx) => {
        colorMap[t] = palette[idx % palette.length];
    });

    // Build datasets: one per therapist
    const datasets = therapists.map(initial => {
        return {
            label: initial,
            data: months.map(month => {
                const row = data.find(r => r.period_month === month && r.employee_initials === initial);
                return row ? row.therapist_profit : null;  // null keeps alignment
            }),
            borderColor: colorMap[initial],
            backgroundColor: colorMap[initial] + "33",
            borderWidth: 2,
            tension: 0.3,
            spanGaps: true
        };
    });

    const canvas = document.getElementById("therapist_profit_chart");
    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: months,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.raw?.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: value => "$" + value.toLocaleString()
                    },
                    grid: {
                        color: (ctx) => ctx.tick.value === 0 ? "#000" : "#ddd",
                        lineWidth: (ctx) => ctx.tick.value === 0 ? 2 : 1
                    }

                },
            }
        }
    });

});
