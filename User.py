class User():
    bank_balance = 50000

    def __init__(self):
        stock_history = {}
    def buy_stock(self, stock_price):
        if(stock_price < self.bank_balance and self.bank_balance >0):
            self.set_bank_balance(stock_price)
            return True



    def get_bank_balance(self):
        return self.bank_balance

    def set_bank_balance(self, amount):
        self.bank_balance -= amount

