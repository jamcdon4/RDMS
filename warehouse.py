import reports
import database
import helpers
import models
import datetime

def updateProductInformation(db):
    print("==========")
    print("Update product information:")
    print("==========")

    # Prompt for Store ID
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Choose store to update product at (Store ID): "))
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
            productId = int(input("Choose product to update (Product ID): "))
            productToUpdate = database.validateProductId(db, productId, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for new name
    newName = input(f"Enter a new name for product ({productToUpdate.name}): ")
    if len(newName.strip()) != 0:
        productToUpdate.name = newName.strip()

    # Prompt for new price
    while True:
        try:
            newPrice = input(f"Enter a new price for product ({helpers.getFormattedPrice(productToUpdate.price)}): ")
            if len(newPrice.strip()) == 0:
                break
            productToUpdate.price = float(newPrice)
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Prompt for new production date
    while True:
        try:
            newProductionDate = input(f"Enter a new production date in YYYY-MM-DD format ({productToUpdate.productionDt}): ")
            if len(newProductionDate.strip()) == 0:
                break
            year, month, day = map(int, newProductionDate.split('-'))
            productToUpdate.productionDt = datetime.date(year, month, day)
            break
        except Exception as error:
            print("Invalid input.  Try again.")

    # Prompt for new expiration date
    while True:
        try:
            newExpirationDt = input(f"Enter a new expiration date in YYYY-MM-DD format ({productToUpdate.productionDt}): ")
            if len(newExpirationDt.strip()) == 0:
                break
            year, month, day = map(int, newExpirationDt.split('-'))
            productToUpdate.expirationDt = datetime.date(year, month, day)
            break
        except Exception as error:
            print("Invalid input.  Try again.")

    database.updateProductInfo(db, productToUpdate)
    print("Product successfully updated.")

def addNewProduct(db):
    print("==========")
    print("Add new product:")
    print("==========")

    product = models.Product()

    # Prompt for store ID to update
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Choose store to add a new product to (Store ID): "))
            store = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for product name
    while True:
        product.name = input("Product name: ")
        if len(product.name.strip()) == 0:
            print("Invalid input.  Try again.")
        else:
            break

    # Prompt for price
    while True:
        try:
            product.price = float(input("Product price: "))
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Prompt for cost
    while True:
        try:
            product.cost = float(input("Product cost: "))
            break
        except ValueError:
            print("Invalid input.  Try again.")

    # Prompt for new production date
    while True:
        try:
            productionDate = input(f"Production date in YYYY-MM-DD format ({product.productionDt}): ")
            year, month, day = map(int, productionDate.split('-'))
            product.productionDt = datetime.date(year, month, day)
            break
        except Exception as error:
            print("Invalid input.  Try again.")

    # Prompt for new expiration date
    while True:
        try:
            expirationDt = input(f"Expiration date in YYYY-MM-DD format ({product.productionDt}): ")
            year, month, day = map(int, expirationDt.split('-'))
            product.expirationDt = datetime.date(year, month, day)
            break
        except Exception as error:
            print("Invalid input.  Try again.")

    # Prompt for supplier
    reports.getAllSuppliers(db)
    while True:
        try:
            supplierId = int(input("Product supplier (Supplier ID): "))
            product.supplier = database.validateSupplierId(db, supplierId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    product.id = (None, storeId)
    product.quantity = 0
    database.addNewProduct(db, product)
    print("Product successfully added.")
    print("Note that the product quantity is 0.  Please order a shipment from the supplier.")

def orderProduct(db):
    print("==========")
    print("Order product:")
    print("==========")

    # Prompt for Supplier ID
    reports.getAllSuppliers(db)
    while True:
        try:
            supplierId = int(input("Choose supplier to order from (Supplier ID): "))
            supplier = database.validateSupplierId(db, supplierId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for Store ID
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Choose store to order product to (Store ID): "))
            store = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    products = {}
    shipmentList = []
    doneSelectingProducts = False
    while True:
        print("Please hit return at any point when done selecting products.")

        # Prompt for Product ID
        reports.getAllProducts(db, supplierIds = [supplierId])
        while True:
            try:
                productId = input("Choose product to order (Product ID): ")
                if len(productId.strip()) == 0:
                    doneSelectingProducts = True
                    break
                productId = int(productId)
                product = database.getProductForOrder(db, productId)
                break
            except (ValueError, LookupError):
                print("Invalid input.  Try again.")

        if doneSelectingProducts:
            break

        # Prompt for quantity
        while True:
            try:
                quantity = input("Enter quantity to order: ")
                if len(quantity.strip()):
                    doneSelectingProducts == True
                    break
                quantity = int(quantity)
                break
            except ValueError:
                print("Invalid input.  Try again.")

        if doneSelectingProducts:
            break

        # make sure you are ordering product to new store
        products[product.id] = quantity

        shipmentList.append((product.name, quantity))

        print(f"Current shipment: {shipmentList}")

    database.orderShipmentOfProducts(db, products, store, supplier)
    print("Shipment of products ordered.")

def transferProductsBetweenStores(db):
    print("==========")
    print("Transfer product:")
    print("==========")

    # Prompt for Store ID
    reports.getAllStores(db)
    while True:
        try:
            storeId = int(input("Choose store to transfer product from (Store ID): "))
            storeFrom = database.validateStoreId(db, storeId)
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
            productId = int(input("Choose product from store to transfer (Product ID): "))
            product = database.validateProductId(db, productId, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for Store ID To
    reports.getAllStores(db)
    while True:
        try:
            storeIdTo = int(input("Choose store to transfer product to (Store ID): "))
            storeTo = database.validateStoreId(db, storeId)
            break
        except (ValueError, LookupError):
            print("Invalid input.  Try again.")

    # Prompt for quantity
    while True:
        try:
            quantity = int(input("Enter quantity to transfer: "))
            if quantity <= 0 or quantity > product.quantity:
                raise ValueError()
            break
        except ValueError:
            print("Invalid input.  Try again.")

    database.manageProductTransfers(db, product, quantity, storeFrom, storeTo)
    print("Product successfully transferred.")