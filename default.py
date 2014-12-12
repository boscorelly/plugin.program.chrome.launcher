#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import re
import os
import time
import subprocess
import xbmcplugin
import xbmcgui
import xbmcaddon


addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
addonPath = addon.getAddonInfo('path')
translation = addon.getLocalizedString
osWin = xbmc.getCondVisibility('system.platform.windows')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osLinux = xbmc.getCondVisibility('system.platform.linux')
useOwnProfile = addon.getSetting("useOwnProfile") == "true"
useCustomPath = addon.getSetting("useCustomPath") == "true"
customPath = xbmc.translatePath(addon.getSetting("customPath"))

userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
profileFolder = os.path.join(userDataFolder, 'profile')
siteFolder = os.path.join(userDataFolder, 'sites')

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)
if not os.path.isdir(profileFolder):
    os.mkdir(profileFolder)
if not os.path.isdir(siteFolder):
    os.mkdir(siteFolder)

youtubeUrl = "http://www.youtube.com/leanback"
vimeoUrl = "http://www.vimeo.com/couchmode"

trace_on = False
try:
    pass
    # import pydevd
    # #pydevd.set_pm_excepthook()
    # pydevd.settrace('192.168.0.16', port=51381, stdoutToServer=True, stderrToServer=True)
    # trace_on = True
except BaseException as ex:
    pass

def index():
    files = os.listdir(siteFolder)
    for file in files:
        if file.endswith(".link"):
            fh = open(os.path.join(siteFolder, file), 'r')
            title = ""
            url = ""
            thumb = ""
            kiosk = "yes"
            stopPlayback = "no"
            for line in fh.readlines():
                entry = line[:line.find("=")]
                content = line[line.find("=")+1:]
                if entry == "title":
                    title = content.strip()
                elif entry == "url":
                    url = content.strip()
                elif entry == "thumb":
                    thumb = content.strip()
                elif entry == "kiosk":
                    kiosk = content.strip()
                elif entry == "stopPlayback":
                    stopPlayback = content.strip()
            fh.close()
            addSiteDir(title, url, 'showSite', thumb, stopPlayback, kiosk)
    addDir("[ Vimeo Couchmode ]", vimeoUrl, 'showSite', os.path.join(addonPath, "vimeo.png"), "yes", "yes")
    addDir("[ Youtube Leanback ]", youtubeUrl, 'showSite', os.path.join(addonPath, "youtube.png"), "yes", "yes")
    addDir("[B]- "+translation(30001)+"[/B]", "", 'addSite', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def addSite(site="", title=""):
    if site:
        filename = getFileName(title)
        content = "title="+title+"\nurl="+site+"\nthumb=DefaultFolder.png\nstopPlayback=no\nkiosk=yes"
        fh = open(os.path.join(siteFolder, filename+".link"), 'w')
        fh.write(content)
        fh.close()
    else:
        keyboard = xbmc.Keyboard('', translation(30003))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            title = keyboard.getText()
            keyboard = xbmc.Keyboard('http://', translation(30004))
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                url = keyboard.getText()
                keyboard = xbmc.Keyboard('no', translation(30009))
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    stopPlayback = keyboard.getText()
                    keyboard = xbmc.Keyboard('yes', translation(30016))
                    keyboard.doModal()
                    if keyboard.isConfirmed() and keyboard.getText():
                        kiosk = keyboard.getText()
                        content = "title="+title+"\nurl="+url+"\nthumb=DefaultFolder.png\nstopPlayback="+stopPlayback+"\nkiosk="+kiosk
                        fh = open(os.path.join(siteFolder, getFileName(title)+".link"), 'w')
                        fh.write(content)
                        fh.close()
    xbmc.executebuiltin("Container.Refresh")


def getFileName(title):
    return (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip()


def getFullPath(path, url, useKiosk, userAgent):
    profile = ""
    if useOwnProfile:
        profile = '--user-data-dir="'+profileFolder+'" '
    kiosk = ""
    if useKiosk=="yes":
        kiosk = '--kiosk '
    if userAgent:
        userAgent = '--user-agent="'+userAgent+'" '
    return '"'+path+'" '+profile+userAgent+'--start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run '+kiosk+'"'+url+'"'


def showSite(url, stopPlayback, kiosk, userAgent):
    if stopPlayback == "yes":
        xbmc.Player().stop()
    if osWin:
        path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        path64 = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=False)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=False)
        elif os.path.exists(path64):
            fullUrl = getFullPath(path64, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=False)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()
    elif osOsx:
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=True)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=True)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()
    elif osLinux:
        path = "/usr/bin/google-chrome"
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=True)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url, kiosk, userAgent)
            subprocess.Popen(fullUrl, shell=True)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()
            return
        
        # Ensure chrome is active window
        def currentActiveWindow():
            # xprop -id $(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) _NET_WM_NAME    
            current_window_id = subprocess.check_output(['xprop', '-root', '32x', '\'\t$0\'', '_NET_ACTIVE_WINDOW'])
            current_window_id = current_window_id.strip("'").split()[1]
            current_window_name = subprocess.check_output(['xprop', '-id', current_window_id, "_NET_WM_NAME"])
            current_window_name = current_window_name.strip().split(" = ")[1].strip('"')
            return current_window_name
            
        timeout = time.time() + 10
        while time.time() < timeout and "chrome" not in currentActiveWindow().lower():
            windows = subprocess.check_output(['wmctrl', '-l'])
            if "Google Chrome" in windows:
                subprocess.Popen(['wmctrl', '-a', "Google Chrome"])
                break
            xbmc.sleep(500)

def removeSite(title):
    os.remove(os.path.join(siteFolder, getFileName(title)+".link"))
    xbmc.executebuiltin("Container.Refresh")


def editSite(title):
    filenameOld = getFileName(title)
    file = os.path.join(siteFolder, filenameOld+".link")
    fh = open(file, 'r')
    title = ""
    url = ""
    kiosk = "yes"
    thumb = "DefaultFolder.png"
    stopPlayback = "no"
    for line in fh.readlines():
        entry = line[:line.find("=")]
        content = line[line.find("=")+1:]
        if entry == "title":
            title = content.strip()
        elif entry == "url":
            url = content.strip()
        elif entry == "kiosk":
            kiosk = content.strip()
        elif entry == "thumb":
            thumb = content.strip()
        elif entry == "stopPlayback":
            stopPlayback = content.strip()
    fh.close()

    oldTitle = title
    keyboard = xbmc.Keyboard(title, translation(30003))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        title = keyboard.getText()
        keyboard = xbmc.Keyboard(url, translation(30004))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            url = keyboard.getText()
            keyboard = xbmc.Keyboard(stopPlayback, translation(30009))
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                stopPlayback = keyboard.getText()
                keyboard = xbmc.Keyboard(kiosk, translation(30016))
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    kiosk = keyboard.getText()
                    content = "title="+title+"\nurl="+url+"\nthumb="+thumb+"\nstopPlayback="+stopPlayback+"\nkiosk="+kiosk
                    fh = open(os.path.join(siteFolder, getFileName(title)+".link"), 'w')
                    fh.write(content)
                    fh.close()
                    if title != oldTitle:
                        os.remove(os.path.join(siteFolder, filenameOld+".link"))
    xbmc.executebuiltin("Container.Refresh")


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, stopPlayback="", kiosk=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&stopPlayback="+urllib.quote_plus(stopPlayback)+"&kiosk="+urllib.quote_plus(kiosk)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addSiteDir(name, url, mode, iconimage, stopPlayback, kiosk):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&stopPlayback="+urllib.quote_plus(stopPlayback)+"&kiosk="+urllib.quote_plus(kiosk)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=editSite&url='+urllib.quote_plus(name)+')',), (translation(30002), 'RunPlugin(plugin://'+addonID+'/?mode=removeSite&url='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
stopPlayback = urllib.unquote_plus(params.get('stopPlayback', 'no'))
kiosk = urllib.unquote_plus(params.get('kiosk', 'yes'))
userAgent = urllib.unquote_plus(params.get('userAgent', ''))
profileFolderParam = urllib.unquote_plus(params.get('profileFolder', ''))
if profileFolderParam:
    useOwnProfile = True
    profileFolder = profileFolderParam


if mode == 'addSite':
    addSite()
elif mode == 'showSite':
    showSite(url, stopPlayback, kiosk, userAgent)
elif mode == 'removeSite':
    removeSite(url)
elif mode == 'editSite':
    editSite(url)
else:
    index()

if trace_on:
    pydevd.stoptrace()
