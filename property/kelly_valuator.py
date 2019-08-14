import requests
import re
from decimal import *

class ChevyMalibu05Valuator:
    def __init__(self, milage, sell_zip):
        self.milage = milage
        self.sell_zip = sell_zip

    def mark_to_market(self):
        resp = requests.get(f'https://www.kbb.com/Api/3.9.426.0/70724/vehicle/upa/PriceAdvisor/meter.svg?action=Get&intent=trade-in-sell&pricetype=Private%20Party&zipcode={self.sell_zip}&vehicleid=256&selectedoptions=6488044|true&hideMonthlyPayment=False&condition=good&mileage={self.milage}')
        return self._parse_price(resp.text)

    def _parse_price(self, xml_str):
        match = re.search('\$(?P<estimate>[0-9\.,]+).*?Private Party Value', xml_str)
        estimate = match['estimate'].replace(',', '')
        return Decimal(estimate)

#v = ChevyMalibu05Valuator(milage=150000, sell_zip=84102)
#print(v.mark_to_market())
