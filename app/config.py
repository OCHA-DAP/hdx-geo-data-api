from logging.config import fileConfig
from os import environ, getenv

from dotenv import load_dotenv

load_dotenv(override=True)

HDX_URL = getenv("HDX_URL", "https://data.humdata.org")
LOGGING_CONF_FILE = getenv("LOGGING_CONF_FILE", "logging.conf")
PREFIX = getenv("PREFIX", "/api")
TIMEOUT = int(getenv("TIMEOUT", "3600"))  # Default: 1 hour
VECTOR_COMMANDS = "Vector commands"

fileConfig(LOGGING_CONF_FILE)

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"
