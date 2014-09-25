# Collect actual settings

from .defaults import *
from .local import *

# A SECRET_KEY and a DB_PASSWORD must be declared in local.py.

DATABASES['default']['PASSWORD'] = DB_PASSWORD
