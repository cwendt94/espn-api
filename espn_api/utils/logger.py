import logging
import sys
import json
from typing import Any, Dict, Optional


class Logger(object):
    def __init__(self, name: str, debug: bool = False) -> None:
        level = logging.DEBUG if debug else logging.INFO
        self.logging: logging.Logger = logging.getLogger(name)

        # if logger already exists don't add handlers
        if len(self.logging.handlers):
            self.logging.handlers[0].setLevel(level)
            return

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(level)

        self.logging.addHandler(handler)
        self.logging.setLevel(level)

    def log_request(
        self,
        endpoint: str,
        response: Any,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        log = f"ESPN API Request: url: {endpoint} params: {params} headers: {headers} \nESPN API Response: {json.dumps(response)}"
        self.logging.debug(log)


# def setup_logger(debug=False) -> logging:
#     '''Setups Debug Logger'''
#     level = logging.DEBUG if debug else logging.INFO
#     logger = logging.getLogger('League')

#     handler = logging.StreamHandler(sys.stdout)
#     formatter = logging.Formatter('%(message)s')
#     handler.setFormatter(formatter)
#     handler.setLevel(level)

#     logger.addHandler(handler)
#     logger.setLevel(level)
#     return logger
