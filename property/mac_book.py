import requests
import re
from decimal import *

class MacBook:
    def mark_to_market(self):
        resp = requests.get('https://www.apple.com/shop/tradein-module?cat=computer&pid=9247&module=questions')
        quote_string = resp.json()['body']['assets']['tradein-quote-estimate']
        match = re.search('\$(?P<estimate>[0-9\.]+) in trade-in value', quote_string)
        return Decimal(match['estimate'])

#mymac = MacBook()
#print(mymac.mark_to_market())
