import mysql.connector as mysql
import models
import datetime
from datetime import date

###################################################################################################################

# Manages all database connections and transactions for the lifetime of the application.
class DatabaseManager:
    def __init__(self):
        self.conn = None

    # Start a connection to the database, run only once on app start
    def initializeConnection(self):
        try:
            conn = mysql.connect(
                host='classdb2.csc.ncsu.edu',
                database='jamcdon3',
                user='jamcdon3',
                password='200098947!'
            )
            # Explicitly set autocommit to true so that we can start the transaction
            # Only when we want to query, with our desired isolation level
            conn.autocommit = True
            self.conn = conn
            print("Connected to database.")
        except mysql.Error as error:
            print(f'Failed to connect to database: {error}')
            exit()

    # Close and cleanup connection, run only once on app exit
    def closeConnection(self):
        if self.conn is not None and self.conn.is_connected():
            self.conn.close()
            print("Connection closed.")

    # Run a transaction of one or more queries.
    # Transactions run at isolation level 'SERIALIZABLE'
    # On error, the entire transaction is rolled back.
    def query(self, query):
        cursor = self.conn.cursor(buffered=True)
        try:
            self.conn.start_transaction(isolation_level='SERIALIZABLE')
            results = cursor.execute(query, multi=True)
            self.conn.commit()
            for result in results:
                if result.with_rows:
                    return result.fetchall()
            return None
        except Exception as error:
            print(f"Unable to execute query `{query}` with error: {error}")
            self.conn.rollback()
        finally:
            cursor.close()

###################################################################################################################

# Check for valid transaction ID by locating the transaction with that ID
def validateTransactionId(db, transactionId):
    transaction = getTransactions(db, transactionIds = [transactionId])
    if len(transaction) == 0:
        raise LookupError()
    transaction = transaction[0]
    return transaction

# Check for valid discount ID by locating the discount with that ID
def validateDiscountId(db, discountId):
    discount = getDiscounts(db, [discountId])
    if len(discount) == 0:
        raise LookupError()
    discount = discount[0]
    return discount

# Check for valid product ID by locating the product with that ID
def validateProductId(db, productId, storeId):
    product = getProducts(db, [(productId, storeId)])
    if len(product) == 0:
        raise LookupError()
    product = product[0]
    return product

# Check for valid supplier ID by locating the supplier with that ID
def validateSupplierId(db, supplierId):
    supplier = getSuppliers(db, [supplierId], False)
    if len(supplier) == 0:
        raise LookupError()
    supplier = supplier[0]
    return supplier

# Check for valid store ID by locating the store with that ID
def validateStoreId(db, storeId):
    store = getStores(db, [storeId])
    if len(store) == 0:
        raise LookupError()
    store = store[0]
    if len(store.staff) == 0:
        raise AttributeError()
    return store

# Check for valid staff ID by locating the staff with that ID
def validateStaffId(db, staffId):
    staff = getStaff(db, [staffId])
    if len(staff) == 0:
        raise LookupError()
    staff = staff[0]
    return staff

# Check for valid customer ID by locating the customer with that ID
def validateCustomerId(db, customerId):
    customer = getCustomers(db, [customerId])
    if len(customer) == 0:
        raise LookupError()
    customer = customer[0]
    return customer

# Add a new customer, and a new membership for that customer
def registerNewCustomer(db, customer, storeId, staffId):
    membershipQuery = f"""
    INSERT INTO Memberships
    (
        MemID, 
        StoreID, 
        StaffID, 
        SignUpDt, 
        MembershipStatus, 
        LevelID, 
        Length
    )
    VALUES
    (
        (SELECT NewMemID FROM (SELECT 1 + IFNULL((SELECT MemID FROM Memberships ORDER BY MemID DESC LIMIT 1), 0) AS NewMemID) InnerMembership),
        {storeId},
        {staffId},
        \"{customer.membership.signUpDt}\",
        1,
        (SELECT LevelID FROM MembershipLevels WHERE LevelName = \"{customer.membership.level.name}\"),
        {customer.membership.length}
    );
    """
    customerQuery = f"""
    INSERT INTO Customers
    (
        CustID,
        FirstName,
        LastName,
        Address,
        Email,
        Phone,
        MemID
    )
    VALUES
    (
        (SELECT NewCustID FROM (SELECT 1 + IFNULL((SELECT CustID FROM Customers ORDER BY MemID DESC LIMIT 1), 0) AS NewCustID) InnerCustomers),
        \"{customer.firstname}\",
        \"{customer.lastname}\",
        \"{customer.address}\",
        \"{customer.email}\",
        \"{customer.phone}\",
        (SELECT MemID FROM Memberships ORDER BY MemID DESC LIMIT 1)
    );
    """
    fullQuery = ''.join([membershipQuery, customerQuery])
    db.query(fullQuery)

# Change basic customer information
def updateCustomerInfo(db, customer):
    customerQuery = f"""
    UPDATE Customers
    SET
        FirstName = \"{customer.firstname}\",
        LastName = \"{customer.lastname}\",
        Address = \"{customer.address}\",
        Email = \"{customer.email}\",
        Phone = \"{customer.phone}\"
    WHERE
        CustID = {customer.id};
    """

    db.query(customerQuery)

# Delete a customer
def unregisterCustomer(db, customer):
    customerQuery = f"""
    DELETE FROM Customers
    WHERE
        CustID = {customer.id};
    """
    memQuery = f"""
    DELETE FROM Memberships
    WHERE
        MemID = (SELECT MemID FROM Customers WHERE CustID = {customer.id});
    """

    unregisterQuery = ''.join([customerQuery, memQuery])
    db.query(unregisterQuery)

# Change membership information
def updateMembership(db, customer):
    membershipQuery = f"""
    UPDATE Memberships
    SET
        MembershipStatus = {customer.membership.status},
        LevelID = (SELECT LevelID FROM MembershipLevels WHERE LevelName = \"{customer.membership.level.name}\"),
        Length = {customer.membership.length}
    WHERE
        MemID = (SELECT MemID FROM Customers WHERE CustID = {customer.id});
    """

    db.query(membershipQuery)

# Change store information
def updateStoreInfo(db, store):
    storeQuery = f"""
    UPDATE Stores
    SET
        Phone = \"{store.phone}\",
        Address = \"{store.address}\"
    WHERE
        StoreID = {store.id};
    """
    removeFromCurrentDepartmentQuery = f"""
    DELETE 
    FROM 
        {store.manager.department}
    WHERE
        StaffID = {store.manager.id};
    """
    addToManagerQuery = f"""
    INSERT INTO 
        Manager
    (
        StaffID
    )
    Values
    (
        {store.manager.id}
    );
    """
    updateStoreOfStaff = f"""
    UPDATE Staff
    SET StoreID = {store.id}
    WHERE StaffID = {store.manager.id};
    """
    StaffID = {store.manager.id}
    
    updateStoreQuery = ''.join([removeFromCurrentDepartmentQuery, addToManagerQuery, storeQuery, updateStoreOfStaff])
    db.query(updateStoreQuery)

# Delete a store
def closeStore(db, store):
    storeQuery = f"""
    DELETE FROM Stores
    WHERE
        StoreID = {store.id};
    """

    db.query(storeQuery)

# Create a new store
def openNewStore(db, store):
    storeQuery = f"""
    INSERT INTO Stores
    (
        StoreID,
        Address,
        Phone,
        StaffID
    )
    VALUES
    (
        (SELECT NewStoreID FROM (SELECT 1 + IFNULL((SELECT StoreID FROM Stores ORDER BY StoreID DESC LIMIT 1), 0) AS NewStoreID) InnerStore),
        \"{store.address}\",
        \"{store.phone}\",
        {store.manager.id}
    );
    """
    removeFromCurrentDepartmentQuery = f"""
    DELETE 
    FROM 
        {store.manager.department}
    WHERE
        StaffID = {store.manager.id};
    """
    addToManagerQuery = f"""
    INSERT INTO 
        Manager
    (
        StaffID
    )
    Values
    (
        {store.manager.id}
    );
    """
    updateStoreOfStaff = f"""
    UPDATE Staff
	SET StoreID = (SELECT StoreID FROM Stores ORDER BY StoreID DESC LIMIT 1)
	WHERE StaffID={store.manager.id};
    """

    openStoreQuery = ''.join([removeFromCurrentDepartmentQuery, addToManagerQuery, storeQuery, updateStoreOfStaff])
    db.query(openStoreQuery)

# Find the store an employee works at, kind of a special case
def getStoreForEmployee(db, employeeId):
    staffQuery = f"""
    SELECT
        StoreID
    From
        Staff
    WHERE
        StaffID = {employeeId};
    """

    return db.query(staffQuery)[0][0]

# Get all stores
def getStores(db, storeIds = None):
    filter = "WHERE 1=1"
    if storeIds is not None:
        stores = [str(storeId) for storeId in storeIds]
        filter = filter + f" AND StoreID IN ({','.join(stores)})"

    stores = []
    storeData = db.query(
    f"""
    SELECT 
        *
    FROM
        Stores
    {filter};
    """
    )
    for data in storeData:
        store = models.Store()
        store.id = data[0]
        store.address = data[1]
        store.phone = data[2]
        store.staff = getStaff(db, storeIds = [data[0]])
        manager = [staffMember for staffMember in store.staff if staffMember.id == data[3]]
        if manager is not None and len(manager) > 0:
            store.manager = manager[0]
        stores.append(store)
    return stores

# Add a new staff member
def hireNewStaffMember(db, staffMember, store):
    staffQuery = f"""
    INSERT INTO Staff
    (
        StaffID,
        Name,
        Age,
        Address,
        Email,
        Phone,
        Title,
        StoreID,
        Tenure
    )
    VALUES
    (
        (SELECT NewStaffID FROM (SELECT 1 + IFNULL((SELECT StaffID FROM Staff ORDER BY StaffID DESC LIMIT 1), 0) AS NewStaffID) InnerStaff),
        \"{staffMember.name}\",
        {staffMember.age},
        \"{staffMember.address}\",
        \"{staffMember.email}\",
        \"{staffMember.phone}\",
        \"{staffMember.title}\",
        {store.id},
        \"{staffMember.startDt}\"
    );
    """

    departmentQuery = f"""
    INSERT INTO {staffMember.department}
    (
        StaffID
    )
    VALUES
    (
        (SELECT StaffID FROM Staff ORDER BY StaffID Desc LIMIT 1)
    );
    """

    newStaffMemberQuery = ''.join([staffQuery, departmentQuery])
    db.query(newStaffMemberQuery)

# Change staff member information
def updateStaffInfo(db, staffMember, newDepartment, newStoreId):
    staffQuery = f"""
    UPDATE Staff
    SET
        Name = \"{staffMember.name}\",
        Age = {staffMember.age},
        Address = \"{staffMember.address}\",
        Email = \"{staffMember.email}\",
        Phone = \"{staffMember.phone}\",
        Title = \"{staffMember.title}\",
        StoreID = {newStoreId}
    WHERE
        StaffID = {staffMember.id};
    """

    removeFromOldDeptQuery = ""
    addToDeptQuery = ""
    if len(newDepartment) != 0:
        removeFromOldDeptQuery = f"""
        DELETE FROM 
            {staffMember.department}
        WHERE
            StaffID = {staffMember.id};
        """
        addToDeptQuery = f"""
        INSERT INTO {newDepartment}
        (
            StaffID
        )
        VALUES
        (
            {staffMember.id}
        );
        """

    updateStaffQuery = ''.join([staffQuery, removeFromOldDeptQuery, addToDeptQuery])
    db.query(updateStaffQuery)

# Delete a staff member
def fireStaffMember(db, staffMember):
    staffQuery = f"""
    DELETE FROM
        Staff
    WHERE
        StaffID = {staffMember.id};
    """

    departmentQuery = f"""
    DELETE FROM 
        {staffMember.department}
    WHERE
        StaffID = {staffMember.id};
    """

    fireQuery = ''.join([staffQuery, departmentQuery])
    db.query(fireQuery)

# Get all staff members
def getStaff(db, staffIds = None, storeIds = None, departmentNames = None):
    filter = "WHERE 1=1"
    if staffIds is not None:
        staffMembers = [str(staffId) for staffId in staffIds]
        filter = filter + f" AND FullStaff.StaffID in ({','.join(staffMembers)})"
    elif departmentNames is not None:
        departments = [f"'{departmentName}'" for departmentName in departmentNames]
        filter = filter + f" AND FullStaff.Department in ({','.join(departments)})"
    if storeIds is not None:
        stores = [str(storeId) for storeId in storeIds]
        filter = filter + f" AND FullStaff.StoreID in ({','.join(stores)})"
    
    staff = []
    staffData = db.query(
    f"""
    SELECT *
    FROM 
        (SELECT *, CASE
            WHEN EXISTS(SELECT * FROM Manager m WHERE s.StaffID = m.StaffID) THEN 'Manager'
            WHEN EXISTS(SELECT * FROM Cashier c WHERE s.StaffID = c.StaffID) THEN 'Cashier'
            WHEN EXISTS(SELECT * FROM Registration r WHERE s.StaffID = r.StaffID) THEN 'Registration'
            WHEN EXISTS(SELECT * FROM Billing b WHERE s.StaffID = b.StaffID) THEN 'Billing'
            WHEN EXISTS(SELECT * FROM Warehouse w WHERE s.StaffID = w.StaffID) THEN 'Warehouse'
            END AS Department
        FROM
            Staff s) AS FullStaff
    {filter};
    """
    )
    for data in staffData:
        staffMember = models.Staff()
        staffMember.id = data[0]
        staffMember.address = data[1]
        staffMember.startDt = data[2]
        staffMember.email = data[3]
        staffMember.name = data[4]
        staffMember.age = data[5]
        staffMember.title = data[6]
        staffMember.phone = data[7]
        staffMember.department = data[9]
        staff.append(staffMember)
    return staff


def getCustomers(db, customerIds = None):
    filter = "WHERE 1=1"
    if customerIds is not None:
        customers = [str(customerId) for customerId in customerIds]
        filter = f" AND CustID IN ({'.'.join(customers)})"

    customerData = db.query(
    f"""
    SELECT 
        cust.CustID,
        cust.FirstName,
        cust.LastName,
        cust.Address,
        cust.Email,
        cust.Phone,
        mem.MembershipStatus,
        mem.SignUpDt,
        mem.Length,
        memLevel.LevelName,
        memLevel.Rate
    FROM 
        Customers as cust 
    INNER JOIN 
        Memberships as mem 
    ON 
        cust.MemID = mem.MemID 
    INNER JOIN 
        MembershipLevels as memLevel 
    ON 
        mem.LevelID = memLevel.LevelID
    {filter};
    """
    )
    customers = []
    for data in customerData:
        membershipLevel = models.MembershipLevel()
        membershipLevel.name = data[9]
        membershipLevel.rewardRate = data[10]

        membership = models.Membership()
        membership.status = data[6]
        membership.signUpDt = data[7]
        membership.length = data[8]
        membership.level = membershipLevel

        customer = models.Customer()
        customer.id = data[0]
        customer.firstname = data[1]
        customer.lastname = data[2]
        customer.address = data[3]
        customer.email = data[4]
        customer.phone = data[5]
        customer.membership = membership

        rewardData = db.query(
        f"""
        SELECT 
            * 
        FROM 
            Rewards 
        WHERE 
            CustID = {customer.id};
        """
        )

        if rewardData is None:
            continue

        for rdata in rewardData:
            reward = models.Reward()
            reward.year = rdata[1]
            reward.amount = rdata[2]
            customer.rewards.append(reward)
        customers.append(customer)
    return customers

def sourceSupplier(db, supplier):
    supplierQuery = f"""
    INSERT INTO Supplier
    (
        SupplierID,
        Name,
        Location,
        Email,
        Phone
    )
    VALUES
    (
        (SELECT NewSupplierID FROM (SELECT 1 + IFNULL((SELECT SupplierID FROM Supplier ORDER BY SupplierID DESC LIMIT 1), 0) AS NewSupplierID) InnerSupplier),
        \"{supplier.name}\",
        \"{supplier.location}\",
        \"{supplier.email}\",
        \"{supplier.phone}\"
    );
    """

    db.query(supplierQuery)

def updateSupplierInfo(db, supplier):
    supplierQuery = f"""
    UPDATE Supplier
    SET
        Name = \"{supplier.name}\",
        Location = \"{supplier.location}\",
        Email = \"{supplier.email}\",
        Phone = \"{supplier.phone}\"
    WHERE
        SupplierID = {supplier.id};
    """

    db.query(supplierQuery)

def removeSupplier(db, supplier):
    supplierQuery = f"""
    DELETE FROM 
        Supplier
    WHERE
        SupplierID = {supplier.id};
    """

    db.query(supplierQuery)

def getSuppliers(db, supplierIds = None, getShipmentInfo = True):
    filter = "WHERE 1=1"
    if supplierIds is not None:
        suppliers = [str(supplierId) for supplierId in supplierIds]
        filter = filter + f" AND SupplierId IN ({','.join(suppliers)})"

    suppliers = []
    supplierData = db.query(
    f"""
    SELECT
        *
    FROM
        Supplier
    {filter};
    """
    )
    for data in supplierData:
        supplier = models.Supplier()
        supplier.id = data[0]
        supplier.name = data[1]
        supplier.location = data[2]
        supplier.phone = data[3]
        supplier.email = data[4]

        if getShipmentInfo:
            shipmentData = db.query(
            f"""
            SELECT
                *
            FROM
                Shipments
            WHERE
                SupplierID = {supplier.id};
            """
            )
            for sdata in shipmentData:
                shipment = models.Shipment()
                shipment.id = sdata[0]
                shipment.shipDt = sdata[1]
                shipmentProductsData = db.query(
                f"""
                SELECT
                    *
                FROM
                    ShipmentStocks
                WHERE
                    ShipID = {shipment.id};
                """
                )
                for spdata in shipmentProductsData:
                    shipmentProduct = models.ShipmentProduct()
                    shipmentProduct.product = getProducts(db, productIds=[(spdata[2], spdata[3])])
                    shipmentProduct.quantity = spdata[0]
                    shipment.shipmentProducts.append(shipmentProduct)
                supplier.shipments.append(shipment)
        suppliers.append(supplier)
    return suppliers

def updateProductInfo(db, product):
    productQuery = f"""
    UPDATE Products
    SET
        Name = \"{product.name}\",
        Price = \"{product.price}\",
        Production = \"{product.productionDt}\",
        ExpireDt = \"{product.expirationDt}\"
    WHERE
        ProductID = {product.id[0]} AND StoreID = {product.id[1]};
    """

    db.query(productQuery)

def addNewProduct(db, product):
    productQuery = f"""
    INSERT INTO Products
    (
        ProductID,
        StoreID,
        Name,
        Quantity,
        Price,
        Cost,
        Production,
        ExpireDt,
        SupplierID
    )
    VALUES
    (
        (SELECT NewProductID FROM (SELECT 1 + IFNULL((SELECT ProductID FROM Products WHERE StoreID = {product.id[1]} ORDER BY ProductID DESC LIMIT 1), 0) AS NewProductID) InnerProducts),
        {product.id[1]},
        \"{product.name}\",
        {product.quantity},
        {product.price},
        {product.cost},
        \"{product.productionDt}\",
        \"{product.expirationDt}\",
        {product.supplier.id}
    );
    """

    db.query(productQuery)

def orderShipmentOfProducts(db, products, store, supplier):
    # Create shipment
    shipmentQuery = f"""
        INSERT INTO Shipments
        (
            ShipID,
            ShipDt,
            SupplierID
        )
        VALUES
        (
            (SELECT NewShipmentID FROM (SELECT 1 + IFNULL((SELECT ShipID FROM Shipments ORDER BY ShipID DESC LIMIT 1), 0) AS NewShipmentID) InnerShipments),
            CURRENT_DATE(),
            {supplier.id}
        );
        """

    # Add to shipmentstocks and update product quantity
    shipmentStocksQueries = []
    productQueries = []
    for productId, quantity in products.items():
        shipmentStocksQuery = f"""
        INSERT INTO ShipmentStocks
        (
            ShipID,
            ProductID,
            StoreID,
            Quantity
        )
        VALUES
        (
            (SELECT ShipID FROM Shipments ORDER BY ShipID Desc LIMIT 1),
            {productId[0]},
            {store.id},
            {quantity}
        );
        """
        shipmentStocksQueries.append(shipmentStocksQuery)

        product = getProducts(db, productIds=[productId])[0]
        productQuery = f"""
        INSERT INTO Products
        (
            ProductID,
            StoreID,
            Name,
            Quantity,
            Price,
            Cost,
            Production,
            ExpireDt,
            SupplierID
        )
        VALUES
        (
            {product.id[0]},
            {store.id},
            \"{product.name}\",
            {quantity},
            {product.price},
            \"{product.cost}\",
            \"{product.productionDt}\",
            \"{product.expirationDt}\",
            {supplier.id}
        )
        ON DUPLICATE KEY UPDATE
            Quantity = Quantity + {quantity};
        """
        productQueries.append(productQuery)

    orderQuery = ''.join([shipmentQuery, ''.join(shipmentStocksQueries), ''.join(productQueries)])
    db.query(orderQuery)

def getProductForOrder(db, productId):
    productQuery = f"""
    SELECT * FROM Products WHERE ProductID = {productId} LIMIT 1;
    """
    productData = db.query(productQuery)
    if len(productData) == 0:
        raise LookupError()
    productData = productData[0]
    return validateProductId(db, productId, productData[6])

def getProducts(db, productIds = None, storeIds = None, supplierIds = None):
    filter = "WHERE 1=1"
    if productIds is not None and len(productIds) != 0:
        products = [str(productId[0]) for productId in productIds]
        stores = [str(productId[1]) for productId in productIds]
        filter = filter + " AND ("
        filterList = []
        for i in range(0, len(products)):
            filterList.append(f"(ProductID = {products[i]} AND StoreID = {stores[i]})")
        filter = filter + " OR ".join(filterList) + ")"
    elif storeIds is not None and len(storeIds) != 0:
        stores = [str(storeId) for storeId in storeIds]
        filter = filter + f" AND StoreID IN ({','.join(stores)})"

    if supplierIds is not None and len(supplierIds) != 0:
        suppliers = [str(supplierId) for supplierId in supplierIds]
        filter = filter + f" AND SupplierID IN ({','.join(suppliers)})"
    
    products = []
    suppliers = getSuppliers(db, getShipmentInfo=False)
    productData = db.query(
    f"""
    SELECT 
        * 
    FROM 
        Products
    {filter};
    """
    )
    for data in productData:
        product = models.Product()
        product.id = (data[2], data[6])
        product.name = data[0]
        product.quantity = data[1]
        product.price = data[3]
        product.productionDt = data[4]
        product.expirationDt = data[5]
        if data[7] is not None:
            product.supplier = [supplier for supplier in suppliers if supplier.id == data[7]][0]
        product.cost = data[8]
        product.discounts = getDiscounts(db, productIds=[product.id])
        if len(product.discounts) != 0:
            todayDate = date.today()
            activeDiscount = [disc for disc in product.discounts if (todayDate >= disc.startDt and todayDate <= disc.endDt)]
            product.activeDiscount = None if len(activeDiscount) == 0 else activeDiscount[0]
            product.salePrice = (product.price * (1 - product.activeDiscount.percent)) if product.activeDiscount is not None else None
        products.append(product)
    
    return products

def getSalesForDate(db, year = None, month = None, day = None):
    query = f"""
    SELECT SUM(PricePaid)
    FROM TransactionContains as transactionContains
    INNER JOIN Transactions as transactions ON transactions.TransID = transactionContains.TransID
    WHERE YEAR(Date)={year}"""

    if month != "":
        query = query + f""" AND MONTH(Date)={month}"""

    if day != "":
        query = query + f""" AND DAY(Date)={day}"""

    query = query + ";"

    salesData = db.query(query)
    totalSales = str(salesData[0][0])
    return totalSales

def getSalesForStore(db, storeID = None, startDate = None, endDate = None):

    query = f"""
    SELECT SUM(PricePaid)
    FROM TransactionContains as transactionContains
    JOIN Transactions as transactions ON transactions.TransID = transactionContains.TransID
    WHERE transactionContains.StoreID={storeID} AND transactionContains.Status=1 AND Date BETWEEN '{startDate}' AND '{endDate}';"""

    salesData = db.query(query)
    totalSales = str(salesData[0][0])
    return totalSales

def getStockForStore(db, storeID = None):

    query = f"""
    select ShipmentStocks.Quantity, ShipmentStocks.ShipID, ShipmentStocks.ProductID, ShipmentStocks.StoreID, ShipmentStocks.Quantity * Products.Cost as ShipmentCost
    from ShipmentStocks 
    inner join Products 
    on ShipmentStocks.ProductID = Products.ProductID and ShipmentStocks.StoreID = Products.StoreID 
    where ShipmentStocks.StoreID ={storeID};"""

    stockData = db.query(query)

    stock = []
    for data in stockData:
        stockItem = models.ShipmentStocks()
        stockItem.cost = data[4]
        stockItem.quantity = data[0]
        stockItem.shipID = data[1]
        stockItem.productID = data[2]
        stockItem.storeID = data[3]
        stock.append(stockItem)
    return stock

def getStockForProduct(db, productID = None):

    query = f"""
    select ShipmentStocks.Quantity, ShipmentStocks.ShipID, ShipmentStocks.ProductID, ShipmentStocks.StoreID, ShipmentStocks.Quantity * Products.Cost as ShipmentCost
    from ShipmentStocks 
    inner join Products 
    on ShipmentStocks.ProductID = Products.ProductID and ShipmentStocks.StoreID = Products.StoreID 
    where ShipmentStocks.ProductID ={productID};"""

    stockData = db.query(query)

    stock = []
    for data in stockData:
        stockItem = models.ShipmentProduct()
        stockItem.cost = data[4]
        stockItem.quantity = data[0]
        stockItem.shipID = data[1]
        stockItem.productID = data[2]
        stockItem.storeID = data[3]
        stock.append(stockItem)
    return stock

def getCustomerForDate(db, year = None, month = None):

    query = f"""
    SELECT COUNT(CustID) FROM Transactions WHERE YEAR(Date)={year}"""

    if month != "":
        query = query + f""" AND MONTH(Date)={month}"""

    query = query + ";"

    customerData = db.query(query)

    totalCustomer = str(customerData[0][0])
    return totalCustomer

def getPurchasesForDate(db, startDate = None, endDate = None, custID = None):

    query = f"""
    SELECT SUM(PricePaid)
    FROM TransactionContains as transactionContains
    JOIN Transactions as transactions
    ON transactions.TransID = transactionContains.TransID
    JOIN Customers as customers
    ON customers.CustID = transactions.CustID
    WHERE customers.CustID={custID} AND Date BETWEEN '{startDate}' AND '{endDate}';"""

    purchasesData = db.query(query)
    totalPurchases = str(purchasesData[0][0])
    return totalPurchases

def createInventoryForNewProduct(db, newProduct):

    query = f"""
    INSERT INTO Products(ProductID, Name, Quantity, Cost, Price, Production, ExpireDt, StoreID, SupplierID)
    VALUES 
    ('{newProduct.id}', 
    '{newProduct.name}', 
    '{newProduct.quantity}', 
    '{newProduct.cost}', 
    '{newProduct.price}', 
    '{newProduct.productionDt}', 
    '{newProduct.expirationDt}', 
    '{newProduct.storeID}', 
    '{newProduct.supplier}');"""

    db.query(query)

def updateInventoryWithReturns(db, currentProduct):

    getExistingQuantity = db.query(f"""SELECT Quantity
    FROM Products
    WHERE ProductID = '{currentProduct.id}';""")
    if (all(getExistingQuantity)):
        existingQuantity = getExistingQuantity[0][0]
    else:
        existingQuantity = 0
    
    getProduct = db.query(f"""SELECT *
    FROM Products
    WHERE ProductID = '{currentProduct.id}';""")
    
    if (not getProduct):
        print("Inventory for this product does not exist.")
        return
    else:
        updateInventory =f"""UPDATE Products
        SET Quantity = '{currentProduct.quantity + existingQuantity}'
        WHERE ProductID = '{currentProduct.id}';"""
        db.query(updateInventory)

def manageProductTransfers(db, product, quantity, storeFrom, storeTo):
    quantityReduceQuery = f"""
    UPDATE Products
    SET
        Quantity = Quantity - {quantity}
    WHERE
        ProductID = {product.id[0]} AND StoreID = {product.id[1]};
    """

    quantityIncreaseQuery = f"""
    INSERT INTO Products
        (
            ProductID,
            StoreID,
            Name,
            Quantity,
            Price,
            Cost,
            Production,
            ExpireDt,
            SupplierID
        )
        VALUES
        (
            {product.id[0]},
            {storeTo.id},
            \"{product.name}\",
            {quantity},
            {product.price},
            \"{product.cost}\",
            \"{product.productionDt}\",
            \"{product.expirationDt}\",
            {product.supplier.id}
        )
        ON DUPLICATE KEY UPDATE
            Quantity = Quantity + {quantity};
    """

    transferQuery = ''.join([quantityReduceQuery, quantityIncreaseQuery])
    db.query(transferQuery)

def generateBillForSupplier(db, supplier):

    query = (f"""SELECT SUM(Cost * Quantity)
    FROM Products
    WHERE SupplierID = '{supplier.id}';""")

    billData = db.query(query)

    if (not billData or billData[0][0] is None):
        print("Supplier ID does not exist.")
        return None

    bill = str(billData[0][0])
    return bill

# Generate reward checks for the specified customer
def generateRewardChecks(db, customer, reward):

    query = (f"""
    SELECT RewardAmt
    FROM Rewards
    WHERE CustID = '{customer.id}' AND Year = '{reward.year}'; """)

    checkData = db.query(query)
    
    if (not checkData or checkData[0][0] is None):
        print("Rewards are not available for this customer and year.")
        return None
    
    check = str(checkData[0][0])
    return check

# Calculate the total price for the transaction
def calculatePriceForTransaction(db, transaction):
    
    query = (f"""
    SELECT SUM(PricePaid - (Percent * PricePaid))
    FROM Discounts as discounts
    JOIN TransactionContains as transactionContains 
    ON transactionContains.ProductID = discounts.ProductID
    JOIN Transactions as transactions 
    ON transactions.TransID = transactionContains.TransID
    WHERE transactions.TransID='{transaction.id}';""")

    priceData = db.query(query)

    if (priceData[0][0] is None):
        query = (f"""
        SELECT PricePaid
        FROM TransactionContains as transactionContains 
        JOIN Transactions as transactions 
        ON transactions.TransID = transactionContains.TransID
        WHERE transactions.TransID='{transaction.id}';""")
        
    priceData = db.query(query)

    if (not priceData or priceData[0][0] is None):
        print("Transaction ID does not exist.")
        return None

    price = str(priceData[0][0])
    return price
  
# Create a new discount on the specified product
def addDiscountForProduct(db, discount, product):
    discountQuery = f"""
    INSERT INTO Discounts
    (
        DiscountID,
        ProductID,
        StoreID,
        StartDt,
        EndDt,
        Percent
    )
    VALUES
    (
        (SELECT NewDiscountID FROM (SELECT 1 + IFNULL((SELECT DiscountID FROM Discounts ORDER BY DiscountID DESC LIMIT 1), 0) AS NewDiscountID) InnerDiscounts),
        {product.id[0]},
        {product.id[1]},
        \"{discount.startDt}\",
        \"{discount.endDt}\",
        {discount.percent}
    );
    """

    db.query(discountQuery)

# Update discount information
def updateDiscount(db, discount):
    discountQuery = f"""
    UPDATE Discounts
    SET
        StartDt = \"{discount.startDt}\",
        EndDt = \"{discount.endDt}\",
        Percent = {discount.percent}
    WHERE
        DiscountID = {discount.id};
    """

    db.query(discountQuery)

# Get all discounts matching the specified filters
def getDiscounts(db, discountIds = None, productIds = None):
    filter = "WHERE 1=1"
    if discountIds is not None:
        discounts = [str(discountId) for discountId in discountIds]
        filter = filter + f" AND DiscountID in ({','.join(discounts)})"
    elif productIds is not None:
        productsFilters = []
        for productId in productIds:
            productsFilters.append(f"(ProductID = {productId[0]} AND StoreID = {productId[1]})")
        filter = filter + " AND (" + " OR ".join(productsFilters) + ")"

    discountQuery = f"""
    SELECT
        *
    FROM
        Discounts
    {filter};
    """

    discounts = []
    discountData = db.query(discountQuery)
    for data in discountData:
        discount = models.Discount()
        discount.id = data[3]
        discount.percent = data[0]
        discount.startDt = data[1]
        discount.endDt = data[2]
        discounts.append(discount)
    return discounts

# Create a new transaction during checkout
def addTransaction(db, custID = None, staffID = None, storeID = None):
    query = f"""
    INSERT INTO Transactions
    (
        TransID,
        Date,
        StoreID,
        CustID,
        StaffID
    )
    VALUES
    (
        (SELECT NewTransID FROM (SELECT 1 + IFNULL((SELECT TransID FROM Transactions ORDER BY TransID DESC LIMIT 1), 0) AS NewTransID) InnerTransactions),
        CURRENT_DATE(),
        {storeID},
        {custID},
        {staffID}
    );
    """

    db.query(query)

# Used to checkout an item during a transaction
def addTransactionItem(db, product, store, quantity):
    transactionItemQuery = f"""
    INSERT INTO TransactionContains
    (
        TransID,
        ProductID,
        StoreID,
        PricePaid,
        Quantity,
        Status,
        Price
    )
    VALUES
    (
        (SELECT TransID FROM Transactions ORDER BY TransID DESC LIMIT 1),
        {product.id[0]},
        {store.id},
        {(quantity * product.price) if product.salePrice is None else (quantity * product.salePrice)},
        {quantity},
        1,
        {product.price}
    );
    """

    productQuery = f"""
    UPDATE Products
    SET
        Quantity = Quantity - {quantity}
    WHERE
        ProductID = {product.id[0]} AND StoreID = {product.id[1]};
    """

    checkoutQuery = ''.join([transactionItemQuery, productQuery])
    db.query(transactionItemQuery)

# Used to set an item in a transaction to refunded
def updateTransactionItem(db, transaction, transactionItem):
    transactionItemQuery = f"""
    UPDATE TransactionContains
    SET
        Status = 0
    WHERE
        TransID = {transaction.id} AND ProductID = {transactionItem.product.id[0]} AND StoreID = {transactionItem.product.id[1]};
    """
    productQuery = f"""
    UPDATE Products
    SET
        Quantity = Quantity + {transactionItem.quantity}
    WHERE
        ProductID = {transactionItem.product.id[0]} AND StoreID = {transactionItem.product.id[1]};
    """

    refundQuery = ''.join([transactionItemQuery, productQuery])
    db.query(refundQuery)

# Get all transactions and their transaction items
def getTransactions(db, transactionIds = None):
    filter = "WHERE 1=1"
    if transactionIds is not None and len(transactionIds) > 0:
        transactions = [str(transactionId) for transactionId in transactionIds]
        filter = filter + f" AND TransID IN ({','.join(transactions)})"

    transactions = []
    transactionData = db.query(
    f"""
    SELECT
        *
    FROM
        Transactions
    {filter};
    """
    )
    for data in transactionData:
        transaction = models.Transaction()
        transaction.id = data[0]
        transaction.date = data[1]
        if data[2] is not None:
            transaction.store = getStores(db, storeIds = [data[2]])[0]
        if data[3] is not None:
            transaction.customer = getCustomers(db, customerIds = [data[3]])[0]
        if data[4] is not None:
            transaction.staff = getStaff(db, staffIds = [data[4]])[0]
        
        transactionItemsQuery = f"""
        SELECT
            *
        FROM
            TransactionContains
        WHERE
            TransID = {transaction.id};
        """
        transactionItemsData = db.query(transactionItemsQuery)

        if transactionItemsData is None or len(transactionItemsData) == 0:
            transactions.append(transaction)
            continue

        for tdata in transactionItemsData:
            transactionItem = models.TransactionProduct()
            products = getProducts(db, productIds = [(tdata[1], tdata[2])])
            transactionItem.product = products[0]
            transactionItem.pricePaid = tdata[3]
            transactionItem.quantity = tdata[4]
            transactionItem.status = tdata[5]
            transactionItem.price = tdata[6]
            transaction.transactionProducts.append(transactionItem)
        transactions.append(transaction)

    return transactions