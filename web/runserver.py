"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import sys
import config
from ga4gh import create_app
from flask.ext.cors import CORS
from flask.ext.cors import cross_origin
from ga4gh import views
from ga4gh.views import ga4gh

# works with new virutalenv changes
basePath = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
configFile = os.path.join(basePath, "web/ga4gh_test.conf")
parser = config.ConfigParser.RawConfigParser()
parser.read(configFile)
if parser.has_section('virtualenv'):
    venv = parser.get('virtualenv', 'virtualenv')

if os.getenv('VIRUTAL_ENV') is None:
    activate_this = venv + '/bin/activate_this.py'
    execfile(activate_this, dict(__file__=activate_this))

config.initConfig("ga4gh_test.conf")

app = create_app(config.LoadedConfig)


cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

host = app.config.get('HOST', 'localhost')
app.register_blueprint(views.ga4gh)

if __name__ == '__main__':
    app.run(host=host, debug=True)
