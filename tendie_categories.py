import os

from flask import request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict

# Create engine object to manage connections to DB, and scoped session to separate user interactions with DB
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Gets and return the users spend categories
def getSpendCategories(userID):
    results = db.execute(
        "SELECT categories.name FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID",
        {"usersID": userID}).fetchall()

    categories = convertSQLToDict(results)

    return categories


# Gets and return the users *inactive* spend categories from their expenses (e.g. they deleted a category and didn't update their expense records that still use the old category name)
def getSpendCategories_Inactive(userID):
    results = db.execute(
        "SELECT category FROM expenses WHERE user_id = :usersID AND category NOT IN(SELECT categories.name FROM usercategories INNER JOIN categories ON categories.id = usercategories.category_id WHERE user_id = :usersID) GROUP BY category",
        {"usersID": userID}).fetchall()

    categories = convertSQLToDict(results)

    return categories


# Get and return all spend categories from the category library
def getSpendCategoryLibrary():
    results = db.execute("SELECT id, name FROM categories").fetchall()

    convertSQLToDict(results)

    return categories


# Get and return the name of a category from the library
def getSpendCategoryName(categoryID):
    name = db.execute(
        "SELECT name FROM categories WHERE id = :categoryID", {"categoryID": categoryID}).fetchone()[0]

    return name


# Gets and return the users budgets, and for each budget the categories they've selected
def getBudgetsSpendCategories(userID):
    results = db.execute("SELECT budgets.name AS budgetname, categories.id AS categoryid, categories.name AS categoryname FROM budgetcategories INNER JOIN budgets on budgetcategories.budgets_id = budgets.id INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgets.user_id = :usersID ORDER BY budgets.name, categories.name",
                         {"usersID": userID}).fetchall()

    budgetsWithCategories = convertSQLToDict(results)

    return budgetsWithCategories


# Gets and returns the users budgets for a specific category ID
def getBudgetsFromSpendCategory(categoryID, userID):
    results = db.execute("SELECT budgets.id AS budgetid, budgets.name AS budgetname, categories.id AS categoryid, categories.name AS categoryname FROM budgetcategories INNER JOIN budgets on budgetcategories.budgets_id = budgets.id INNER JOIN categories on budgetcategories.category_id = categories.id WHERE budgets.user_id = :usersID AND budgetcategories.category_id = :categoryID ORDER BY budgets.name, categories.name", {
        "usersID": userID, "categoryID": categoryID}).fetchall()

    budgets = convertSQLToDict(results)

    return budgets


# Updates budgets where an old category needs to be replaced with a new one (e.g. renaming a category)
def updateSpendCategoriesInBudgets(budgets, oldCategoryID, newCategoryID):
    for budget in budgets:
        # Update existing budget record with the new category ID
        db.execute("UPDATE budgetcategories SET category_id = :newID WHERE budgets_id = :budgetID AND category_id = :oldID",
                   {"newID": newCategoryID, "budgetID": budget["budgetid"], "oldID": oldCategoryID})
    db.commit()


# Updates budgets where a category needs to be deleted
def deleteSpendCategoriesInBudgets(budgets, categoryID):
    for budget in budgets:
        # Delete existing budget record with the old category ID
        db.execute("DELETE FROM budgetcategories WHERE budgets_id = :budgetID AND category_id = :categoryID",
                   {"budgetID": budget["budgetid"], "categoryID": categoryID})

    db.commit()


# Generates a ditionary containing all spend categories and the budgets associated with each category
def generateSpendCategoriesWithBudgets(categories, categoryBudgets):
    categoriesWithBudgets = []

    # Loop through every category
    for category in categories:
        # Build a dictionary to hold category ID + Name, and a list holding all the budgets which have that category selected
        categoryWithBudget = {"name": None, "budgets": []}
        categoryWithBudget["name"] = category["name"]

        # Insert the budget for the spend category if it exists
        for budget in categoryBudgets:
            if category["name"] == budget["categoryname"]:
                categoryWithBudget["budgets"].append(budget["budgetname"])

        # Add the completed dict to the list
        categoriesWithBudgets.append(categoryWithBudget)

    return categoriesWithBudgets


# Checks if the category name exists in the 'library' or 'registrar' (categories table) - if so, return the ID for it so it can be passed to below add
def existsInLibrary(newName):
    # Query the library for a record that matches the name
    row = db.execute(
        "SELECT * FROM categories WHERE LOWER(name) = :name", {"name": newName.lower()}).fetchone()

    if row:
        return True
    else:
        return False


# Get category ID from DB
def getCategoryID(categoryName, userID=None):
    # If no userID is supplied, then it's searching the category library
    if userID is None:
        categoryID = db.execute(
            "SELECT id FROM categories WHERE LOWER(name) = :name", {"name": categoryName.lower()}).fetchone()

        if not categoryID:
            return None
        else:
            return categoryID["id"]

    # Otherwise search the users selection of categories
    else:
        categoryID = db.execute(
            "SELECT categories.id FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID AND LOWER(categories.name) = :name", {"usersID": userID, "name": categoryName.lower()}).fetchone()

        if not categoryID:
            return None
        else:
            return categoryID["id"]


# Checks if the category name exists in the users seleciton of categories (usercategories table) - if so, just return as False?
def existsForUser(newName, userID):
    # Query the library for a record that matches the name
    row = db.execute(
        "SELECT categories.id FROM usercategories INNER JOIN categories ON usercategories.category_id = categories.id WHERE usercategories.user_id = :usersID AND LOWER(categories.name) = :name", {"usersID": userID, "name": newName.lower()}).fetchone()

    if row:
        return True
    else:
        return False


# Adds a category to the database (but not to any specific users account)
def addCategory_DB(newName):
    # Create a new record in categories table
    categoryID = db.execute(
        "INSERT INTO categories (name) VALUES (:name) RETURNING id", {"name": newName}).fetchone()[0]
    db.commit()

    return categoryID


# Adds a category to the users account
def addCategory_User(categoryID, userID):
    db.execute("INSERT INTO usercategories (user_id, category_id) VALUES (:usersID, :categoryID)",
               {"usersID": userID, "categoryID": categoryID})
    db.commit()


# Deletes a category from the users account
def deleteCategory_User(categoryID, userID):
    db.execute("DELETE FROM usercategories WHERE user_id = :usersID AND category_id = :categoryID",
               {"usersID": userID, "categoryID": categoryID})
    db.commit()


# Update just the spend categories of expense records (used for category renaming)
def updateExpenseCategoryNames(oldCategoryName, newCategoryName, userID):
    db.execute("UPDATE expenses SET category = :newName WHERE user_id = :usersID AND category = :oldName",
               {"newName": newCategoryName, "usersID": userID, "oldName": oldCategoryName})
    db.commit()


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


# Delete a category
def deleteCategory(categoryID, userID):
    # Get budgets that are currently using the category they want to delete
    budgets = getBudgetsFromSpendCategory(categoryID, userID)

    # Delete categories from the users budgets
    if budgets:
        deleteSpendCategoriesInBudgets(budgets, categoryID)

    # Delete the category from the users account
    deleteCategory_User(categoryID, userID)
