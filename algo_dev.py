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
from strike_selector import *

indices = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']

get_master()

# Angel Login

angel_obj = SmartConnect(angel_apikey)
data = angel_obj.generateSession(
    angel_clientId, angel_password, pyotp.TOTP(angel_otp_token).now())
refreshToken = data['data']['refreshToken']  # type: ignore
FEED_TOKEN = angel_obj.getfeedToken()
user_details = angel_obj.getProfile(refreshToken)

# Shoonya Login

api = ShoonyaApiPy()
try:
    obj = api.login(userid=user_id, password=password, twoFA=twoFA,
                    vendor_code=vendor_code, api_secret=api_key, imei=imei)
except Exception as e:
    print(e)

print("Angel One Login")
print(user_details)

print("Shoonya Login")
print(obj)

desired_quotes = get_quote_details('NFO', 'NIFTY', 'FUTIDX')

current_expiry = desired_quotes[0]
token = current_expiry['Token']
print(current_expiry, token)


def get_intraday_data(token: str, historic_params: dict):
    historicParam = historic_params
    intraday_data = pd.DataFrame(angel_obj.getCandleData(historicParam)['data'], columns=[            # type: ignore
                                 'DateTime', 'O', 'H', 'L', 'C', 'V'])
    intraday_data['DateTime'] = intraday_data['DateTime'].str.slice(stop=16)
    intraday_data['DateTime'] = pd.to_datetime(intraday_data['DateTime'])
    return intraday_data


def get_strike(price):
    if price % 100 < 50 and price % 50 <= 25:
        return price - price % 100
    elif price % 100 < 50 and price % 50 > 25:
        return price - price % 100 + 50
    elif price % 100 >= 50 and price % 50 < 25:
        return price - price % 100 + 50
    elif price % 100 >= 50 and price % 50 >= 25:
        return price - price % 100 + 100

# store = api.place_order(
# "B", "I", "NFO", current_expiry['TradingSymbol'], 100, 0, "MKT", 0, 0, "DAY", "NO", None)
# print(store)

def placeOrder(signal: str, exchg: str, trading_symbol: str, mkt_lim: float, stoploss: float, qty: str, lim_price: float = 0):
    try:
        buy_or_sell = signal
        product_type = 'I'
        exchange = exchg
        tradingsymbol = trading_symbol
        quantity = qty
        disclosedqty = 0
        price_type = mkt_lim
        price = lim_price
        trigger_price = stoploss

    except Exception as e:
        print(e)
buy = 0
sell = 0
orb_high = 0
orb_low = 0
stop_loss_buy = 0
stop_loss_sell = 0

# Main Strategy
if (today_is_a_trading_holiday() == False and dt.datetime.now(tz=tz.gettz('Asia/Kolkata')).weekday() < 5):
    while True:
        curr_date = dt.datetime.now(tz=tz.gettz('Asia/Kolkata'))
        minutes = curr_date.minute % 15
        to_date = (dt.datetime.now(tz=tz.gettz('Asia/Kolkata')) - dt.timedelta(minutes=minutes + 15)
                   ).strftime("%Y-%m-%d %H:%M")
        if curr_date.time() < dt.time(9, 30):
            print(curr_date, "Waiting for first candle.")
            time.sleep(1)
        elif curr_date.time() >= dt.time(9, 30) and curr_date.time() < dt.time(15, 30):
            historic_params = {
                "exchange": "NFO",
                "symboltoken": token,
                "interval": "FIFTEEN_MINUTE",
                "fromdate": dt.datetime.now(tz=tz.gettz('Asia/Kolkata')).replace(hour=9, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M"),
                "todate": to_date
            }
            time.sleep(7)
            intraday_data = get_intraday_data(token, historic_params)
            print(intraday_data)
            if curr_date.time() < dt.time(12, 30):
                orb_high = intraday_data['H'].max()
                orb_low = intraday_data['L'].min()
                print(curr_date, "HIGH AND LOW")
                print(curr_date, orb_high, orb_low)
            elif curr_date.time() > dt.time(12, 30):
                if orb_high == 0 and orb_low == 0:
                    orb_high = intraday_data.head(4)['H'].max()
                    orb_low = intraday_data.head(4)['L'].min()
                    print(curr_date, "HIGH AND LOW")
                    print(curr_date, orb_high, orb_low)
                # Code for placing order
                if intraday_data['C'].iloc[-1] > orb_high and buy == 0 and sell == 0:
                    strikes = select_strike(get_strike(intraday_data['C'].iloc[-1]), 'PE')
                    buy = intraday_data['C'].iloc[-1]
                    stop_low = intraday_data['L'].iloc[-1]
                    stop_loss_buy = intraday_data['C'].iloc[-1] - 40
                    # placeOrder('BUY', symbol, token, buy,
                    #            stop_loss_buy, quantity)
                    print(curr_date, "Buy at:", intraday_data['C'].iloc[-1])
                elif intraday_data['C'].iloc[-1] < orb_low and buy == 0 and sell == 0:
                    strikes = select_strike(get_strike(intraday_data['C'].iloc[-1]), 'CE')
                    sell = intraday_data['C'].iloc[-1]
                    stop_high = intraday_data['H'].iloc[-1]
                    # stop_loss_sell = intraday_data['C'].iloc[-1] + 40
                    # placeOrder('SELL', symbol, token,
                    #            sell, stop_loss_sell, quantity)
                    print(curr_date, "Sell at:", intraday_data['C'].iloc[-1])
                elif buy and (intraday_data['C'].iloc[-1] < stop_low):
                    # placeOrder('SELL', symbol, token, '0', '0', quantity)
                    print(curr_date, "Stop Loss Hit")
                    break
                elif sell and (intraday_data['C'].iloc[-1] > stop_high):
                    # placeOrder('BUY', symbol, token, '0', '0', quantity)
                    print(curr_date, "Stop loss Hit.")
                    break
            time.sleep(900 - (curr_date.time().minute *
                              60 + curr_date.time().second) % 900)
        elif curr_date.time() >= dt.time(15, 30):
            print("Market Closed.")
else:
    print("Today is a trading holiday.")