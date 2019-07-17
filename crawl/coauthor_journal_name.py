# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 15:36:21 2018

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
    magzine = []
    for i in range(10):
        js='document.getElementsByClassName("x-grid-view x-fit-item x-grid-view-default x-unselectable")[0].scrollTop=%d' %(i*600)
        driver.execute_script(js)
        time.sleep(2) #休眠2秒
        jurnallist = litte_parser(driver).findAll('tr', {"data-boundview": "gridview-1027"})
        magzine.extend(jurnallist)
    csv_name = data_path + str(year)+'/'+'.csv'
    pd.DataFrame({'url':list(set(magzine))}).to_csv(csv_name) 
    return magzine

if  __name__=='__main__':
    jurnal_list_url='http://jcr.incites.thomsonreuters.com'
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    magzine = []
    for i in list(range(21)):
        driver.get(jurnal_list_url)    #输入网址
        driver.implicitly_wait(5)
        category_Elem=driver.find_element_by_xpath('//*[@id="ext-gen1018"]/div[1]/div[2]/div[4]/div[4]/a[2]/button')       #找到id为kw的元素
        category_Elem.click()   #模拟点击功能
        down_Elem=driver.find_element_by_xpath('//*[@id="skip-to-content"]/div/div[1]/div[1]/div/div[4]/i')       #找到id为kw的元素
        down_Elem.click() 
    #    stat_Elem=driver.find_element_by_xpath('//*[@id="id"]/label/input[@type="checkbox" and @value="XY"]')       #找到id为kw的元素
    #    stat_Elem.click() 
        roll_Elem=driver.find_element_by_xpath('//*[@id="ext-gen1081"]')       #找到id为kw的元素
        roll_Elem.click() 
        time.sleep(2)
        year_Elem=driver.find_element_by_xpath('//div[@id="boundlist-1143-listEl"]/ul[@class="x-list-plain"]/li[14]')       #找到id为kw的元素
        year = litte_parser(driver).findAll('li', {"role": "option"})[0].get_text()
        mkdir_name = data_path + str(year)
        mkdir(mkdir_name)
        year_Elem.click() 
        submit_Elem=driver.find_element_by_xpath('//*[@id="skip-to-content"]/div/div[1]/div[1]/div/div[6]/div[3]/a[2]')       #找到id为kw的元素
        submit_Elem.click()
        
        time.sleep(10)
        
        jurnal_Elem=driver.find_element_by_xpath('//*[@id="gridview-1022-record-ext-record-700"]/td[4]/div/a')       #找到id为kw的元素
        jurnal_Elem.click()
        time.sleep(2)
        for i in range(10):
            js='document.getElementsByClassName("x-grid-view x-fit-item x-grid-view-default x-unselectable")[0].scrollTop=%d' %(i*600)
            driver.execute_script(js)
            jurnallist = litte_parser(driver).findAll('tr', {"data-boundview": "gridview-1027"})
            magzine.extend([item.find('a',{"href":'#'}).get_text() for item in jurnallist])
    
    magzine= list(set(magzine))
    
    csv_name = data_path +'journal_name'+'.csv'
    pd.DataFrame({'url':list(set(magzine))}).to_csv(csv_name) 
