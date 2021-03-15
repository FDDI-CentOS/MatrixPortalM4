import time
import board
import terminalio
import json
from random import randint
import adafruit_requests as requests
from adafruit_matrixportal.matrixportal import MatrixPortal

# --- Instantiate Display Object and Initialize Cron Clocks ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)
last_update = time.monotonic()
update_delay = 3600
SCROLL_DELAY = .04

# --- Function to Parse Time JSON Data ---
def time_Parser():
    try:
        time_url = 'http://worldtimeapi.org/api/timezone/America/Los_Angeles'
        current_time = json.loads(matrixportal.fetch(time_url, timeout=5))
        tc = current_time['datetime']
        utc = tc.split('T')
        t = str(utc[1].split('.')[0])
        d = str(utc[0])
        dt = d + ' ' + t
        return dt

    except Exception as e:
        return f"Error: Time Parser Failed, {e}"
        

# --- Function to Parse CoinDesk JSON Data ---
def crypto_Parser():
    try:
        crypto_url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        crypto_data = json.loads(matrixportal.fetch(crypto_url, timeout=5))
        crypto_quote = 'BTC: $'
        
        crypto_quote += crypto_data['bpi']['USD']['rate'][:-2]
        return crypto_quote

    except Exception as e:
        return f"Error: Crypt Parser Failed, {e}"
        

# --- Function to Parse Finance JSON Data ---
def stock_Parser(stock_portfolio):
    try:
        # --- Conditional to Update Stocks Only Once Every Two Hours ---
        fcs_key = '<Your Key Here>'
        sp = stock_portfolio
        stocks = ''
        output = ''

        # --- Query Builder for Fetch Command ---
        for i in list(stock_portfolio.keys()):
            stocks += str(i)+","
        stocks = stocks[:-1]
        stock_query = f'https://fcsapi.com/api-v3/stock/latest?symbol={stocks}&access_key={fcs_key}'
        stock_json = json.loads(matrixportal.fetch(stock_query, timeout=10))
        for k, v in stock_json.items():
            if k == 'response':
                for i in v:
                    if i['cty'] == 'united-states':
                        output += i['s'] + ': ' + i['l'] + ' '
        return output[:-1]

    except Exception as e:
        return f"Error: Stock Parser Failed, {e}"

# --- HTML Color Dictionary ---
colors = {'RED':'#cf2727','GREEN':'#77D71C','BLUE':'#0846e4','YELLOW':'#E0F011','ORANGE':'#F0A211','PURPLE':'#824BEB'}

# --- Portfolio Data Structure: Symbol [Purchase Price, Qty, Currnet Price] ---
stock_portfolio = {'GOOG':[0.0,0,0],'SHOP':0,0,0],'DIS':[0,0,0],'PLUG':[0,0,0],'TGT':[0,0,0]}

# --- Initialize Parser Calls ---
tc = time_Parser()
cp = crypto_Parser()
sp = stock_Parser(stock_portfolio)

# --- Function to Update Parser Call Data ---
def update_data():
    try:
        tc = time_Parser()
        cp = crypto_Parser()
        
        # --- Pause Stock Feed for Off Hours --- 6 am - 2 pm PST
        if int(tc[-8]) == 0 and int(tc[-7]) < 6:
            sp = "*** Stock Market Off Hours ***"
            pass
        elif int(tc[-8:-6]) > 14:
            sp = "*** Stock Market Off Hours ***"
            pass
        else:
            sp = stock_Parser(stock_portfolio)
    except Exception as e:
        return f"Error Updating Data: {e}"

# --- Set Text Label ID 0 First Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)-2),
    scrolling=True,
    text_scale = 0,
)

# --- Set Text Label ID 1 Second Row --- Static Title
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+2),
    scrolling=False,
    text_scale = 0,
)

# --- Set Text Label ID 2 Third Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+6),
    scrolling=True,
    text_scale = 0,
)

# --- Set Text Label ID 3 Fourth Row --- Static Title
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+10),
    scrolling=False,
    text_scale = 0,
)

# --- Set Text Label ID 4 Fifth Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+14),
    scrolling=True,
    text_scale = 0,
)

# --- Set Text Loop ---
while True:
    pallet = list(colors.values())
    matrixportal.set_text(" Ticker",1)
    matrixportal.set_text_color(pallet[randint(0,5)],1)
    matrixportal.set_text("      Time",3)
    
    matrixportal.set_text(tc,0)
    matrixportal.set_text_color(pallet[0],0)
    time.sleep(3)
    
    matrixportal.set_text(cp,2)
    matrixportal.set_text_color(pallet[3],2)
    time.sleep(3)
    
    matrixportal.set_text(sp,4)
    matrixportal.set_text_color(pallet[1],4)
    time.sleep(3)
    
    # --- Scroll Text ---
    matrixportal.scroll_text(SCROLL_DELAY)

    # --- Data Feed Cron Check ---
    if time.monotonic() > last_update + update_delay:
        update_data()
        last_update = time.monotonic()
