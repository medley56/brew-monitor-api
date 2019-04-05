import os

environment = os.getenv('BREW_MONITOR_SETTINGS', 'development')

if environment == 'development':
    print('DEVELOPMENT')
    from .development import *
else:
    print('PRODUCTION')
    from .production import *
