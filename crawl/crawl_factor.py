# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 23:18:18 2019

@author: Bokkin Wang
"""

import sys
import bs4
import re
import os
from selenium import webdriver                #selenium实现自动化
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
sys.path.append("D:/bigdatahw/论文合作网络论文/code")
os.chdir("D:/bigdatahw/论文合作网络论文")
data_path = 'D:/bigdatahw/论文合作网络论文/data/crawl data/' 
re_sum = re.compile(r"\((\d+?)\)")

def mkdir(path):
	folder = os.path.exists(path) 
	if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
		print ("---  new folder...  ---")
		print ("---  OK  ---") 
	else:
		print ("---  There is this folder!  ---")
        
def litte_parser(driver):
    html=driver.page_source
    soup=bs4.BeautifulSoup(html,'html.parser',from_encoding="gb18030")
    return soup

def random_roll(driver):
    ActionChains(driver).move_by_offset(100, 500).move_by_offset(500, 100).move_by_offset(200, 200).perform()
    ActionChains(driver).move_by_offset(100, 500).move_by_offset(500, 100).move_by_offset(200, 200).release()
    

def get_jurnal(driver,year):    
    
    journal_url = []
    journal_name = []
    journal_total_cites = []
    journal_factor = []
    journal_score = []
    
    for i in range(10):
        js='document.getElementsByClassName("x-grid-view x-fit-item x-grid-view-default x-unselectable")[0].scrollTop=%d' %(i*600)
        driver.execute_script(js)
        time.sleep(2) #休眠2秒
        journal_url.extend(litte_parser(driver).findAll('tr', {"data-boundview": "gridview-1027"}))
    journal_name = [ journal.find('a',{"href":'#'}).get_text() for journal in journal_url ]    
    journal_total_cites = [journal.findAll('a',{"role":'gridcell'})[2].get_text() for journal in journal_url]
    journal_factor = [journal.findAll('a',{"href":'#'})[1].get_text() for journal in journal_url]
    journal_score = [journal.findAll('a',{"role":'gridcell'})[4].get_text() for journal in journal_url]
    journal_name_new = []
    journal_total_cites_new = []
    journal_factor_new = []
    journal_score_new = []
    i = 0
    for journal in journal_name:
        if journal not in journal_name_new:
            journal_name_new.append(journal)
            journal_total_cites_new.append(journal_total_cites[i])
            journal_factor_new.append(journal_factor[i])
            journal_score_new.append(journal_score[i])
        i = i+1
    csv_name = data_path + str(year)+'.csv'
    pd.DataFrame({'full_journal_title':journal_name_new, 'total_cites':journal_total_cites_new, 'impact_factor':journal_factor_new}).to_csv(csv_name) 


if  __name__=='__main__':
    year = 1997
    jurnal_list_url='http://jcr.incites.thomsonreuters.com/JCRJournalHomeAction.action?pg=JRNLHOME&categoryName=STATISTICS%20%26%20PROBABILITY&year=2017&edition=SCIE&categories=XY#'
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    driver.get(jurnal_list_url)    #输入网址
    driver.implicitly_wait(5)
    category_Elem=driver.find_element_by_xpath('//*[@id="ext-gen1018"]/div[1]/div[2]/div[4]/div[4]/a[2]/button')       #找到id为kw的元素
    category_Elem.click()   #模拟点击功能
    down_Elem=driver.find_element_by_xpath('//*[@id="skip-to-content"]/div/div[1]/div[1]/div/div[4]/i')       #找到id为kw的元素
    down_Elem.click() 
    stat_Elem=driver.find_element_by_xpath('//*[@id="id"]/label/input[@type="checkbox" and @value="XY"]')       #找到id为kw的元素
    stat_Elem.click() 
    roll_Elem=driver.find_element_by_xpath('//*[@id="ext-gen1081"]')       #找到id为kw的元素
    roll_Elem.click() 
    time.sleep(10)
    year_Elem=driver.find_element_by_xpath('//div[@id="boundlist-1143-listEl"]/ul[@class="x-list-plain"]/li[1]')       #找到id为kw的元素
    year = litte_parser(driver).findAll('li', {"role": "option"})[0].get_text()
    mkdir_name = data_path + str(year)
    mkdir(mkdir_name)
    year_Elem.click() 
    submit_Elem=driver.find_element_by_xpath('//*[@id="skip-to-content"]/div/div[1]/div[1]/div/div[6]/div[3]/a[2]')       #找到id为kw的元素
    submit_Elem.click()
    time.sleep(10)
    try:
        jurnal_Elem=driver.find_element_by_xpath('//*[@id="gridview-1022-record-ext-record-515"]/td[4]/div/a')       #找到id为kw的元素
        jurnal_Elem.click()
    except:
        jurnal_Elem=driver.find_element_by_xpath('//*[@id="gridview-1022-record-ext-record-508"]/td[4]/div/a')       #找到id为kw的元素
        jurnal_Elem.click()
    time.sleep(2)
    
    jurnal = get_jurnal(driver,year)