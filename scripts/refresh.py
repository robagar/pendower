#!/usr/bin/env python3

import sys
import importlib.util
from pathlib import Path
import json
import toml
from PIL import Image, ImageDraw, ImageFont
import arrow

try:
    from inky.auto import auto
    inky = auto()
except ImportError:
    inky = None

scripts_dir = Path(__file__).parent
project_dir = scripts_dir.parent 
lib_dir = project_dir / "lib"
data_dir = project_dir / "data"
assets_dir = project_dir / "assets"

##############################################################################
def import_lib(name): 
    spec = importlib.util.spec_from_file_location(name, lib_dir / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
###############################################################################

sg = import_lib("stormglass")
util = import_lib("util")
bezier = import_lib("bezier")
gradient = import_lib("gradient")

config_file = scripts_dir / "config.toml"

with open(config_file, "r") as f:
    config = toml.load(f)

spot = sg.Spot(**config["spot"])
print(spot)

stormglass = sg.Stormglass(config["stormglass"], data_dir)

today = arrow.now().floor('day')

num_days = 3
time_span = today.span('day', num_days)
(time_from, time_to) = time_span
print(f'{time_from} → {time_to}')

weather_data = stormglass.get_weather(spot, time_span, 'waveHeight')
tide_data = stormglass.get_tides(spot, time_span)
astronomy_data = stormglass.get_astronomy(spot, time_span)

# actual display size
display_width = 640
display_height = 400

# draw surface size
draw_width = display_width * 4
draw_height = display_height * 4

t_from = time_from.timestamp()
t_to = time_to.timestamp()

def time_x(t):
    w = draw_width
    return w * (t.timestamp() - t_from) / (t_to - t_from)  

image = Image.new("RGB", (draw_width, draw_height), "seashell")
draw = ImageDraw.Draw(image)

days = arrow.Arrow.interval('days', time_from, time_to)
day_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 80)

##############################################################################
# nights

def draw_nights():
    h = draw_height
    w = draw_width

    sunset_x = 0
    for a in astronomy_data:
        x = time_x(a.sunrise)
        draw.rectangle([(sunset_x,0), (x, h)], fill='lightgray')
        sunset_x = time_x(a.sunset)

    if sunset_x < w:
        draw.rectangle([(sunset_x,0), (w, h)], fill='lightgray')

    dusk_x = 0    
    for a in astronomy_data:
        x = time_x(a.nautical_dawn)
        draw.rectangle([(dusk_x,0), (x, h)], fill='silver')
        dusk_x = time_x(a.nautical_dusk)

    if dusk_x < w:
        draw.rectangle([(dusk_x,0), (w, h)], fill='silver')


##############################################################################
# tides

tide_pixels_per_metre = 50    

def tide_y(h):
    return 280 - h * tide_pixels_per_metre

def draw_tides():
    points = []
    last_x = None
    last_y = None 
    for t in tide_data:
        x = time_x(t.time)
        y = tide_y(t.height)
        if last_x is not None:
            control_points = []
            d = (x - last_x) / 3
            control_points.append((last_x,last_y))
            control_points.append((last_x + d, last_y))
            control_points.append((x - d, y))
            control_points.append((x,y))

            curve_bezier = bezier.make_bezier(control_points)
            ts = [t/100.0 for t in range(101)]
            points.extend(curve_bezier(ts))
        last_x = x
        last_y = y

    draw.line(points, fill="green", width=8)

##############################################################################
# wave height

wave_height_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 60)
wave_pixels_per_metre = 360    
bottom = draw_height - 150

def draw_wave_height_bars():
    points = [(0,bottom)]
    last_x = None
    last_y = None
    for d in weather_data:
        x = time_x(d.time)
        y = bottom - d.wave_height * wave_pixels_per_metre

        if last_x is not None:
            points.append((last_x, y))

        points.append((x, y))
        
        last_x = x
        last_y = y
        
    points.append((draw_width, last_y))
    points.append((draw_width, bottom))

    gradient.draw_vertical_gradient_polygon(image, points, bottom='navy', top='aquamarine')

def draw_days():
    h = draw_height
    for i,d in enumerate(days):
        day = d[0]
        if i == 0:
            day_name = "Today"
        elif i == 1:
            day_name = "Tomorrow"
        else:
            day_name = day.format("dddd")

        x = time_x(day)

        if i != 0:
            draw.line([(x,0), (x,h)], fill="gray")

        x = time_x(day.shift(hours=+12))
        draw.text((x + 20, h - 130), day_name, anchor="ma", font=day_font, fill="black")

def draw_wave_height_lines_metres():
    w = draw_width
    for i in range(1,5):
        y = bottom - i * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), f'{i}m', font=wave_height_font, fill="gray") 

def draw_wave_height_lines_feet():
    w = draw_width
    for (h,l) in [(3, "3ft"), (6, "6ft"), (9, "9ft")]:
        y = bottom - util.feet_to_metres(h) * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), l, font=wave_height_font, fill="gray") 

def draw_wave_height_lines_human():
    w = draw_width
    for (h,l) in [(3, "small"), (6, "large"), (9, "huge!")]:
        y = bottom - util.feet_to_metres(h) * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), l, font=wave_height_font, fill="gray") 

now_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 60)
def draw_now():
    t = arrow.now()
    x = time_x(t)
    h = draw_height
    draw.line([(x,0), (x,h)], fill="red", width=4)
    draw.text((x + 10, 0), t.format("HH:mm"), font=now_font, anchor="la", fill="red")


title_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 100)
def draw_title():
    draw.text((draw_width - 20, 0), spot.name, font=title_font, anchor="ra", fill="black")

def draw_all():
    draw_nights()
    draw_tides()
    draw_wave_height_bars()
    draw_days()
    draw_wave_height_lines_human()
    draw_now()
    draw_title()

draw_all()

# resize with anti-aliasing
image = image.resize((display_width, display_height), Image.LANCZOS)

if inky:
    inky.set_image(image)
    inky.show()
else:
    image.show()




