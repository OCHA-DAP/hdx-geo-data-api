from logging.config import fileConfig
from os import environ, getenv

from dotenv import load_dotenv
from mixpanel import Mixpanel

load_dotenv(override=True)

BASE_URL_PATH = getenv("BASE_URL_PATH", "")
DOCS_URL = f"{BASE_URL_PATH}{getenv('DOCS_URL', '/docs')}"
HDX_URL = getenv("HDX_URL", "http://data.humdata.local")
HDX_AUTH_URL = f"{HDX_URL}/api/3/action/hdx_token_info"
LOGGING_CONF_FILE = getenv("LOGGING_CONF_FILE", "logging.conf")
MIXPANEL_TOKEN = getenv("MIXPANEL_TOKEN", "")
OPENAPI_URL = f"{BASE_URL_PATH}{getenv('OPENAPI_URL', '/openapi.json')}"
PREFIX = f"{BASE_URL_PATH}{getenv('PREFIX', '/api')}"
REDOC_URL = f"{BASE_URL_PATH}{getenv('REDOC_URL', '/redoc')}"
TIMEOUT = int(getenv("TIMEOUT", f"{5 * 60}"))  # Default: 5 min
VECTOR_COMMANDS = "Vector commands"

fileConfig(LOGGING_CONF_FILE)

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"

mixpanel = Mixpanel(MIXPANEL_TOKEN) if MIXPANEL_TOKEN else None
