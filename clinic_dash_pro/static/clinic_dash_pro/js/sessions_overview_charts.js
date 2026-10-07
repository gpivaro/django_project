// ============================================================================
// Sessions Overview Charts
// - Renders 3 donut charts:
//      1. Paid vs Unpaid (with total number in center)
//      2. Sessions by Payer
//      3. Sessions by Employee
// - Responds ONLY to the date range filter
// - Uses shared filterByDate() from report_filters.js
// ============================================================================

document.addEventListener("DOMContentLoaded", function () {

    // ------------------------------------------------------------------------
    // Load dataset from Django JSON script tag
    // ------------------------------------------------------------------------
    let sessionsData = JSON.parse(
        document.getElementById("sessions_overview-data-json").textContent
    );

    // ------------------------------------------------------------------------
    // Chart.js Plugin: Draw text in the center of a doughnut chart
    // Only used for Chart #1 (Paid vs Unpaid)
    // ------------------------------------------------------------------------
    const centerTextPlugin = {
        id: "centerTextPlugin",
        beforeDraw(chart, args, options) {

            // Only draw if text is provided
            if (!options || !options.text) return;

            const { ctx, chartArea } = chart;

            ctx.save();
            ctx.font = "bold 28px sans-serif";
            ctx.fillStyle = "#333";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            // Draw centered text
            ctx.fillText(
                options.text,
                (chartArea.left + chartArea.right) / 2,
                (chartArea.top + chartArea.bottom) / 2
            );

            ctx.restore();
        }
    };

    Chart.register(centerTextPlugin);

    // ------------------------------------------------------------------------
    // Color palette for charts
    // ------------------------------------------------------------------------
    const palette = [
        "#4CAF50", "#F44336", "#2196F3", "#FFC107", "#9C27B0",
        "#00BCD4", "#8BC34A", "#FF5722", "#3F51B5", "#E91E63"
    ];

    // ------------------------------------------------------------------------
    // Chart instance holders (so we can destroy and rebuild them)
    // ------------------------------------------------------------------------
    let paidUnpaidChart = null;
    let payerChart = null;
    let employeeChart = null;

    // ------------------------------------------------------------------------
    // Main chart rendering function
    // Called on page load and whenever filters are applied
    // ------------------------------------------------------------------------
    function renderCharts(rows) {

        

        

        // Destroy existing charts to avoid duplicates
        if (paidUnpaidChart) paidUnpaidChart.destroy();
        if (payerChart) payerChart.destroy();
        if (employeeChart) employeeChart.destroy();

        // --------------------------------------------------------------------
        // Filter dataset: Only include Paid + Unpaid sessions
        // (No-charge sessions are excluded)
        // --------------------------------------------------------------------
        const filteredSessions = rows.filter(r => {
            const status = r.status?.toLowerCase();
            return status === "paid" || status === "unpaid";
        });

        console.log("filtered:", filteredSessions);

        // Count paid/unpaid
        const paidCount = filteredSessions.filter(r => r.status === "paid").length;
        const unpaidCount = filteredSessions.filter(r => r.status === "unpaid").length;

        // Total sessions (for center number)
        const totalSessions = paidCount + unpaidCount;

        // Safe fallback values (avoid division by zero)
        const safePaid = paidCount || 0;
        const safeUnpaid = unpaidCount || 0;

        const paidPct = totalSessions ? ((safePaid / totalSessions) * 100).toFixed(1) : 0;
        const unpaidPct = totalSessions ? ((safeUnpaid / totalSessions) * 100).toFixed(1) : 0;

        // --------------------------------------------------------------------
        // Chart 1: Paid vs Unpaid (with center number)
        // --------------------------------------------------------------------
        paidUnpaidChart = new Chart(document.getElementById("sessions_paid_unpaid_chart"), {
            type: "doughnut",
            data: {
                labels: [`Paid (${paidPct}%)`, `Unpaid (${unpaidPct}%)`],
                datasets: [{
                    data: [safePaid, safeUnpaid],
                    backgroundColor: [palette[0], palette[1]]
                }]
            },
            options: {
                responsive: false,
                cutout: "70%", // donut hole size
                plugins: {
                    legend: { position: "bottom" },
                    centerTextPlugin: { text: totalSessions.toString() } // ⭐ center number
                }
            }
        });

        // --------------------------------------------------------------------
        // Chart 2: Sessions by Type
        // --------------------------------------------------------------------
        const payerCounts = {};
        filteredSessions.forEach(r => {
            const payer = r.item || "Unknown";
            payerCounts[payer] = (payerCounts[payer] || 0) + 1;
        });

        payerChart = new Chart(document.getElementById("sessions_type_chart"), {
            type: "doughnut",
            data: {
                labels: Object.keys(payerCounts),
                datasets: [{
                    data: Object.values(payerCounts),
                    backgroundColor: Object.keys(payerCounts).map((_, i) => palette[i % palette.length])
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: { position: "bottom" },
                    centerTextPlugin: false // no center text for this chart
                }
            }
        });

        // --------------------------------------------------------------------
        // Chart 3: Sessions by Employee Initials
        // --------------------------------------------------------------------
        const employeeCounts = {};
        filteredSessions.forEach(r => {
            const emp = r.employee_initials || "Unknown";
            employeeCounts[emp] = (employeeCounts[emp] || 0) + 1;
        });

        employeeChart = new Chart(document.getElementById("sessions_employee_chart"), {
            type: "doughnut",
            data: {
                labels: Object.keys(employeeCounts),
                datasets: [{
                    data: Object.values(employeeCounts),
                    backgroundColor: Object.keys(employeeCounts).map((_, i) => palette[(i + 3) % palette.length])
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: { position: "bottom" },
                    centerTextPlugin: false // no center text for this chart
                }
            }
        });
    }

    // ------------------------------------------------------------------------
    // Apply Filters (DATE RANGE ONLY)
    // Uses shared filterByDate() from report_filters.js
    // ------------------------------------------------------------------------
    document.getElementById("apply-filters").addEventListener("click", () => {

        const range = document.getElementById("filter-date-range").value;

        // Filter sessions using period_year, period_quarter, period_month
        const filtered = filterByDate(sessionsData, range);

        // Re-render charts with filtered data
        renderCharts(filtered);
    });

    // ------------------------------------------------------------------------
    // Clear Filters → Reset date range to "all"
    // ------------------------------------------------------------------------
    document.getElementById("clear-filters").addEventListener("click", () => {

        document.getElementById("filter-date-range").value = "all";

        // Render charts with full dataset
        renderCharts(sessionsData);
    });

    // ------------------------------------------------------------------------
    // Initial Render (full dataset)
    // ------------------------------------------------------------------------
    renderCharts(sessionsData);

    


});
