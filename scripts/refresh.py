#!/usr/bin/env python3

import sys
import importlib.util
from pathlib import Path
import json
import toml


scripts_dir = Path(__file__).parent
lib_dir = scripts_dir.parent / "lib"
data_dir = scripts_dir.parent / "data"

##############################################################################
# Python import 
spec = importlib.util.spec_from_file_location("stormglass", lib_dir / "stormglass.py")
sg = importlib.util.module_from_spec(spec)
sys.modules["stormglass"] = sg
spec.loader.exec_module(sg)
###############################################################################

config_file = scripts_dir / "config.toml"

with open(config_file, "r") as f:
    config = toml.load(f)

spot = sg.Spot(**config["spot"])
print(spot)

stormglass = sg.Stormglass(config["stormglass"], data_dir)

data = stormglass.get_weather(spot, 'waveHeight')



print(data)


