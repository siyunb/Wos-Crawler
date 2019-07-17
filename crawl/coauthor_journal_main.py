# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 19:57:03 2018

@author: Bokkin Wang
"""

import re
import os
import bs4
import sys
sys.path.append("D:/bigdatahw/pan_paper/talent_program/code")
from multiprocessing.dummy import Pool
from selenium import webdriver                #selenium实现自动化
import pandas as pd
from coauther_parser import parse,parse1
from coauthor_parser2 import  parse2 
import time
import requests

os.chdir("D:/bigdatahw/pan_paper/talent_program")
path="D:/bigdatahw/pan_paper/talent_program/journal"
mou_path = 'D:/bigdatahw/论文合作网络论文/data/crawl data/alldata1'
jurnal_url = 'http://gateway.webofknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcAuth=TSMetrics&SrcApp=TSM_TEST&DestApp=WOS_CPL&DestLinkType=FullRecord&KeyUT=WOS%3A000365750600005'
rev_path = "D:/bigdatahw/论文合作网络论文/data/crawl data/rev_alldata"
re_sum = re.compile(r"\((\d+?)\)")

def litte_parser(driver):
    html=driver.page_source
    soup=bs4.BeautifulSoup(html,'html.parser',from_encoding="gb18030")
    return soup


def parse_title(content: bs4.BeautifulSoup) -> str:
    try:
        return content.select(".title value")[0].text
    except:
        return 'NO TITLE'
    
def load_name(path):
    csvnames = os.listdir(path)
    csvnames = [os.path.splitext(csvname)[0] for csvname in csvnames]
    return csvnames

def load_csv(path):
    csvnames = os.listdir(path)
    return csvnames

def minus(waiting,mou_journals):
    for item in mou_journals:
        if item in waiting:
            waiting.remove(item)
    return waiting
    
def all_name(string):
    if 'http://apps.webofknowledge.com' in string:
        return string
    else:
        return 'http://apps.webofknowledge.com'+string

def crawl_url(journals):
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    for journal in journals:
        driver.get('http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=7Akq16NW3PSKXQ2Vwfe&preferencesSaved=')
        close_Elem=driver.find_element_by_xpath('//*[@id="clearIcon1"]')       #找到id为kw的元素
        close_Elem.click()
        Elem=driver.find_element_by_xpath('//*[@id="value(input1)"]')       #找到id为kw的元素
        Elem.send_keys(journal)  
        driver.implicitly_wait(3)
        stat_Elem=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button')       #找到id为kw的元素
        stat_Elem.click()
        driver.implicitly_wait(3)
        page_count = litte_parser(driver).find('span', {"id": "pageCount.bottom"}).get_text()
        url =[]
        first = [all_name(item['href']) for item in litte_parser(driver).findAll('a', {"class": "smallV110 snowplow-full-record"})]
        url.extend(first)
        for i in range(int(page_count)-1):
            down_Elem=driver.find_element_by_xpath('//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a/i')       #找到id为kw的元素
            down_Elem.click() 
            driver.implicitly_wait(3)
            circel = [all_name(item['href']) for item in litte_parser(driver).findAll('a', {"class": "smallV110 snowplow-full-record"})]
            url.extend(circel)
        csv_name = mou_path + 'journal/'+journal+'.csv'
        pd.DataFrame({'url':list(set(url))}).to_csv(csv_name,encoding='utf-8',index=False) 
        print(journal+'    succeed!')

def crawl_url2(journals):
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    columns = ['title','publisher','doi','published','cited_num','times_cited','abstract','keywords','keyword_plus','authors_address','author_university','author_id']
    for journal in journals:
        driver.get('http://apps.webofknowledge.com/')
        language_Elem=driver.find_element_by_xpath('/html/body/div[2]/div[22]/ul[2]/li[3]/a')       #找到id为kw的元素
        language_Elem.click() 
        english_Elem=driver.find_element_by_xpath('/html/body/div[2]/div[22]/ul[2]/li[3]/ul/li[3]/a')       #找到id为kw的元素
        english_Elem.click()
        kind_Elem=driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b')       #找到id为kw的元素
        kind_Elem.click()
        publish_Elem=driver.find_element_by_xpath('//*[@id="select2-select1-results"]/li[7]')       #找到id为kw的元素
        publish_Elem.click()        
        close_Elem=driver.find_element_by_xpath('//*[@id="clearIcon1"]')       #找到id为kw的元素
        close_Elem.click()
        Elem=driver.find_element_by_xpath('//*[@id="value(input1)"]')       #找到id为kw的元素
        Elem.send_keys(journal)  
        driver.implicitly_wait(3)
        stat_Elem=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button')       #找到id为kw的元素
        stat_Elem.click()
        driver.implicitly_wait(3)
        soup = litte_parser(driver)
        paper_count = soup.find('span', {"id": "hitCount.top"}).get_text().replace(',','')
        url =[]
        first = all_name(soup.findAll('a', {"class": "smallV110 snowplow-full-record"})[0]['href'])
        page_href = re.sub(r"page=1&doc=1",'page=%d&doc=%d',first)
        for j in list(range(int(paper_count))):
            ur = page_href%(1,j+1)
            url.append(ur)
        results = {'title':[],'publisher':[],'doi':[],'published':[],'cited_num':[],'times_cited':[],'abstract':[],'keywords':[],'keyword_plus':[],'authors_address':[],'author_university':[],'author_id':[]}
        for ur in url:
            driver.get(ur)    #输入网址
            try:
                surpeme = litte_parser(driver)
            except:
                driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
                driver.get(ur)    #输入网址
                response = requests.get(ur)
                surpeme=response.content
            results = (crawler_one(surpeme,results))
        pd.DataFrame(results).to_csv("alldata/" + journal+".csv",encoding='utf-8',index=False,columns=columns)    
        print(journal+'    succeed!')


def crawl_url3(need_journals,mou_path = 'alldata'):
    result = pd.read_csv(mou_path+'/'+need_journals+'.csv')
    page = result[result['title'] == 'Error'].index.tolist()
    columns = ['title','publisher','doi','published','cited_num','times_cited','abstract','keywords','keyword_plus','authors_address','author_university','author_id']
    if len(page)>0 :
        driver =webdriver.Chrome('C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe')   #打开浏览器
        columns = ['title','publisher','doi','published','cited_num','times_cited','abstract','keywords','keyword_plus','authors_address','author_university','author_id']
        driver.get('http://apps.webofknowledge.com/')
        language_Elem=driver.find_element_by_xpath('/html/body/div[2]/div[22]/ul[2]/li[3]/a')       #找到id为kw的元素
        language_Elem.click() 
        english_Elem=driver.find_element_by_xpath('/html/body/div[2]/div[22]/ul[2]/li[3]/ul/li[3]/a')       #找到id为kw的元素
        english_Elem.click()
        kind_Elem=driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b')       #找到id为kw的元素
        kind_Elem.click()
        publish_Elem=driver.find_element_by_xpath('//*[@id="select2-select1-results"]/li[7]')       #找到id为kw的元素
        publish_Elem.click()        
        close_Elem=driver.find_element_by_xpath('//*[@id="clearIcon1"]')       #找到id为kw的元素
        close_Elem.click()
        Elem=driver.find_element_by_xpath('//*[@id="value(input1)"]') #找到id为kw的元素
        Elem.send_keys(need_journals)  
        driver.implicitly_wait(3)
        stat_Elem=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button')       #找到id为kw的元素
        stat_Elem.click()
        driver.implicitly_wait(3)
        soup = litte_parser(driver)
        url = []
        first = all_name(soup.findAll('a', {"class": "smallV110 snowplow-full-record"})[0]['href'])
        page_href = re.sub(r"page=1&doc=1",'page=%d&doc=%d',first)
        for j in page:
            ur = page_href%(1,j+1)
            url.append(ur)
        for i,ur in enumerate(url):
            driver.get(ur) 
            response = requests.get(ur)
            surpeme=response.content
            surpeme = bs4.BeautifulSoup(surpeme,'html.parser',from_encoding="gb18030")
            results = crawler_two(surpeme,result,page,i)
        driver.quit()
        results.to_csv("rev_alldata/" + need_journals+".csv",encoding='utf-8',index=False,columns=columns)    
        print(need_journals+'    succeed!')
    else:
        result.to_csv("rev_alldata/" + need_journals+".csv",encoding='utf-8',index=False,columns=columns)    
        print(need_journals+'    succeed!')

def crawl_url4(journals):
    for journal in journals:
        driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
        driver.get('http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=8ElaRa6s6qJf4ztRity&preferencesSaved=')
        time.sleep(10)
        driver.refresh()
#        language_Elem=driver.find_element_by_xpath('/html/body/div[1]/div[22]/ul[2]/li[3]/a/i')       #找到id为kw的元素
#        language_Elem.click() 
#        english_Elem=driver.find_element_by_xpath('/html/body/div[1]/div[22]/ul[2]/li[3]/ul/li[3]/a')       #找到id为kw的元素
#        english_Elem.click()
#        kind_Elem=driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b')       #找到id为kw的元素
#        kind_Elem.click()
#        publish_Elem=driver.find_element_by_xpath('//*[@id="select2-select1-result-7r6j-SO"]')       #找到id为kw的元素
#        publish_Elem.click()        
#        close_Elem=driver.find_element_by_xpath('//*[@id="clearIcon1"]')       #找到id为kw的元素
#        close_Elem.click()
        Elem=driver.find_element_by_xpath('//*[@id="value(input1)"]')       #找到id为kw的元素
        Elem.send_keys(journal)  
        driver.implicitly_wait(3)
        stat_Elem=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button')       #找到id为kw的元素
        stat_Elem.click()
        year_Elem=driver.find_element_by_xpath('//*[@id="PublicationYear_2"]')       #找到id为kw的元素
        year_Elem.click()
        refine_Elem=driver.find_element_by_xpath('//*[@id="PublicationYear_tr"]/button[1]')       #找到id为kw的元素
        refine_Elem.click()         
        driver.implicitly_wait(3)
        soup = litte_parser(driver)
        paper_count = soup.find('span', {"id": "hitCount.top"}).get_text().replace(',','')
        url =[]
        first = all_name(soup.findAll('a', {"class": "smallV110 snowplow-full-record"})[0]['href'])
        page_href = re.sub(r"page=1&doc=1",'page=%d&doc=%d',first)
        for j in list(range(int(paper_count))):
            ur = page_href%(1,j+1)
            url.append(ur)
        url_pool = list_of_groups(url,15)
        for item in url_pool:
            item.append(journal) 
        driver.quit()        
        p=Pool(8)
        p.map(pool_url, url_pool)
        p.close()
        p.join()  
        
def pool_url(url_list):
    journal = url_list[-1]
    url = url_list[:-1]
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器    
    results = {'title':[],'publisher':[],'doi':[],'published':[],'cited_num':[],'times_cited':[],'abstract':[],'keywords':[],'keyword_plus':[],'authors_address':[],'author_university':[],'author_id':[],'cited':[]}
    columns = ['title','publisher','doi','published','cited_num','times_cited','abstract','keywords','keyword_plus','authors_address','author_university','author_id','cited']    
    ur = url[0]
    driver.get(ur)    #输入网址
    driver.implicitly_wait(5)
    driver.refresh()    
    try:
        surpeme = litte_parser(driver)
    except:
        driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
        driver.get(ur)    #输入网址
        response = requests.get(ur)
        driver.implicitly_wait(5)
        driver.refresh() 
        surpeme=response.content
    results = (crawler_one(surpeme,results,driver))
    for ur in url[1:]:
        driver.get(ur)    #输入网址
        time.sleep(2)
        try:
            surpeme = litte_parser(driver)
            results = (crawler_one(surpeme,results,driver))
        except:
            driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
            driver.get(ur)    #输入网址
            response = requests.get(ur)
            response.encoding='UTF-8'
            page = response.text
            surpeme =  bs4.BeautifulSoup(page,'html.parser')
            results = (crawler_one_one(surpeme,results,driver))
    driver.quit()
    if journal not in load_name('D:/bigdatahw/pan_paper/talent_program/data'):
        pd.DataFrame(results).to_csv("data/" + journal+".csv",encoding='utf-8',index=False,columns=columns)    
        print(journal+'    succeed!')
    else:
        pd.DataFrame(results).to_csv("data/" + journal+".csv",encoding='utf-8',index=False,columns=columns,header=False,mode = 'a')    
        print(journal+'   add'+'    succeed!')

def crawl_url5(journal):
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
    driver.get('http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=7ETTBP7W6QYAegynixZ&preferencesSaved=')
    time.sleep(10)
    driver.refresh()
    language_Elem=driver.find_element_by_xpath('/html/body/div[1]/div[22]/ul[2]/li[3]/a/i')       #找到id为kw的元素
    language_Elem.click() 
    english_Elem=driver.find_element_by_xpath('/html/body/div[2]/div[22]/ul[2]/li[3]/ul/li[3]/a')       #找到id为kw的元素
    english_Elem.click()
    kind_Elem=driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b')       #找到id为kw的元素
    kind_Elem.click()
    publish_Elem=driver.find_element_by_xpath('//*[@id="select2-select1-results"]/li[7]')       #找到id为kw的元素
    publish_Elem.click()        
    close_Elem=driver.find_element_by_xpath('//*[@id="clearIcon1"]')       #找到id为kw的元素
    close_Elem.click()
    Elem=driver.find_element_by_xpath('//*[@id="value(input1)"]')       #找到id为kw的元素
    Elem.send_keys(journal)  
    driver.implicitly_wait(3)
    stat_Elem=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button')       #找到id为kw的元素
    stat_Elem.click()
    driver.implicitly_wait(3)
    soup = litte_parser(driver)
    paper_count = soup.find('span', {"id": "hitCount.top"}).get_text().replace(',','')
    url =[]
    first = all_name(soup.findAll('a', {"class": "smallV110 snowplow-full-record"})[0]['href'])
    page_href = re.sub(r"page=1&doc=1",'page=%d&doc=%d',first)
    for j in list(range(int(paper_count))):
        ur = page_href%(1,j+1)
        url.append(ur)
    url_pool = list_of_groups(url,100)
    for item in url_pool:
        item.append(journal) 
    driver.quit()        
    p=Pool(6)
    p.map(pool_url_bu, url_pool)
    p.close()
    p.join()  
        
def pool_url_bu(url_list):
    journal = url_list[-1]
    url = url_list[:-1]
    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器    
    driver.get(url[2])
    driver.refresh()
    title = parse_title(litte_parser(driver))
    all_title =list( pd.read_csv("alldata1/"+journal+".csv",encoding="ISO-8859-1")['title'])
    if title in all_title:
        driver.quit()
    else:
        try:
            results = {'title':[],'publisher':[],'doi':[],'published':[],'cited_num':[],'times_cited':[],'abstract':[],'keywords':[],'keyword_plus':[],'authors_address':[],'author_university':[],'author_id':[],'cited':[]}
            columns = ['title','publisher','doi','published','cited_num','times_cited','abstract','keywords','keyword_plus','authors_address','author_university','author_id','cited']    
            for ur in url:
                try:
                    driver.get(ur)    #输入网址
                except:
                    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器    
                    driver.get(ur)    #输入网址
                try:
                    surpeme = litte_parser(driver)
                    results = (crawler_one(surpeme,results,driver))
                except:
                    driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
                    driver.get(ur)    #输入网址
                    response = requests.get(ur)
                    response.encoding='UTF-8'
                    page = response.text
                    surpeme =  bs4.BeautifulSoup(page,'html.parser')
                    results = (crawler_one_one(surpeme,results,driver))
            driver.quit()
            if journal not in load_name('D:/bigdatahw/论文合作网络论文/data/crawl data/alldata1'):
                pd.DataFrame(results).to_csv("alldata1/" + journal+".csv",encoding='utf-8',index=False,columns=columns)    
                print(journal+'    succeed!')
            else:
                pd.DataFrame(results).to_csv("alldata1/" + journal+".csv",encoding='utf-8',index=False,columns=columns,header=False,mode = 'a')    
                print(journal+'   add'+'    succeed!')
        except:
            print(ur)

def crawler_one(soup,result,driver):
    result = parse(soup,result,driver)
    print("succeed!")
    return result

def crawler_one_one(soup,result,driver):
    result = parse1(soup,result,driver)
    print("succeed!")
    return result

def crawler_two(soup,result,page,i):
    result = parse2(soup,result,page,i)
    print("succeed!")
    return result


def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) *children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count !=0 else end_list
    return end_list

if  __name__=='__main__':
    journals = load_name(path)
#    mou_journals = load_name(mou_path)
#    p=Pool(3)
#    p.map(crawl_url2,[first,second,third])       #爬取4页内容
    journal = journals[0]
    crawl_url4(journals)
    crawl_url5(journal)


    rev_journals = load_name(rev_path)
    need_journals = minus(mou_journals,rev_journals)
    p=Pool(4)
    p.map(crawl_url3, need_journals)
    p.close()
    p.join()       
    