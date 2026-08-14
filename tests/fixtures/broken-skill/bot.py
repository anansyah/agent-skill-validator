import os
from os import environ as env
API_KEY = env.get("EXAMPLE_API_KEY")
API_SECRET = env.get("EXAMPLE_API_SECRET")
password = env.get("EXAMPLE_PASSWORD")
os.system("rm -rf /tmp/old")
