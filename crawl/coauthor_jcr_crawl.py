# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 18:53:06 2018

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
        for j in list(range(len(jurnallist))):
            name = jurnallist[j].find('a',{"href":'#'}).get_text()
            if name not in magzine:
                magzine.append(name)
                try:
                    item_Elem=driver.find_element_by_xpath('//*[@data-recordindex="%d"]/td[3]/div/div'%(len(magzine)-1))       #找到id为kw的元素
                    item_Elem.click()
                except:
                    item_Elem=driver.find_element_by_xpath('//*[@data-recordindex="%d"]/td[3]/div/div'%(len(magzine)-1))       #找到id为kw的元素
                    item_Elem.click()
                time.sleep(20)              
                windows = driver.current_window_handle #定位当前页面句柄
                all_handles = driver.window_handles   #获取全部页面句柄
                while len(all_handles) != 3:
                    time.sleep(5)
                    windows = driver.current_window_handle #定位当前页面句柄
                    all_handles = driver.window_handles   #获取全部页面句柄
                for handle in all_handles:          #遍历全部页面句柄
                    if handle != windows:          #判断条件
                        driver.switch_to.window(handle)      #切换到新页面
                try:
                    artlist_Elem=driver.find_element_by_xpath('//*[@id="view"]/jif-webapp/main/home/div/div/dashboard/div[2]/div/div[3]/div/jif-calculation/div/div/div/div/div[2]/div[1]/div/div[1]/button')       #找到id为kw的元素
                    artlist_Elem.click()
                    time.sleep(2)
                    soup = litte_parser(driver)
                    artlist = []                
                    len_list = re_sum.findall(soup.find('a',{"class":'nav-link active'}).get_text().replace('\n','').strip())[0] 
                except:
                    try:   
                        time.sleep(25)
                        artlist_Elem=driver.find_element_by_xpath('//*[@id="view"]/jif-webapp/main/home/div/div/dashboard/div[2]/div/div[3]/div/jif-calculation/div/div/div/div/div[2]/div[1]/div/div[1]/button')       #找到id为kw的元素
                        artlist_Elem.click()
                        time.sleep(2)
                        soup = litte_parser(driver)
                        artlist = []                
                        len_list = re_sum.findall(soup.find('a',{"class":'nav-link active'}).get_text().replace('\n','').strip())[0] 
                    except:
                        return magzine
                artlist.extend(list(map(lambda x : x.find('a')['href'],litte_parser(driver).findAll('div',{"class":"citable-item-row"}))))
                while len(list(set(artlist))) < int(len_list):
                    try:
                        dragger = driver.find_element_by_class_name("wui-card")  # 被拖拽元素
                        item1 = driver.find_element_by_xpath('//*[@id="view"]/ngb-modal-window/div/div/jif-calculation-citables-modal/div/div[2]/div[%d]'%(2+len(list(set(artlist)))))  # 目标元素1
                        time.sleep(0.5)
                        random_roll(driver)
                        ActionChains(driver).drag_and_drop(dragger, item1).release().perform()                  
                        artlist.extend(list(map(lambda x : x.find('a')['href'],litte_parser(driver).findAll('div',{"class":"citable-item-row"}))))
                        random_roll(driver)
                        time.sleep(0.5)
                    except:
                        return magzine
                time.sleep(0.5)
                driver.close()
                driver.switch_to_window(all_handles[0]) 
                csv_name = data_path + str(year)+'/'+soup.find('div',{"class":'h3'}).get_text()+'.csv'
                pd.DataFrame({'url':list(set(artlist))}).to_csv(csv_name) 
                print(len(magzine)-1)
        #jur_list= list(map(lambda x: x.find('a',{"href":'#'}).get_text() ,jurnallist))
        #magzine.extend(jur_list)
    js='document.getElementsByClassName("x-grid-view x-fit-item x-grid-view-default x-unselectable")[0].scrollTop=0' 
    driver.execute_script(js)
    return magzine

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


item_Elem=driver.find_element_by_xpath('//*[@data-recordindex="%d"]/td[3]/div/div'%(0))       #找到id为kw的元素
item_Elem.click()
time.sleep(10)
windows = driver.current_window_handle #定位当前页面句柄
all_handles = driver.window_handles   #获取全部页面句柄
for handle in all_handles:          #遍历全部页面句柄
    if handle != windows:          #判断条件
        driver.switch_to.window(handle)      #切换到新页面
time.sleep(2)
artlist_Elem=driver.find_element_by_xpath('//*[@id="view"]/jif-webapp/main/home/div/div/dashboard/div[2]/div/div[3]/div/jif-calculation/div/div/div/div/div[2]/div[1]/div/div[1]/button')       #找到id为kw的元素
artlist_Elem.click()
artlist = []
len_list = re_sum.findall(soup.find('a',{"class":'nav-link active'}).get_text().replace('\n','').strip())[0] 
while len(list(set(artlist))) < int(len_list):
    artlist.extend(list(map(lambda x : x.find('a')['href'],litte_parser(driver).findAll('div',{"class":"citable-item-row"}))))
    dragger = driver.find_element_by_class_name("wui-card")  # 被拖拽元素
    item1 = driver.find_element_by_xpath('//*[@id="view"]/ngb-modal-window/div/div/jif-calculation-citables-modal/div/div[2]/div[%d]'%(2+len(list(set(artlist)))))  # 目标元素1
    ActionChains(driver).drag_and_drop(dragger, item1).perform()


