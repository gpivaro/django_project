document.addEventListener("DOMContentLoaded", function () {

    const rawJson = document.getElementById("income-statement-json")?.textContent;
    let data = JSON.parse(rawJson);

    // Populate filters
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

    // ============================
    // Render Table
    // ============================
    function renderTable(rows) {
        const tbody = document.querySelector("#income-statement-table tbody");
        tbody.innerHTML = "";

        let total = 0;

        rows.forEach(r => {
            const raw = r.amount;
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

        document.getElementById("income-total").textContent =
            "$" + total.toLocaleString(undefined, { minimumFractionDigits: 2 });
    }

    // ============================
    // Render Bar Chart (Amount by Account)
    // ============================
    let barChart = null;

    function renderBarChart(rows) {
    const ctx = document.getElementById("income_bar_chart").getContext("2d");

    const grouped = {};

    rows.forEach(r => {
        const raw = r.amount;
        const amount = typeof raw === "string"
            ? Number(raw.replace(/[^0-9.-]/g, ""))
            : Number(raw || 0);

        grouped[r.related_account] = (grouped[r.related_account] || 0) + amount;
    });

    const labels = Object.keys(grouped);
    const originalValues = Object.values(grouped);

    // Compute total BEFORE removing negatives
    const totalOriginal = originalValues.reduce((acc, v) => acc + v, 0);

    // Add TOTAL as an extra account
    labels.push("TOTAL");
    originalValues.push(totalOriginal);

    // Convert all values to positive for plotting
    const plottedValues = originalValues.map(v => Math.abs(v));

    // Color based on original sign
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
            indexAxis: "y",              // horizontal bars
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




    // ============================
    // Date Range Filtering
    // ============================
    function toDate(periodMonth) {
        const [y, m] = periodMonth.split("-");
        return new Date(Number(y), Number(m) - 1);
    }

    function getQuarter(m) {
        return Math.floor((m - 1) / 3) + 1;
    }

    function filterByDate(rows, range) {
        if (range === "all") return rows;

        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth() + 1;
        const currentQuarter = getQuarter(month);

        return rows.filter(r => {
            const [rowYearStr, rowMonthStr] = r.period_month.split("-");
            const rowYear = Number(rowYearStr);
            const rowMonth = Number(rowMonthStr);
            const rowDate = toDate(r.period_month);
            const rowQuarter = getQuarter(rowMonth);

            switch (range) {
                case "this_month":
                    return rowYear === year && rowMonth === month;

                case "last_month": {
                    const lastMonthDate = new Date(year, month - 2);
                    const lmYear = lastMonthDate.getFullYear();
                    const lmMonth = lastMonthDate.getMonth() + 1;
                    return rowYear === lmYear && rowMonth === lmMonth;
                }

                case "this_quarter":
                    return rowYear === year && rowQuarter === currentQuarter;

                case "last_quarter": {
                    let lqYear = year;
                    let lqQuarter = currentQuarter - 1;
                    if (lqQuarter === 0) {
                        lqQuarter = 4;
                        lqYear = year - 1;
                    }
                    return rowYear === lqYear && rowQuarter === lqQuarter;
                }

                case "this_year":
                    return rowYear === year;

                case "last_year":
                    return rowYear === year - 1;

                case "mtd":
                    return rowYear === year && rowMonth === month && rowDate <= today;

                case "qtd":
                    return rowYear === year && rowQuarter === currentQuarter && rowDate <= today;

                case "ytd":
                    return rowYear === year && rowDate <= today;

                default:
                    return true;
            }
        });
    }

    // ============================
    // Apply Filters
    // ============================
    function applyFilters() {
        let filtered = [...data];

        const dateRange = document.getElementById("filter-date-range").value;
        const category = document.getElementById("filter-category").value;
        const account = document.getElementById("filter-account").value;

        filtered = filterByDate(filtered, dateRange);

        if (category !== "all") {
            filtered = filtered.filter(r => r.category === category);
        }

        if (account !== "all") {
            filtered = filtered.filter(r => r.related_account === account);
        }

        filtered.sort((a, b) => a.related_account.localeCompare(b.related_account));

        renderTable(filtered);
        renderBarChart(filtered);
    }

    document.getElementById("apply-filters").addEventListener("click", applyFilters);

    // ============================
    // Clear Filters
    // ============================
    document.getElementById("clear-filters").addEventListener("click", () => {
        document.getElementById("filter-date-range").value = "all";
        document.getElementById("filter-category").value = "all";
        document.getElementById("filter-account").value = "all";

        renderTable(data);
        renderBarChart(data);
    });

    // Initial render
    renderTable(data);
    renderBarChart(data);
});
