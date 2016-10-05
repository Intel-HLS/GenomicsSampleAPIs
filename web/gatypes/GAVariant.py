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

import GACall
import json


class GAVariant(object):
    """GAVariant representation for ga4gh responses"""

    def __init__(
            self,
            id,
            variantSetId,
            start,
            end,
            referenceBases,
            names=[],
            created=None,
            updated=None,
            referenceName='',
            alternateBases=[],
            info={},
            calls=[]):

        start = long(start)
        end = long(end)

        if referenceBases:
            referenceBases = str(referenceBases)

        if created:
            created = long(created)

        if updated:
            updated = long(updated)

        self.gavariant_info = {
            'id': id,
            'variantSetId': variantSetId,
            'names': names,
            'created': created,
            'updated': updated,
            'referenceName': referenceName,
            'start': start,
            'end': end,
            'referenceBases': referenceBases,
            'alternateBases': alternateBases,
            'info': info,
            'calls': calls}

    def getJSON(self):
        return json.dumps(self.gavariant_info)
