#!/usr/bin/env python
#
# gen-py-errors.py: Generate a python module which maps error names to numbers.
#                   (The purpose being easier writing of the python tests.)
#
# ====================================================================
#    Licensed to the Apache Software Foundation (ASF) under one
#    or more contributor license agreements.  See the NOTICE file
#    distributed with this work for additional information
#    regarding copyright ownership.  The ASF licenses this file
#    to you under the Apache License, Version 2.0 (the
#    "License"); you may not use this file except in compliance
#    with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an
#    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#    KIND, either express or implied.  See the License for the
#    specific language governing permissions and limitations
#    under the License.
# ====================================================================
#
#
# Locates svn_error_codes.h based on its relative location to this script.
#
# Generates to STDOUT. Typically, redirect this into svntest/err.py
#

import sys
import os
import re

HEADER = '''#!/usr/bin/env python
### This file automatically generated by tools/dev/gen-py-errors.py,
### which see for more information
###
### It is versioned for convenience.
'''

# Established by svn 1.0. May as well hard-code these.
APR_OS_START_ERROR = 20000
APR_OS_START_USERERR = APR_OS_START_ERROR + 50000 * 2
SVN_ERR_CATEGORY_SIZE = 5000

RE_CAT_NAME = re.compile(r'SVN_ERR_([A-Z_]+)_CATEG')
RE_CAT_VALUE = re.compile(r'\d+')

RE_DEF_NAME = re.compile(r'SVN_ERRDEF\(([A-Z0-9_]+)')
RE_DEF_VALUE = re.compile(r'SVN_ERR_([A-Z_]+)_CATEG[^0-9]*([0-9]+)')


def write_output(codes):
  print HEADER

  for name, value in codes:
    # skip SVN_ERR_ on the name
    print '%s = %d' % (name[8:], value)


def main(codes_fname):
  categ = { }
  codes = [ ]

  f = open(codes_fname)

  # Parse all the category start values
  while True:
    line = f.next()
    m = RE_CAT_NAME.search(line)
    if m:
      name = m.group(1)
      m = RE_CAT_VALUE.search(f.next())
      assert m
      value = int(m.group(0))
      categ[name] = APR_OS_START_USERERR + value * SVN_ERR_CATEGORY_SIZE

    elif line.strip() == 'SVN_ERROR_START':
      break

  # Parse each of the error values
  while True:
    line = f.next()
    m = RE_DEF_NAME.search(line)
    if m:
      name = m.group(1)
      line = f.next()
      m = RE_DEF_VALUE.search(line)
      if not m:
        # SVN_ERR_WC_NOT_DIRECTORY is defined as equal to NOT_WORKING_COPY
        # rather than relative to SVN_ERR_WC_CATEGORY_START
        #print 'SKIP:', line
        continue
      cat = m.group(1)
      value = int(m.group(2))
      codes.append((name, categ[cat] + value))

    elif line.strip() == 'SVN_ERROR_END':
      break

  write_output(sorted(codes))


if __name__ == '__main__':
  this_dir = os.path.dirname(os.path.abspath(__file__))
  codes_fname = os.path.join(this_dir, os.path.pardir, os.path.pardir,
                             'subversion', 'include', 'svn_error_codes.h')
  main(codes_fname)