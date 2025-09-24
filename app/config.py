from os import getenv

from dotenv import load_dotenv

load_dotenv(override=True)

PREFIX = getenv("PREFIX", "/api")
