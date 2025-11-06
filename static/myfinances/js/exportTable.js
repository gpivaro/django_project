function exportTable() {
    const timestamp = new Date().toISOString().slice(0,19).replace(/[:T]/g, "-");


    $("#tblData").table2excel({
        exclude: ".noExport",
        filename: `Transactions_Categorized_${timestamp}.xls`
    });

    $("#tableCategoryExpenses").table2excel({
        exclude: ".noExport",
        filename: `Expenses_by_Categories_${timestamp}.xls`
    });
}