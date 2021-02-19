function exportTable() {
    $("#tblData").table2excel({
        exclude: ".noExport",
        filename: "Transactions.xls"
    });
};