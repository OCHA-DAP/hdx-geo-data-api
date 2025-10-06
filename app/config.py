from os import environ, getenv

from dotenv import load_dotenv

load_dotenv(override=True)

PREFIX = getenv("PREFIX", "/api")
HDX_URL = getenv("HDX_URL", "https://data.humdata.org")
VECTOR_COMMANDS = "Vector commands"

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"
