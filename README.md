# Pendower

![Pendower](https://github.com/robagar/pendower/raw/main/images/pendower.jpeg)

A simple app for displaying local tide and surf conditions.

* High and low tides over the next few days
* Wave heights (combined swell and wind waves)
* Sunrise and sunset, with nautical twilight 

Designed for
* [Raspberry Pi Zero](https://www.raspberrypi.com/products/raspberry-pi-zero/)
* [Inky Impression 4"](https://shop.pimoroni.com/products/inky-impression-4?variant=39599238807635) or [Inky Impression 5.7"](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371) e-ink display
* Pendower Beach, Cornwall - my local beach, great for swimming and very occasionally surfable :)
* ...but can be configured for other locations

Data from the fantastic [stormglass.io](https://stormglass.io) API.  It only makes three requests per day, so is well under the limit for the free non-commercial plan.

## Installation

Clone or download the tarball of this repository, then install the Python dependencies with `pip`:

```bash
$ cd pendower
$ pip install -r requirements.txt
```

## Configuration

Save this with your configuration as _config.toml_ in the project root directory

```toml
[display]
# Inky Impression 4"
width = 640
height = 400

# Inky Impression 5.7"
# width = 600
# height = 448

[spot]
name = "Pendower Beach"
latitude = 50.204553
longitude = -4.947837

[stormglass]
api_key = "(your stormglass.io API key)"
data_source_preference = ["meto", "noaa", "sg"]
```

Test the configuration with

```bash
$ python scripts/refresh.py
```

*NB* If you change the configuration other than the `display` section, delete the _.json_ files in the _data_ directory before refreshing the display.


To refresh the display every 15 minutes with cron, run `crontab -e` and add a line like:

```
*/15 * * * * /your/path/to/pendower/scripts/refresh.py
```

## Version History

### 1.3

* display config

### 1.2

* configurable weather data source preference

### 1.1

* moon phase

### 1.0

* tides
* wave heights
