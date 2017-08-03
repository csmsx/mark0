Mark 0
======

Requirements
------------

* Raspberry Pi. Tested on Model 3 B.
* A compatible camera.
* LEDs
* DHT11
* A 5V fan.
* An MG-811 CO2 sensor, with MCP3008 converter.

Usage
-----

Mark 0 relies on a daemon and a collection program. Usages in 3 steps:

0. Ensure your Pi timezone settings.
1. Launch the daemon.
2. Run the program, or register it for periodic execution (e.g. with `cron`).

The following procedure is based on `cron` to run every hour. All programs run as the default `pi` user. The environment variable `WORK_DIR` is set to the repository path.

    $ sudo timedatectl set-timezone Asia/Tokyo # Replace Asia/Tokyo by your timezone, e.g. UTC.
    $ cd $WORK_DIR
    $ sudo pip install -r requirements.txt
    $ ./devices.d
    $ crontab -e
    # Add entry:
    # 0 * * * * /usr/bin/python /path/to/collect.py

In the `crontab`, please edit the path to the `collect.py` script.


Troubleshooting
---------------

## Suspension in syslog

If you see many "suspensions" in `/var/log/syslog`, exactly at the time you expect `collect.py` execution by `cron`, you are probably hitting an old `rsyslog` bug (circa 2015-2016). The fix exists for long, but it is not applied up to and including Raspbian Jessie. The workaround is to remove a pipe to `/dev/console` in `/etc/rsyslog.conf`.

Typical `syslog` symptom:

    Aug  2 23:16:25 raspberrypi rsyslogd-2007: action 'action 17' suspended, next retry is Wed Aug  2 23:17:55 2017 [try http://www.rsyslog.com/e/2007 ]

References:
* Rsyslog [bug discussion on Github](https://github.com/rsyslog/rsyslog/issues/35).
* Debian fix [commit message](https://anonscm.debian.org/cgit/collab-maint/rsyslog.git/commit/?id=67bc8e5326b0d3564c7e2153dede25f9690e6839). Note this is not included in Raspbian Jessie.

## Dropped output from cron

You may see dropped output in `cron`:

    CRON[8380]: (CRON) info (No MTA installed, discarding output)

This is NOT a problem, however a missed opportunity. It means `cron` has detected the command writes to `stdout`. `cron` expects then a redirection to a file, a mail reader, a mail server, etc.

The output from `collect.py` contains the sensor readings. If you want to have both an "heartbeat" email and an idea of the sensor values, you can install `postfix` and set `MAILTO=` to the target email address in your `crontab`.

Alternatively you can just drop the output explicitly by redirecting to `/dev/null`, or redirect to any file (e.g. in `/var/log`).

Copyrights & Thanks
-------------------

This work relies on external libraries:

* `lib/ext/dht11.py`: [DHT11 Python library](https://github.com/szazo/DHT11_Python), copyright (c) 2016 Zoltan Szarvas (MIT License)
* `python-daemon`: [PIP library](https://pypi.python.org/pypi/python-daemon/), copyright Ben Finney, unclear if the parts used are Apache 2.0 or GPLv3. If GPLv3, I will drop for another implementation.
