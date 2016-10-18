import json
import urllib2
import csv

host = 'https://maps.googleapis.com'
path = '/maps/api/geocode/json?address='
#key = '&key=AIzaSyAVMrYBonMijyj8Nr_nCk--newUokknIvU'
key = '&key=AIzaSyDha81jpDDxWITU4138PBwC5aCWbtfelLg'
#keys = ['&key=AIzaSyAVMrYBonMijyj8Nr_nCk--newUokknIvU','&key=AIzaSyDha81jpDDxWITU4138PBwC5aCWbtfelLg']
def getAddr(companyName):
    url = host+path+companyName+query
    data = json.load(urllib2.urlopen(url))
    return data

def getGeoLocation(companyaddr):
    try:
        companyaddr = companyaddr.replace(' ','+')
        url = host+path+companyaddr+key
        print url
        retval = json.load(urllib2.urlopen(url))
        storeGeo = retval['results'][0]['geometry']
        return storeGeo['location']
    except:
        return ''
