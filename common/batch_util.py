from datetime import datetime, timedelta
import csv, os, sys
import logging
from common.util import get_files, move_file
from common.env_variable import *
from common.scrap_func import *
from common.crawl_func import *
from common.log_util import log

'''
배치 처리에 필요한 공통 유틸
- created by park363 2017-05-29 14:30
- modified by park363 2017-05-30 11:23
'''

## 기간 생성 함수 - 내일 부터 기간동안의 날 까지
def crawl_period(interval):
    return [(datetime.today()+timedelta(1)*i).strftime('%Y%m%d') for i in range(1,interval+1)]
## 파일명 생성 함수
def file_name(site_code,dpt,arr,dpt_date,airline=None):
    dpt_txt = str(dpt)
    if dpt_txt.find('/') >= 0:
        dpt_txt = dpt_txt.split('/')[0]
    if len(dpt_txt) > 3:
        dpt_txt = dpt_txt[:3]
    arr_txt = str(arr)
    if arr_txt.find('/') >= 0:
        arr_txt = arr_txt.split('/')[0]
    if len(arr_txt) > 3:
        arr_txt = arr_txt[:3]
    if airline: ## 실시간용
        return '{}/{}_{}_{}_{}_{}_{}_{}.txt'.format(CRAWL_DIR,FILE_NAME_HEAD,datetime.today().strftime('%Y%m%d%H'),
                                                       site_code,airline,dpt_txt,arr_txt,dpt_date)
    else: ## 항공사용
        return '{}/{}_{}_{}_{}_{}_{}_{}.txt'.format(CRAWL_DIR,FILE_NAME_HEAD,datetime.today().strftime('%Y%m%d%H'),
                                                    site_code,site_code,dpt_txt,arr_txt,dpt_date)
## 저장시 헤더 정보 생성
## 포맷 : [날짜시간,사이트코드,국내선/국제선구분,항공사코드,출발지,도착지,출발일]
def set_headinfo(site_code,dom_int,airline,dpt,arr,dpt_date,crawl_date=None):
    if crawl_date is None:
        crawl_date=datetime.today().strftime('%Y%m%d%H')
    return '[{},{},{},{},{},{},{}]'.format(crawl_date,site_code,dom_int,airline,dpt,arr,dpt_date)
def get_headinfo(head):
    head_list = head.strip().split(',')
    if len(head_list) < 6:
        return None
    head_info = {}
    head_info['crawl_date'] = head_list[0][1:]
    head_info['site_code'] = head_list[1]
    head_info['dom_int'] = head_list[2]
    head_info['airline'] = head_list[3]
    head_info['dpt'] = head_list[4]
    head_info['arr'] = head_list[5]
    head_info['dpt_date'] = head_list[6][:-1]
    return head_info
## site 함수 생성
def get_scrap_site_func(dom_int,site):
    for site_code in SCRAP_SITE_CODES:
        #log(site_code)
        if site_code.dom_int == dom_int and site_code.site == site:
            try:
                log(site_code)
                func = eval(site_code.func)
            except NameError as e:
                log(e,level=logging.ERROR)
                return None
            return func
    return None
def get_crawl_site_func(dom_int,site):
    for site_code in CRAWL_SITE_CODES:
        #log(site_code)
        if site_code.dom_int == dom_int and site_code.site == site:
            try:
                log(site_code)
                func = eval(site_code.func)
            except NameError as e:
                log(e,level=logging.ERROR)
                return None
            return func,site_code.isairline
    return None,None
# 크롤링 함수 실행 및 오류 처리를 위한 함수
def crawling_func(func,*argv):
    try:
        return func(*argv)
    except TypeError as te:
        return str(te)
    except ConnectionError as ce:
        return str(ce)
    except:
        log("Unexpected error:", sys.exc_info()[0])
        raise
## 크롤 데이터 파일로 부터 내용을 읽어 헤더와 내용 리턴
## 스크랩된 데이터(CSV) 파일 처리를 위해 csv 옵션 추가
def read_crawled_file(file,csv=False):
    with open(file,'rt',encoding='utf-8') as fp:
        raw_data = fp.read()
        if csv:
            head = get_headinfo(raw_data.splitlines()[0].replace('"',''))
            raw_data = '\n'.join(raw_data.splitlines()[1:])
        else:
            head = get_headinfo(raw_data.splitlines()[0])
            raw_data = ''.join(raw_data.splitlines()[1:])
    return head, raw_data

def get_crawled_file_list(crawl_dir):
    file_list = get_files(crawl_dir,check=FILE_NAME_HEAD)
    if file_list is None:
        log('there is no files for scraping in the {} fold!'.format(CRAWL_DIR),level=logging.WARNING)
    return file_list
## 리스트를 csv 파일로 저장 처리, 파일명은 패스포함
def scraped_list_to_csv(head,raw_list,csvfile):
    with open(csvfile, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, #delimiter=' ',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)#csv.QUOTE_ALL)
        ## 헤더 출력
        csvwriter.writerow([head])
        ## 내용 출력
        for d in raw_list:
            csvwriter.writerow(d)
def move_scraped_file(file,fold):
    if file is None or fold is None:
        log('check your file or fold![{},{}]'.format(file,fold),level=logging.WARNING)
        return None
    ## 파일 존재 여부, 폴더 존재 여부 체크
    if not os.path.isfile(file):
        log('file not found![{}]'.format(file),level=logging.WARNING)
        return None
    if not os.path.isdir(fold):
        log('fold not found![{}]'.format(fold),level=logging.WARNING)
        return None
    ## 이동 대상 폴더에 파일이 존재 할 경우 해당 폴더의 파일 삭제 처리
    if os.path.isfile(os.path.join(fold,os.path.split(file)[-1])):
        os.remove(os.path.join(fold,os.path.split(file)[-1]))
    return move_file(file,fold)
