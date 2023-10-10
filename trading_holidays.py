import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


def today_is_a_trading_holiday():
    response = requests.get(
        'https://zerodha.com/marketintel/holiday-calendar/')
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find_all(name='h4')[0]
    holiday = soup.find(string=re.compile("The next trading holiday"))
    next_holiday = '-'.join(re.findall(
        '([0-3][0-9]) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', holiday)[0])
    next_holiday = next_holiday+'-'+str(datetime.now().year)
    next_holiday = datetime.strptime(next_holiday, '%d-%b-%Y').date()
    return next_holiday == datetime.today().date()
