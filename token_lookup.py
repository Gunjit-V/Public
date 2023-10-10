import pandas as pd
import quotes_master
import datetime as dt


def get_quote_details(exchange, symbol, instrument, option_type='XX', strike_price='-0.01'):
    print("Opening file: " + exchange + '_symbols.txt')
    with open(exchange + '_symbols.txt', 'r') as file:
        quotes = file.read().splitlines()
    attributes = quotes[0].split(',')
    quotes_list = []

    for quote in quotes[1:]:
        quote_list = quote.split(',')
        new_dict = {}
        for i in range(0, len(attributes)):
            new_dict[attributes[i]] = quote_list[i]
        quotes_list.append(new_dict)
    desired_quotes = []
    for quote_dict in quotes_list:
        if (exchange == "NFO" and quote_dict['Symbol'] == symbol and quote_dict['Instrument'] == instrument and quote_dict['OptionType'] == option_type and quote_dict['StrikePrice'] == strike_price):
            desired_quotes.append(quote_dict)
        if (exchange == "NSE" and quote_dict['Symbol'] == symbol):
            desired_quotes.append(quote_dict)
    if (exchange == "NFO"):
        sorted_data = sorted(
            desired_quotes, key=lambda x: dt.datetime.strptime(x['Expiry'], '%d-%b-%Y'))
        desired_quotes = sorted_data
    return desired_quotes