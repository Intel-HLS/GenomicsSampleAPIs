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

import gc
import sys
from datetime import datetime

now = datetime.now

DEBUG = False


def garbageCollect(debug=False):
    v = gc.collect()
    if debug:
        print "Garbage {0}".format(v)
    for obj in gc.garbage:
        del obj


def flattenStartEnd(startList, endList):
    start = list()
    end = list()
    if DEBUG:
        print "[util:flattenStartEnd] Input Start {0} ".format(startList)
        print "[util:flattenStartEnd] Input End {0} ".format(endList)
    for i in xrange(0, len(startList)):
        insert_Start = startList[i]
        insert_End = endList[i]

        binarySearchInsert(start, end, insert_Start, insert_End)

    return start, end


def binarySearchInsert(startList, endList, insert_Start, insert_End):
    if len(startList) == 0:
        startList.insert(0, insert_Start)
        endList.insert(0, insert_End)
        return

    m = 0
    n = len(startList) - 1

    while m <= n:
        mid = int(m + (n - m) / 2)
        if insert_Start < startList[mid]:
            # Start is lesser than the start at mid, search left tree
            n = mid - 1
            continue
        elif insert_Start >= startList[mid] and insert_Start <= endList[mid]:
            # insert_Start is between the start and end at mid, so insert
            # insert_Start and insert_End correctly
            insertEnd(startList, endList, insert_End, mid)
            return
        else:
            # insert_Start is greater than the start at mid,
            # and not less than the end at mid. Search right tree
            m = mid + 1

    if n == -1:
        insertAt(startList, endList, insert_Start, insert_End, 0)
    else:
        insertAt(startList, endList, insert_Start, insert_End, m)
    return


def insertAt(startList, endList, insert_Start, insert_End, index):
    if index == len(startList):
        startList.append(insert_Start)
        endList.append(insert_End)
    if insert_Start < startList[index]:
        if insert_End == (startList[index] - 1):
            startList[index] = insert_Start
        elif insert_End < startList[index]:
            startList.insert(index, insert_Start)
            endList.insert(index, insert_End)
        elif insert_End <= endList[index]:
            startList[index] = insert_Start
        else:
            insertEnd(startList, endList, insert_End, index)
            startList[index] = insert_Start
    # After inserting the end at the right spot check if the
    # index - 1's end and the current start are just 1 off and merge
    if index != 0 and (insert_Start - 1) == endList[index - 1]:
        endList[index - 1] = endList[index]
        del startList[index]
        del endList[index]


def insertEnd(startList, endList, insert_End, index):
    removeList = list()
    if index == -1:
        mid = 0
    else:
        mid = index
    while not (insert_End < endList[mid]):
        # insert_End is greater than the end at mid, so
        # either combine with next or extend the current end
        if mid + 1 < len(startList):
            # There are valid entries at mid + 1, check them
            if insert_End < startList[mid + 1]:
                endList[mid] = insert_End
                break
            else:
                # insert_End is greater than the start at mid + 1,
                # so go through the while loop again
                removeList.append(mid + 1)
                mid = mid + 1
        else:
            # We are at the end of list so extend the end at mid
            # to the new insert_End
            endList[mid] = insert_End
            break

    if len(removeList) != 0:
        if index == -1:
            endList[0] = endList[removeList[-1]]
            index = 0
        else:
            endList[index] = endList[removeList[-1]]
        removeList.sort(reverse=True)
        for i in removeList:
            del startList[i]
            del endList[i]
    return index


def progressPrint(outString):
    sys.stdout.write("\r" + outString)
    sys.stdout.flush()


def log(outString):
    print "{0}: {1}".format(now(), outString)
