function exportTable() {
    $("#tblData").table2excel({
        exclude: ".noExport",
        filename: "Transactions_Categorized.xls"
    });

    $("#tableCategoryExpenses").table2excel({
        exclude: ".noExport",
        filename: "Expenses_by_Categories.xls"
    });
};