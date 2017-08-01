# File: easywifi.py
# Version: 1
# Description: Wrapper that makes using wifi simple
# License: MIT
# Authors: Renze Nicolai <renze@rnplus.nl>

import time, network, badge, easydraw

nw = network.WLAN(network.STA_IF)

def enable(showStatus=True):
    if not nw.isconnected():
        nw.active(True)
        ssid = badge.nvs_get_str('badge', 'wifi.ssid', 'SHA2017-insecure')
        password = badge.nvs_get_str('badge', 'wifi.password')
        if showStatus:
            easydraw.msg("Connecting to '"+ssid+"'...")
        nw.connect(ssid, password) if password else nw.connect(ssid)
        timeout = badge.nvs_get_u8('badge', 'wifi.timeout', 40)
        while not nw.isconnected():
            time.sleep(0.1)
            timeout = timeout - 1
            if (timeout<1):
                if showStatus:
                    easydraw.msg("Error: could not connect!")
                nw.active(False)
                return False
        if showStatus:
            easydraw.msg("Connected!")
    return True

def disable():
    nw = network.WLAN(network.STA_IF)
    nw.active(False)

def status():
    return nw.active()
