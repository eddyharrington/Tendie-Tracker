// SUMMARY: this file handles all of the functionality to view, update, or delete a users expense history on the 'Expense History' page of Tendie Tracker.

//Data Table
$(document).ready(function () {
    $('#expenses').DataTable({
        "pagingType": "full_numbers",
        "order": [[0, "desc"]],
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel'
        ]
    });
});

// Delete expense UX functionality
var expenseDetailsBody;
var saveButton = $('#btnSave');
var deleteButton = $('#btnDelete');
var isDeleteUX = false;
$(document).ready(function () {
    $("#btnDelete, #btnDeleteCancel").click(function () {
        toggleDeleteUX();
        if (isDeleteUX == false) {
            isDeleteUX = true;
        }
        else {
            isDeleteUX = false;
        }
    });
});

function toggleDeleteUX() {
    // Show the expense detail body if it's been hidden/detached already and hide delete message/buttons
    if (expenseDetailsBody) {
        expenseDetailsBody.appendTo(".modal-body");
        expenseDetailsBody = null;
        // Hide the delete message and show the Save button
        $("#deleteDetails").hide();
        saveButton.show();
        deleteButton.show();

        // Otherwise hide/detach the expense detail body and show the delete message/buttons
    } else {
        expenseDetailsBody = $("#newExpenseDetails").detach();
        saveButton.hide();
        deleteButton.hide();
        $("#deleteDetails").show();
    }
}

// While the modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the expense fields
$('#updateModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var description = button.data('description') // Extract info from data-* attributes
    var category = button.data('category') // Extract info from data-* attributes
    var date = button.data('date') // Extract info from data-* attributes
    var payer = button.data('payer') // Extract info from data-* attributes
    var amount = button.data('amount') // Extract info from data-* attributes
    var submitTime = button.data('submittime')
    var modal = $(this)
    modal.find('.modal-title').text("Update Expense Record")
    // Fields for current expense values
    modal.find('#oldDescription').val(description)
    modal.find('#oldCategory').val(category)
    modal.find('#oldDate').val(date)
    modal.find('#oldPayer').val(payer)
    modal.find('#oldAmount').val(amount)
    modal.find('#submitTime').val(submitTime)
    // Fields for updating the expense
    modal.find('#description').val(description)
    modal.find('#category').val(category)
    modal.find('#date').val(date)
    modal.find('#payer').val(payer)
    modal.find('#amount').val(amount)
})

// As the modal becomes hidden (CSS transitions are 100% finished), clear the fields from the modal
$('#updateModal').on('hidden.bs.modal', function () {
    $('#description').val('')
    $('#category').val('')
    $('#date').val('')
    $('#payer').val('')
    $('#amount').val('')

    // Make sure the UX toggles back to the default 'update expense' mode (instead of delete)
    if (isDeleteUX == true) {
        toggleDeleteUX();
        isDeleteUX = false;
    }
})
