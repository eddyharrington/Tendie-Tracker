// SUMMARY: this file handles all of the functionality on the various Reporting pages of Tendie Tracker.

// Loads *budget report data* from Flask/Jinja that is passed from the request
function loadBudgetData(budgetData) {
    budgets = JSON.parse(budgetData);
    loadBudgetCharts(budgets);
    loadBudgetTables(budgets);
}

// Loads *monthly spending* data from Flask/Jinja that is passed from the request
function loadMonthlySpendingData(monthlyData) {
    monthlySpending = JSON.parse(monthlyData);
    loadMonthlySpendingChart(monthlySpending.chart);
    loadMonthlySpendingTable(monthlySpending.table);
}

// Loads *spending trends* data from Flask/Jinja that is passed from the request
function loadTrendsData(trendsData_chart, trendsData_table) {
    spendingTrends_chart = JSON.parse(trendsData_chart);
    spendingTrends_table = JSON.parse(trendsData_table);
    loadSpendingTrendsChart(spendingTrends_chart);
    loadSpendingTrendsTable(spendingTrends_table);
}

// Loads *payers* data from Flask/Jinja that is passed from the request
function loadPayersData(payersData) {
    payersSpending = JSON.parse(payersData);
    loadPayersSpendingChart(payersSpending);
}

function loadBudgetCharts(budgets) {
    if (budgets == null) {
        return;
    }
    // Loop through the budgets and build the charts
    else {
        let chartElement = []
        let budgetCharts = []
        for (i = 0; i < budgets.length; i++) {
            chartElement[i] = document.getElementById('budgetChart.' + (i)).getContext('2d');
            budgetCharts[i] = new Chart(chartElement[i], {
                type: 'doughnut',
                data: {
                    labels: ['Spent', 'Remaining'],
                    datasets: [{
                        label: budgets[i].name,
                        data: [(Math.round(budgets[i].spent * 100) / 100), (Math.round(budgets[i].remaining * 100) / 100)],
                        backgroundColor: [
                            'rgba(240, 173, 78, 1)',
                            'rgba(2, 184, 117, 1)'
                        ],
                        borderColor: [
                            'rgba(192, 138, 62, 1)',
                            'rgba(1, 147, 93, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        labels: {
                            fontColor: 'black'
                        }
                    }
                }
            });
        }
    }
}

function loadBudgetTables(budgets) {
    if (budgets == null) {
        return;
    }
    // Loop through the budgets and build the charts
    else {
        for (i = 0; i < budgets.length; i++) {
            $('#budgetTable_' + (i + 1)).DataTable({
                "order": [[5, "desc"]],
                "scrollY": "300px",
                "scrollCollapse": true,
                "paging": false,
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel'
                ],
                "searching": false
            });
        }
    }
}

function loadMonthlySpendingChart(monthlySpendingChart) {
    if (monthlySpendingChart == null) {
        return;
    }
    else {
        // Build arrays to hold the months and amounts for chart labels and data
        let months = []
        let amounts = []
        for (i = 0; i < monthlySpendingChart.length; i++) {
            months[i] = monthlySpendingChart[i].name;
            amounts[i] = (Math.round(monthlySpendingChart[i].amount * 100) / 100);
        }

        // Draw the chart
        let chartElement = document.getElementById('monthlyChart').getContext('2d');
        let spendingChart = new Chart(chartElement, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [{
                    label: 'Total $ Spent',
                    data: amounts,
                    backgroundColor: [
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)'
                    ],
                    borderColor: [
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Total spending per month'
                },
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }
}

function loadMonthlySpendingTable(monthlySpendingTable) {
    if (monthlySpendingTable == null) {
        return;
    }
    else {
        $('#monthlyExpenses').DataTable({
            "pagingType": "full_numbers",
            "order": [[0, "desc"]],
            "scrollY": "300px",
            "scrollCollapse": true,
            "paging": false,
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel'
            ]
        });
    }
}

function loadSpendingTrendsChart(spendingTrends_chart) {
    if (spendingTrends_chart == null) {
        return;
    }
    else {
        // Build dict/array to hold the data
        let trendsDataset = []

        // Loop through each JSON object that was received from Flask/Jinja and populate a dict that matches ChartJS parameters
        for (i = 0; i < spendingTrends_chart.length; i++) {
            data = {
                label: spendingTrends_chart[i].name,
                backgroundColor: "rgba(240, 173, 78, 0.7)",
                borderColor: "rgba(2, 184, 117, 1)",
                borderWidth: 2,
                data: [{
                    x: (Math.round(spendingTrends_chart[i].totalSpent * 100) / 100),
                    y: spendingTrends_chart[i].totalCount,
                    r: spendingTrends_chart[i].proportionalAmount
                }]
            }

            // Add the data set to the list
            trendsDataset.push(data)
        }

        // Draw the chart
        let chartElement = document.getElementById('spendingChart').getContext('2d');
        let spendingChart = new Chart(chartElement, {
            type: 'bubble',
            data: {
                labels: "Spend Categories",
                datasets: trendsDataset
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                title: {
                    display: true,
                    text: 'Total spent, total # of expenses, and % of overall spent per spend category'
                },
                scales: {
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "Total # of Expenses"
                        }
                    }],
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "Total $ Spent"
                        }
                    }]
                }
            }
        });
    }
}

function loadSpendingTrendsTable(spendingTrends_table) {
    if (spendingTrends_table == null) {
        return;
    }
    else {
        $('#monthlyCategoryExpenses').DataTable({
            "pagingType": "full_numbers",
            "bSort": false,
            "bFilter": false,
            "bInfo": false,
            "paging": false,
            dom: 'Bfrtip',
            buttons: ['copy', 'csv', 'excel', 'colvis']
        });
    }
}

function loadPayersSpendingChart(payersSpending) {
    if (payersSpending == null) {
        return;
    }
    else {
        // Loop through the payers object and build the labels
        payerNames = []
        for (i = 0; i < payersSpending.length; i++) {
            // If the payer represents less than 1% of overall expenses do not include
            if (payersSpending[i].percentAmount < 1) {
                continue;
            }
            else {
                payerNames.push(payersSpending[i].name)
            }
        }

        // Loop through the payers object and build the amounts dataset
        payerAmounts = []
        for (i = 0; i < payersSpending.length; i++) {
            // If the payer represents less than 1% of overall expenses do not include
            if (payersSpending[i].percentAmount < 1) {
                continue;
            }
            else {
                payerAmounts.push((Math.round(payersSpending[i].amount * 100) / 100))
            }
        }

        // Build the chart
        chartElement = document.getElementById('payersChart').getContext('2d');
        budgetCharts = new Chart(chartElement, {
            type: 'pie',
            data: {
                labels: payerNames,
                datasets: [{
                    data: payerAmounts,
                    // Note: the color scheme for this is hard-coded with an assumption of 6 total payers including the default 'Self' payer. 
                    // If max payer count changes in the future, the background/border colors will need to as well
                    backgroundColor: [
                        'rgba(240, 173, 78, 1)',
                        'rgba(2, 184, 117, 1)',
                        'rgba(69, 130, 236)',
                        'rgba(23, 162, 184)',
                        'rgba(202, 207, 212)',
                        'rgba(217, 83, 79)'
                    ],
                    borderColor: [
                        'rgba(192, 138, 62, 1)',
                        'rgba(1, 147, 93, 1)',
                        'rgba(64, 121, 220)',
                        'rgba(21, 151, 171)',
                        'rgba(173, 181, 189)',
                        'rgba(195, 74, 71)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    labels: {
                        fontColor: 'black'
                    }
                }
            }
        });

    }
}