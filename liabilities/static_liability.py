from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

class StaticLiability:
    def __init__(self, amount, expiration_date):
        self.amount = amount
        self.expiration_date = expiration_date

    def amount_remaining(self, now):
        if now > self.expiration_date:
            return Decimal(0)
        return self.amount

education_liabilities = [
    StaticLiability(Decimal(2681.80), datetime.fromisoformat('2019-08-04').date() + relativedelta(years=+1))
]
