import database
import models
import reports
import datetime
from datetime import date

def putProductOnSale(db):
    print("==========")
    print("Create a new discount:")
    print("==========")

    discount = models.Discount()

    # Prompt for Store ID
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Choose store for sale (Store ID): "))
            store = database.validateStoreId(db, storeId)
            if len(database.getProducts(db, storeIds=[storeId])) == 0:
                print("This store has no products.  Please select another.")
                continue
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for Product ID
    reports.getAllProducts(db, storeIds = [storeId])
    while True:
        try:
            productId = int(input("Choose product from store to put on sale (Product ID): "))
            product = database.validateProductId(db, productId, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Enter percentage
    while True:
        try:
            discount.percent = float(input("Enter sale percentage (between 0 - 1): "))
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Enter sale start date
    while True:
        try:
            saleStartDt = input(f"Enter a sale start date in YYYY-MM-DD format (today or in the future): ")
            year, month, day = map(int, saleStartDt.split('-'))
            discount.startDt = datetime.date(year, month, day)
            if discount.startDt >= date.today():
                break
            raise Exception()
        except Exception as error:
            print("Invalid input.  Try again.")

    # Enter sale end date
    while True:
        try:
            saleEndDt = input(f"Enter a sale end date in YYYY-MM-DD format: ")
            year, month, day = map(int, saleEndDt.split('-'))
            discount.endDt = datetime.date(year, month, day)
            if discount.endDt > discount.startDt:
                break
            raise Exception()
        except Exception as error:
            print("Invalid input.  Try again.")

    database.addDiscountForProduct(db, discount, product)
    print("Discount successfully added to product.")

def modifyDiscount(db):
    print("==========")
    print("Update a discount:")
    print("==========")

    # Prompt for discount ID
    reports.getAllDiscounts(db)
    while True:
        try:
            discountId = int(input("Choose discount to update (Discount ID): "))
            discount = database.validateDiscountId(db, discountId)
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Enter percentage
    while True:
        try:
            newPercent = input("Enter new sale percentage (0 - 1): ")
            if len(newPercent.strip()) != 0:
                discount.percent = float(newPercent)
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Enter sale start date
    while True:
        try:
            saleStartDt = input(f"Enter a new sale start date in YYYY-MM-DD format (today or in the future): ")
            if len(saleStartDt.strip()) == 0:
                break
            year, month, day = map(int, saleStartDt.split('-'))
            discount.startDt = datetime.date(year, month, day)
            if discount.startDt >= date.today():
                break
            raise Exception()
        except Exception as error:
            print("Invalid input.  Try again.")

    # Enter sale end date
    while True:
        try:
            saleEndDt = input(f"Enter a new sale end date in YYYY-MM-DD format: ")
            if len(saleEndDt.strip()) == 0:
                break
            year, month, day = map(int, saleEndDt.split('-'))
            discount.endDt = datetime.date(year, month, day)
            if discount.endDt > discount.startDt:
                break
            raise Exception()
        except Exception as error:
            print("Invalid input.  Try again.")

    database.updateDiscount(db, discount)
    print("Discount successfully updated.")

def sourceNewSupplier(db):
    print("==========")
    print("Source a new supplier:")
    print("==========")

    supplier = models.Supplier()

    # Prompt for name
    while True:
        supplier.name = input("Name: ")
        if len(supplier.name.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for address
    while True:
        supplier.location = input("Address: ")
        if len(supplier.location.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for email
    while True:
        supplier.email = input("Email: ")
        if len(supplier.email.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for phone
    while True:
        supplier.phone = input("Phone: ")
        if len(supplier.phone.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    database.sourceSupplier(db, supplier)
    print("New supplier successfully added.")

def updateSupplierInfo(db):
    print("==========")
    print("Update a supplier's info:")
    print("==========")

    # Prompt for supplier
    reports.getAllSuppliers(db)
    while True:
        try:
            supplierId = int(input("Select a supplier to update (Supplier ID): "))
            supplier = database.validateSupplierId(db, supplierId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for name
    newSupplierName = input(f"Enter a new supplier name ({supplier.name}): ")
    if len(newSupplierName.strip()) != 0:
        supplier.name = newSupplierName.strip()

    # Prompt for address
    newSupplierLocation = input(f"Enter a new supplier address ({supplier.location}): ")
    if len(newSupplierLocation.strip()) != 0:
        supplier.location = newSupplierLocation.strip()

    # Prompt for email
    newSupplierEmail = input(f"Enter a new supplier email ({supplier.email}): ")
    if len(newSupplierEmail.strip()) != 0:
        supplier.email = newSupplierEmail.strip()

    # Prompt for phone
    newSupplierPhone = input(f"Enter a new supplier phone ({supplier.phone}): ")
    if len(newSupplierPhone.strip()) != 0:
        supplier.phone = newSupplierPhone.strip()

    database.updateSupplierInfo(db, supplier)
    print("Supplier information successfully updated.")

def removeSupplier(db):
    print("==========")
    print("Remove a supplier:")
    print("==========")

    # Prompt for supplier
    reports.getAllSuppliers(db)
    while True:
        try:
            supplierId = int(input("Enter a supplier (Supplier ID): "))
            supplier = database.validateSupplierId(db, supplierId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    database.removeSupplier(db, supplier)
    print("Supplier successfully removed.")

def generateBillForSupplier(db):
    pass

def generateRewardChecks(db):
    pass

