// SUMMARY: this file handles all of the functionality on the 'Your Account' page of Tendie Tracker.

///////////////////////////////////////////////////////////////////////////////////////
// Payer Collapseables (sets focus, clears input field, and collapses areas for UX)
///////////////////////////////////////////////////////////////////////////////////////

// Set focus to new payer name field when collapsed area is shown
$('#collapsePayer').on('shown.bs.collapse', function () {
    $('#payerName').trigger('focus');
})

// Clear new payer name field when collapsed area is hidden
$('#collapsePayer').on('hidden.bs.collapse', function () {
    $('#payerName').val('');
})

// Collapse 'Manage Payers' area when 'Add Payer' is clicked
$("#btnAddPayer").click(function (e) {
    $("#collapsePayers").collapse("hide");
});

// Collapse 'Add Payer' area when 'Manage Payers' is clicked
$("#btnManagePayers").click(function (e) {
    $("#collapsePayer").collapse("hide");
});

///////////////////////////////////////////////////////////////////////////////////////
// Payer Rename/Delete Modals
///////////////////////////////////////////////////////////////////////////////////////

// While the modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the fields
$('#renameModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var payer = button.data('payer'); // Extract info from data-* attributes
    var modal = $(this);
    modal.find('.modal-title').text("Rename payer '" + payer + "'");
    modal.find('#oldpayer').val(payer);
})

// As the modal becomes hidden (CSS transitions are 100% finished), clear the 'newpayer' and alert message fields
$('#renameModal').on('hidden.bs.modal', function () {
    $('#newpayer').val('');
})

// While the modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the fields
$('#deleteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var payer = button.data('payer'); // Extract info from data-* attributes
    var modal = $(this);
    modal.find('.modal-title').text("Delete payer '" + payer + "'");
    modal.find('#delete').val(payer);
})

///////////////////////////////////////////////////////////////////////////////////////
// Income Functionality (on collapse, sets focus and clear input field)
///////////////////////////////////////////////////////////////////////////////////////

// Set focus to new income field when collapsed area is shown
$('#collapseIncome').on('shown.bs.collapse', function () {
    $('#income').trigger('focus');
})
// Clear new income name field when collapsed area is hidden
$('#collapseIncome').on('hidden.bs.collapse', function () {
    $('#income').val('');
})

///////////////////////////////////////////////////////////////////////////////////////
// Password Functionality (on collapse, sets focus and clear input field)
///////////////////////////////////////////////////////////////////////////////////////

// Set focus to new password field when collapsed area is shown
$('#collapsePassword').on('shown.bs.collapse', function () {
    $('#currentPassword').trigger('focus');
})
// Clear password fields when collapsed area is hidden
$('#collapsePassword').on('hidden.bs.collapse', function () {
    $('#currentPassword').val('');
    $('#newPassword').val('');
})