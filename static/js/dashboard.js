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
                        data: [budgets[i].spent, budgets[i].remaining],
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
                labels: [weeklySpending[0].startOfWeek.slice(5) + " - " + weeklySpending[0].endOfWeek.slice(5), weeklySpending[1].startOfWeek.slice(5) + " - " + weeklySpending[1].endOfWeek.slice(5), weeklySpending[2].startOfWeek.slice(5) + " - " + weeklySpending[2].endOfWeek.slice(5), weeklySpending[3].startOfWeek.slice(5) + " - " + weeklySpending[3].endOfWeek.slice(5)],
                datasets: [{
                    label: 'Total $ Spent',
                    data: [weeklySpending[0].amount, weeklySpending[1].amount, weeklySpending[2].amount, weeklySpending[3].amount],
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
            amounts[i] = monthlySpending[i].amount;
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
                    text: 'Total spending per month during the current the year'
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
                    x: spendingTrends[i].totalSpent,
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