# This is a python example algorithm using REST API for the RIT ALGO2 Case

import signal
import requests
from time import sleep
import pprint

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
SPREAD = 0.01
BUY_VOLUME = 1000
SELL_VOLUME = 1000


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

# this helper method submits a pair of limit orders to buy and sell VOLUME of each security, at the last price +/- SPREAD
def buy_sell(session, to_buy, to_sell, last, BUY_VOLUME, SELL_VOLUME, SPREAD):
    buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME, 'action': 'BUY', 'price': last - SPREAD}
    sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME, 'action': 'SELL', 'price': last + SPREAD}
    session.post('http://localhost:9999/v1/orders', params=buy_payload)
    session.post('http://localhost:9999/v1/orders', params=sell_payload)

# this helper method gets all the orders of a given type (OPEN/TRANSACTED/CANCELLED)
def get_orders(session, status):
    payload = {'status': status}
    resp = session.get('http://localhost:9999/v1/orders', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    orders = resp.json()
    return orders
    

# this is the main method containing the actual market making strategy logic
def main():
    # creates a session to manage connections and requests to the RIT Client
    with requests.Session() as s:
        # add the API key to the session to authenticate during requests
        s.headers.update(API_KEY)
        # get the current time of the case
        tick = get_tick(s)

                #    CTRL + SHIFT + L = Change all names of the tickers

        # while the time is between 5 and 295, do the following
        while tick > 1 and tick < 297:


            # get the open order book and ALGO last tick's close price
            orders = get_orders(s, 'OPEN')
            algo_close = ticker_close(s, 'ALGO')

            # Gets our Posistion of the Ticker
            position = s.get('http://localhost:9999/v1/securities?ticker=ALGO').json()
            myposition = position[0]['position']
            # pprint.pprint(position[0]['position'])

            # If My posistion is Greater than 10000 then we set the variables as these
            if int(myposition) > 10000:
                SPREAD1 = 0.01
                SPREAD2 = 0.02
                BUY_VOLUME = 10
                SELL_VOLUME = 500 
        
            # If My position is Less than -10000 then we set the vairables as these
            elif myposition < -10000:
                SPREAD1 = 0.01
                SPREAD2 = 0.02
                BUY_VOLUME = 500
                SELL_VOLUME = 10  

            #  Other wise we set the variables as these 
            else:
                SPREAD1 = 0.01
                SPREAD2 = 0.02
                BUY_VOLUME = 150
                SELL_VOLUME = 150   

            # check if you have 0 open orders
            if len(orders) == 0:
                # submit a pair of orders and update your order book

                # Submiting orders for the entire duration of the case
                for i in range(200):
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    position = s.get('http://localhost:9999/v1/securities?ticker=ALGO').json()
                    myposition = position[0]['position']
                    # pprint.pprint(myposition)
                    if int(myposition) > 10000:
                        SPREAD1 = 0.01
                        BUY_VOLUME = 10
                        SELL_VOLUME = 500 
                    elif myposition < -10000:
                        SPREAD1 = 0.01
                        BUY_VOLUME = 500
                        SELL_VOLUME = 10  
                    else:
                        SPREAD1 = 0.01
                        BUY_VOLUME = 150
                        SELL_VOLUME = 150 

                    # This is entering in the limit orders into the book
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD1)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD1)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD1)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD1)


                    # This is rechecking the position and the ticker close and doing the exact same thing at the 2nd spread level
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    position = s.get('http://localhost:9999/v1/securities?ticker=ALGO').json()
                    myposition = position[0]['position']
                    # pprint.pprint(myposition)
                    if int(myposition) > 10000:
                        SPREAD2 = 0.02
                        BUY_VOLUME = 10
                        SELL_VOLUME = 500 
                    elif myposition < -10000:
                        SPREAD2 = 0.02
                        BUY_VOLUME = 500
                        SELL_VOLUME = 10   
                    else:
                        SPREAD2 = 0.02
                        BUY_VOLUME = 150
                        SELL_VOLUME = 150 
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD2)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD2)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD2)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD2)
                    orders = get_orders(s, 'OPEN')


                    # This is rechecking the position and the ticker close and doing the exact same thing at the 2nd spread level
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    position = s.get('http://localhost:9999/v1/securities?ticker=ALGO').json()
                    myposition = position[0]['position']
                    # pprint.pprint(myposition)
                    if int(myposition) > 10000:
                        SPREAD3 = SPREAD2 +.01
                        BUY_VOLUME = 10
                        SELL_VOLUME = 500 
                    elif myposition < -10000:
                        SPREAD3 = SPREAD2 +.01
                        BUY_VOLUME = 500
                        SELL_VOLUME = 10   
                    else:
                        SPREAD3 = SPREAD2 +.01
                        BUY_VOLUME = 150
                        SELL_VOLUME = 150 
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD3)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD3)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD3)
                    sleep(.1)
                    orders = get_orders(s, 'OPEN')
                    algo_close = ticker_close(s, 'ALGO')
                    buy_sell(s, 'ALGO', 'ALGO', algo_close, BUY_VOLUME, SELL_VOLUME, SPREAD3)
                    orders = get_orders(s, 'OPEN')
                    
                # sleep(5)


        # We are not canceling any orders that we enter.
        
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
