// ============================================================================
// report_filters.js
// Shared filtering module used by:
//   - Income Statement charts
//   - Sessions Overview charts
//   - Any dataset using period_year, period_quarter, period_month
//
// This file centralizes all filter logic so every dashboard behaves consistently.
// ============================================================================



// ============================================================================
// DATE HELPERS
// ============================================================================

/**
 * Convert a "YYYY-MM" or "YYYY-MM-DD" string into a Date object.
 * Used by income statement and sessions datasets.
 *
 * @param {string} value - The date string to parse.
 * @returns {Date|null} - A valid Date object or null if invalid.
 */
function safeParseDate(value) {
    if (!value) return null;

    // Case 1: "2026-09" → treat as first day of month
    if (/^\d{4}-\d{2}$/.test(value)) {
        const [y, m] = value.split("-");
        return new Date(Number(y), Number(m) - 1, 1);
    }

    // Case 2: "2026-09-14" → full date
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        return new Date(value);
    }

    return null;
}

/**
 * Convert a month number (1–12) into a quarter number (1–4).
 *
 * @param {number} m - Month number.
 * @returns {number} - Quarter number.
 */
function getQuarterFromMonth(m) {
    return Math.floor((m - 1) / 3) + 1;
}



// ============================================================================
// DATE RANGE FILTER
// ============================================================================

/**
 * Filter rows based on a date range selection.
 * Works for both Income Statement and Sessions datasets.
 *
 * Expected fields:
 *   - period_year: "2026"
 *   - period_quarter: "2026Q3" or "3"
 *   - period_month: "2026-09"
 *
 * @param {Array} rows - The dataset to filter.
 * @param {string} range - The selected date range.
 * @returns {Array} - Filtered dataset.
 */
function filterByDate(rows, range) {
    if (range === "all") return rows;

    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth() + 1;
    const currentQuarter = getQuarterFromMonth(currentMonth);

    return rows.filter(r => {

        // --------------------------------------------------------------------
        // SAFETY: Ignore rows missing date fields
        // Sessions dataset sometimes includes rows without period metadata.
        // --------------------------------------------------------------------
        if (!r.period_year || !r.period_quarter || !r.period_month) {
            return false;
        }

        // --------------------------------------------------------------------
        // Extract date components
        // --------------------------------------------------------------------
        const rowYear = Number(r.period_year);

        // period_quarter may be "2026Q3" or "3"
        const quarterString = String(r.period_quarter);
        const rowQuarter = quarterString.includes("Q")
            ? Number(quarterString.split("Q")[1])
            : Number(quarterString);

        const [y, m] = r.period_month.split("-");
        const rowMonth = Number(m);

        // Convert "YYYY-MM" into a Date object
        const rowDate = new Date(Number(y), Number(m) - 1);

        // --------------------------------------------------------------------
        // Apply date range logic
        // --------------------------------------------------------------------
        switch (range) {

            // -----------------------------
            // CLOSED MONTHS
            // -----------------------------
            case "last_month": {
                const lastMonthDate = new Date(currentYear, currentMonth - 2);
                const lmYear = lastMonthDate.getFullYear();
                const lmMonth = lastMonthDate.getMonth() + 1;
                return rowYear === lmYear && rowMonth === lmMonth;
            }

            case "prior_month": {
                const priorMonthDate = new Date(currentYear, currentMonth - 3);
                const pmYear = priorMonthDate.getFullYear();
                const pmMonth = priorMonthDate.getMonth() + 1;
                return rowYear === pmYear && rowMonth === pmMonth;
            }

            // -----------------------------
            // CLOSED QUARTERS
            // -----------------------------
            case "last_quarter": {
                let lqYear = currentYear;
                let lqQuarter = currentQuarter - 1;

                if (lqQuarter === 0) {
                    lqQuarter = 4;
                    lqYear = currentYear - 1;
                }

                return rowYear === lqYear && rowQuarter === lqQuarter;
            }

            case "prior_quarter": {
                let pqYear = currentYear;
                let pqQuarter = currentQuarter - 2;

                if (pqQuarter <= 0) {
                    pqQuarter += 4;
                    pqYear -= 1;
                }

                return rowYear === pqYear && rowQuarter === pqQuarter;
            }

            // -----------------------------
            // CLOSED YEARS
            // -----------------------------
            case "last_year":
                return rowYear === currentYear - 1;

            case "prior_year":
                return rowYear === currentYear - 2;

            // -----------------------------
            // CURRENT PARTIAL PERIODS
            // -----------------------------
            case "mtd":
                return rowYear === currentYear &&
                    rowMonth === currentMonth &&
                    rowDate <= today;

            case "qtd":
                return rowYear === currentYear &&
                    rowQuarter === currentQuarter &&
                    rowDate <= today;

            case "ytd":
                return rowYear === currentYear &&
                    rowDate <= today;

            default:
                return true;
        }

    });
}



// ============================================================================
// CATEGORY FILTER
// ============================================================================

/**
 * Filter rows by category.
 * Works for:
 *   - Income Statement (category)
 *   - Sessions (item)
 *
 * @param {Array} rows - Dataset.
 * @param {string} category - Selected category.
 * @returns {Array} - Filtered dataset.
 */
function filterByCategory(rows, category) {
    if (category === "all") return rows;

    return rows.filter(r =>
        r.category === category ||
        r.item === category
    );
}



// ============================================================================
// ACCOUNT FILTER
// ============================================================================

/**
 * Filter rows by account.
 * Works for:
 *   - Income Statement (related_account)
 *   - Sessions (employee_initials)
 *
 * @param {Array} rows - Dataset.
 * @param {string} account - Selected account.
 * @returns {Array} - Filtered dataset.
 */
function filterByAccount(rows, account) {
    if (account === "all") return rows;

    return rows.filter(r =>
        r.related_account === account ||
        r.employee_initials === account
    );
}



// ============================================================================
// MASTER FILTER FUNCTION
// ============================================================================

/**
 * Apply all filters in sequence:
 *   1. Date range
 *   2. Category
 *   3. Account
 *
 * Used by income_statement.js.
 * Sessions charts only use date filtering.
 *
 * @param {Array} rows - Dataset.
 * @returns {Array} - Fully filtered dataset.
 */
function applyFiltersToDataset(rows) {

    const dateRange = document.getElementById("filter-date-range").value;
    const category = document.getElementById("filter-category").value;
    const account = document.getElementById("filter-account").value;

    let filtered = [...rows];

    filtered = filterByDate(filtered, dateRange);
    filtered = filterByCategory(filtered, category);
    filtered = filterByAccount(filtered, account);

    return filtered;
}
