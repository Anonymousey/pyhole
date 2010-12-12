#!/usr/bin/env python

#   Copyright 2010 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""pyhole - A modular IRC bot for Python developers."""


import logging
import threading
import time
import sys

from pyhole import config
from pyhole import irc


__version__ = "0.0.1"
__config__ = "pyhole.cfg"

b_config = config.Config(__config__, "pyhole")


def logger(name):
    """Log handler"""
    debug = b_config.get("debug", "bool")
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s:%(levelname)s] %(message)s")
    return logging.getLogger(name)


def network_list(sections):
    """Prepare the list of IRC networks"""
    networks = []
    for network in sections:
        if network != "pyhole":
            networks.append(network)
    return networks


def irc_thread(b_log, b_config, network):
    """IRC network connection thread"""
    n_config = config.Config(__config__, network)
    n_log = logger(network)
    reconnect_delay = b_config.get("reconnect_delay", "int")

    while True:
        try:
            connection = irc.IRC(b_config, n_config, n_log, __version__)
        except Exception as e:
            b_log.error(e)
            b_log.error("Retrying in %d seconds" % reconnect_delay)
            time.sleep(reconnect_delay)

        connection.start()


def main():
    """Main Loop"""
    b_log = logger("MAIN")
    networks = network_list(b_config.sections())

    for network in networks:
        t = threading.Thread(
            target=irc_thread,
            args=(b_log, b_config, network))
        t.daemon = True
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
