import phonenumbers

def getFormattedPhoneNumber(phoneNumber):
    return phonenumbers.format_number(phonenumbers.parse(phoneNumber, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)

def getFormattedPrice(price):
    if price is None:
        return "-"
    return f"${round(price, 2)}"

def getFormattedDecimalAsPercent(num):
    if num is None:
        return "-"
    return f"{round(num * 100, 2)}%"