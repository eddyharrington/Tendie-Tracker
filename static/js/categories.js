// SUMMARY: this file handles all of the functionality on the 'Manage Spend Categories' page of Tendie Tracker.

// Set focus to new category name field when collapsed area is shown
$('#collapseCategory').on('shown.bs.collapse', function () {
    $('#name').trigger('focus')
})

// Clear new category name field when collapsed area is hidden
$('#collapseCategory').on('hidden.bs.collapse', function () {
    $('#name').val('')
})

// While the Rename modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the fields
$('#renameModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget) // Button that triggered the modal
    let category = button.data('category') // Extract info from data-* attributes
    let budgets_string = button.data('budgets') // Get the semi-colon delimitted string of budgets that are associated with the category
    let budgets = budgets_string.split(";")
    let modal = $(this)
    modal.find('.modal-title').text("Rename category '" + category + "'")
    modal.find('#oldname').val(category)
    msg = modal.find('#renameAlert_msg');
    msg_budgets = modal.find('#renameAlert_budgets');
    // Loop through the budgets associated with a category. note: length of budgets will be 1 due to empty string when no budgets exist.
    if (budgets.length > 1) {
        msg[0].innerText = "The following budgets will have the category name updated:";
        for (i = 0; i < budgets.length; i++) {
            // Last element is an empty string due to semicolon separated values, so ignore it in the loop to avoid having a blank list item
            if (budgets[i] != '') {
                msg_budgets[0].innerHTML += "<li>" + budgets[i] + "</li>";
            }
        }
    }
    else {
        msg[0].innerText = "No budgets will be affected by this change";
    }
})

// As the Rename modal becomes hidden (CSS transitions are 100% finished), clear the 'newname' and alert message fields
$('#renameModal').on('hidden.bs.modal', function () {
    $('#newname').val('');
    $('#renameAlert_budgets').empty();
})

// While the Delete modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the fields
$('#deleteModal').on('show.bs.modal', function (event) {
    let button = $(event.relatedTarget) // Button that triggered the modal
    let category = button.data('category') // Extract info from data-* attributes
    let budgets_string = button.data('budgets') // Get the semi-colon delimitted string of budgets that are associated with the category
    let budgets = budgets_string.split(";")
    let modal = $(this)
    modal.find('.modal-title').text("Delete category '" + category + "'")
    modal.find('#delete').val(category)
    msg = modal.find('#deleteAlert_msg');
    msg_budgets = modal.find('#deleteAlert_budgets');
    // Loop through the budgets associated with a category. note: length of budgets will be 1 due to empty string when no budgets exist.
    if (budgets.length > 1) {
        msg[0].innerText = "The following budgets will have the category name deleted. Make sure you update your budgets after deleting the category!";
        for (i = 0; i < budgets.length; i++) {
            // Last element is an empty string due to semicolon separated values, so ignore it in the loop to avoid having a blank list item
            if (budgets[i] != '') {
                msg_budgets[0].innerHTML += "<li>" + budgets[i] + "</li>";
            }
        }
    }
    else {
        msg[0].innerText = "No budgets will be affected by this change";
    }
})

// As the Delete modal becomes hidden (CSS transitions are 100% finished), clear the alert message fields
$('#deleteModal').on('hidden.bs.modal', function () {
    $('#deleteAlert_budgets').empty();
})