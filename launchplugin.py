# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, json, os, time
ADDON = xbmcaddon.Addon(id='screensaver.customslideshow')

#########################
# Constants
check_gui = xbmc.translatePath(os.path.join('special://home/addons/screensaver.customslideshow'))
#########################


def main():
    get_sec = ADDON.getSetting("initiate_me")
    xbmc.log("INITIATE IN SECONDSSSSS: " + str(get_sec), 2)
    is_active = '{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"screensaver.mode" } }'
    res = json.loads(xbmc.executeJSONRPC(is_active))
    xbmc.log("RES  :" + str(res["result"]["value"]), 2)
    if res["result"]["value"] == "screensaver.customslideshow":
        xbmc.executebuiltin("Dialog.Close(all, true)", True)
        for x in range(1, 50):
            xbmc.log("X  : " + str(x), 2)
            time.sleep(1)
            if int(xbmc.getGlobalIdleTime()) == int(get_sec):
                xbmc.log("global idle time : " + str(xbmc.getGlobalIdleTime()), 2)
                xbmc.log("INITIATE STARTS>>>>>>>", 2)
                xbmc.executebuiltin('RunScript(%s)' % (os.path.join(check_gui,"screensaver.py")))
                break
