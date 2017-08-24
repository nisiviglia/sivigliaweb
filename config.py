class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URL= 'mongodb://localhost:27017/test'
    SECRET_KEY = '\xb3\x15[\xe9d\xe8\xd6\x1e\xf0%\x12/\xd5\xcd\x0eru\x15\xda$\xdb\xb3II]'

class ProductionConfig(Config):
    DATABASE_URL= 'mongodb://localhost:27017/siviglia'

class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class TestingConfig(Config):
    DATABASE_URL= 'mongodb://localhost:27017/Unittest'
    TESTING = True
