import yaml
import os

dir = os.path.dirname(__file__)

config = {}
with open(os.path.join(dir, 'config/config.yml')) as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
