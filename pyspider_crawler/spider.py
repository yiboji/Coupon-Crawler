#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-06-23 00:30:46
# Project: again7

from pyspider.libs.base_handler import *
import threading 
import csv
import os
from pyquery import PyQuery as pq
import re
import copy
import requests
import sys

DIR_PATH = '/home/yiboji/crawler/moneymailer/'
TYPE = ['automotive','beauty','dining','entertainment','healthfitness','homegarden','professional','services','shopping']
START_URL = 'http://www.moneymailer.com/coupons/online/los+angeles/ca/'
COMPANY_HEADER = 'CompanyName,Location,State,ZIPCode,Latitude,Telephone,Type,ImageURL'
COUPON_HEADER = 'CompanyName,Title,CouponInformation,ExpireDate,CouponURL'

class Handler(BaseHandler):

    def __init__(self):
        self.baseURL = START_URL
        self.types = TYPE
        self._value_lock = threading.Lock()
        save = Save()
        save.openCompanySheet('company.csv',COMPANY_HEADER,'wb')
        save.openCouponSheet('coupon.csv',COUPON_HEADER,'wb')
        del save
        requests.post(self.baseURL,data={'searchRadius':25})
    @every(minutes=24 * 60)
    def on_start(self):
        for type in self.types:  
            url = self.baseURL+type
            self.crawl(url, callback=self.index_page, save={'type':type},method='POST',data={'searchRadius':25})

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        pageList = response.doc('.paging')('.pagenum').items()
        hasPage = False
        pagesum = 0
        for page in pageList:
            hasPage = True
            pagesum = pq(page)('a').text()
            
        if hasPage is False:
            self.crawl(response.url,callback=self.detail_page,save={'type':response.save['type']},method='POST',data={'searchRadius':25})
        else:
            pagesum = int(pagesum)
            print pagesum
            for page in range(pagesum):
                url = response.url+'?pageNum='+str(page+1)
                print url
                self.crawl(url,callback=self.detail_page,save={'type':response.save['type']},method='POST',data={'searchRadius':25})
                        
    @config(priority=2)
    def detail_page(self, response):
        coupons = response.doc('.couponlist')('.coupon').items()
        
        for coupon in coupons:
            pqdetail = pq(coupon)('.info')('.text')
            expire = pqdetail('.leftside')('.expiration').text()
            subpageURL = pqdetail('.rightside')('.viewlink')('a').attr('href')
            subpageURL = subpageURL.split('online')
            url = subpageURL[0]+'online'+subpageURL[2] 
            self.crawl(url,callback=self.coupon_detail,save={'type':response.save['type'],'expiredate':expire},method='POST',data={'searchRadius':25})

    @config(priority=3)
    def coupon_detail(self,response):
        pqcoupon = response.doc('#selectedcoupon')
        CompanyName = pqcoupon('.coupontitle')('h2')('.text').text()
        CompanyType = response.save['type']
        CompanyLocation = pqcoupon('.rightside')('.address').text()
        CompanyTel = pqcoupon('.rightside')('.phone').text()
        ImageURL = pqcoupon('.leftside')('#couponimg')('img').attr('src')
        companyObj = Company()
        couponObj = Coupon()
        companyObj.companyName = CompanyName
        companyObj.location = CompanyLocation
        companyObj.latitude = ''
        companyObj.tel = CompanyTel
        companyObj.type = CompanyType
        companyObj.imageURL = ImageURL
        print CompanyName
        print CompanyType
        print CompanyLocation
        print CompanyTel
        print ImageURL
        titles = pqcoupon('.leftside')('.text')('ul')('li').items()
        count = 1
        CouponTitle = ''
        CouponDetail = ''
        for title in titles:
            couponobj = Coupon()
            if count is 1:
                CouponTitle = title.text()
                CouponDetail += '('+str(count)+')'+title.text()+' '
            else:
                CouponDetail += '('+str(count)+')'+title.text() + ' '
            count = count + 1
        CouponDetail = CouponDetail.strip()
        ExpireDate = response.save['expiredate']
        CouponURL = response.url
        couponObj.companyName = CompanyName
        couponObj.title = CouponTitle
        couponObj.couponInformation = CouponDetail
        couponObj.expireDate = ExpireDate
        couponObj.couponURL = CouponURL
        print CouponTitle
        print CouponDetail
        print ExpireDate
        print CouponURL
        self._value_lock.acquire()
        save = Save()
        save.openCompanySheet('company.csv','',mode='a')
        save.openCouponSheet('coupon.csv','',mode='a')
        save.writeCompany(companyObj)
        save.writeCoupon(couponObj)
        del save
        self._value_lock.release()

class Company:

    def __init__(self):
        self.companyName = None
        self.location = None
        self.latitude = None
        self.tel = None
        self.type = None
        self.imageURL = None

class Coupon:

    def __init__(self):
        self.companyName = None
        self.title = None
        self.couponInformation = None
        self.expireDate = None
        self.couponURL = None   

class Save:

    def __init__(self):
        self.path=DIR_PATH
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    def openCompanySheet(self,filename,header,mode):
        self.csvFileCompany = open(self.path+filename,mode)
        self.companyWriter = csv.writer(self.csvFileCompany)
        if mode=='a':
            pass
        else:
            row = header.split(',')
            self.companyWriter.writerow(row)
    def openCouponSheet(self,filename,header,mode):
        self.csvFileCoupon = open(self.path+filename,mode)
        self.couponWriter = csv.writer(self.csvFileCoupon)
        if mode=='a':
            pass
        else:
            row = header.split(',')
            self.couponWriter.writerow(row)
    def writeCompany(self, company):
        row = []
        row.append(company.companyName)
        row.append(company.location)
        row.append('')#State
        row.append('')#ZIPcode
        row.append(company.latitude)
        row.append(company.tel)
        row.append(company.type)
        row.append(company.imageURL)
        self.companyWriter.writerow(row)
        self.csvFileCompany.flush()
    def writeCoupon(self,coupon):
        row = []
        row.append(coupon.companyName)
        row.append(coupon.title)
        row.append(coupon.couponInformation)
        row.append(self.filter(coupon.expireDate))
        row.append(coupon.couponURL)
        self.couponWriter.writerow(row)
        self.csvFileCoupon.flush()
    def filter(self,data):
        retstr = re.sub(r'Expires','',data).strip()
        return retstr
    def __del__(self):
        self.csvFileCoupon.close()
        self.csvFileCompany.close()
