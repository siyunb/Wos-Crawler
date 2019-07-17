# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 15:38:25 2018

@author: situ
"""

import re
from copy import deepcopy

re_author = re.compile(r"\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+),([0-9]+).+?\]|\((.{6,31})\)\[\s+([0-9]+).+?\]|\((.+?)\)")
re_address = re.compile(r"\[.+?([0-9]+).+?\]\s+(.+)")
re_doi = re.compile(r"DOI:</span><value>(.*?)</value>")
re_published = re.compile(r"Published:</span>(.*?)</p>")
re_tableid = re.compile(r"<display_name>(.*?)</display_name>.*([A-Z]-\d{4}-\d{4}).*(http:.*/\d{4}-\d{4}-\d{4}-\d{4})|<display_name>(.*?)</display_name>.*([A-Z]-\d{4}-\d{4})|<display_name>(.*?)</display_name>.*(http:.*/\d{4}-\d{4}-\d{4}-\d{4})",re.DOTALL)

def parse_title1(content):
    try:
        return content.find('div', {"class": "title"}).get_text().strip()
    except:
        return 'NO TITLE'
    
def parse_publisher1(content) :
    try:
        return content.find('p', {"class": "sourceTitle"}).get_text().strip()
    except:
        return 'NO PUBLISHER'
    
def parse_doi1(content):
    massage = str(content.find('div', {"class": "block-record-info block-record-info-source"})).replace("\n", "")
    try:
        doi = re_doi.findall(massage)[0]
    except:
        doi = 'NO DOI'
    if doi == None:
        return "NO DOI"
    else:
        return doi
    
def parse_published1(content):
    try:
        massage ='' .join(str(content.findAll('p', {"class": "FR_field"}))).replace("\n", "")
        published = re_published.findall(massage)[0]
        if published == None:
            return "NO DATE"
        else:
            return published
    except:
        return "NO DATE"
    
def parse_cited_num1(content):
    try:
        return content.select(".large-number")[1].text.replace(" ", "")
    except:
        return "NO CITED"
    
def parse_abstract1(content):
    try:
        if content.select("div.title3")[0].text == 'Abstract':
            return content.select("div.title3 ~ p")[0].text
        else:
            return 'no abstract'
    except:
        return "NO ABSTRACT"
    
def parse_keywords1(content):
    try:
        return ",".join(map(lambda x: x.text,content.select("a[title='Find more records by this author keywords']")))
    except:
        return "NO KEYWORDS"
    
def parse_keyword_plus1(content):
    try:
        return ",".join(map(lambda x: x.text,content.select("a[title='Find more records by this keywords plus']")))
    except:
        return "NO KEYWORDPLUS"
    
def parse_times_cited1(content):
    try:
        return content.select("div.flex-row-partition1 span")[0].text.replace(" ", "")
    except:
        return "NO TIMECITED"
    
def parse_authors1(content):
    
    def no_null1(list):
        while '' in list:
            list.remove('')
        if len(list) ==1:
            list.append('Unknow')
        return list
    
    def uniq1(item):
        uni_list = list(set(item.split('@')[1:]))
        if ('Unknow' in uni_list and len(uni_list)>1):
            uni_list.remove('Unknow')
        uni_list.insert(0,item.split('@')[0])
        return '@'.join(uni_list)
    
    def universitys1(content):
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
        
    author_tuple = re_author.findall(content.select("div.block-record-info > p ")[0].text.replace("\n", ""))
    author_list = [no_null1(list(item)) for item in author_tuple]
    address_dict = dict(map(lambda x: re_address.findall(x.text)[0],content.select(".fr_address_row2 a")))
    university_dict = universitys1(content)

        
        
    def author_address1(author_list,address_dict) :
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
            
    
    def author_university1(author_list,university_dict):
        try:
            aut_uni = []
            for author in author_list:
                auts = [author[0]]
                for i in author[1:]:
                    val = university_dict.get(i, "Unknow")
                    if val not in auts:
                        auts.append(val)
                aut_uni.append("@".join(auts))
            aut_uni = [uniq1(item) for item in aut_uni]
            return "::".join(aut_uni)
        except:
            return 'NO UNIVERSITY'
        
    def author_id1(content):
        try:
            id_list = list(map(lambda x:"@".join(no_null1(list(re_tableid.findall(str(x))[0]))),
                    content.find('table',{"class": "FR_table_borders"}).findAll('tr')[1:]))
            return "::".join(id_list)
        except:
            return 'not exist'
    return author_address1(author_list,address_dict),author_university1(author_list,university_dict),author_id1(content)

def parse_cited1(content):
    re_title = re.compile(r"<value lang_id=\"\">(.*?)</value>")
    re_author = re.compile(r"By: </span>(.*?)</div>")
    re_publish = re.compile(r"<div><value>(.*?)</value>")
    re_time = re.compile(r"Published:      </span><span class=\"data_bold\"><value>(.*?)</value></span>")
    def cite_parse1(cite):
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
        
    try:
        cite_list = content.findAll('div', {"class": "search-results-item"})
        cites = []
        for cite in cite_list:
            cites.append(cite_parse1(cite))
        return '::'.join(cites)
    except:
        return 'No cited'
        
    
def parse2(content ,result, page,i):
    test=deepcopy(result)
    try:
        result['title'][page[i]] = parse_title1(content)
        result['publisher'][page[i]] = parse_publisher1(content)
        result['doi'][page[i]] = parse_doi1(content)
        result['published'][page[i]] = parse_published1(content)
        result['cited_num'][page[i]] = parse_cited_num1(content)
        result['times_cited'][page[i]] = parse_times_cited1(content)
        result['abstract'][page[i]] = parse_abstract1(content)
        result['keywords'][page[i]] = parse_keywords1(content)  
        result['keyword_plus'][page[i]] = parse_keyword_plus1(content)
        result['authors_address'][page[i]] = parse_authors1(content)[0]
        result['author_university'][page[i]] = parse_authors1(content)[1]
        result['author_id'][page[i]] = parse_authors1(content)[2]
        result['cited'][page[i]] = parse_cited1(content)      
        return result
    except:
        test['title'][page[i]] = "Error"
        test['publisher'][page[i]] = ''
        test['doi'][page[i]] = ''
        test['published'][page[i]] = ''
        test['cited_num'][page[i]] = ''
        test['times_cited'][page[i]] = ''
        test['abstract'][page[i]] = ''
        test['keywords'][page[i]] = ''  
        test['keyword_plus'][page[i]] = ''
        test['authors_address'][page[i]] = ''
        test['author_university'][page[i]] = ''
        test['author_id'][page[i]] = ''
        test['cited'][page[i]] = ''        
        return test