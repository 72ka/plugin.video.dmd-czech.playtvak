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

#Nacteni informaci o doplnku
__addon__      = xbmcaddon.Addon()
__addonname__  = __addon__.getAddonInfo('name')
__addonid__    = __addon__.getAddonInfo('id')
__cwd__        = __addon__.getAddonInfo('path').decode("utf-8")
__language__   = __addon__.getLocalizedString


def log(msg):
    xbmc.log(("### [%s] - %s" % (__addonname__.decode('utf-8'), msg.decode('utf-8'))).encode('utf-8'), level=xbmc.LOGDEBUG)

def load(url):
    r = requests.get(url)
    return r.text

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
    items = doc.find("ul", "slider-a parts-list")
    items = items.findAll('li')

    for item in items:
            urlel = item.find("a")
            url = urlel['href']
	    img = item.find("img")
	    #ToDo: doresit kodovani
            title = urlel.getText().strip().encode('windows-1250','replace') + " - " + img['alt'].encode('utf','ignore')	    
	    thumb = "http:" + img['src']                       
            addDir(title,url,4,thumb,1,desc)

    #Dalsi nejnovejsi porady
    items = doc.find("div", "parts-list")
    items = items.findAll('li')

    for item in items:
            urlel = item.find("div","cell").find("a")
            url = urlel['href']
	    img = item.find("img")
	    #ToDo: doresit kodovani
            title = urlel.getText().strip().encode('windows-1250','replace') + " - " + img['alt'].encode('windows-1250','replace')	    
	    thumb = "http:" + img['src']                       
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
	    img = item.find("img")
	    #ToDo: doresit kodovani
            title = urlel.getText().strip().encode('windows-1250','replace') + " - " + img['alt'].encode('windows-1250','replace')	    
	    thumb = "http:" + img['src']                       
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
	    thumb = "http:" + item.find("img")['src']                       
            addDir(title,url,2,thumb,1,desc)

def INDEX(url,page):

    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    xbmc.log(str(doc.title))
    try:
    		desc = doc.find("div", "colophon").p.getText(" ").encode('windows-1250')
    except:
		desc = ""

    items = doc.find("div", "parts-list").ul
    items = items.findAll('li')

    for item in items:
            urlel = item.find("a")
            url = urlel['href']
            title = urlel.getText().strip()
	    title = title.encode('windows-1250','replace')
	    thumb = "http:" + item.find("img")['src']                       
            addDir(title,url,4,thumb,1,desc)

    items = doc.find("div", "pack").ul
    items = items.findAll('li')

    for item in items:
            urlel = item.find("a")
            url = urlel['href']
            title = urlel.getText().strip()
	    title = title.encode('windows-1250','replace')
	    thumb = "http:" + item.find("img")['src']                       
            addDir(title,url,4,thumb,1,desc)

def VIDEOLINK(url,name):

    html = load(url).encode('utf-8')
    doc = bs4.BeautifulSoup(html)
    video = doc.findAll("meta", property="og:video:url")
    video_name = name

    for item in video:
		if "configURL=" in item['content']:
	    		xmlurl = item['content'].replace("http://g.idnes.cz/swf/flv/player.swf?configURL=","")
			configxml = load(xmlurl).encode('utf-8')
    			configxml = bs4.BeautifulSoup(configxml)
			thumb = configxml.find("imageprev").getText()
			desc = configxml.find("title").getText()
			linkvideo = configxml.find("linkvideo")
			server = linkvideo.find("server").getText()
			for video in linkvideo.findAll("file"):
				name = "Kvalita: " + video['quality']
				url = server + video.getText()
				addLink(name,video_name, url,"http:"+thumb,desc)           

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
