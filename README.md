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


Copyrights & Thanks
-------------------

This work relies on external libraries:

* `lib/ext/dht11.py`: [DHT11 Python library](https://github.com/szazo/DHT11_Python), copyright (c) 2016 Zoltan Szarvas (MIT License)
* `python-daemon`: [PIP library](https://pypi.python.org/pypi/python-daemon/), copyright Ben Finney, unclear if the parts used are Apache 2.0 or GPLv3. If GPLv3, I will drop for another implementation.
