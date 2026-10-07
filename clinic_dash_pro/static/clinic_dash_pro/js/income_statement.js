// ============================================================================
// income_statement.js
// Renders:
//   1. Income Statement Table
//   2. Bar Chart (Amount by Account)
//   3. Monthly Trend Chart (Amount vs Account)
//
// Responds to:
//   - Date Range filter (period_year, period_quarter, period_month)
//   - Category filter
//   - Account filter
//
// Uses shared filtering logic from report_filters.js
// ============================================================================

document.addEventListener("DOMContentLoaded", function () {

    // ------------------------------------------------------------------------
    // Load dataset from Django JSON script tag
    // ------------------------------------------------------------------------
    const rawJson = document.getElementById("income-statement-json")?.textContent;
    let data = JSON.parse(rawJson);

    // ------------------------------------------------------------------------
    // Populate Category and Account dropdowns dynamically
    // ------------------------------------------------------------------------
    const categories = [...new Set(data.map(r => r.category))].sort();
    const accounts = [...new Set(data.map(r => r.related_account))].sort();

    const catSelect = document.getElementById("filter-category");
    const accSelect = document.getElementById("filter-account");

    categories.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        catSelect.appendChild(opt);
    });

    accounts.forEach(a => {
        const opt = document.createElement("option");
        opt.value = a;
        opt.textContent = a;
        accSelect.appendChild(opt);
    });

    // ========================================================================
    // TABLE RENDERING
    // ========================================================================

    /**
     * Render the income statement table.
     * @param {Array} rows - Filtered dataset.
     */
    function renderTable(rows) {
        const tbody = document.querySelector("#income-statement-table tbody");
        tbody.innerHTML = "";

        let total = 0;

        rows.forEach(r => {
            const raw = r.amount;

            // Convert "$1,234.56" or numeric into a number
            const amount = typeof raw === "string"
                ? Number(raw.replace(/[^0-9.-]/g, ""))
                : Number(raw || 0);

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.period_year ?? ""}</td>
                <td>${r.period_quarter ?? ""}</td>
                <td>${r.period_month}</td>
                <td>${r.category}</td>
                <td>${r.related_account}</td>
                <td style="text-align:right;">$${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
            `;

            total += amount;
            tbody.appendChild(tr);
        });

        // Update total at bottom of table
        document.getElementById("income-total").textContent =
            "$" + total.toLocaleString(undefined, { minimumFractionDigits: 2 });
    }

    // ========================================================================
    // BAR CHART — Amount by Account
    // ========================================================================

    let barChart = null;

    /**
     * Render bar chart showing total amount per account.
     * @param {Array} rows - Filtered dataset.
     */
    function renderBarChart(rows) {

        const ctx = document.getElementById("income_bar_chart").getContext("2d");

        const grouped = {};

        // Group totals by account
        rows.forEach(r => {
            const raw = r.amount;
            const amount = typeof raw === "string"
                ? Number(raw.replace(/[^0-9.-]/g, ""))
                : Number(raw || 0);

            grouped[r.related_account] = (grouped[r.related_account] || 0) + amount;
        });

        const labels = Object.keys(grouped);
        const originalValues = Object.values(grouped);

        // Compute total BEFORE converting negatives
        const totalOriginal = originalValues.reduce((acc, v) => acc + v, 0);

        // Add TOTAL as final bar
        labels.push("TOTAL");
        originalValues.push(totalOriginal);

        // Convert values to positive for chart display
        const plottedValues = originalValues.map(v => Math.abs(v));

        // Green for positive, red for negative
        const barColors = originalValues.map(v => v >= 0 ? "#2ecc71" : "#e74c3c");

        if (barChart) barChart.destroy();

        barChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    data: plottedValues,
                    backgroundColor: barColors,
                    borderColor: barColors,
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: "y", // horizontal bars
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const original = originalValues[ctx.dataIndex];
                                return "$" + original.toLocaleString();
                            }
                        }
                    },
                    datalabels: {
                        anchor: "end",
                        align: "right",
                        formatter: (v, ctx) => {
                            const original = originalValues[ctx.dataIndex];
                            return "$" + original.toLocaleString();
                        },
                        color: "#000",
                        font: { weight: "bold" }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            callback: v => "$" + v.toLocaleString()
                        }
                    },
                    y: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 0,
                            minRotation: 0
                        }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    }

    // ========================================================================
    // MONTHLY TREND CHART — Amount vs Account
    // ========================================================================

    let monthlyChart = null;

    /**
     * Render monthly trend chart showing each account over time.
     * @param {Array} rows - Filtered dataset.
     */
    function renderMonthlyChart(rows) {

        const ctx = document.getElementById("monthly_account_chart").getContext("2d");

        const grouped = {};

        // Group by month → account → total
        rows.forEach(r => {
            const raw = r.amount;
            const original = typeof raw === "string"
                ? Number(raw.replace(/[^0-9.-]/g, ""))
                : Number(raw || 0);

            const amount = Math.abs(original); // always positive for chart

            const month = r.period_month; // "2026-09"
            const account = r.related_account;

            if (!grouped[month]) grouped[month] = {};
            grouped[month][account] = (grouped[month][account] || 0) + amount;
        });

        const months = Object.keys(grouped).sort();
        const accounts = [...new Set(rows.map(r => r.related_account))].sort();

        // Build datasets for each account
        const datasets = accounts.map(acc => {
            const data = months.map(m => grouped[m][acc] || 0);

            return {
                label: acc,
                data,
                borderWidth: 2,
                fill: false,
                tension: 0.2,
                borderColor: "#" + Math.floor(Math.random() * 16777215).toString(16),
            };
        });

        if (monthlyChart) monthlyChart.destroy();

        monthlyChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: months,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        align: "start" // left-to-right alignment
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const acc = ctx.dataset.label;
                                const val = ctx.raw;
                                return `${acc}: $${val.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: v => "$" + v.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    // ========================================================================
    // APPLY FILTERS
    // ========================================================================

    /**
     * Apply all filters using shared report_filters.js
     * Then re-render table + charts.
     */
    function applyFilters() {

        // Use shared filter module
        const filtered = applyFiltersToDataset(data);

        // Sort by account for consistent display
        filtered.sort((a, b) => a.related_account.localeCompare(b.related_account));

        renderTable(filtered);
        renderBarChart(filtered);
        renderMonthlyChart(filtered);
    }

    // ========================================================================
    // FILTER BUTTONS
    // ========================================================================

    document.getElementById("apply-filters").addEventListener("click", applyFilters);

    document.getElementById("clear-filters").addEventListener("click", () => {
        document.getElementById("filter-date-range").value = "all";
        document.getElementById("filter-category").value = "all";
        document.getElementById("filter-account").value = "all";

        applyFilters();
    });

    // ========================================================================
    // INITIAL RENDER
    // ========================================================================
    applyFilters();

});
