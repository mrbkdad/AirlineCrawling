from collections import namedtuple
import json
'''
기준정보 정의
- 사이트 코드 정보, 대상 노선 정보, 노선과 사이트 코드 정보 매핑 테이블
- 크롤링 기간 정보
- 실시간 여행사 정보 크롤링 대상 항공사 코드
- created by park363 2017-05-26 09:14
- modified by park363 2017-05-30 11:21
'''

## 크롤링 기간 정보
CRAWL_INTERVAL = 60
## 실시간 여행사 스크래핑 대상 항공사 코드
TARGET_AIRLINES = ['7C','TW','LJ','BX','KE','OZ','ZE']
## 생성 파일명 시작 문자열
FILE_NAME_HEAD = 'scrap'
## 폴더 정보
CRAWL_DIR = 'crawl'
SCRAP_DATA_DIR   = 'scrap_data'    ## 스크래핑 완료후 CSV 파일 저장
SCRAP_OK_DIR     = 'scrap_ok'      ## 스크래핑 완료후 raw_data 파일 이동 저장
DB_OK_DIR        = 'db_ok'         ## 데이터베이스 처리 오류시 csv 파일 이동 저장
NODATA_DIR       = 'crawl/nodata'  ## 스크래핑후 잔존 파일, 데이터가 존재하지 않음
JOIN_DIR         = 'join_data'     ## 로드 팩터등 추가 처리를 위한 파일 체크 폴더
JOIN_OK_DIR      = 'join_data/join_ok'  ## 추가 파일 처리후 이동 폴더

## 오류 처리 폴더 : 오류 발생시 해당 파일을 해당 폴더에 유지, 해당 폴더 모니터링시 일정기간 이상 보관된 파일을 오류 처리 방향으로 진행
#SCRAP_ERROR_DIR  = 'scrap_error' ## 스크래핑시 오류 raw_data 파일 이동 저장
#DB_ERROR_DIR     = 'db_error'       ## 데이터베이스 처리 완료후 csv 파일 저장

## 국내선 국제선 구분 - 0 국내선, 1 국제선
## 크롤링/스크래핑 함수용 자료형
CrawlDef = namedtuple('CrawlDefpDef',['dom_int','site','func','isairline'])
ScrapDef = namedtuple('ScrapDef',['dom_int','site','func'])
## 대상 노선 정보 - 국내/국제 구분, 출발지 국가코드, 공항코드, 도착지 국가코드, 공항코드(namedtuple 활용)
Route = namedtuple('Route',['dom_int','dpt_2n','dpt_3p','arr_2n','arr_3p'])

## 기본 정보 초기화 및 관련 변수들
CRAWL_ROUTES = {}
CRAWL_SITE_CODES = []
ROUTE_SITE_MAP = {}
SCRAP_SITE_CODES = []
def init_env_variable(env_file):
    ## 필요정보 json 파일 통한 초기화
    with open(env_file) as fp:
        json_data = json.load(fp)
    ## 포맷 : 'CJJ-CJU': Route(dom_int='0', dpt_2n='KO', dpt_3p='CJJ', arr_2n='KO', arr_3p='CJU')
    for k,v in json_data['CRAWL_ROUTES'].items():
        CRAWL_ROUTES[k] = Route(*v)
    ## 포맷 : CrawlDefpDef(dom_int='0', site='IP', func='crawling_IP_dom', isairline=False)
    for v in json_data['CRAWL_SITE_CODES']:
        CRAWL_SITE_CODES.append(CrawlDef(*v))
    ## 포맷 : 'CJJ-CJU': ['IP', '7C', 'LJ', 'OZ', 'KE', 'ZE']
    ROUTE_SITE_MAP = json_data['ROUTE_SITE_MAP']
    ## 포맷 : ScrapDef(dom_int='0', site='IP', func='scraping_IP_dom')
    for v in json_data['SCRAP_SITE_CODES']:
        SCRAP_SITE_CODES.append(ScrapDef(*v))