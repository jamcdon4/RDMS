class Staff:
    def __init__(self):
        self.id = None
        self.address = None
        self.startDt = None
        self.email = None
        self.name = None
        self.age = None
        self.title = None
        self.phone = None
        self.department = None

class Customer:
    def __init__(self):
        self.id = None
        self.firstname = None
        self.lastname = None
        self.address = None
        self.email = None
        self.phone = None
        self.membership = None
        self.rewards = []

class Membership:
    def __init__(self):
        self.signUpDt = None
        self.status = None
        self.level = None
        self.length = None

class MembershipLevel:
    def __init__(self):
        self.name = None
        self.rewardRate = None

class Transaction:
    def __init__(self):
        self.id = None
        self.date = None
        self.store = None
        self.customer = None
        self.staff = None
        self.transactionProducts = []

class TransactionProduct:
    def __init__(self):
        self.product = None
        self.quantity = None
        self.status = None
        self.pricePaid = None
        self.price = None

class Store:
    def __init__(self):
        self.id = None
        self.address = None
        self.phone = None
        self.manager = None
        self.staff = []
        self.products = []

class Product:
    def __init__(self):
        # Tuple of (product id, store id)
        self.id = None
        self.name = None
        self.quantity = None
        self.cost = None
        self.price = None
        self.salePrice = None
        self.productionDt = None,
        self.expirationDt = None,
        self.supplier = None
        self.activeDiscount = None
        self.discounts = []

class Discount:
    def __init__(self):
        self.id = None
        self.startDt = None
        self.endDt = None
        self.percent = None

class Shipment:
    def __init__(self):
        self.id = None
        self.shipDt = None
        self.shipmentProducts = []

class ShipmentProduct:
    def __init(self):
        self.product = None
        self.quantity = None

class Supplier:
    def __init__(self):
        self.id = None
        self.name = None
        self.location = None
        self.phone = None
        self.email = None
        self.shipments = []

class Reward:
    def __init__(self):
        self.year = None
        self.amount = None