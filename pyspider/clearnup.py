import csv
import re 
import string
from datetime import datetime
from googleapi import *
PATH = './'
def removeDupCompany(path,filename):
    with open(path+filename,'r') as inFile, open(path+'moneymail_'+filename,'wb') as outFile:
        reader = csv.reader(inFile,delimiter=',')
        writer = csv.writer(outFile,delimiter=',')
        seen = set()
        firstrow = True
        for row in reader:
            if firstrow is True:
                writer.writerow('CompanyName,Location,State,ZIPCode,Latitude,Telephone,Type,ImageURL'.split(','))
                firstrow = False
            else:
                newrow = []
                compareRow = '' 
                compareRow += row[0]+row[1]
                if compareRow in seen:
                    continue
                seen.add(compareRow)
                addr = row[1]
                '''
                tel = re.search(r'\(\d{3}\)\d{3}-\d{4}',addr)
                if tel is not None:
                    tel = tel.group()
                else:
                    tel = ''
                addr = re.sub(r'\(\d{3}\)\d{3}-\d{4}.*?$','',addr)
                '''
                state = addr.split(',')
                addr = state[0]
                if len(state)>1:
                    arr = state[len(state)-1].strip()
                    arr = arr.split(' ')
                    state = arr[0]
                    zipcode = arr[1]
                    '''
                    if re.search(r'\d{5}',arr) is not None:
                        arr = arr.split(' ')
                        state = arr[0]
                        zipcode = arr[1]
                    '''
                else:
                    state = ''
                    zipcode = ''
                newrow.append(row[0])
                newrow.append(addr)
                newrow.append(state)
                newrow.append(zipcode)
                newrow.append(row[4])
                newrow.append(row[5])
                if row[6]=="dining":
                    row[6] = "Restaurant"
                newrow.append(row[6])
                newrow.append(row[7])
                writer.writerow(newrow)

def uniformCouponDate(path, filename):
    with open(path+filename, 'r') as inFile, open(path+'moneymail_'+filename,'wb') as outFile:
        reader = csv.reader(inFile, delimiter=',')
        writer = csv.writer(outFile,delimiter=',')
        firstrow = True
        title = ['CouponID','CompanyName', 'Location', 'radius', 'Title', 'CouponInformation', 'ExpireDate', 'CouponURL']
        for row in reader:
            if firstrow is False:
                try:
                    newrow = []
                    date = row[4]
                    date = date.split('/')
                    datestr = ''
                    for index, item in enumerate(date):
                        if index!=len(date)-1:
                            if len(date[index])==1:
                                datestr = datestr+'0'+date[index]
                            else:
                                datestr = datestr + date[index]
                            datestr = datestr + '/'
                        else:
                            datestr = datestr + date[index]
                    dateObj = datetime.strptime(datestr,'%m/%d/%Y')
                    row[4] = dateObj.strftime("%m/%d/%Y")

                    geoloc = getGeoLocation(row[1])
                    print geoloc
                    if geoloc != '':
                        row[1] = '%f,%f' %(geoloc['lat'],geoloc['lng'])
                    else:
                        row[1] = '';
                    couponid = row[2]+'_'+row[1]+'_'+row[4]
                    newrow.append(couponid)
                    newrow.append(row[0])
                    newrow.append(row[1])
                    newrow.append('200')
                    newrow.append(row[2])
                    newrow.append(row[3])
                    newrow.append(row[4])
                    newrow.append(row[5])
                    print newrow
                    writer.writerow(newrow)
                except:
                    print "expire date error:" + str(row)
            else:
                writer.writerow(title)
                firstrow = False
def cleanSpecChar(row):
    printable = set(string.printable)
    retrow = []
    for item in row:
        item = re.sub(r'\n',' ',item)
        item = re.sub(r'\(\d{3}\)\d{3}-\d{4}.*?$','',item)
        #filter out non-printable characters
        item = filter(lambda x: x in printable, item)
        item = item.strip()
        retrow.append(item)
    return retrow

removeDupCompany(PATH,'company.csv')
uniformCouponDate(PATH,'coupon.csv') 
