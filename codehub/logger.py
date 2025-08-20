import os
import yaml
from pathlib import Path
import logging.config


def setup_logging():
    with open(os.path.join(Path(__file__).parent, "logger.yaml"), "rt") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
