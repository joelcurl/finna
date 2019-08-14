from csv import DictReader
from recordclass import recordclass
from decimal import *

class MacuStatement:
    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = DictReader(csv_iter)
        fields = [MacuStatement.translate_field(name) for name in self.reader.fieldnames]
        self.MacuTransaction = recordclass('MacuTransaction', fields)

        self.transactions = []
        for row in self.reader:
            row = {MacuStatement.translate_field(key): value for key, value in row.items()}
            self.transactions.append(self.MacuTransaction(**row))
        self._calc_balances()

    def balance(self):
        return self.transactions[0].Balance if len(self.transactions) > 0 else Decimal(0)

    @staticmethod
    def translate_field(field):
        return field.strip(' ').translate(str.maketrans(' ', '_'))

    def _calc_balances(self):
        for transaction in self.transactions:
            transaction.Balance = Decimal(transaction.Balance)

#with open('input/ExportedTransactions.csv') as f:
#    ms = MacuStatement(f.read())
#    print(ms.balance())
