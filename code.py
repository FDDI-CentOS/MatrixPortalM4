import time
import board
import terminalio
import json
from random import randint
import adafruit_requests as requests
from adafruit_matrixportal.matrixportal import MatrixPortal

# --- Function to Parse Time JSON Data ---
def time_Parser():
    try:
        time_url = 'http://api.timezonedb.com/v2.1/get-time-zone?key=Q7ZT79VNRQIK&format=json&by=zone&zone=America/Los_Angeles'
        current_time = json.loads(matrixportal.fetch(time_url, timeout=10))
        tc = current_time['formatted']
        utc = tc.split(' ')
        dt = utc[0] + ' ' + utc[1]
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

# --- Query Builder for Fetch Command ---
def fetchQuotes():
    stocks = ''
    output = ''
    fcs_key = '0LClGTTVWuZgD1fTMOrADE'

    for i in stock_portfolio:
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

# --- Function to Parse Finance JSON Data ---
def stock_Parser(tc):
    try:
        # --- Time Check for Market Closure
        print("*** Getting Stock Updates ****")
        hour = tc[-8:]
        
        if int(hour[0]) == 0 and int(hour[1]) <= 5:
            return f"*** Market Closed: Before Trading Day {tc}"
        elif int(hour[0]) == 1 and int(hour[1]) >= 4:
            return f"*** Market Closed: After Hours {tc}"
        elif time.monotonic() - last_stock_update  >= stock_update_delay:
            temp = fetchQuotes()
            print(temp)
            return temp
        else:
            return sp
    except Exception as e:
        print(f"Stock Parser Error: {e}")
        return f"Stock Parser Error: {e}"
# --- Function to Render Title and Flash Text ---
def renderTitle():
    matrixportal.set_text(" Ticker",1)
    matrixportal.set_text_color(pallet[randint(0,len(pallet)-1)],1)
    matrixportal.set_text("      Time",3)
    return None

# --- Function to Update Parser Call Data ---
def update_data():
    try:
        print("*** Updating Data and Pulling APIs ***")
        tc = time_Parser()
        cp = crypto_Parser()
        sp = stock_Parser(tc)

        updates = [tc,cp,sp]

        # --- Loop to Set Text and Scroll ---
        print(" ----------------Scrolling Text -------------------")
        for i in range(0,5,2):
            if i != 0:
                if i == 2:
                   index = i - 1
                else:
                    index = i - 2
            else:
                index = 0
            matrixportal.set_text(updates[index],i)
            matrixportal.set_text_color(pallet[index],i)

            # --- Scroll Text ---
            renderTitle()
            matrixportal.scroll_text(SCROLL_DELAY)
            time.sleep(2)

    except Exception as e:
        return f"Error Updating Data: {e}"


# --- Instantiate Display Object and Initialize Cron Clocks ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True, default_bg = './Stock3.bmp')
last_update = time.monotonic()
last_stock_update = time.monotonic()
stock_update_delay = 3600
update_delay = 60
SCROLL_DELAY = .04

# --- HTML Color Dictionary ---
colors = {'RED':'#cf2727','YELLOW':'#E0F011','ORANGE':'#F0A211','GREEN':'#77D71C','BLUE':'#0846e4','PURPLE':'#824BEB'}
pallet = list(colors.values())

# --- Portfolio Data Structure: Symbol [Purchase Price, Qty, Currnet Price] ---
stock_portfolio = ['GOOG','SHOP','DIS','PLUG','TGT']

# --- Initialize Parser Variable Values ---
tc = time_Parser()
cp = crypto_Parser()
sp = fetchQuotes()

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
    renderTitle()
    time.sleep(3)

    # --- Data Feed Cron Check ---
    if time.monotonic() - last_update > update_delay:
        update_data()
        last_update = time.monotonic()
