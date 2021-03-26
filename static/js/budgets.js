// SUMMARY: this file handles all of the functionality on the 'Create Budget' and 'Update Budget' pages of Tendie Tracker.

/////////////////////////////////
// Core Budget Functionality
/////////////////////////////////

// Load budget years and calculate estimates on page load to set initial amounts in the muted text
$(document).ready(function () {
    loadBudgetYears();
    calculateEstimates();
});

// Generates the allowed years to scope a budget for
function loadBudgetYears() {
    // Get the budget year element from the form
    let years = document.getElementById("year")

    // Get the current year from users machine
    let currentYear = new Date().getFullYear();

    // Try getting the budgets year if user is updating existing budget (will be null if creating a new budget)
    let updatableYear = document.getElementById('year').getAttribute('data-year')

    // Generate allowable years to select for budget (2020 thru current year)
    for (let i = currentYear; i >= 2020; i--) {
        // Create an option tag
        let option = document.createElement("option");
        option.innerHTML = i;
        option.value = i;

        // Check if an existing budget year exists (this means user is updating an existing budget)
        if (updatableYear !== null) {
            // Set the selected year to the existing budgets year
            if (i.toString() == updatableYear) {
                option.selected = true;
            }
        }
        // User is creating a new budget
        else {
            // Set the selected year to the current year
            if (i == currentYear) {
                option.selected = true;
            }
        }
        years.appendChild(option);
    }
}

// Sets the budget amount to the remaining income that has not yet been budgeted
function fillBudgetAmount(amount) {
    document.getElementById('amount').value = amount;
    calculateEstimates();
}

// Disables the form submit button unless at least one category is selected - courtesy of Sergio on StackOverflow: https://stackoverflow.com/a/20688095
var checkBoxes = $('.custom-control-input');
checkBoxes.change(function () {
    $('#btnSaveBudget').prop('disabled', checkBoxes.filter(':checked').length < 1);
});
$('.custom-control-input').change();

// Calculates weekly/monthly budget estimates based on the total budget amount
function calculateEstimates() {
    // Update the budget amount estimates
    let budget = document.getElementById("amount").value;
    const weekly = (budget / 52)
    const monthly = (budget / 12)
    document.getElementById("weekly").innerHTML = "Weekly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(weekly);
    document.getElementById("monthly").innerHTML = "Monthly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(monthly);

    // Get all of the checked categories and update their estimates
    let checkedCategories = getAllCheckedCategories()
    if (checkedCategories) {
        for (i = 0; i < checkedCategories.length; i++) {
            // Pass the individual input box (or category % amount)
            percentInput = checkedCategories[i].nextElementSibling.nextElementSibling.nextElementSibling;
            calculateCategories(percentInput)
        }
    }
}

/////////////////////////////////
// Spend Categories Functionality
/////////////////////////////////

// Shows or hides the spend category percentage budgets based on whether or not the user has checked a spend category
function displayCategoryAmounts(category) {
    let categoryPercentageInput = category.nextElementSibling.nextElementSibling.nextElementSibling;
    let percentageLabel = categoryPercentageInput.nextElementSibling;
    let percentageAmountLabel = percentageLabel.nextElementSibling;

    // Show the percentage input box and labeling
    if (category.checked == true) {
        categoryPercentageInput.type = "number";
        categoryPercentageInput.hidden = false;
        categoryPercentageInput.required = true;
        categoryPercentageInput.readOnly = false;
        percentageLabel.hidden = false;
        percentageAmountLabel.hidden = false;
    }
    // Hide the percentage input box and lebeling
    else {
        categoryPercentageInput.type = "hidden";
        categoryPercentageInput.hidden = true;
        categoryPercentageInput.required = false;
        categoryPercentageInput.readOnly = true;
        percentageLabel.hidden = true;
        percentageAmountLabel.hidden = true;
    }
}

// Prevents any numbers/chars but 0-9 to be entered into the percentage inputs (solution from Stack Overflow: https://stackoverflow.com/questions/14806200/disable-some-characters-from-input-field)
$(function () {
    $('.categoryPercent').keypress(function (e) {
        // Allowed char: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
        let allow_char = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57];
        // Block keypress unless the char is allowed
        if (allow_char.indexOf(e.which) !== -1) {
            return true;
        }
        else {
            return false;
        }
    });
});

// Gets all checked inputs / spend categories and returns as an array
function getAllCheckedCategories() {
    // Get all checkbox inputs
    var categories = $('.custom-control-input');

    // Loop through all checkbox inputs and store the checked ones in an array
    var allCheckedCategories = [];
    for (i = 0; i < categories.length; i++) {
        if (categories[i].checked) {
            allCheckedCategories.push(categories[i]);
        }
    }

    // Only return the array if at least one checkbox input is checked
    if (allCheckedCategories.length > 0) {
        return allCheckedCategories;
    }
    else {
        return false;
    }
}

// Calculates the dollar amount of a spend category based on the users input of percentage, then displays the output to the user
function calculateCategories(percentInput) {
    let categoryBudget = document.getElementById("amount").value;
    const categoryWeekly = (categoryBudget / 52);
    const categoryMonthly = (categoryBudget / 12);
    let categoryLabel = percentInput.nextElementSibling.nextElementSibling;

    // Only calculate the amount if user enters a percent value of 1-100
    if (percentInput.value > 0 && percentInput.value <= 100) {
        // Show the calculations to the user
        categoryLabel.innerHTML = "Total amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryBudget * (percentInput.value / 100)) + "<br>Weekly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryWeekly * (percentInput.value / 100)) + "<br>Monthly amount: " + new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(categoryMonthly * (percentInput.value / 100));
        document.getElementById("btnSaveBudget").disabled = false;
    }
    // Display error message
    else {
        categoryLabel.innerHTML = "⚠ Enter a percentage between 1 to 100, or uncheck the category ⚠";
        document.getElementById("btnSaveBudget").disabled = true;
    }
}

// Validates form by checking every spend category that's been selected by the user for
function validateCategories() {
    // Get all of the checked checkboxes and store in an array
    var allCheckBoxes = $('.custom-control-input');
    var checkBoxesChecked = [];
    for (i = 0; i < allCheckBoxes.length; i++) {
        let checkbox = allCheckBoxes[i];
        if (checkbox.checked) {
            checkBoxesChecked.push(checkbox);
        }
    }

    // Loop through all the checked checkboxes and sum up the values
    var sum = 0;
    for (i = 0; i < checkBoxesChecked.length; i++) {
        let percent = checkBoxesChecked[i].nextElementSibling.nextElementSibling.nextElementSibling;
        // If the field is empty automatically set it to 0
        sum += parseInt(percent.value) || 0;
    }

    // Validate that the summed percentages equals 100%. If it doesn't, prevent form submission and show message.
    var submitAlert = document.getElementById('submitAlert');
    if (sum != 100) {
        submitAlert.innerHTML = "Your spend categories budgets add up to " + sum + "% and it must be equal to 100%";
        submitAlert.hidden = false;
        // Prevent the form from being submitted
        event.preventDefault();
    }
}