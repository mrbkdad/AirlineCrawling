from collections import namedtuple
'''
기준정보 정의
- 사이트 코드 정보, 대상 노선 정보, 노선과 사이트 코드 정보 매핑 테이블
- 크롤링 기간 정보
- 실시간 여행사 정보 크롤링 대상 항공사 코드
- created by park363 2017-05-26 09:14
- modified by park363 2017-05-30 11:21
'''

## 국내선 국제선 구분 - 0 국내선, 1 국제선
## 사이트 코드 정보 - 코드 : 국내/국제 구분, 해당 크롤링 함수 정보(국내선용, 국제선용 namedtuple)
CrawlDef = namedtuple('CrawlDefpDef',['dom_int','site','func','isairline'])
CRAWL_SITE_CODES = [
    CrawlDef('0','IP','crawling_IP_dom',False),
    CrawlDef('1','IP','crawling_IP_int',False),
    CrawlDef('0','7C','crawling_7C_dom',True),
    CrawlDef('0','TW','crawling_TW_dom',True),
    CrawlDef('0','LJ','crawling_LJ_dom',True),
    CrawlDef('0','BX','crawling_BX_dom',True),
    CrawlDef('0','ZE','crawling_ZE_dom_int',True),
]
## 대상 노선 정보 - 국내/국제 구분, 출발지 국가코드, 공항코드, 도착지 국가코드, 공항코드(namedtuple 활용)
Route = namedtuple('Route',['dom_int','dpt_2n','dpt_3p','arr_2n','arr_3p'])
CRAWL_ROUTES = {## 키(출발지-도착지[-왕복]), 노선정보
    ## 국내선
    'GMP-CJU':Route('0','KO','GMP','KO','CJU'),
    'CJJ-CJU':Route('0','KO','CJJ','KO','CJU'),
    'KUV-CJU':Route('0','KO','KUV','KO','CJU'),
    'PUS-CJU':Route('0','KO','PUS','KO','CJU'),
    'GMP-PUS':Route('0','KO','GMP','KO','PUS'),
    
    ## 국제선
    'ICN-NRT':Route('1','KO','ICN','JP','NRT'),
}
## 노선과 사이트 매핑 정보
ROUTE_SITE_MAP = {
    'GMP-CJU':['IP','7C','TW','LJ','BX','ZE'],
    'CJJ-CJU':['IP','7C','LJ','OZ','KE','ZE'],
    'KUV-CJU':['IP','KE','ZE'],
    'PUS-CJU':['IP','7C','LJ','OZ','KE','ZE'],
    'GMP-PUS':['IP','7C','BX','OZ','ZE'],
    'ICN-NRT':['IP','7C','TW','LJ','ZE'],
}
## 크롤링 기간 정보
CRAWL_INTERVAL = 60
## 실시간 여행사 스크래핑 대상 항공사 코드
TARGET_AIRLINES = ['7C','TW','LJ','BX','KE','OZ','ZE']
## 생성 파일명 시작 문자열
FILE_NAME_HEAD = 'scrap'
## 폴더 정보
CRAWL_DIR = 'crawl'
SCRAP_DATA_DIR   = 'scrap_data'  ## 스크래핑 완료후 CSV 파일 저장
SCRAP_OK_DIR     = 'scrap_ok'    ## 스크래핑 완료후 raw_data 파일 이동 저장
DB_OK_DIR        = 'db_ok'    ## 데이터베이스 처리 오류시 csv 파일 이동 저장

## 오류 처리 폴더 : 오류 발생시 해당 파일을 해당 폴더에 유지, 해당 폴더 모니터링시 일정기간 이상 보관된 파일을 오류 처리 방향으로 진행
#SCRAP_ERROR_DIR  = 'scrap_error' ## 스크래핑시 오류 raw_data 파일 이동 저장
#DB_ERROR_DIR     = 'db_error'       ## 데이터베이스 처리 완료후 csv 파일 저장
## scraping 함수용 site code

ScrapDef = namedtuple('ScrapDef',['dom_int','site','func'])
SCRAP_SITE_CODES = {
    ScrapDef('0','IP','scraping_IP_dom'),
    ScrapDef('1','IP','scraping_IP_int'),
    ScrapDef('0','TW','scraping_TW_dom'),
    ScrapDef('1','TW','scraping_TW_int'),
    ScrapDef('0','7C','scraping_7C_dom'),
    ScrapDef('1','7C','scraping_7C_int'),
    ScrapDef('0','LJ','scraping_LJ_dom'),
    ScrapDef('1','LJ','scraping_LJ_int'),
    ScrapDef('0','BX','scraping_BX_dom'),
    ScrapDef('1','BX','scraping_BX_int'),
    ScrapDef('0','ZE','scraping_ZE_dom'),
    ScrapDef('1','ZE','scraping_ZE_int'), ## 국내선, 국제선 동일 여부 체크
}