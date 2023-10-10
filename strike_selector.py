from token_lookup import *
from api_helper import ShoonyaApiPy
from cred import *
from quotes_master import *

get_master()

api = ShoonyaApiPy()

obj = api.login(userid=user_id, password=password, twoFA=twoFA,
                    vendor_code=vendor_code, api_secret=api_key, imei=imei)

margin_available = float(api.get_limits()['cash']) + float(api.get_limits()['payout']) - 10000
print(f'Margin Available : {margin_available}')
def get_hedge(atm_strike, optt):
    flag = False
    diff = 400
    print("Final Strike price : ", atm_strike, optt)
    atm = get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, atm_strike)[0]
    print(atm)
    positionList = []
    atm_obj = {
        "prd" : "M",
        "exch" : atm['Exchange'],
        "instname" : atm["Instrument"],
        "symname" : atm["Symbol"],
        "exd" : atm["Expiry"],
        "optt" : optt,
        "strprc" : atm_strike,
        "sellqty" : str(int(atm["LotSize"]) * 1)
    }
    positionList.append(atm_obj)
    print("_________________Position List_________________")
    print(positionList)
    hedge_strike = '0'
    print("_________________Hedge Strike_________________")
    print(hedge_strike)
    while True:
        if optt == 'CE':
            hedge = get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, str(int(atm_strike) + diff))[0]
            hedge_strike = str(int(atm_strike) + diff)
            print("New Hedge : ", hedge_strike, " Diff : ", diff)
        elif optt == 'PE':
            hedge = get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, str(int(atm_strike) - diff))[0]
            hedge_strike = str(int(atm_strike) - diff)
            print("New Hedge : ", hedge_strike, " Diff : ", diff)
        if hedge_strike == atm_strike:
            print("Margin Not available. Exiting")
            return []
        hedge_obj = {
            "prd" : "M",
            "exch" : hedge['Exchange'],
            "instname" : hedge["Instrument"],
            "symname" : hedge["Symbol"],
            "exd" : hedge["Expiry"],
            "optt" : optt,
            "strprc" : hedge_strike,
            "buyqty" : str(int(hedge["LotSize"]) * 1)
        }
        positionList.append(hedge_obj)
        print("_________________Position List After Hedge_________________")
        print(positionList)
        try:
            margin = api.span_calculator("FA64003",positionList)
            span = float(margin["span_trade"])
            exposure = float(margin["expo_trade"])
        except Exception as e:
            print(e)
        print("Margin for : ", atm_strike, hedge_strike," : " ,span + exposure)
        if span + exposure > margin_available:
            print("Margin Exceeded Condition")
            if optt == "CE":
                print("changing CE")
                diff = diff + 50
            elif optt == "PE":
                print("changing PE")
                diff = diff - 50
            positionList.pop()
            print("_________________Position List After Pop_________________")
            print(positionList)
        elif span + exposure <= margin_available:
            strikes = [hedge_strike, atm_strike]
            flag = True
        if flag:
            break
    return strikes

def select_strike(atm_strike, optt):
    while True:
        atm_quote = get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, atm_strike)[0]
        ltp = api.get_quotes(atm_quote['Exchange'], atm_quote['Token'])['lp']
        print(ltp)
        if float(ltp) >= 50:
            if optt == 'PE':
                print(str(int(atm_strike) - 50), optt)
                atm_strike = str(int(atm_strike) - 50)
            elif optt == 'CE':
                print(str(int(atm_strike) + 50), optt)
                atm_strike = str(int(atm_strike) + 50)
        elif float(ltp) >= 20 and float(ltp) < 50:
            print("Finding hedge")
            hedge = get_hedge(atm_strike, optt)
            break
        elif float(ltp) < 20:
            print("Not Enough premium today.")
            break
    
    return [get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, hedge[0])[0], get_quote_details('NFO', 'NIFTY', 'OPTIDX', optt, hedge[1])[0]]
    
# final_strikes = select_strike('19600', 'PE')
# print("_________________Final Strikes_________________")
# print(final_strikes)

# print(api.get_quotes('NFO', get_quote_details('NFO', 'NIFTY', 'OPTIDX', 'PE', final_strikes[0])[0]['Token']))
# print(api.get_quotes('NFO', get_quote_details('NFO', 'NIFTY', 'OPTIDX', 'PE', final_strikes[1])[0]['Token']))