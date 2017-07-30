# File: services.py
# Version: 2
# API version: 1
# Description: Background services for SHA2017 badge
# License: MIT
# Authors: Renze Nicolai <renze@rnplus.nl>
#          Thomas Roos   <?>

import uos, ujson, easywifi

services = [] #List containing all the service objects

loop_callbacks = {} #Dict containing: {<FUNCTION>:[TIME IN MS UNTIL NEXT EXECUTION,WIFI REQUIRED ON NEXT RUN]}
draw_callbacks = {} #Dict containing draw functions as keys and the time until their next redraw in ms as value

def setup():
    global services
    global loop_callbacks
    global draw_callbacks
    
    # Status of wifi
    wifiFailed = False
    
    #Check if lib folder exists and get application list, else stop
    try:
        apps = uos.listdir('lib')
    except OSError:
        return
    
    #For each app...
    for app in apps:
        try:
            #Try to open and read the json description
            fd = open('/lib/'+app+'/service.json')
            description = ujson.loads(fd.read())
            fd.close()
        except:
            print("[SERVICES] No description found for "+app)
            break #Or skip the app
        
        try:
            #Try to open the service itself
            fd = open('/lib/'+app+'/service.py')
            fd.close()
        except:
            print("[SERVICES] No script found for "+app)
            break #Or skip the app
        
        rtcRequired = False # True if RTC should be set before starting service
        loopEnabled = False # True if loop callback is requested
        drawEnabled = False # True if draw callback is requested
        
        wifiInSetup = False # True if wifi needed in setup
        wifiInLoop = False # True if wifi needed in loop
        
        try:
            if description['apiVersion']!=1:
                print("[SERVICES] Service for "+app+" is not compatible with current firmware")
                break #Skip the app
            wifiInSetup = description['wifi']['setup']
            wifiInLoop = description['wifi']['setup']
            rtcRequired = description['rtc']
            loopEnabled = description['loop']
            drawEnabled = description['draw']
        except:
            print("[SERVICES] Could not parse description of app "+app)
            break #Skip the app
        
        print("[SERVICES] Found service for "+app)
        
        # Import the service.py script
        try:
            srv = __import__('lib/'+app+'/service')
        except:
            print("[SERVICES] Could not import service of app "+app)
            break #Skip the app
        
        if wifiInSetup:
            if wifiFailed:
                print("[SERVICES] Service of app "+app+" requires wifi and wifi failed so the service has been disabled.")
                break
             if not easywifi.status():
                if not easywifi.enable():
                    wifiFailed = True
                    print("[SERVICES] Could not connect to wifi!")
                    break#Skip the app
                        
                        
        try:
            srv.setup()
        except BaseException as msg:
            print("[SERVICES] Exception in service setup "+app+": ", msg)
            break
        
        if loopEnabled:
            try:
                loop_callbacks[srv.loop] = 0
            except:
                print("[SERVICES] Loop requested but not defined in service "+app)
            
        if drawEnabled:
            try:
                draw_callbacks[srv.draw] = 0
            except:
                print("[SERVICES] Draw requested but not defined in service "+app)
        
        # Add the script to the global service list
        services.append(srv)

# That's it for today... -Renze
#------

def loop(lcnt):
    noSleep = False
    global services
    for srv in services:
        try:
            if (srv.loop(lcnt)):
                noSleep = True
        except BaseException as msg:
            print("[SERVICES] Service loop exception: ", msg)
    return noSleep

def draw():
    global services
    x = 0
    y = 64
    for srv in services:
        try:
            space_used = srv.draw(x,y)
            if (space_used>0):
                y = y + abs(space_used)
        except BaseException as msg:
            print("[SERVICES] Service draw exception: ", msg)

services = []
