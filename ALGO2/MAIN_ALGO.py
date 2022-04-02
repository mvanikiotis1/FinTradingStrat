# This is a python example algorithm using REST API for the RIT ALGO2 Case

import signal
import requests
from time import sleep

# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

# set your API key to authenticate to the RIT client
API_KEY = {'X-API-Key': '474RQCA1'}
shutdown = False
# other settings for market making algo
SPREAD = 0.02
SCALP_SPREAD = 0.03
BUY_VOLUME = 1000
SELL_VOLUME = 1000
SCALP_VOLUME = 5000



# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    case = resp.json()
    return case['tick']

# this helper method returns the last close price for the given security, one tick ago
def ticker_close(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    ticker_history = resp.json()
    if ticker_history:
        return ticker_history[0]['close']
    else:
        raise ApiException('Response error. Unexpected JSON response.')

def ticker_bid(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    ticker_history = resp.json()
    if ticker_history:
        print(ticker_history[0])
        # return ticker_history[0]['bid']
    else:
        raise ApiException('Response error. Unexpected JSON response.')

def ticker_ask(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    ticker_history = resp.json()
    if ticker_history:
        print(ticker_history[0])
        # return ticker_history[0]['ask']
    else:
        raise ApiException('Response error. Unexpected JSON response.')

# this helper method submits a pair of limit orders to buy and sell VOLUME of each security, at the last price +/- SPREAD
def buy_sell(session, to_buy, to_sell, last):
    buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME, 'action': 'BUY', 'price': last - SPREAD}
    sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME, 'action': 'SELL', 'price': last + SPREAD}
    session.post('http://localhost:9999/v1/orders', params=buy_payload)
    session.post('http://localhost:9999/v1/orders', params=sell_payload)

def buy_bid(session, to_buy, bid, BUY_SCALP_VOLUME):
    buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_SCALP_VOLUME, 'action': 'BUY', 'price': bid + .01}
    session.post('http://localhost:9999/v1/orders', params=buy_payload)

def sell_ask(session, to_sell, ask, SELL_SCALP_VOLUME):
    buy_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_SCALP_VOLUME, 'action': 'SELL', 'price': ask - .01 }
    session.post('http://localhost:9999/v1/orders', params=buy_payload)

# this helper method gets all the orders of a given type (OPEN/TRANSACTED/CANCELLED)
def get_orders(session, status):
    payload = {'status': status}
    resp = session.get('http://localhost:9999/v1/orders', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    orders = resp.json()
    return orders

def ticker_bid_ask(session, ticker): 
   payload = {'ticker': ticker} 
   resp = session.get('http://localhost:9999/v1/securities/book',params=payload) 
   if resp.ok: 
       book = resp.json() 
       return book['bids'][0]['price'], book['asks'][0]['price'] 
   raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the APIhyperlink in the client toolbar and/or the RIT REST API Documentation.pdf)') 

# this is the main method containing the actual market making strategy logic
def main():
    # creates a session to manage connections and requests to the RIT Client
    with requests.Session() as s:
        # add the API key to the session to authenticate during requests
        s.headers.update(API_KEY)
        # get the current time of the case
        tick = get_tick(s)

        # while the time is between 5 and 295, do the following
        while tick > 2 and tick < 298:
            # get the open order book and ALGO last tick's close price
            orders = get_orders(s, 'OPEN')
            algo_close = ticker_close(s, 'ALGO')
            bid, ask = ticker_bid_ask(s, 'ALGO')

            position = s.get('http://localhost:9999/v1/securities?ticker=ALGO').json()
            myposition = position[0]['position']
            # pprint.pprint(myposition)
            if myposition >= 15000:
                SPREAD1 = 0.01
                BUY_SCALP_VOLUME = 0
                SELL_SCALP_VOLUME = 5000
            elif myposition <= -15000:
                SPREAD1 = 0.01
                BUY_SCALP_VOLUME = 5000
                SELL_SCALP_VOLUME = 0 
            else:
                SPREAD1 = 0.01
                BUY_SCALP_VOLUME = 5000
                SELL_SCALP_VOLUME = 5000

            if ask - bid > .03:
                buy_bid(s, 'ALGO', bid, BUY_SCALP_VOLUME)
                sell_ask(s, 'ALGO', ask, SELL_SCALP_VOLUME)
                buy_bid(s, 'ALGO', bid, BUY_SCALP_VOLUME)
                sell_ask(s, 'ALGO', ask, SELL_SCALP_VOLUME)
                buy_bid(s, 'ALGO', bid, BUY_SCALP_VOLUME)
                sell_ask(s, 'ALGO', ask, SELL_SCALP_VOLUME)
                sleep(2)
            
            

            # check if you have 0 open orders
            # if len(orders) == 0:
            #     # submit a pair of orders and update your order book
            #     buy_sell(s, 'ALGO', 'ALGO', algo_close)
            #     orders = get_orders(s, 'OPEN')
            #     sleep(.1)

            # check if you don't have a pair of open orders
            # if len(orders) != 2 and len(orders) > 0:
            #     # submit a POST request to the order cancellation endpoint to cancel all open orders
            #     s.post('http://localhost:9999/v1/commands/cancel?all=1')
            #     sleep(1)

            # refresh the case time. THIS IS IMPORTANT FOR THE WHILE LOOP
            tick = get_tick(s)

# this calls the main() method when you type 'python algo2.py' into the command prompt
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
