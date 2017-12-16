# Collect actual settings

from .defaults import *
from .local import *

# A SECRET_KEY and a DB_PASSWORD must be declared in local.py.

DATABASES['default']['PASSWORD'] = DB_PASSWORD

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
