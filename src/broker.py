import niquests as requests
from dotenv import dotenv_values

env_config = dotenv_values("../.env")


def make_request(headers, payload):
    if not env_config:
        raise FileNotFoundError("The .env file doesn't exist or is empty. Did you copy the"
                                ".env.sample file to .env and set your values?")

    print(env_config)
    print(headers)
    print(payload)
