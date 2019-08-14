from datetime import date, timedelta
from decimal import *

class TimedLiability:
    def __init__(self, start_date, end_date, amount):
        self.start_date = date.fromisoformat(start_date)
        self.end_date = date.fromisoformat(end_date)
        self.amount = Decimal(amount)

    @property
    def length(self):
        if self.end_date < self.start_date:
            return timedelta(0)
        return self.end_date - self.start_date

    def remaining(self, now):
        now = date.fromisoformat(now)
        if now > self.end_date:
            return timedelta(0)
        if now < self.start_date:
            return self.end_date - self.start_date
        return self.end_date - now

    def ratio_remaining(self, now):
        return self.remaining(now) / self.length

    def amount_remaining(self, end_date):
        return self.amount * Decimal(self.ratio_remaining(end_date))

concept_lease = TimedLiability('2019-07-20', '2020-01-19', 999.00 * 6)
