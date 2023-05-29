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

data = stormglass.get_weather(spot, time_span, 'waveHeight')

# actual display size
display_width = 640
display_height = 400

# draw surface size
w = display_width * 4
h = display_height * 4

t_from = time_from.timestamp()
t_to = time_to.timestamp()

def time_x(t):
    return w * (t.timestamp() - t_from) / (t_to - t_from)  

image = Image.new("RGB", (w, h), "white")
draw = ImageDraw.Draw(image)

days = arrow.Arrow.interval('days', time_from, time_to)

# day_font = ImageFont.truetype(f'{assets_dir / "ToThePointRegular.ttf"}', 100)
day_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 80)
wave_height_font = ImageFont.truetype(f'{assets_dir / "OpenSans.ttf"}', 40)

wave_pixels_per_metre = 300
    
bottom = h - 150

def draw_wave_height_bars():
    n = len(data)
    dx =  w / n
    points = [(0,bottom)]
    last_x = None
    last_y = None
    for d in data:
        x = time_x(d.time)
        y = bottom - d.wave_height * wave_pixels_per_metre

        if last_x is not None:
            points.append((last_x, y))

        points.append((x, y))
        
        last_x = x
        last_y = y
        
    points.append((w, last_y))
    points.append((w, bottom))

    draw.polygon(points, fill="blue")

def draw_days():
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

        draw.text((x + 20, h - 130), day_name, font=day_font, fill="black")

def draw_wave_height_lines_metres():
    for i in range(1,5):
        y = bottom - i * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), f'{i}m', font=wave_height_font, fill="gray") 

def draw_wave_height_lines_feet():
    for (h,l) in [(3, "3ft"), (6, "6ft"), (9, "9ft")]:
        y = bottom - util.feet_to_metres(h) * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), l, font=wave_height_font, fill="gray") 

def draw_wave_height_lines_human():
    for (h,l) in [(0.5, "flat"), (3, "small"), (6, "large"), (9, "huge!")]:
        y = bottom - util.feet_to_metres(h) * wave_pixels_per_metre
        draw.line([(0,y), (w,y)], fill="gray") 
        draw.text((10, y), l, font=wave_height_font, fill="gray") 

def draw_now():
    x = time_x(arrow.now())
    draw.line([(x,0), (x,h)], fill="red")

def draw_wave_heights():
    draw_wave_height_bars()
    draw_days()
    draw_wave_height_lines_human()
    draw_now()

draw_wave_heights()

# resize with anti-aliasing
image = image.resize((display_width, display_height), Image.LANCZOS)

if inky:
    inky.set_image(image)
    inky.show()
else:
    image.show()




