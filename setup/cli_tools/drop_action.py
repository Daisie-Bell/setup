from svaeva import Svaeva

from dotenv import load_dotenv

import logging

import os

load_dotenv()

svaeva = Svaeva()

logg = logging.getLogger("svaeva")

logg.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.FileHandler("drop_action.log")

fh.setFormatter(formatter)

logg.addHandler(fh)

for _ in svaeva.database.actions(platform="telegram"):
    print(_["id"])
    try:
        svaeva.database.actions.__delattr__(_["id"])
    except Exception as e:
        logg.error(e)
        continue

