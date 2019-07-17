# -*- coding: utf-8 -*-
"""
Created on Sat Jul  7 23:19:15 2018

@author: Bokkin Wang
"""
import re
import os
import bs4
import requests
from copy import deepcopy
from selenium import webdriver                #selenium实现自动化

re_author = re.compile(r"\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+).+?\]|\((.+?)\)")
re_address = re.compile(r"\[.+?([0-9]+).+?\]\s+(.+)")
re_doi = re.compile(r"DOI:</span><value>(.*?)</value>")
re_published = re.compile(r"Published:</span>(.*?)</p>")
re_tableid = re.compile(r"<display_name>(.*?)</display_name>.*([A-Z]-\d{4}-\d{4}).*(http:.*/\d{4}-\d{4}-\d{4}-\d{4})|<display_name>(.*?)</display_name>.*([A-Z]-\d{4}-\d{4})|<display_name>(.*?)</display_name>.*(http:.*/\d{4}-\d{4}-\d{4}-\d{4})",re.DOTALL)

def litte_parser(driver):
    html=driver.page_source
    soup=bs4.BeautifulSoup(html,'html.parser',from_encoding="gb18030")
    return soup

def parse_title(content: bs4.BeautifulSoup) -> str:
    try:
        return content.select(".title value")[0].text.strip()
    except:
        return 'NO TITLE'
    
def parse_publisher(content: bs4.BeautifulSoup) -> str:
    try:
        return content.find('p', {"class": "sourceTitle"}).get_text().strip()
    except:
        return 'NO PUBLISHER'
    
def parse_doi(content: bs4.BeautifulSoup) -> str:
    massage = str(content.find('div', {"class": "block-record-info block-record-info-source"})).replace("\n", "")
    try:
        doi = re_doi.findall(massage)[0]
    except:
        doi = 'NO DOI'
    if doi == None:
        return "NO DOI"
    else:
        return doi
    
def parse_published(content: bs4.BeautifulSoup) -> str:
    try:
        massage = str(content.find('div', {"class": "block-record-info block-record-info-source"})).replace("\n", "")
        published = re_published.findall(massage)[0]
        if published == None:
            return "NO DATE"
        else:
            return published
    except:
        return "NO DATE"
    
def parse_cited_num(content: bs4.BeautifulSoup) -> str:
    try:
        return content.select(".large-number")[1].text.replace(" ", "")
    except:
        return "NO CITED"
    
def parse_abstract(content: bs4.BeautifulSoup) -> str:
    try:
        name = [item.text for item in content.select("div.title3")]
        if 'Abstract' in name:
            i = name.index('Abstract')
            return content.findAll('div', {"class": "block-record-info"})[2+i].find('p', {"class": "FR_field"}).text
        else:
            return 'no abstract'
    except:
        return "NO ABSTRACT"
  
def parse_keywords(content: bs4.BeautifulSoup) -> str:
    try:
        return ",".join(map(lambda x: x.text,content.select("a[title='Find more records by this author keywords']")))
    except:
        return "NO KEYWORDS"
    
def parse_keyword_plus(content):
    try:
        return ",".join(map(lambda x: x.text,content.select("a[title='Find more records by this keywords plus']")))
    except:
        return "NO KEYWORDPLUS"
    
def parse_times_cited(content):
    try:
        return content.select("div.flex-row-partition1 span")[0].text.replace(" ", "")
    except:
        return "NO TIMECITED"
    
def parse_authors(content: bs4.BeautifulSoup) -> str:
    
    def no_null(list):
        while '' in list:
            list.remove('')
        if len(list) ==1:
            list.append('Unknow')
        return list
    
    def uniq(item):
        uni_list = list(set(item.split('@')[1:]))
        if ('Unknow' in uni_list and len(uni_list)>1):
            uni_list.remove('Unknow')
        uni_list.insert(0,item.split('@')[0])
        return '@'.join(uni_list)
    
    def universitys(content):
        university_dict = dict()
        try:
            university_list = content.select("table.FR_table_noborders")[-1].findAll('tr')
            for i,university in enumerate(university_list):
                uni_list= university.findAll('preferred_org')
                if len(uni_list) == 0:
                    university_dict[str(i+1)] = 'Unknow'
                else:
                    university_dict[str(i+1)] = '@'.join(list(map(lambda x:x.text,uni_list)))
            return university_dict
        except:
            return university_dict
    
    def author_address(author_list,address_dict) -> str:
        try:
            aut_add = []
            for author in author_list:
                auts = [author[0]]
                for i in author[1:]:
                    auts.append(address_dict.get(i, "Unknow"))
                aut_add.append("@".join(auts))
            return "::".join(aut_add)
        except:
            return 'NO ADDRESS'
             
    def author_university(author_list,university_dict):
        try:
            aut_uni = []
            for author in author_list:
                auts = [author[0]]
                for i in author[1:]:
                    val = university_dict.get(i, "Unknow")
                    if val not in auts:
                        auts.append(val)
                aut_uni.append("@".join(auts))
            aut_uni = [uniq(item) for item in aut_uni]
            return "::".join(aut_uni)
        except:
            return 'NO UNIVERSITY'
        
    def author_id(content):
        try:
            id_list = list(map(lambda x:"@".join(no_null(list(re_tableid.findall(str(x))[0]))),
                    content.find('table',{"class": "FR_table_borders"}).findAll('tr')[1:]))
            return "::".join(id_list)
        except:
            return 'not exist'
        
    author_tuple = re_author.findall(content.select("div.block-record-info > p ")[0].text.replace("\n", ""))
    author_list = [no_null(list(item)) for item in author_tuple]
    address_dict = dict(map(lambda x: re_address.findall(x.text)[0],content.select(".fr_address_row2 a")))
    university_dict = universitys(content)    
    chame = []
    for item in author_list:
        chame.extend(item[1:])
        chame = list(set(chame))

    if  len(chame) ==1 and chame[0] == 'Unknow':
        author_name = [[item[0]] for item in author_list] 
        if university_dict:
            univer= '@'.join(list(university_dict.values()))
            for item in author_name:
                item.append(univer) 
            author_uni= '::'.join(['@'.join(item) for item in author_name])
        else:
            univer= 'Unknow'
            for item in author_name:
                item.append(univer) 
            author_uni= '::'.join(['@'.join(item) for item in author_name])
        author_name = [[item[0]] for item in author_list]             
        if address_dict:
            univer= '@'.join(list(address_dict.values()))
            for item in author_name:
                item.append(univer) 
            author_add= '::'.join(['@'.join(item) for item in author_name])
        else:
            univer= 'Unknow'
            for item in author_name:
                item.append(univer) 
            author_add= '::'.join(['@'.join(item) for item in author_name])        
        return author_add,author_uni,author_id(content)
    else:
        return author_address(author_list,address_dict),author_university(author_list,university_dict),author_id(content)

def parse_cited(driver):
    re_title = re.compile(r"<value lang_id=\"\">(.*?)</value>")
    re_author = re.compile(r"By: </span>(.*?)</div>")
    re_publish = re.compile(r"<div><value>(.*?)</value>")
    re_time = re.compile(r"Published:      </span><span class=\"data_bold\"><value>(.*?)</value></span>")    
    content = litte_parser(driver)
    
    def cite_parse(cite):
        cite = str(cite).replace("\n", "") 
        try:
            title = re_title.findall(cite)[0]
        except:
            title = 'no title'
        try:
            author = re_author.findall(cite)[0]
        except:
            author = 'no author'
        try:
            publish = re_publish.findall(cite)[0]
        except:
            publish = 'no publish'
        try:
            time = re_time.findall(cite)[0]
        except:
            time = 'no time'
        return '+'.join([title,author,publish,time])
    
    if  int(parse_cited_num(content))>30:
        try:
            cited_Elem=driver.find_element_by_xpath('//*[@id="cited-refs-full-record"]/div[1]/h3/a')       #找到id为kw的元素
            cited_Elem.click()
            soup = litte_parser(driver)
            page = int(soup.find('span',{"id": "pageCount.top"}).get_text())
            cite_list = []
            cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
            for i in range(page-1):
                page_Elem=driver.find_element_by_xpath('//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a/i')       #找到id为kw的元素
                page_Elem.click()
                soup = litte_parser(driver)
                cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
        except:
            return 'No cited'
    else:
        cite_list = []
        cite_list.extend(content.findAll('div', {"class": "search-results-item"}))                
    cites = []
    for cite in cite_list:
        cites.append(cite_parse(cite))
    return '::'.join(cites)

def parse_cited1(content,driver):
    re_title = re.compile(r"<value lang_id=\"\">(.*?)</value>")
    re_author = re.compile(r"By: </span>(.*?)</div>")
    re_publish = re.compile(r"<div><value>(.*?)</value>")
    re_time = re.compile(r"Published:      </span><span class=\"data_bold\"><value>(.*?)</value></span>")    
    
    def cite_parse(cite):
        cite = str(cite).replace("\n", "") 
        try:
            title = re_title.findall(cite)[0]
        except:
            title = 'no title'
        try:
            author = re_author.findall(cite)[0]
        except:
            author = 'no author'
        try:
            publish = re_publish.findall(cite)[0]
        except:
            publish = 'no publish'
        try:
            time = re_time.findall(cite)[0]
        except:
            time = 'no time'
        return '+'.join([title,author,publish,time])
    
    if  int(parse_cited_num(content))>30:
        try:
            cited_Elem=driver.find_element_by_xpath('//*[@id="cited-refs-full-record"]/div[1]/h3/a')       #找到id为kw的元素
            cited_Elem.click()
            ur = driver.current_url
            try:
                soup = litte_parser(driver)
                page = int(soup.find('span',{"id": "pageCount.top"}).get_text())
                cite_list = []
                cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
                for i in range(page-1):
                    page_Elem=driver.find_element_by_xpath('//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a/i')       #找到id为kw的元素
                    page_Elem.click()
                    soup = litte_parser(driver)
                    cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
            except:
                driver =webdriver.Chrome('C:/Program Files (x86)/Google/chrome/Application/chromedriver.exe')   #打开浏览器
                driver.get(ur)   
                response = requests.get(driver.current_url)
                response.encoding='UTF-8'
                page = response.text
                soup =  bs4.BeautifulSoup(page,'html.parser')
                page = int(soup.find('span',{"id": "pageCount.top"}).get_text())
                cite_list = []
                cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
                for i in range(page-1):
                    page_Elem=driver.find_element_by_xpath('//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a/i')       #找到id为kw的元素
                    page_Elem.click()
                    response = requests.get(driver.current_url)
                    response.encoding='UTF-8'
                    page = response.text
                    soup =  bs4.BeautifulSoup(page,'html.parser')
                    cite_list.extend(soup.findAll('div', {"class": "search-results-item"}))
        except:
            return 'No cited'
    else:
        cite_list = []
        cite_list.extend(content.findAll('div', {"class": "search-results-item"}))                
    cites = []
    for cite in cite_list:
        cites.append(cite_parse(cite))
    return '::'.join(cites)


def parse(content ,result,driver ):
    test=deepcopy(result)
    try:
        result['title'].append(parse_title(content))
        result['publisher'].append(parse_publisher(content))
        result['doi'].append(parse_doi(content))
        result['published'].append(parse_published(content))
        result['cited_num'].append(parse_cited_num(content))
        result['times_cited'].append(parse_times_cited(content))
        result['abstract'].append(parse_abstract(content))
        result['keywords'].append(parse_keywords(content))   
        result['keyword_plus'].append(parse_keyword_plus(content))
        result['authors_address'].append(parse_authors(content)[0])
        result['author_university'].append(parse_authors(content)[1])
        result['author_id'].append(parse_authors(content)[2])
        result['cited'].append(parse_cited(driver))
        return result
    except:
        test['title'].append("Error")
        test['publisher'].append('')
        test['doi'].append('')
        test['published'].append('')
        test['cited_num'].append('')
        test['times_cited'].append('')
        test['abstract'].append('')
        test['keywords'].append('')   
        test['keyword_plus'].append('')
        test['authors_address'].append('')
        test['author_university'].append('')
        test['author_id'].append('')
        test['cited'].append('')
        return test

def parse1(content ,result,driver ):
    test=deepcopy(result)
    try:
        result['title'].append(parse_title(content))
        result['publisher'].append(parse_publisher(content))
        result['doi'].append(parse_doi(content))
        result['published'].append(parse_published(content))
        result['cited_num'].append(parse_cited_num(content))
        result['times_cited'].append(parse_times_cited(content))
        result['abstract'].append(parse_abstract(content))
        result['keywords'].append(parse_keywords(content))   
        result['keyword_plus'].append(parse_keyword_plus(content))
        result['authors_address'].append(parse_authors(content)[0])
        result['author_university'].append(parse_authors(content)[1])
        result['author_id'].append(parse_authors(content)[2])
        result['cited'].append(parse_cited1(content,driver))
        return result
    except:
        test['title'].append("Error")
        test['publisher'].append('')
        test['doi'].append('')
        test['published'].append('')
        test['cited_num'].append('')
        test['times_cited'].append('')
        test['abstract'].append('')
        test['keywords'].append('')   
        test['keyword_plus'].append('')
        test['authors_address'].append('')
        test['author_university'].append('')
        test['author_id'].append('')
        test['cited'].append('')
        return test

if __name__ == '__main__':
    os.chdir("D:/bigdatahw/论文合作网络论文")
    url = 'http://apps.webofknowledge.com/full_record.do?product=UA&search_mode=GeneralSearch&qid=7&SID=8CymVW5jQM1Bd8nPVWn&page=1&doc=1'
    html = requests.get(url)
    content= bs4.BeautifulSoup(html.content,'html.parser',from_encoding="gb18030") 
   
