// SUMMARY: this file handles all of the functionality to add 1 or more expenses on the 'Add Expenses' page of Tendie Tracker.

// Non-Flask/Jinja vars
var rowCount;
var selectedRow;

// Loads data from Flask/Jinja that is passed from the request
function loadData(categoryData, dateData, payersData) {
    categories = JSON.parse(categoryData);
    today = dateData;
    payers = JSON.parse(payersData);
}

// Add row to table
function addRow() {
    // Build the HTML string for a new row
    let newRow = "<tr> <td onclick='selectRow(this);'><br></td><td><textarea class='form-control-sm' name='description.' form='expenseForm' required maxlength='200'></textarea></td><td><select class='form-control-sm' name='category.' form='expenseForm' required'>"

    // Loop through the categories
    for (i = 0; i < categories.length; i++) {
        newRow += "<option value='" + categories[i].name + "'>" + categories[i].name + "</option>"
    }

    newRow += "</select></td><td><input type='date' class='form-control-sm' name='date.' form='expenseForm' required value='" + today + "'></td><td><select class='form-control-sm' name='payer.' form='expenseForm' required><option value='Self'>Self</option>"

    // Loop through the payers
    for (i = 0; i < payers.length; i++) {
        newRow += "<option value='" + payers[i].name + "'>" + payers[i].name + "</option>"
    }

    // Complete the HTML string for the new row
    newRow += "</select></td><td><input type='text' class='form-control-sm' name='amount.' form='expenseForm' size='10' placeholder='$' maxlength='10' required pattern='(?=.*?\\d)^(([1-9]\\d{0,2}(\\d{3})*)|\\d+)?(\\.\\d{1,2})?$' title='Format must be currency value without dollar sign or commas e.g. 1, 2.50, 1500.75'></td></tr>"

    // Append the table by adding a new row to it with the constructed HTML string
    $("#expenseTable tbody").append(newRow);

    // Update row numbering, names of elements, and button availability
    rowCount = countRows();
    updateTableElements(rowCount);
    updateRowButton();

    // Lastly, focus the users attention on the new row
    $("textarea[name='description." + rowCount + "']").focus()
}


// Counts and returns the current number of rows
function countRows() {
    let table = document.getElementById("expenseTable");
    let rows = table.children[1].childElementCount;
    return rows;
}

// Update # column based on amount of rows added/removed, and update element names in table to be unique based on row count
function updateTableElements(rowCount) {
    let table = document.getElementById("expenseTable");

    for (let i = 0; i < rowCount; i++) {
        // Update the column numbering so row numbers are understandable to user
        table.children[1].children[i].children[0].innerHTML = String(i + 1) + " <i class='far fa-hand-pointer'></i>"

        // Update the element names so every element in a row is numbered correctly/uniquely and can be sent to server via POST
        for (let j = 0; j < 5; j++) {
            let oldName = table.children[1].children[i].children[j + 1].firstElementChild.name;
            let n = oldName.indexOf(".");
            let newName = oldName.substring(0, n + 1) + String(i + 1);
            table.children[1].children[i].children[j + 1].firstElementChild.setAttribute('name', newName);
        }
    }
}

// Select a row from the table (so it can be deleted if the user wants to)
function selectRow(cell) {
    let row = cell.parentNode;
    // Remove the highlight if the user clicks the same row
    if (row.className == "table-danger") {
        $("tr").removeClass("table-danger");
        $("textarea").removeClass("selected");
        $("select").removeClass("selected");
        $("input").removeClass("selected");

        // Disable the delete button
        document.getElementById("btnDeleteRow").disabled = true;
    }

    // Clear the last highlighted row and highlight the new one
    else {
        // Remove existing highlighted rows
        $("tr").removeClass("table-danger");
        $("textarea").removeClass("selected");
        $("select").removeClass("selected");
        $("input").removeClass("selected");

        // Highlight the selected row
        $(row).addClass("table-danger");

        // Enable the delete button if there's more than 1 row
        if (countRows() > 1) {
            document.getElementById("btnDeleteRow").disabled = false;
        }
        else {
            document.getElementById("btnDeleteRow").disabled = true;
        }


        // Set global variable to row if user wants to delete the row
        selectedRow = row;
    }
}

// Remove a row from the table
function removeRow(row) {
    $(row).remove();

    // Disable the delete button
    document.getElementById("btnDeleteRow").disabled = true;

    // Update row numbering, names of elements, and button availability
    rowCount = countRows();
    updateTableElements(rowCount);
    updateRowButton();
}

// Enables/disables the new row button - arbitrarily set to a max of 10 rows
function updateRowButton() {
    count = countRows();

    if (count < 10) {
        // Enable the add row button
        document.getElementById("btnNewRow").disabled = false;
    }

    else {
        // Disable the add row button
        document.getElementById("btnNewRow").disabled = true;
    }
}