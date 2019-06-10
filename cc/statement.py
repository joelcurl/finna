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
        _total = Decimal(0)
        for _, category in self.groups.items():
            _total += category().total
        return _total

    def category(self, category):
        return self.groups[category]()
