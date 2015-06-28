import os

# we set DJANGO_ENVIRONMENT via /etc/environment in django/tasks/set_machine_purpose.yml
ENVIRONMENT = os.getenv("DJANGO_ENVIRONMENT")

# load appropriate config
if ENVIRONMENT == "production":
    from production import *
elif ENVIRONMENT == "staging":
    from staging import *
elif ENVIRONMENT == "development":
    from development import *


#from .secret_settings import *
#DATABASES['default'].update(CONNECTION)
#DATABASES['default']['NAME']=CONNECTION['NAME']
