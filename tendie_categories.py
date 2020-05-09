from cs50 import SQL
from flask import request, session
from flask_session import Session

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///budget.db")


# Gets and return the users spend categories
def getSpendCategories(userID):
    categories = db.execute(
        "SELECT categories.id, categories.name FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID",
        usersID=userID)

    return categories


# Get and return all spend categories from the category library
def getSpendCategoryLibrary():
    categories = db.execute("SELECT id, name FROM categories")
    return categories


# Get and return the name of a category from the library
def getSpendCategoryName(categoryID):
    name = db.execute(
        "SELECT name FROM categories WHERE id = :categoryID", categoryID=categoryID)

    return name[0]["name"]


# Gets and return the users budgets, and for each budget the categories they've selected
def getBudgetsSpendCategories(userID):
    budgetsWithCategories = db.execute("SELECT budgets.name AS 'BudgetName', categories.id AS 'CategoryID', categories.name AS 'CategoryName' FROM budgetCategories INNER JOIN budgets on budgetCategories.budgets_id = budgets.id INNER JOIN categories on budgetCategories.category_id = categories.id WHERE budgets.user_id = :usersID ORDER BY budgets.name, categories.name",
                                       usersID=userID)

    return budgetsWithCategories


# Gets and returns the users budgets for a specific category ID
def getBudgetsFromSpendCategory(categoryID, userID):
    budgets = db.execute("SELECT budgets.id AS 'BudgetID', budgets.name AS 'BudgetName', categories.id AS 'CategoryID', categories.name AS 'CategoryName' FROM budgetCategories INNER JOIN budgets on budgetCategories.budgets_id = budgets.id INNER JOIN categories on budgetCategories.category_id = categories.id WHERE budgets.user_id = :usersID AND budgetCategories.category_id = :categoryID ORDER BY budgets.name, categories.name", usersID=userID, categoryID=categoryID)

    return budgets


# Updates budgets where an old category needs to be replaced with a new one (e.g. renaming a category)
def updateSpendCategoriesInBudgets(budgets, oldCategoryID, newCategoryID):
    for budget in budgets:
        # Update existing budget record with the new category ID
        db.execute("UPDATE budgetCategories SET category_id = :newID WHERE budgets_id = :budgetID AND category_id = :oldID",
                   newID=newCategoryID, budgetID=budget["BudgetID"], oldID=oldCategoryID)


# Updates budgets where a category needs to be deleted
def deleteSpendCategoriesInBudgets(budgets, categoryID):
    for budget in budgets:
        # Delete existing budget record with the old category ID
        db.execute("DELETE FROM budgetCategories WHERE budgets_id = :budgetID AND category_id = :categoryID",
                   budgetID=budget["BudgetID"], categoryID=categoryID)


# Generates a ditionary containing all spend categories and the budgets associated with each category
def generateSpendCategoriesWithBudgets(categories, categoryBudgets):
    categoriesWithBudgets = []

    # Loop through every category
    for category in categories:
        # Build a dictionary to hold category ID + Name, and a list holding all the budgets which have that category selected
        categoryWithBudget = {"id": None, "name": None, "budgets": []}
        categoryWithBudget["id"] = category["id"]
        categoryWithBudget["name"] = category["name"]

        # Insert the budget for the spend category if it exists
        for budget in categoryBudgets:
            if category["name"] == budget["CategoryName"]:
                categoryWithBudget["budgets"].append(budget["BudgetName"])

        # Add the completed dict to the list
        categoriesWithBudgets.append(categoryWithBudget)

    return categoriesWithBudgets


# Checks if the category name exists in the 'library' or 'registrar' (categories table) - if so, return the ID for it so it can be passed to below add
def existsInLibrary(newName):
    # Query the library for a record that matches the name
    row = db.execute(
        "SELECT * FROM categories WHERE LOWER(name) = :name", name=newName.lower())

    if row:
        return True
    else:
        return False


# Get category ID from DB
def getCategoryID(categoryName, userID=None):
    # If no userID is supplied, then it's searching the category library
    if userID is None:
        categoryID = db.execute(
            "SELECT id FROM categories WHERE LOWER(name) = :name", name=categoryName.lower())

        if not categoryID:
            return None
        else:
            return categoryID[0]["id"]

    # Otherwise search the users selection of categories
    else:
        categoryID = db.execute(
            "SELECT categories.id FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID AND LOWER(categories.name) = :name", usersID=userID, name=categoryName.lower())

        if not categoryID:
            return None
        else:
            return categoryID[0]["id"]


# Checks if the category name exists in the users seleciton of categories (userCategories table) - if so, just return as False?
def existsForUser(newName, userID):
    # Query the library for a record that matches the name
    row = db.execute(
        "SELECT categories.id FROM userCategories INNER JOIN categories ON userCategories.category_id = categories.id WHERE userCategories.user_id = :usersID AND LOWER(categories.name) = :name", usersID=userID, name=newName.lower())

    if row:
        return True
    else:
        return False


# Adds a category to the database (but not to any specific users account)
def addCategory_DB(newName):
    # Create a new record in categories table
    categoryID = db.execute(
        "INSERT INTO categories (name) VALUES (:name)", name=newName)

    return categoryID


# Adds a category to the users account
def addCategory_User(categoryID, userID):
    db.execute("INSERT INTO userCategories (user_id, category_id) VALUES (:usersID, :categoryID)",
               usersID=userID, categoryID=categoryID)


# Deletes a category from the users account
def deleteCategory_User(categoryID, userID):
    db.execute("DELETE FROM userCategories WHERE user_id = :usersID AND category_id = :categoryID",
               usersID=userID, categoryID=categoryID)


# Update just the spend categories of expense records (used for category renaming)
def updateExpenseCategoryNames(oldCategoryName, newCategoryName, userID):
    db.execute("UPDATE expenses SET category = :newName WHERE user_id = :usersID AND category = :oldName",
               newName=newCategoryName, usersID=userID, oldName=oldCategoryName)


# Rename a category
def renameCategory(oldCategoryID, newCategoryID, oldCategoryName, newCategoryName, userID):
    # Add the renamed category to the users account
    addCategory_User(newCategoryID, userID)

    # Delete the old category from their account
    deleteCategory_User(oldCategoryID, userID)

    # Update users budgets (if any exist) that are using the old category to the new one
    budgets = getBudgetsFromSpendCategory(oldCategoryID, userID)

    if budgets:
        updateSpendCategoriesInBudgets(budgets, oldCategoryID, newCategoryID)

    # Update users expense records that are using the old category to the new one
    updateExpenseCategoryNames(oldCategoryName, newCategoryName, userID)
