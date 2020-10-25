"""
This example will access the twitter follow button API, grab a number like
the number of followers... and display it on a screen!
if you can find something that spits out JSON data, we can display it
"""
import sys
import time
import board
from adafruit_pyportal import PyPortal
cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
sys.path.append(cwd)
import openweather_graphics  # pylint: disable=wrong-import-position

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

### START AIO CODE
# Import Adafruit IO HTTP Client
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
ADAFRUIT_IO_DATA_SOURCE = 'http://wifitest.adafruit.com/testwifi/index.html'
ADAFRUIT_IO_USER = secrets['aio_username']
ADAFRUIT_IO_KEY = secrets['aio_key']
ADAFRUIT_IO_DATA_LOCATION = []
### END AIO CODE

# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB"
LOCATION = "Richland, WA, US"

# Set up where we'll be fetching data from
DATA_SOURCE = "http://api.openweathermap.org/data/2.5/weather?q="+LOCATION
DATA_SOURCE += "&appid="+secrets['openweather_token']
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
DATA_LOCATION = []


# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=ADAFRUIT_IO_DATA_SOURCE,
                    json_path=ADAFRUIT_IO_DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000)

pyportal.set_backlight(0.75)
gfx = openweather_graphics.OpenWeather_Graphics(pyportal.splash, am_pm=True, celsius=False)

# push some test data to AIO
t0 = time.monotonic()
print('* pushing to aio...', (time.monotonic()-t0) / 60)
pyportal.push_to_io('shoplightlevel', (time.monotonic()-t0) / 60)
pyportal.push_to_io('shoplightlevel', (time.monotonic()-t0) / 60)
print('*** pushed to aio.   ', (time.monotonic()-t0) / 60)

### START AIO CODE
pyportal._url = DATA_SOURCE
pyportal._json_path = DATA_LOCATION

# Go get that data
print("Fetching text from", pyportal._url)
data = pyportal.fetch()
### END AIO CODE

localtile_refresh = None
weather_refresh = None
pyportal.play_file("storm_tracker.wav", wait_to_finish=True)  # True to disable speaker after playing
t0 = time.monotonic()

while True:
    # only query the online time once per hour (and on first run)
    if (not localtile_refresh) or (time.monotonic() - localtile_refresh) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time()
            localtile_refresh = time.monotonic()
        except (ValueError, RuntimeError) as e:  # ValueError added from quote.py change
            print("Some error occured, retrying! -", e)
            continue

    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            value = pyportal.fetch()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()

            print('*** pushing to aio...', (time.monotonic()-t0) / 60)
            pyportal.push_to_io('shoplightlevel', (time.monotonic()-t0) / 60)
            print('*** pushed to aio.   ', (time.monotonic()-t0) / 60)
            t0 = time.monotonic()

        except (ValueError, RuntimeError) as e:  # ValueError added from quote.py change
            print("Some error occured, retrying! -", e)
            continue

    gfx.update_time()
    time.sleep(30)  # wait 30 seconds before updating anything again
