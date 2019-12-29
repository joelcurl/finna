from collections import namedtuple
from dataclasses import dataclass
from decimal import Decimal
import re
from datetime import datetime


@dataclass
class Earnings:
    wages_detail: dict
    bonus_detail: dict
    net_detail: dict
    total_detail: dict

    @property
    def wages(self):
        return sum(self.wages_detail.values())

    @property
    def bonuses(self):
        return sum(self.bonus_detail.values())

@dataclass
class PreTaxDeductions:
    hsa_detail: dict
    vision_detail: dict
    dental_detail: dict
    pension401k_detail: dict
    medical_detail: dict
    total_detail: dict

    @property
    def total(self):
        return sum(self.total_detail.values())

@dataclass
class PostTaxDeductions:
    long_term_disability_detail: dict
    legal_detail: dict
    roth_pension401k_detail: dict
    total_detail: dict

    @property
    def total(self):
        return sum(self.total_detail.values())

@dataclass
class Deductions:
    pretax: PreTaxDeductions
    posttax: PostTaxDeductions

    @property
    def total(self):
        return sum([self.pretax.total, self.posttax.total])

@dataclass
class Taxes:
    taxable_wages_detail: dict
    state_withholding_detail: dict
    fed_withholding_detail: dict
    ss_tax_detail: dict
    medicare_tax_detail: dict
    total_detail: dict

    @property
    def taxable_wages(self):
        return sum(self.taxable_wages_detail.values())

    @property
    def federal_withheld(self):
        return sum(self.fed_withholding_detail.values())

    @property
    def state_withheld(self):
        return sum(self.state_withholding_detail.values())

    @property
    def total(self):
        return sum(self.total_detail.values())

Paystub = namedtuple('Paystub', 'earnings deductions taxes')
PayPeriod = namedtuple('PayPeriod', 'start end')

class AcmePaystub:
    def __init__(self, parse_str):
        self.parse_str = parse_str.replace('\n', '')
        parsed = self.__parse_paystub()
        self.current = Paystub(*parsed['current'])
        self.ytd = Paystub(*parsed['ytd'])
        self.employer = 'Acme'
        self.pay_period = PayPeriod(**parsed['pay_period'])

    def __parse_paystub(self):
        items = [
                self.__parse_earnings(),
                self.__parse_deductions(),
                self.__parse_taxes(),
                ]
        return {'current': [item['current'] for item in items], 'ytd': [item['ytd'] for item in items], 'pay_period': self.__parse_pay_period()}

    def __parse_earnings(self):
        line_items = self.__parse_cur_ytd_named_line_items([
            'Salary',
            'Total Taxable Earnings',
            ])
        extra_comp = self.__parse_cur_repeated_ytd_named_line_items(['Extra Compensation'])
        nontax_earnings = self.__find_cur_ytd_named_pair('Total NonTax Earnings')
        extra_comp = self.__merge_line_items([extra_comp, nontax_earnings])
        line_items.insert(1, extra_comp)

        net_pay = {'Net Pay': {'current': self.__find_named_val('Total Net'), 'ytd': self.__find_named_val('YTD Net')}}
        line_items.append(net_pay)
        return {'current': Earnings(*self.__current(line_items)), 'ytd': Earnings(*self.__ytd(line_items))}

    def __parse_pretax_ded(self):
        try:
            line_items = [{'HSAP Savings Plan Pre-Tax': {'current': '0', 'ytd': self.__find_named_val('HSAP Savings Plan Pre-Tax')}}]
            line_items += self.__parse_cur_ytd_named_line_items([
                'Vision EE pre-tax',
                'Cigna Dental HMO Pre-Tax',
                '401k Savings Plan Pre-Tax',
                'NielsenHealth HFSA',
                'Total Pre-Tax Deductions',
                ])
            return {'current': PreTaxDeductions(*self.__current(line_items)), 'ytd': PreTaxDeductions(*self.__ytd(line_items))}
        except LookupError:
            return {'current': PreTaxDeductions(*([{'Total Pre-Tax Deductions': Decimal(0)}] * 6)), 'ytd': PreTaxDeductions(*([{'Total Pre-Tax Deductions': Decimal(0)}] * 6))} # six zeros for req args

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
        return {'current': Deductions(pretax['current'], posttax['current']), 'ytd': Deductions(pretax['ytd'], posttax['ytd'])}

    def __parse_taxes(self):
        try:
            line_items = [{'Taxable Wages': self.__find_cur_ytd_pair('Note:')}]
        except LookupError:
            line_items = [{'Taxable Wages': self.__find_cur_ytd_pair('-*\s*Total NonTax Earnings')}]
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
    
    def __parse_cur_repeated_ytd_named_line_items(self, line_items_repeated):
        parsed = {}
        for repeated_line_item in line_items_repeated:
            vals = Decimal(sum([Decimal(num) for num in self.__find_named_vals(repeated_line_item)]))
            ytd = self.__find_cur_ytd_named_pair(repeated_line_item)[repeated_line_item]['ytd']
            parsed[repeated_line_item] = {'current': str(vals), 'ytd': ytd}
        return parsed

    def __parse_pay_period(self):
        pay_periods = re.search('Pay Period:\s.+?(?P<start>[0-9\/]+)[\s-]+?(?P<end>[0-9\/]+)', self.parse_str).groupdict()
        return {key: datetime.strptime(value, '%m/%d/%Y').date() for key, value in pay_periods.items()}

    def __merge_line_items(self, items):
        title = [*(items[0].keys())][0]
        cur = Decimal(0)
        ytd = Decimal(0)
        for item in items:
            cur += sum([Decimal(line['current'].replace(',', '')) for line in item.values()])
            ytd += sum([Decimal(line['ytd'].replace(',', '')) for line in item.values()])
        return {title: {'current': str(cur), 'ytd': str(ytd)}}

    def __current(self, items):
        return [{k: self.__to_decimal(v['current']) for k,v in item.items()} for item in items]

    def __ytd(self, items):
        return [{k: self.__to_decimal(v['ytd']) for k,v in item.items()} for item in items]

    def __to_decimal(self, val):
        return Decimal(val.replace(',', ''))

    def __find_cur_ytd_pair(self, lookahead):
        try:
            search_re = f'(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)\s+{lookahead}'
            return re.search(search_re, self.parse_str).groupdict()
        except AttributeError:
            raise LookupError(f'Could not find pattern in paystub: {search_re}')

    def __find_cur_ytd_named_pair(self, name):
        try:
            return {name: re.search(f'{name}\s+(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)', self.parse_str).groupdict()}
        except AttributeError: # no match
            return {name: {'current': '0.00', 'ytd': '0.00'}}
    
    def __find_cur_ytd_named_pair_nth_match(self, name, n):
        matches = re.findall(f'{name}\s+(?P<current>[\d,\.]+)\s+(?P<ytd>[\d,\.]+)', self.parse_str)
        return {name: {'current': matches[n][0], 'ytd': matches[n][1]}}

    def __find_cur_cur_ytd_named_pair(self, name):
        try:
            return {name: re.search}
            pass
        except AttributeError:
            return self.__find_cur_ytd_named_pair(name)

    def __find_named_val(self, name):
        return self.__find_named_val_nth_match(name, 0)

    def __find_named_val_nth_match(self, name, n):
        return self.__find_named_vals(name)[n]
        
    def __find_named_vals(self, name):
        try:
            return re.findall(f'{name}\s+([\d,\.]+)', self.parse_str)
        except AttributeError:
            raise LookupError(f'Could not find {name}')
