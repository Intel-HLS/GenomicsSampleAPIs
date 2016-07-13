import sys
import os
import config
from ga4gh import create_app
from ga4gh import views

ga4ghPath = None
for path in sys.path:
    if path.endswith('web'):
        ga4ghPath = path
        break
if ga4ghPath is None:
    raise Exception("GA4GHAPI path is not set. Run GenomicsSampleAPIs/web/install.py, \
  and use --system-site-packages when creating a virtualenv")


config.initConfig(os.path.join(ga4ghPath, "ga4gh_test.conf"))

if os.getenv('VIRUTAL_ENV') is None:
    activate_this = config.LoadedConfig.VIRTUALENV + '/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

application = create_app('config.LoadedConfig')

application.register_blueprint(ga4gh)
