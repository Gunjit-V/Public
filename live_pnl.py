from cred import *
from api_helper import ShoonyaApiPy, get_time
import datetime
import logging
import time
import pandas as pd
from quotes_master import *
from token_lookup import *
from config import *
from SmartApi import SmartConnect
from trading_holidays import *
from dateutil import tz

# Shoonya Login

api = ShoonyaApiPy()
try:
    obj = api.login(userid=user_id, password=password, twoFA=twoFA,
                    vendor_code=vendor_code, api_secret=api_key, imei=imei)
    # print(obj)
except Exception as e:
    print(e)

while True:
    try:
        print(float(api.get_limits()['uzpnl_d_i']) * -1)
        time.sleep(1)
    except Exception as e:
        print(e)