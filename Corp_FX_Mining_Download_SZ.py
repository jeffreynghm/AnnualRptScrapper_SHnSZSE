import subprocess
import nltk
import jieba
#import jieba.analyse
import os
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


FIREFOXPROFILE = "C:\\Users\\Jeffrey Ng\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\urnj58kz.default"     
def scrapReports(link,stockcode,driver,res):
    #make sure the download function works

    #change pdf default behavior on firefox to be download about:preferences#applications

    try:
        driver.get(link)
    except Exception:
        print('cannot load the page '+stockcode)
    
    driver.implicitly_wait(5) # seconds
   
    element = driver.find_element_by_name("stockCode")
    element.send_keys(stockcode)

    try:
        driver.find_element_by_xpath("//select[@name='noticeType']/option[text()='年度报告']").click()
    except NoSuchElementException:
        print('nothing for '+stockcode)

    element = driver.find_element_by_name("startTime")
    element.clear()
    element.send_keys("2015-09-22")
    element = driver.find_element_by_name("endTime")
    element.clear()
    element.send_keys("2016-09-22")
    
    driver.find_element_by_xpath("//input[@src='images2008/button_qd.gif']").click()

    pattern = re.compile(r"(年度报告)+^(摘要)^(取消)", re.UNICODE)
    
    try:
        elements = driver.find_elements_by_partial_link_text("年年度报告")
    except NoSuchElementException:
        print('nothing for '+stockcode)

    match = False
    for element in elements:
        
        match = pattern.match(element.text, re.UNICODE)
        #RE not working
        #if match:
        docName = element.text
        newpage = element.get_attribute('href')
        head, tail = os.path.split(newpage)
        data={'stockcode':stockcode,'filename':tail,'fileDescription':docName,'KeywordSet':'','link':newpage,'set':['']}
        res = res.append(pd.DataFrame(data),ignore_index=True)
        
        #element.click()
        print(tail)
        
        try:
            urllib.request.urlretrieve(newpage,".\\PDF\\"+tail)
        except Exception:
            print("can't download "+newpage)
            
    return res


def calScore(f,res,filetxt,resScore):
    #v1
    #all_lines = ''
    #all_seg_lines = ''
    wordList = ['']
    FX_Score = 0
    
    keywords = set(['外汇'])
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

    #    all_lines = all_lines + line
    #tags = jieba.analyse.extract_tags(all_lines, topK=100)
    #print(tags)
 
    #words = jieba.tokenize(unicode(f, 'utf-8'))
    #for tk in words:
    #    print(tk)
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
        'KeywordSet':'',
        'set':['']
        }

    res = pd.DataFrame(data)
    resScore = pd.DataFrame(data)
    outputfileName = "scrapResult_SZ.txt"
    #use a spider to crawl the annual reports of the companies
    #use current profile
    #about:support
    #under application basic: show folders
    #originalDLPath = 'C:\\Users\\Jeffrey Ng\\Downloads'
    profile = webdriver.firefox.firefox_profile.FirefoxProfile(FIREFOXPROFILE)
    profile.set_preference('browser.download.dir', pathname)
    driver = webdriver.Firefox(profile)
    driver.set_page_load_timeout(30)
    link = 'http://disclosure.szse.cn/m/search0425.jsp'
    stockcodes = '.\StockCodes.txt'
    for stockcode in open(stockcodes, "r",encoding = 'utf-8'):
        res=scrapReports(link,stockcode,driver,res)
    res.to_csv(outputfileName,encoding = 'utf-8',sep='\t')
    
    print('Now converting the pdf into text and immediately mine it')
    #use subprocess to convert the file into text    
    PDFpath = os.path.dirname(os.path.realpath(__file__))+'\\PDF\\'
    for file in os.listdir(PDFpath):
        if file.endswith(".PDF"):
            
            #os.chdir(PDFpath)
            print(os.getcwd())
            
            try:
                subprocess.check_output([".\\Xpdf\\pdftotext.exe","-table","-enc","UTF-8",PDFpath+file],shell=True,stderr=subprocess.STDOUT)
            except Exception:
                continue
            
            filetxt = os.path.splitext(file)[0]
            txtPath = PDFpath + filetxt+'.txt'
            #output the score
            f =  open(txtPath, "r",encoding = 'utf-8')
            resScore=calScore(f,res,filetxt,resScore)

    #renameFiles(PDFpath)
    resScore.to_csv("scrapResultScore.txt",encoding = 'utf-8')
    res_M=res.merge(resScore,how='inner',on='filename')
    res_M.to_csv("scrapResult_M.txt",encoding = 'utf-8',sep='\t')

if __name__ == '__main__':
  main()
