from .visa import TransactionDb
from .categories import categories
from decimal import Decimal

class CcStatement:
    transactions = []

    def __init__(self, cc_reader, mcc_reader, categories = categories(), db = TransactionDb()):
        self.db = db
        self.groups = categories
        self.cc_reader = cc_reader
        self.transactions = self.cc_reader.visa_transactions
        self.db.add_many(self.transactions)
        self.mcc_reader = mcc_reader
        self.db.add_many(self.mcc_reader.codes)

    @property
    def total(self):
        return sum([transaction.amount for transaction in self.transactions])

    @property
    def start(self):
        return min(self.dates)

    @property
    def end(self):
        return max(self.dates)

    @property
    def dates(self):
        return [transaction.date for transaction in self.transactions]

    @property
    def creditor(self):
        return self.cc_reader.creditor

    def category(self, category):
        return self.groups[category]()
