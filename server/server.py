#!/usr/bin/python3

import json
from core import Core

config = json.load(open("config.json","r"))

core = Core(config)
core.run()