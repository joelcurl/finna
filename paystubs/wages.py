from collections import namedtuple
from decimal import Decimal
import re

Paystub = namedtuple('Paystub', 'earnings deductions taxes')
Earnings = namedtuple('Earnings', 'wages bonus net total')
Deductions = namedtuple('Deductions', 'pretax posttax total')
PreTaxDeductions = namedtuple('PreTaxDeductions', 'hsa vision dental pension401k medical total')
PostTaxDeductions = namedtuple('PostTaxDeductions', 'long_term_disability legal roth_pension401k total')
Taxes = namedtuple('Taxes', 'taxable_wages state_withholding fed_withholding ss_tax medicare_tax total')

class AcmePaystub:
    def __init__(self, parse_str):
        self.parse_str = parse_str
        parsed = self.__parse_paystub()
        self.current = Paystub(*parsed['current'])
        self.ytd = Paystub(*parsed['ytd'])

    def __parse_paystub(self):
        items = [
                self.__parse_earnings(),
                self.__parse_deductions(),
                self.__parse_taxes(),
                ]
        return {'current': [item['current'] for item in items], 'ytd': [item['ytd'] for item in items]}

    def __parse_earnings(self):
        line_items = self.__parse_cur_ytd_named_line_items([
            'Salary',
            'Extra Compensation',
            'Total Taxable Earnings',
            ])
        net_pay = {'Net Pay': {'current': self.__find_named_val('Total Net'), 'ytd': self.__find_named_val('YTD Net')}}
        line_items.append(net_pay)
        return {'current': Earnings(*self.__current(line_items)), 'ytd': Earnings(*self.__ytd(line_items))}

    def __parse_pretax_ded(self):
        line_items = [{'HSAP Savings Plan Pre-Tax': {'current': '0', 'ytd': self.__find_named_val('HSAP Savings Plan Pre-Tax')}}]
        line_items += self.__parse_cur_ytd_named_line_items([
            'Vision EE pre-tax',
            'Cigna Dental HMO Pre-Tax',
            '401k Savings Plan Pre-Tax',
            'NielsenHealth HFSA',
            'Total Pre-Tax Deductions',
            ])
        return {'current': PreTaxDeductions(*self.__current(line_items)), 'ytd': PreTaxDeductions(*self.__ytd(line_items))}

    def __parse_posttax_ded(self):
        line_items = self.__parse_cur_ytd_named_line_items([ 
            'Long-Term Disability',
            'Legal',
            'Roth Basic Post Tax NS',
            'Total Post-Tax Deductions',
            ])
        return {'current': PostTaxDeductions(*self.__current(line_items)), 'ytd': PostTaxDeductions(*self.__ytd(line_items))}

    def __parse_deductions(self):
        pretax = self.__parse_pretax_ded()
        posttax = self.__parse_posttax_ded()
        cur_total = {'Total Deductions': Decimal(pretax['current'].total['Total Pre-Tax Deductions']) + Decimal(posttax['current'].total['Total Post-Tax Deductions'])}
        ytd_total = {'Total Deductions': Decimal(pretax['ytd'].total['Total Pre-Tax Deductions']) + Decimal(posttax['ytd'].total['Total Post-Tax Deductions'])}
        return {'current': Deductions(pretax['current'], posttax['current'], cur_total), 'ytd': Deductions(pretax['ytd'], posttax['ytd'], ytd_total)}

    def __parse_taxes(self):
        line_items = [{'Taxable Wages': self.__find_cur_ytd_pair('Note:')}]
        line_items += [self.__find_cur_ytd_named_pair_nth_match('TX Withholding Tax', 1)]
        line_items += self.__parse_cur_ytd_named_line_items([
            'TX Withholding Tax',
            'TX EE Social Security Tax',
            'TX EE Medicare Tax',
            'Total Taxes'
            ])
        return {'current': Taxes(*self.__current(line_items)), 'ytd': Taxes(*self.__ytd(line_items))}

    def __parse_cur_ytd_named_line_items(self, items):
        return [self.__find_cur_ytd_named_pair(line) for line in items]

    def __current(self, items):
        return [{k: self.__to_decimal(v['current']) for k,v in item.items()} for item in items]

    def __ytd(self, items):
        return [{k: self.__to_decimal(v['ytd']) for k,v in item.items()} for item in items]

    def __to_decimal(self, val):
        return Decimal(val.replace(',', ''))

    def __find_cur_ytd_pair(self, lookahead):
        return re.search(f'(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)\s+{lookahead}', self.parse_str).groupdict()

    def __find_cur_ytd_named_pair(self, name):
        return {name: re.search(f'{name}\s+(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)', self.parse_str).groupdict()}
    
    def __find_cur_ytd_named_pair_nth_match(self, name, n):
        matches = re.findall(f'{name}\s+(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)', self.parse_str)
        return {name: {'current': matches[n][0], 'ytd': matches[n][1]}}

    def __find_named_val(self, name):
        return re.search(f'{name}\s+([\d,\.]+)', self.parse_str).groups()[0]

