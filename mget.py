#!/usr/bin/env python
from datetime import date
import hashlib
import urllib
import os
try:
    import wx
    hasWx = True
except:
    hasWx = False

baseurl = 'http://g2.start.no/tegneserier/striper/m/mstriper/' 

redownload = False
verbose    = True
duplikates = False
makealbum = True

strips = {} # List of md5 sums for files you already have

nonex = urllib.urlopen(baseurl + "nonexistingfile").read()
nonexmd5 = hashlib.md5(nonex).hexdigest()

start = date(2004,10,25).toordinal()
stop  = date.today().toordinal()

numdays = stop - start

def mksubdir(direc):
    direcs = map(lambda s: s + '/', direc.split('/'))
    for i in range(0, len(direcs)):
        if not os.path.exists(''.join(direcs[0:(i+1)])):
            os.mkdir(''.join(direcs[0:(i+1)]))
if hasWx:
    app = wx.PySimpleApp()
    prd = wx.ProgressDialog("Fremgang", "Fremgang", numdays,
        style = wx.PD_AUTO_HIDE 
        | wx.PD_ELAPSED_TIME
        | wx.PD_ESTIMATED_TIME)

for i in range(start, stop+1):
    if hasWx:
        prd.Update(i - start)
    
    normdate = date.fromordinal(i)    
    if i < date(2005,1,16).toordinal(): 
        stripfile = normdate.strftime('%d%m%Y')
    else: 
        stripfile = 'm'+normdate.isoformat().replace('-','') 
    stripfile += '.gif'
    
    if verbose: print "Laster ned stripe %i av %i(%s)... " % (i-start+1, numdays,stripfile),
    
    folder = "striper/" + str(normdate.year) + "/" + ("%02i" % normdate.month) + "/"
    if (not redownload) and os.path.exists(folder + stripfile):
        if verbose: print "eksisterer allerede"
        temp = open(folder + stripfile, "rb")
        md5sum = hashlib.md5(temp.read()).hexdigest()
        temp.close()
        if not md5sum in strips:
            strips[md5sum] = [(date.fromordinal(i), folder + stripfile)]
        elif duplikates:
            strips[md5sum].append((date.fromordinal(i), folder + stripfile))
        continue
    
    strip = urllib.urlopen(baseurl + stripfile).read()
    
    md5sum = hashlib.md5(strip).hexdigest()
    
    if md5sum == nonexmd5:
        if verbose: print 'eksisterer ikke'
        continue
    
    if md5sum in strips:
        if duplikates:
            strips[md5sum].append((date.fromordinal(i), folder + stripfile))
        else:
            if verbose: print 'duplikat'
            continue
    else:
        strips[md5sum] = [(date.fromordinal(i), folder + stripfile)]
    
    mksubdir(folder)
    open(folder + stripfile,"wb").write(strip)
    if verbose: print "ferdig"

if makealbum:
    x = 0
    s = strips.values()
    s.sort()
    album = '<html><body><center><h1>"Daglige" M-striper</h1></center>\n'
    for i in s:
        x += 1
        album += str(x) + "/" + str(len(s)) + ": " + i[0][0].strftime('%d.%m.%Y') + ':<br><img src="' + i[0][1] + '"><br>\n'
    album += '</body></html>'
    f = open('album.html','w')
    f.write(album)
    f.close()
