from os import getenv

from dotenv import load_dotenv

load_dotenv(override=True)

PREFIX = getenv("PREFIX", "/api")
HDX_URL = getenv("HDX_URL", "https://data.humdata.org")
VECTOR_COMMANDS = "Vector commands"
