import json
from rest_framework.parsers import BaseParser


class PlainTextJSONParser(BaseParser):
    """
    Parse text/plain requests that contain JSON into Python data.
    """
    media_type = "text/plain"

    def parse(self, stream, media_type=None, parser_context=None):
        raw = stream.read().decode("utf-8")
        return json.loads(raw)