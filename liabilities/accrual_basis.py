from datetime import date
from decimal import *

class AccrualBasis:
    annual_accrual_basis = Decimal(1.0/365)

    def __init__(self, amount, basis_per_day):
        self.amount = abs(Decimal(amount))
        self.basis_per_day = basis_per_day

    def accrued(self, then, now):
        then = date.fromisoformat(then)
        now = date.fromisoformat(now)
        timediff = now - then
        amount_accrued = self.amount * self.basis_per_day * timediff.days
        return amount_accrued if amount_accrued > 0 else Decimal(0)

class SemesterAccrualBasis(AccrualBasis):
    def __init__(self, amount):
        super().__init__(amount, self.annual_accrual_basis * 3) # 3 semesters in a year

class QuarterlyAccrualBasis(AccrualBasis):
    def __init__(self, amount):
        super().__init__(amount, self.annual_accrual_basis * 4) # 4 quarters in a year

class MonthlyAccrualBasis(AccrualBasis):
    def __init__(self, amount):
        super().__init__(amount, self.annual_accrual_basis * 12) # 12 months in a year
        
