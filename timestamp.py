#!/usr/bin/python

# ==============================================================================

# A simple script to convert calendar dates to/from UNIX timestamps

# Pass --help for usage instructions.

# Requires the python-dateutil third-party library to parse dates in a wide
# variety of formats.

# Copyright (c) 2020 Meithan West. This program is free software released
# under the terms of the GNU GPLv3.

# ==============================================================================

import datetime
import sys
import time

try:
  import dateutil.parser
  import dateutil.tz
except:
  print("The python-dateutil third-party library is required; try 'pip install python-dateutil'")
  sys.exit()

# ==============================================================================

def print_usage():
  print("""
Usage: timestamp [-h] [-m] [-u] [-i] [timestamp | date/time]

Converts a calendar date to or from a UNIX timestamp. If no timestamp or date
is given, prints current date and UNIX timestamp.

Requires the python-dateutil third-party library; install through pip.

Main arguments (either of the following, or none):

  timestamp   A UNIX timestamp, i.e. the number of seconds elapsed since
              1 Jan 1970. Can have fractional seconds.

  datetime    A calendar date/time. Any format recognized by dateutil.parser
              can be used. The special strings 'now' (current date and time)
              and 'today' (current date at 00:00 hours) are also accepted.

Options:

  -h, --help     Show this help message and exit.
  -m, --milis    Include miliseconds in output date or timestamp.
  -u, --utc      Interpret input or show output as UTC instead of local time.
  -i, --iso      Display output date in ISO format instead of 'human' format.

Copyright (c) 2020 Meithan West. This program is free software released
under the terms of the GNU GPLv3.
""")

# ------------------------------------------------------------------------------

# Receives a python timezone-aware datetime object and returns either its
# corresponding UNIX timestamp or a formatted calendar date
def format_date(dt, show_timestamp=False, iso=False, milis=False, utc=False):

  if show_timestamp:
    stamp = dt.timestamp()
    if milis:
      return "{:.3f}".format(stamp)
    else:
      return "{:.0f}".format(stamp)

  else:

    # Format time
    _time = dt.strftime("%H:%M:%S")
    if milis:
      _time += "." + "{:03.0f}".format(round(int(dt.strftime("%f"))/1000))

    # Format date
    if iso:
      _date = dt.strftime("%Y-%m-%d")
    else:
      _date = dt.strftime("%a")
      _date += " " + dt.strftime("%d").lstrip("0")
      _date += " " + dt.strftime("%b %Y")

    # Format timezone
    hours = int(dt.utcoffset().total_seconds() // 3600)
    mins = int(dt.utcoffset().total_seconds() % 3600)
    if iso and utc:
      _tz = "Z"
    elif iso and not utc:
      _tz = dt.strftime('%z')
    elif not iso and utc:
      _tz = "UTC"
    elif not iso and not utc:
      if time.localtime(dt.timestamp()).tm_isdst == 1:
        tzname = time.tzname[1]
      else:
        tzname = time.tzname[0]
      _tz = "{} (UTC{})".format(tzname, int(dt.strftime('%z')[:3]))

    # Assemble parts
    if iso:
      retval = "{}T{}{}".format(_date, _time, _tz)
    else:
      retval = "{} {} {}".format(_date, _time, _tz)

    return retval

# ==============================================================================

# Parse arguments
show_milis = False
use_utc = False
show_iso = False
main_args = []

for arg in sys.argv[1:]:
  if arg.startswith('-') or arg.startswith('--'):
    _arg = arg.lower()
    if _arg in ["-h", "--help"]:
      print_usage()
      sys.exit()
    elif _arg in ["-m", "--m", "--milis", "--mili"]:
      show_milis = True
    elif _arg in ["-u", "--u", "--utc"]:
      use_utc = True
    elif _arg in ["-i", "--i", "--iso"]:
      show_iso = True
    else:
      print("\nError: Unrecognized option: {}".format(arg))
      print_usage()
      sys.exit()
  else:
    main_args.append(arg)

if len(main_args) == 0:
  no_args = True
else:
  no_args = False

# Determine if main argument is timestamp or datetime
if no_args:

  # When no arguments are given, output current calendar date and timestamp
  date = datetime.datetime.now()
  mode = "now"

else:

  if len(main_args) == 1:
    if main_args[0].lower() == "now":
      mode = "now"
    elif main_args[0].lower() == "today":
      mode = "today"
    else:
      # If a single argument is given and it can be converted to a float,
      # interpret it as a UNIX timestamp; otherwise, assume it's a date
      try:
        given_timestamp = float(main_args[0])
        mode = "timestamp"
      except:
        mode = "datetime"
  else:
    mode = "datetime"

# Set timezone to local or to UTC
if use_utc:
  timezone = datetime.timezone.utc
else:
  timezone = dateutil.tz.tzlocal()

# Create date from given input, or set to current date and/or time
if mode == "now":

  dt = datetime.datetime.now(tz=timezone)

elif mode == "today":

  dt = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time()).replace(tzinfo=timezone)

elif mode == "timestamp":

  dt = datetime.datetime.fromtimestamp(given_timestamp, tz=timezone)

elif mode == "datetime":

  try:
    date_str = " ".join(main_args)
    dt = dateutil.parser.parse(date_str)
  except:
    print("Couldn't parse date string: {}".format(date_str))
    sys.exit()
  dt = dt.replace(tzinfo=timezone)

# Print result
if mode == "now":

  print("Current date: {}".format(format_date(dt, show_timestamp=False, iso=show_iso, milis=show_milis, utc=use_utc)))
  print("Current UNIX: {}".format(format_date(dt, show_timestamp=True, iso=show_iso, milis=show_milis, utc=use_utc)))

elif mode == "timestamp":

  print(format_date(dt, show_timestamp=False, iso=show_iso, milis=show_milis, utc=use_utc))

elif mode == "datetime" or mode == "today":

  print("Parsed date: {}".format(dt.strftime("%Y-%b-%d %H:%M:%S %Z")))
  print("UNIX Timestamp: {}".format(format_date(dt, show_timestamp=True, milis=show_milis)))
