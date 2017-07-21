# import subprocess
import nltk
import jieba
#import jieba.analyse
import os
import sys
#sys.path.append('C:\\Jeffrey Ng\\gecko')
#sys.path.append('C:\\Jeffrey Ng\\gecko\\geckodriver.exe')
from collections import Counter
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

import pandas as pd

import urllib.request #download the file before proceeding
import socket #catch gaddrinfo error

import datetime # convert to date for comparsion

def mmYYYY_toVal(mmYYYY_CHI):
    mth_yr = mmYYYY_CHI.split(" ")
    for date_ele in mth_yr:
        if date_ele == '一月':
            mth = 1
        elif date_ele == '二月':
            mth = 2
        elif date_ele == '三月':
            mth = 3
        elif date_ele == '四月':
            mth = 4
        elif date_ele == '五月':
            mth = 5
        elif date_ele == '六月':
            mth = 6
        elif date_ele == '七月':
            mth = 7
        elif date_ele == '八月':
            mth = 8
        elif date_ele == '九月':
            mth = 9
        elif date_ele == '十月':
            mth = 10
        elif date_ele == '十一月':
            mth = 11
        elif date_ele == '十二月':
            mth = 12
        else:
            year_int = int(date_ele)
    return datetime.date(year_int,mth,1)

#input: text
def mmYYYY_Compare(mmYYYY_CHI,mmYYYY_CHI_Input):
    #mmYYYY_CHI_Input = "十月 2015"
    mmYYYY_Val = mmYYYY_toVal(mmYYYY_CHI)
    mmYYYY_Input_Val = mmYYYY_toVal(mmYYYY_CHI_Input)
    if mmYYYY_Val == mmYYYY_Input_Val:
        result = 0
    elif mmYYYY_Val > mmYYYY_Input_Val:
        result =1
    elif mmYYYY_Val < mmYYYY_Input_Val:
        result =-1
    return result


#mmYYYY_CHI_Input is what we are targeting
#datePicker is the element being init
def datePicker(datepickerElement,dateElement,driver,mmYYYY_CHI_Input):
    print('datePicker function')
    element_text = datepickerElement.text
    print('element.text : {0}'.format(element_text)+'datepickerElement')
    
    datepickerDays=datepickerElement.find_element_by_css_selector("div.datetimepicker-days")
    #datepickersDays=datepickerElement.find_elements_by_xpath("//div[@class='datetimepicker-days']")
    #for d in datepickersDays:
    #    element_text = d.text
    #    if element_text != '':
    #        datepickerDays=d
    #        break
    #datepickerDays.click()
    element_text = datepickerDays.text
    print('element.text : {0}'.format(element_text)+'datepickerdays')
    todayButton = datepickerDays.find_element_by_css_selector("th.today")
    #debug: todayButton = datepickerElement.find_element_by_css_selector("th.today")

    #i = 0
    #for countTdyButton in datepickerDays.find_elements_by_css_selector("th.today"):
    #    print(str(i+1)+' Tdy Button')

    element_text = todayButton.text
    print('element.text : {0}'.format(element_text)+'todayButton')
    
    #todayButton = datepickerDays.find_elements_by_xpath("//*[contains(text(), '今天')]")

    
    #js = 'document.querySelectorAll("div")[0].style.display="block";'
    #driver.execute_script(js)
    #loc = todayButton.location
    #for i in loc:
    #    print(i)
    
    #print('Today butt ' + todayButton.location)
    if todayButton.is_displayed():
        print('Today butt is here')
        todayButton.click()
    else:
        print('Cannot get hold of Today button')
    dateElement.click()
    
    #datepickerDays=datepickerElement.find_element_by_xpath("//div[@class='datetimepicker-days']")
    
    mmYYYY_CHI_TXT = datepickerDays.find_element_by_class_name("switch").text
    mmYYYY_Compare_res = mmYYYY_Compare(mmYYYY_CHI_TXT, mmYYYY_CHI_Input)

    while  mmYYYY_Compare_res != 0:
        if mmYYYY_Compare_res == 1:
            leftArrow = datepickerDays.find_element_by_class_name("icon-arrow-left")
            leftArrow.click()
        if mmYYYY_Compare_res == -1:
            rightArrow = datepickerDays.find_element_by_class_name("icon-arrow-right")
            rightArrow.click()
        mmYYYY_CHI_TXT = datepickerDays.find_element_by_class_name("switch").text
        mmYYYY_Compare_res = mmYYYY_Compare(mmYYYY_CHI_TXT, mmYYYY_CHI_Input)
    #do not update the day
    dayButtons = datepickerDays.find_elements_by_css_selector("td.day")
    for dayButton in dayButtons:
        thestr = dayButton.text
        if thestr == '1':
            dayButton.click()
            break
    print('date picker 1')
    
    return
  
def scrapReports_SHSE(link,stockcode,driver,res,fr_str="四月 2016",to_str="六月 2017"):

    driver.get(link)
    driver.implicitly_wait(5) # seconds
   
    element = driver.find_element_by_xpath("//input[@placeholder='证券代码或简称']")
    element.send_keys(stockcode)

    dateElement = driver.find_element_by_id("start_date")
    dateElement.click()
    
    datepickerElement=driver.find_element_by_css_selector("div.datetimepicker.datetimepicker-dropdown-bottom-right.dropdown-menu")
    datePicker(datepickerElement,dateElement,driver,fr_str)
    #1900 2016
    
    dateElement2 = driver.find_element_by_id("end_date")
    print('key sent')
    dateElement2.click()

    datepickerElements=driver.find_elements_by_css_selector("div.datetimepicker.datetimepicker-dropdown-bottom-right.dropdown-menu")
    for datepickerElement in datepickerElements:
        #debug
        element_text = datepickerElement.text
        element_attribute_value = datepickerElement.get_attribute('value')

        if element_text != '':
            print("datepicker selected")
            datePicker(datepickerElement,dateElement2,driver,to_str)
            break
    
    try:
        driver.find_element_by_css_selector("button.btn.btn-primary.active").click()
    except Exception:
        driver.find_element_by_css_selector("button.btn.btn-primary").click()
        
    pattern = re.compile(r"(年度报告)+^(摘要)^(取消)", re.UNICODE)
    
    try:
        elements = driver.find_elements_by_partial_link_text("年年度报告")
    except NoSuchElementException:
        print('nothing for '+stockcode)

    for element in elements:
        ##RE not working
        tmp = element.text
        match = pattern.search(element.text, re.UNICODE)
        #if match:
        docName = element.text
        newpage = element.get_attribute('href')
        if newpage.upper().endswith('.PDF'):
            head, tail = os.path.split(newpage)
            data={'stockcode':stockcode,'filename':tail,'fileDescription':docName,'KeywordSet':[''],'link':newpage}
            res = res.append(pd.DataFrame(data),ignore_index=True)
            #element.click()
            print(tail)
            try:
                urllib.request.urlretrieve(newpage,".\\PDF_SH\\"+tail)
            except Exception:
                print("can't download "+newpage)
                continue
            
    return res

def calScore(f,res,filetxt,resScore):
    #v1
    #all_lines = ''
    #all_seg_lines = ''
    wordList = ['']
    FX_Score = 0
    
    keywords = set(['外汇损益','掉期','海外市场','外汇波动','外汇市场汇率波动','外汇远期合约'])
    #add these keywords into the dictionary
    for addword in keywords:
        jieba.add_word(addword, freq=None, tag=None)
    
    for line in f:
        seg_words = jieba.cut(line,cut_all=True)
        for word in seg_words:
            if word in keywords:
                FX_Score += 1
                wordList.append(word)
    wordListStr = str(Counter(wordList))
    data={'filename':filetxt+'.PDF','KeywordSet':wordListStr,'fxScore':FX_Score,'set':['']}
    resScore = resScore.append(pd.DataFrame(data),ignore_index=True)
    
    
    print(filetxt)
    print(Counter(wordList))
    print(FX_Score)

    return resScore
def main():

    pathname = os.path.dirname(os.path.abspath(__file__))
    #create dataframe that store all output data
    data = {
        'stockcode':'',
        'filename':'',
        'fileDescription':'',
        'link':'',
        'fxScore':0,
        'KeywordSet':['']
        }

    res = pd.DataFrame(data)
    resScore = pd.DataFrame(data)
    
    #use a spider to crawl the annual reports of the companies
    #use current profile
    #about:support
    #under application basic: show folders
    
    profile = webdriver.firefox.firefox_profile.FirefoxProfile('C:\\Users\\Jeffrey Ng\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\urnj58kz.default')
    profile.set_preference('browser.download.dir', pathname)
    #gecko driver can be downloaded from github and place in any place, as long as it is specified below
    driver = webdriver.Firefox(profile,executable_path='C:\\Jeffrey Ng\\gecko\\geckodriver.exe')
    link = 'http://disclosure.szse.cn/m/search0425.jsp'
    stockcodes = '.\StockCodes_SH.txt'
    for stockcode in open(stockcodes, "r",encoding = 'utf-8'):
        res=scrapReports_SHSE(link,stockcode,driver,res)
##    stockcode ='600739' #debug
    res=scrapReports_SHSE(link,stockcode,driver,res)
    res.to_csv("scrapResult_SH.txt",encoding = 'utf-8',sep='\t')
    resScore.to_csv("scrapResultScore_SH.txt",encoding = 'utf-8')
    res_M=res.merge(resScore,how='inner',on='filename')
    res_M.to_csv("scrapResult_M_SH.txt",encoding = 'utf-8',sep='\t')

if __name__ == '__main__':
  main()
