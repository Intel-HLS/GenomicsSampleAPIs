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

from jinja2.runtime import Undefined
import ansible.runner.filter_plugins.core as core


def well_defined(var):
    if isinstance(var, Undefined) or var is None:
        return False
    else:
        return True


def is_defined_true(var):
    if(not well_defined(var)):
        return False
    return core.bool(var)


def get_defined_string(var):
    if(not well_defined(var)):
        return ''
    return str(var)


class FilterModule(object):
    ''' Ansible additional jinja2 filters for Genomics API'''

    def filters(self):
        return {
            "well_defined": well_defined,
            "is_defined_true": is_defined_true,
            "get_defined_string": get_defined_string
        }
