# -*- coding: utf-8 -*-
import urllib2,urllib,re,os,sys,string,time,base64,datetime,gzip
from urlparse import urlparse
import aes
import bs4
import requests
try:
    import hashlib
except ImportError:
    import md5

from parseutils import *
from stats import *
import xbmcplugin,xbmcgui,xbmcaddon
__baseurl__ = 'http://www.playtvak.cz'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
addon = xbmcaddon.Addon('plugin.video.dmd-czech.playtvak')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
__settings__ = xbmcaddon.Addon(id='plugin.video.dmd-czech.playtvak')
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
nexticon = xbmc.translatePath( os.path.join( home, 'nextpage.png' ) )
fanart = xbmc.translatePath( os.path.join( home, 'fanart.jpg' ) )
defaultprotocol = 'http:'

#Nacteni informaci o doplnku
__addon__      = xbmcaddon.Addon()
__addonname__  = __addon__.getAddonInfo('name')
__addonid__    = __addon__.getAddonInfo('id')
__cwd__        = __addon__.getAddonInfo('path').decode("utf-8")
__language__   = __addon__.getLocalizedString

# Prvni spusteni
if not (__addon__.getSetting("settings_init_done") == "true"):
        DEFAULT_SETTING_VALUES = {"quality": "high",
                                  "auto_quality": "true",
                                  "skip_logo": "false",
                                  }
        for setting in DEFAULT_SETTING_VALUES.keys():
            val = __addon__.getSetting(setting)
            if not val:
                __addon__.setSetting(setting, DEFAULT_SETTING_VALUES[setting])
        __addon__.setSetting("settings_init_done", "true")
    ###############################################################################
_auto_quality_ = (__addon__.getSetting('auto_quality') == "true")
_quality_ = __addon__.getSetting('quality')
_skip_logo_ = (__addon__.getSetting('skip_logo') == "true")


def log(msg):
    xbmc.log(("### [%s] - %s" % (__addonname__.decode('utf-8'), msg.decode('utf-8'))).encode('utf-8'), level=xbmc.LOGDEBUG)

def load(url):
    r = requests.get(url)
    return r.text

def normalize_url(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        if url.startswith('//'):
            return defaultprotocol + url
        else:
            return defaultprotocol + '//' + url
    return url

def OBSAH():
    addDir('Nejnovější epizody','http://www.playtvak.cz',6,icon,1,"Playtvak.cz - Nejnovější epizody")
    addDir('Pořady','http://www.playtvak.cz/porady.aspx',5,icon,1,"Playtvak.cz - Všechny pořady")
    addDir('Nejsledovanější','http://www.playtvak.cz/nejsledovanejsi.aspx',2,icon,1,"Playtvak.cz - Nejsledovanější")   
    addDir('Playtvákovy hity','http://www.playtvak.cz',7,icon,1,"Playtvak.cz - Playtvákovy hity")  

def NEW(url,page):
    
    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    xbmc.log(str(doc.title))
    try:
    		desc = doc.find("div", "colophon").p.getText(" ").encode('windows-1250')
    except:
		desc = ""

    #Prvni tri nejnovejsi porady
    items_doc = doc.find("ul", "slider-a parts-list")
    items = items_doc.findAll('li')

    #Dalsi nejnovejsi porady
    items_doc = doc.find("div", "parts-list")
    items = items + items_doc.findAll('li')

    for item in items:
            urlel = item.find("div","cell").find("a")
            url = urlel['href']
            nazev = urlel.getText().strip().encode('windows-1250','replace')
            img = item.find("img")
            urlel = item.find("a")	    
            title = urlel.getText().strip().encode('windows-1250','replace') + " - " + nazev	    
	    thumb = normalize_url(img['src'])
            addDir(title,url,4,thumb,1,desc)

def HITS(url,page):
    
    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    xbmc.log(str(doc.title))
    try:
    		desc = doc.find("div", "colophon").p.getText(" ").encode('windows-1250')
    except:
		desc = ""

    #Playtvakovy hity
    items = doc.find("div", "searcher-list")
    items = items.findAll('li')

    for item in items:
            urlel = item.find("div","cell").find("a")
            url = urlel['href']
            nazev = urlel.getText().strip().encode('windows-1250','replace')
            img = item.find("img")
            urlel = item.find("a")	    
            title = urlel.getText().strip().encode('windows-1250','replace') + " - " + nazev	    
	    thumb = normalize_url(img['src'])
            addDir(title,url,4,thumb,1,desc)

def CATEGORIES(url,page):

    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    xbmc.log(str(doc.title))

    items = doc.find("div", "parts-list").ul
    items = items.findAll('li')
    desc = str(doc.title)

    for item in items:
            urlel = item.find("a")
            url = urlel['href']
	    if "slowtv" in url:
			continue 
            title = urlel.getText(" ").encode('windows-1250')
	    urlel = item.find("p")
            desc = urlel.getText(" ").encode('windows-1250')
	    thumb = normalize_url(item.find("img")['src'])
            addDir(title,url,2,thumb,1,desc)

def INDEX(url,page):

    html = load(url)
    doc = bs4.BeautifulSoup(html)
    xbmc.log(str(doc.title))
    try:
    		desc = doc.find("div", "colophon").p.getText(" ").encode('utf-8')
    except:
		desc = ""

    items = doc.find("div", "parts-list").ul
    items = items.findAll('li')

    for item in items:
            urlel = item.find("a")
            url = urlel['href']
            title = urlel.getText().strip()
	    title = title.encode('utf-8')
	    thumb = normalize_url(item.find("img")['src'])
            addDir(title,url,4,thumb,1,desc)

    try:

	    items = doc.find("div", "pack").ul
	    items = items.findAll('li')

	    for item in items:
		    urlel = item.find("a")
		    url = urlel['href']
		    title = urlel.getText().strip()
		    title = title.encode('utf-8')
		    thumb = normalize_url(item.find("img")['src'])
		    addDir(title,url,4,thumb,1,desc)
    except:
      	    pass

def VIDEOLINK(url,name):

    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    video = doc.findAll("meta", property="og:video:url")
    video_name = name

    porad = doc.find("div", "playtvak-info").find("a", "btn")

    for item in video:
        if "configURL=" in item['content']:
            xmlurl = item['content'].split("configURL=")[1]
            configxml = load(xmlurl).encode('utf-8')
            configxml = bs4.BeautifulSoup(configxml)
            thumb = normalize_url(configxml.find("imageprev").getText())
            desc = configxml.find("title").getText()
            linkvideo = configxml.find("linkvideo")
            server = linkvideo.find("server").getText()
            url = None
            if _auto_quality_:
                for video in linkvideo.findAll("file"):
                    if video['quality'] == _quality_:
                        url = normalize_url(server + "/" + video.getText())
                # v pripade, ze zvolena kvalita nebyla nalezena, prehraj
                # posledni match
                if not url:
                    print('Expected quality not found, playing the last link')
                    url = normalize_url(server + "/" + video.getText())

                player = xbmc.Player()
                player.play(url)
                if _skip_logo_:
                    while not player.isPlaying():
                        pass
                    time.sleep(1)
                    player.seekTime(6)
            else:
                for video in linkvideo.findAll("file"):
                    name = "Kvalita: " + video['quality']
                    url = normalize_url(server + "/" + video.getText())
                    addLink(name, video_name, url, thumb, desc)

    urlporad = porad['href'].replace("?playList=all","")

    addDir("[COLOR blue]Další díly pořadu >>>[/COLOR]",urlporad,2,thumb,1,"Přejít na další epizody aktuálního pořadu")

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param



def addLink(name,video_name, url,iconimage,popis):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": video_name, "Plot": popis} )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage,page,popis):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&page="+str(page)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": popis } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
params=get_params()
url=None
name=None
thumb=None
mode=None
page=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        page=int(params["page"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Page: "+str(page)

if mode==None or url==None or len(url)<1:
        print ""
        STATS("OBSAH", "Function")
        OBSAH()

elif mode==6:
        print ""+url
        print ""+str(page)
        STATS("NEW", "Function")                
        NEW(url,page)

elif mode==7:
        print ""+url
        print ""+str(page)
        STATS("HITS", "Function")                
        NEW(url,page)
        
elif mode==5:
        print ""+url
        print ""+str(page)      
        STATS("CATEGORIES", "Function") 
        CATEGORIES(url,page)
        
elif mode==2:
        print ""+url
        print ""+str(page) 
        STATS("INDEX", "Function")       
        INDEX(url,page)

elif mode==4:
        print ""+url
        STATS("VIDEOLINK", "Item")
        VIDEOLINK(url, name)
     
elif mode==3:
        print ""+url
        try:
            STATS(name, "Item")
            VIDEOLINK(url, name)
        except IndexError:
            INDEX(url, name)
 
xbmcplugin.endOfDirectory(int(sys.argv[1]))
