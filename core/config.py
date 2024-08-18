from datetime import timedelta

from environs import Env

env = Env()
env.read_env()

class Config(object):
    FLASK_APP = env.str("FLASK_APP", default="app.py")
    FLASK_ENV = env.str("FLASK_ENV", default="development")
    SECRET_KEY = env.str("SECRET_KEY", default="")
    FLASK_DEBUG = env.bool("FLASK_DEBUG", default=True)
