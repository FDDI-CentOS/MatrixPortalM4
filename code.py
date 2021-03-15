import time
import board
import terminalio
import json
from random import randint
import adafruit_requests as requests
from adafruit_matrixportal.matrixportal import MatrixPortal

# --- Instantiate Display Object and Initialize Cron Clocks ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)
timer = 60
last_update = time.monotonic()

# --- Function Request Get JSON Source Data ---
def getData(url):
    try:
        data = matrixportal.fetch(url,timeout=10)
        data = json.loads(data)
        return data
    except Exception as e:
        error = f"Data API Error: {e}"
        return error

# --- Function to Parse CoinDesk JSON Data ---
def crypto_Parser():
    try:

        crypto_url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        crypto_data = getData(crypto_url)
        crypto_quote = 'BTC: $'

        for k, v in crypto_data.items():
            if k == 'bpi':
                for e, i in v.items():
                    if e == 'USD':
                        for c, d in i.items():
                            if c == 'rate':
                                crypto_quote += d[:-2]
        return crypto_quote

    except Exception as e:
        return f"Error: Crypt Parser Failed, {e}"

# --- Function to Parse Yahoo Finance JSON Data ---
def stock_Parser(stock_portfolio):
    try:
        # --- Conditional to Update Stocks Only Once Every Two Hours ---
        fcs_key = '0LClGTTVWuZgD1fTMOrADE'
        sp = stock_portfolio
        stocks = ''
        output = ''

        # --- Query Builder for Fetch Command ---
        for i in list(stock_portfolio.keys()):
            stocks += str(i)+","
        stocks = stocks[:-1]

        stock_query = f'https://fcsapi.com/api-v3/stock/latest?symbol={stocks}&access_key={fcs_key}'
        stock_json = getData(stock_query)

        for k, v in stock_json.items():
            if k == 'response':
                for i in v:
                    if i['cty'] == 'united-states':
                        output += i['s'] + ': ' + i['l'] + ' '
        return output[:-1]

    except Exception as e:
        return f"Error: Stock Parser Failed, {e}"

# --- Function to Parse Time JSON Data ---
def time_Parser():
    try:
        time_url = 'http://worldtimeapi.org/api/timezone/America/Los_Angeles'
        current_time = getData(time_url)

        # --- Date Time String Generator ---
        for k,v in current_time.items():
            if k == 'datetime':
                utc = v.split('T')
                t = utc[1].split('.')[0]
                d = utc[0]
                dt = str(d) + ' ' + str(t)
                time_clock = time.monotonic()
                return dt

    except Exception as e:
        return f"Error: Time Parser Failed, {e}"

# --- Portfolio Data Structure: Symbol [Purchase Price, Qty, Currnet Price] ---
stock_portfolio = {'GOOG':[1086.0,0,0],'SHOP':[1123.53,0,0],'DIS':[124.23,0,0],'PLUG':[15.80,0,0],'TGT':[178.42,0,0]}

# --- HTML Color Dictionary ---
colors = {'RED':'#cf2727','GREEN':'#77D71C','BLUE':'#0846e4','YELLOW':'#E0F011','ORANGE':'#F0A211','PURPLE':'#824BEB'}

# --- Initialize Parser Calls ---
tc = time_Parser()
cp = crypto_Parser()
sp = stock_Parser(stock_portfolio)

# --- Function to Update Parser Call Data ---
def update_data():
    tc = time_Parser()
    cp = crypto_Parser()
    sp = stock_Parser(stock_portfolio)


# --- Set Text Label ID 0 Top Row Title ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+2),
    scrolling=False,
    text_scale = 0
)

# --- Set Text Label ID 1 Second Row Sub-Title ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)+10),
    scrolling=False,
    text_scale = 0
)

# --- Set Text Label ID 2 Third Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4)-2),
    scrolling=True,
    text_scale = 0
)

# --- Set Text Label ID 3 Fourth Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4) +6),
    scrolling=True,
    text_scale = 0
)

# --- Set Text Label ID 4 Fifth Row ---
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, (matrixportal.graphics.display.height // 4) +14),
    scrolling=True,
    text_scale = 0
)

SCROLL_DELAY = 0.03

# --- Set Text Loop ---
while True:
    pallet = list(colors.values())
    matrixportal.set_text(" Ticker",0)
    matrixportal.set_text_color(pallet[randint(0,5)],0)
    matrixportal.set_text("      Time",1)
    matrixportal.set_text(tc,2)
    matrixportal.set_text_color(pallet[0],2)
    matrixportal.set_text(cp,3)
    matrixportal.set_text_color(pallet[3],3)
    matrixportal.set_text(sp,4)
    matrixportal.set_text_color(pallet[1],4)

    # Scroll Text
    matrixportal.scroll_text(SCROLL_DELAY)

    # Data Refresh
    if time.monotonic() - last_update >= timer:
        last_udpate = time.monotonic()
        update_data()
