// SUMMARY: this file handles all of the functionality on the 'Dashboard' page of Tendie Tracker.

// Loads *budget data* from Flask/Jinja that is passed from the request
function loadBudgetData(budgetData) {
    budgets = JSON.parse(budgetData);
    loadBudgetCharts(budgets);
}

// Loads *weekly spending* data from Flask/Jinja that is passed from the request
function loadWeeklySpendingData(weeklyData) {
    weeklySpending = JSON.parse(weeklyData);
    loadWeeklySpendingCharts(weeklySpending);
}

// Loads *monthly spending* data from Flask/Jinja that is passed from the request
function loadMonthlySpendingData(monthlyData) {
    monthlySpending = JSON.parse(monthlyData);
    loadMonthlySpendingChart(monthlySpending);
}

// Loads *spending trends* data from Flask/Jinja that is passed from the request
function loadTrendsData(trendsData) {
    spendingTrends = JSON.parse(trendsData);
    loadSpendingTrendsChart(spendingTrends);
}

// Loads *payers* data from Flask/Jinja that is passed from the request
function loadPayersData(payersData) {
    payersSpending = JSON.parse(payersData);
    loadPayersSpendingChart(payersSpending);
}

// After the modal is fully rendered, focus input into the new 'description' field
$('#quickExpenseModal').on('shown.bs.modal', function () {
    $('#description').trigger('focus')
})

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

function loadWeeklySpendingCharts(weeklySpending) {
    if (weeklySpending == null) {
        return;
    }
    else {
        let chartElement = document.getElementById('weeklyChart').getContext('2d');
        let spendingChart = new Chart(chartElement, {
            type: 'line',
            data: {
                labels: [weeklySpending[0].startOfWeek.slice(0, 6) + " - " + weeklySpending[0].endOfWeek.slice(0, 6), weeklySpending[1].startOfWeek.slice(0, 6) + " - " + weeklySpending[1].endOfWeek.slice(0, 6), weeklySpending[2].startOfWeek.slice(0, 6) + " - " + weeklySpending[2].endOfWeek.slice(0, 6), weeklySpending[3].startOfWeek.slice(0, 6) + " - " + weeklySpending[3].endOfWeek.slice(0, 6)],
                datasets: [{
                    label: 'Total $ Spent',
                    data: [(Math.round(weeklySpending[0].amount * 100) / 100), (Math.round(weeklySpending[1].amount * 100) / 100), (Math.round(weeklySpending[2].amount * 100) / 100), (Math.round(weeklySpending[3].amount * 100) / 100)],
                    pointRadius: 9,
                    fill: false,
                    lineTension: 0.1,
                    borderWidth: 2,
                    backgroundColor: "rgba(240, 173, 78, 1)",
                    borderColor: "rgba(2, 184, 117, 1)"
                }]
            },
            options: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Total spending per week of the last 4 weeks'
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

function loadMonthlySpendingChart(monthlySpending) {
    if (monthlySpending == null) {
        return;
    }
    else {
        // Build arrays to hold the months and amounts for chart labels and data
        let months = []
        let amounts = []
        for (i = 0; i < monthlySpending.length; i++) {
            months[i] = monthlySpending[i].name;
            amounts[i] = (Math.round(monthlySpending[i].amount * 100) / 100);
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
                    text: 'Total spending per month during the current year'
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

function loadSpendingTrendsChart(spendingTrends) {
    if (spendingTrends == null) {
        return;
    }
    else {
        // Build dict/array to hold the data
        let trendsDataset = []

        // Loop through each JSON object that was received from Flask/Jinja and populate a dict that matches ChartJS parameters
        for (i = 0; i < spendingTrends.length; i++) {
            data = {
                label: spendingTrends[i].name,
                backgroundColor: "rgba(240, 173, 78, 0.7)",
                borderColor: "rgba(2, 184, 117, 1)",
                borderWidth: 2,
                data: [{
                    x: (Math.round(spendingTrends[i].totalSpent * 100) / 100),
                    y: spendingTrends[i].totalCount,
                    r: spendingTrends[i].proportionalAmount
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