from logging.config import fileConfig
from os import environ, getenv

from dotenv import load_dotenv

load_dotenv(override=True)

HDX_URL = getenv("HDX_URL", "http://data.humdata.local")
LOGGING_CONF_FILE = getenv("LOGGING_CONF_FILE", "logging.conf")
BASE_URL_PATH = getenv("BASE_URL_PATH", "")
PREFIX = f"{BASE_URL_PATH}{getenv('PREFIX', '/api')}"
DOCS_URL = f"{BASE_URL_PATH}{getenv('DOCS_URL', '/docs')}"
OPENAPI_URL = f"{BASE_URL_PATH}{getenv('OPENAPI_URL', '/openapi.json')}"
REDOC_URL = f"{BASE_URL_PATH}{getenv('REDOC_URL', '/redoc')}"
TIMEOUT = int(getenv("TIMEOUT", "3600"))  # Default: 1 hour
VECTOR_COMMANDS = "Vector commands"

fileConfig(LOGGING_CONF_FILE)

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"
