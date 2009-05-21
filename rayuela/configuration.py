### Copyright (C) 2006-2009 Manuel Ospina <ospina.manuel@gmail.com>

# This file is part of rayuela.
#
# rayuela is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# rayuela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rayuela; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

"""
USAGE:

from configuration import options

value = options[key]
"""

RC_FILE = os.path.join(os.environ.get('HOME'), '.rayuela')

options = {}

def _read_configuration_(filename):
    """Read configuration file and set options."""
    fh = open(filename)
    for line in fh.readlines():
        if line in ("\n", ""):
            continue
        if line.startswith("#"):
            continue
        key, value = line.split("=")
        if value.strip():
            options[key.strip()] = value.strip()
    fh.close()

def write_configuration(filename=RC_FILE):
    """Write the configuration File."""
    fh = open(filename, "w")
    for i in options.keys():
        line = "%s = %s\n" % (i, options[i])
        fh.write(line)
    fh.close()

for RC in [RC_FILE]:
    if os.path.isfile(RC):
        _read_configuration_(RC)
