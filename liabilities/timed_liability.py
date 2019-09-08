from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import *

class TimedLiability:
    def __init__(self, start_date, end_date, amount):
        self.start_date = start_date
        self.end_date = end_date
        self.amount = Decimal(amount)

    @property
    def length(self):
        if self.end_date < self.start_date:
            return timedelta(0)
        return self.end_date - self.start_date

    def remaining(self, now):
        if now > self.end_date:
            return timedelta(0)
        if now < self.start_date:
            return self.end_date - self.start_date
        return self.end_date - now

    def ratio_from(self, start, end):
        if start > end:
            raise ValueError(f'start {start} is past end {end}')
        return Decimal((self.remaining(start) - self.remaining(end)) / self.length)

    def ratio_remaining(self, now):
        return self.ratio_from(now, self.end_date)

    def amount_from(self, start_date, end_date):
        return self.amount * self.ratio_from(start_date, end_date)

    def amount_remaining(self, end_date):
        return self.amount * self.ratio_remaining(end_date)

    @property
    def daily_amount(self):
        return self.amount_from(self.start_date, self.start_date + relativedelta(days=1))

    @property
    def monthly_amount(self):
        return self.amount_from(self.start_date, self.start_date + relativedelta(months=1))

class AccrualBasis(TimedLiability):
    def accrued(self, then, now):
        return self.amount_from(then, now)

class SemesterAccrualBasis(AccrualBasis):
    def __init__(self, amount, start_date):
        end_date = start_date + relativedelta(months=+4) # 4 months to a semester
        super().__init__(start_date, end_date, amount)

class QuarterlyAccrualBasis(AccrualBasis):
    def __init__(self, amount, start_date):
        end_date = start_date + relativedelta(months=+3) # 3 months to a quarter
        super().__init__(start_date, end_date, amount)

class MonthlyAccrualBasis(AccrualBasis):
    def __init__(self, amount, start_date):
        end_date = start_date + relativedelta(months=+1)
        super().__init__(start_date, end_date, amount)

concept_lease = TimedLiability(date.fromisoformat('2019-07-20'), date.fromisoformat('2020-01-19'), 999.00 * 6)

