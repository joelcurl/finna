from collections import namedtuple
from decimal import Decimal

tax_bracket = namedtuple('TaxBracket', 'rate ceiling')

class SingleTax:

    income_brackets = [
            tax_bracket(Decimal(0.10), Decimal(9700)),
            tax_bracket(Decimal(0.12), Decimal(39475)),
            tax_bracket(Decimal(0.22), Decimal(84200)),
            tax_bracket(Decimal(0.24), Decimal(160725)),
            tax_bracket(Decimal(0.32), Decimal(204100)),
            tax_bracket(Decimal(0.35), Decimal(510300)),
            tax_bracket(Decimal(0.37), Decimal('inf')),
    ]

    pref_capital_gains_brackets = [
            tax_bracket(Decimal(0.00), Decimal(39375)),
            tax_bracket(Decimal(0.15), Decimal(434550)),
            tax_bracket(Decimal(0.20), Decimal('inf')),
    ]

    @staticmethod
    def calc_income_tax(taxable_income):
        if taxable_income < 0:
            return Decimal(0)

        taxable_remaining = taxable_income
        tax_burden = Decimal(0)
        for tax_bracket in SingleTax.income_brackets:
            if taxable_income > tax_bracket.ceiling:
                taxable_at_bracket = tax_bracket.ceiling - 1
                tax_burden += taxable_at_bracket * tax_bracket.rate
                taxable_remaining -= tax_bracket.ceiling - 1
            else:
                tax_burden += taxable_remaining * tax_bracket.rate
                return tax_burden

    @staticmethod
    def calc_flat_tax(taxable_income, rate):
        return Decimal(taxable_income) * Decimal(rate)

    @staticmethod
    def calc_pref_capital_gains(ordinary_income, pref_capital_income):
        tax_bracket = None
        for bracket in SingleTax.pref_capital_gains_brackets:
            tax_bracket = bracket
            if ordinary_income > bracket.ceiling:
                continue
        return pref_capital_income * tax_bracket.rate

