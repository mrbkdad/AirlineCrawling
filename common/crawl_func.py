import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging
from common.log_util import log
from common.crawling_util import simple_crawling,session_crawling,jsonpayload_crawling, payload_crawling
'''
사이트 크롤링 함수
- 크롤링 대상 사이트 크롤링 처리를 위한 함수 모음
- park363 2017-05-26 09:14
'''
## 인터파크
def crawling_IP_dom(airline,dpt,arr,dpt_date):
    log('Crawling Interpark domastic schedule site')
    url = 'http://domair.interpark.com/api/booking/airJourney.do'
    param = {
        'format':'json',   # JSON 포맷
        'dep':dpt,         # 출발
        'arr':arr,         # 도착
        'depDate':dpt_date, # 출발일 yyyymmdd
        'airlineCode':airline, # 항공사 코드
        'tripDivi':'0',     #편도 왕복 구분 0 - 편도 1 - 왕복
        'adt':'1',
        'chd':'0',
        'inf':'0'
    }
    return simple_crawling(url,param,method='get',json=False)
def crawling_IP_int(airline,dpt,arr,dpt_date):
    log('Crawling Interpark domastic schedule site')
    url = "http://smartair.interpark.com/HtmlSearch/GetGoodsSmartList.aspx"
    param = {
        'FLEX':'N',         'Soto':'N',
        'ptype':'I',        'SeatAvail':'Y',
        'comp':'Y',         'JSON':'Y',
        'enc':'u',          'BEST':'Y',
        'Change':'',        'StayLength':'',
        'SeatType':'A',     'trip':'OW',            # 퍈도 왕복
        'adt':'1',         'chd':'0',        'inf':'0',
        'SplitNo':'100',        # 읽어올 데이터 사이즈
        'AirLine':airline,
        'dep0':dpt,             # 출발지
        'arr0':arr,             # 도착지
        'depdate0':dpt_date,    # 출발일
    }
    ## 문자 앞부분과 끝부분을 제외한 부분만 읽어오기 JSON 포맷 에러 발생
    return simple_crawling(url,param,method='get',json=False)[1:-1]
## 티웨이
def crawling_TW_dom(dpt,arr,dpt_date):
    return crawling_TW(dpt,arr,dpt_date,'Y')
def crawling_TW_int(dpt,arr,dpt_date):
    return crawling_TW(dpt,arr,dpt_date,'N')
def crawling_TW(dpt,arr,dpt_date,dom_int):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling twayair homepage schedule site')
    session_url = "https://www.twayair.com/booking/availabilityList.do"
    session_head = {
        'Referer':'https://www.twayair.com/main.do',
    }
    
    url = 'https://www.twayair.com/booking/ajax/searchAvailability.do'
    head = {
        'Referer':'https://www.twayair.com/booking/availabilityList.do',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    param ={
        'origin':dpt,                  'destination':arr,
        'origin1':dpt,                 'destination1':arr,
        'origin2':arr,                 'destination2':dpt,
        'onwardDateStr':dpt_date,      'returnDateStr':dpt_date,
        'today':datetime.today().strftime('%Y%m%d'),
        #'searchAvailId':searchAvailId,
        #'currencyCode':'KRW',          'pointOfPurchase':'KR',
        'travelType':'OW',#'RT',
        'domesticYn':dom_int, ## 국내선 'Y', 국제선'N'
        'paxTypeCountStr':'1,0,0',
        'searchType':'byDate',
        'orderByOW':'',               'orderByRT':'',
        'fareBasisCodeOW':'',         'fareBasisCodeRT':'',
        'arrivCntryCode':'',          'promotionCode':'',
    }
    return session_crawling(session_url,url,param,session_head=session_head,head=head,method='get',json=False)
# 제주항공
def crawling_7C_dom(dpt,arr,dpt_date):
    return crawling_7C(dpt,arr,dpt_date,'D')
def crawling_7C_int(dpt,arr,dpt_date):
    return crawling_7C(dpt,arr,dpt_date,'I')
def crawling_7C(dpt,arr,dpt_date,dom_int):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling jejuair homepage schedule site')
    session_url = "https://www.jejuair.net/jejuair/com/jeju/ibe/availInit.do"
    session_head = {
        'Referer':'http://www.jejuair.net/jejuair/main.jsp',
    }
    
    url = 'https://www.jejuair.net/jejuair/com/jeju/ibe/searchAvail.do'
    head = {
        'Referer':'https://www.jejuair.net/jejuair/com/jeju/ibe/availInit.do',
    }
    param ={
        'AdultPaxCnt':'1',
        'ChildPaxCnt':'0',
        'InfantPaxCnt':'0',
        'RouteType':dom_int,  ## 국내선 D, 국제선 I
        'SystemType':'IBE',
        'Language':'KR',
        'DepStn':dpt,
        'ArrStn':arr,
        'SegType':'DEP',
        'TripType':'OW',
        'DepDate':dpt_date,
        'Index':'1' # 국제선용
    }
    return session_crawling(session_url,url,param,session_head=session_head,head=head,method='post',json=False)
## 진에어
def crawling_LJ_dom(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling jinair homepage schedule site')
    url = "https://www.jinair.com/RSV/RSV_WebResult.aspx"
    head = {
        'Referer':'https://www.jinair.com/RSV/Reservation.aspx',
    }
    param ={
        'TASK':'NormalFare',
        'OWListId':'ctl00_ContentPlaceHolder1_fltlstDownLine',
        'OWDepDate':dpt_date,
        'OWDep':dpt,
        'OWArr':arr,
        'MemberClass':'I',
        'DisCode':'',
        'MbrGb':'N'
    }
    payload = '<REQUEST><TASK>{TASK}</TASK><OWListId>{OWListId}</OWListId><OWDepDate>{OWDepDate}</OWDepDate>'
    payload += '<OWDep>{OWDep}</OWDep><OWArr>{OWArr}</OWArr><MemberClass>{MemberClass}</MemberClass>'
    payload += '<DisCode>{DisCode}</DisCode><MbrGb>{MbrGb}</MbrGb></REQUEST>'

    return payload_crawling(url,payload.format(**param),head=head,method='post',json=False)
## 출도착지 코드 형식 준수, 날짜 형식 준수
def crawling_LJ_int(dpt,arr,dpt_date):
    if dpt.split('/')[1] == 'KOR': ##국내출발인 경우
        return crawling_LJ_int_kor(dpt,arr,dpt_date)
    else: ##현지출발인 경우
        return crawling_LJ_int_local(dpt,arr,dpt_date)
## 국내출발인 경우 
def crawling_LJ_int_kor(dpt,arr,dpt_date):
    print('Crawling jinair homepage schedule site')
    print('Param : ',dpt,arr,dpt_date)
    today = datetime.today().strftime('%Y-%m-%d')
    ## 국제선 예매사이트 1차 접속
    url = 'https://www.jinair.com/bookflight/flightSearch.aspx'
    head = {
        'Referer':'https://www.jinair.com/bookflight/flightSearch.aspx',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    sess = requests.Session()
    req = sess.get(url,headers=head)
    soup = BeautifulSoup(req.text,'lxml')

    ## 국제선 예매사이트 viewstate 값얻기 위한 2차 접속, 출발지 선택시 웹페이지에서 호출됨
    param = {
        'ctl00$ScriptManager1':'ctl00$ContentPlaceHolder$UpdatePanel7|ctl00$ContentPlaceHolder$ddlGDeparture',
        '__EVENTTARGET':'ctl00$ContentPlaceHolder$ddlGDeparture',
        '__EVENTARGUMENT':'',
        '__LASTFOCUS':'',
        '__VIEWSTATE':soup.select('#__VIEWSTATE')[0]['value'],
        '__VIEWSTATEGENERATOR':'52375EB0',
        'ctl00$ContentPlaceHolder$rdoItnerary':'2',
        'ctl00$ContentPlaceHolder$ddlGDeparture':dpt,
        'ctl00$ContentPlaceHolder$ddlCDeparture':'',
        'ctl00$ContentPlaceHolder$txtFrom':today,  ## today로 처리
        'ctl00$ContentPlaceHolder$txtTo':today,
        'ctl00$ContentPlaceHolder$ddlAdult':'1',
        'ctl00$ContentPlaceHolder$ddlChild':'0',
        'ctl00$ContentPlaceHolder$ddlInfant':'0',
        'ctl00$ContentPlaceHolder$SearchType':'rdoSchedule',
        'BDC_VCID_c_bookflight_flightsearch_ctl00_contentplaceholder_debotcaptcha':'05038f944aa44d53996721b3b81476fe',
        'BDC_BackWorkaround_c_bookflight_flightsearch_ctl00_contentplaceholder_debotcaptcha':'1',
        'ctl00$ContentPlaceHolder$txtCaptchaCode':'',
        'ctl00$ContentPlaceHolder$hdnDriven':'F',
        'ctl00$ContentPlaceHolder$hdnIsCharterIssue':'',
        'ctl00$ContentPlaceHolder$hdnDepRgnName':'/한국/한국//한국//동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//동남아//중국/중국/중국/중국//중국//일본/일본/일본/일본/일본//일본//대양주//대양주//미주',
        'ctl00$ContentPlaceHolder$hdnArrRgnName':'/중국/중국',
        'ctl00$ContentPlaceHolder$hdnRequestVerifyToken':'',
        'ctl00$ContentPlaceHolder$hdCorpCode':'',
        'ctl00$ContentPlaceHolder$hdPromoCode':'',
        'ctl00$ContentPlaceHolder$hdTcpCnt':'',
    }
    req = sess.post(url,param,headers=head)
    soup = BeautifulSoup(req.text,'lxml')

    ## 국제선 예매사이트 최종 검색 1단계 진행
    param = {
        '__EVENTTARGET':'ctl00$ContentPlaceHolder$ibtnNextStep',
        '__EVENTARGUMENT':'',
        '__LASTFOCUS':'',
        '__VIEWSTATE':soup.select('#__VIEWSTATE')[0]['value'],
        '__VIEWSTATEGENERATOR':'52375EB0',
        'ctl00$ContentPlaceHolder$rdoItnerary':'1',
        'ctl00$ContentPlaceHolder$ddlGDeparture':dpt,
        'ctl00$ContentPlaceHolder$ddlCDeparture':arr,
        'ctl00$ContentPlaceHolder$txtFrom':dpt_date,  ## 검색 날짜
        'ctl00$ContentPlaceHolder$txtTo':'',
        'ctl00$ContentPlaceHolder$ddlAdult':'1',
        'ctl00$ContentPlaceHolder$ddlChild':'0',
        'ctl00$ContentPlaceHolder$ddlInfant':'0',
        'ctl00$ContentPlaceHolder$SearchType':'rdoSchedule',
        'BDC_VCID_c_bookflight_flightsearch_ctl00_contentplaceholder_debotcaptcha':'05038f944aa44d53996721b3b81476fe',
        'BDC_BackWorkaround_c_bookflight_flightsearch_ctl00_contentplaceholder_debotcaptcha':'1',
        'ctl00$ContentPlaceHolder$txtCaptchaCode':'',
        'ctl00$ContentPlaceHolder$hdnDriven':'F',
        'ctl00$ContentPlaceHolder$hdnIsCharterIssue':'',
        'ctl00$ContentPlaceHolder$hdnDepRgnName':'/한국/한국//한국//동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//동남아//중국/중국/중국/중국//중국//일본/일본/일본/일본/일본//일본//대양주//대양주//미주',
        'ctl00$ContentPlaceHolder$hdnArrRgnName':'/동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//동남아//중국//중국//일본/일본/일본/일본/일본//일본//대양주//대양주//미주',
        'ctl00$ContentPlaceHolder$hdnRequestVerifyToken':'',
        'ctl00$ContentPlaceHolder$hdCorpCode':'',
        'ctl00$ContentPlaceHolder$hdPromoCode':'',
        'ctl00$ContentPlaceHolder$hdTcpCnt':'',
    }
    req = sess.post(url,param,headers=head)
    #soup = BeautifulSoup(req.text,'lxml')

    ## 신규 창 생성
    url = 'https://www.jinair.com/BookFlight/BookingProcess.aspx'
    req = sess.get(url,headers=head)

    ## 다른 URL 로 이동
    url = 'https://www.jinair.com/BookFlight/FlightSearchBridge.aspx'
    head = {
        'Referer':'https://www.jinair.com/BookFlight/BookingProcess.aspx',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    req = sess.get(url,headers=head)
    soup = BeautifulSoup(req.text,'lxml')

    ## 파라미터 생성
    param = {}
    inputs = soup.select('input')
    for field in inputs:
        param[field['id']] = field['value']
    target_url = param.get('hdnFormAction','post')
    target_method = param.get('hdnFormMethod','https://wftc3.e-travel.com/plnext/jinairDX/Override.action')
    #target_url = param['hdnFormAction']
    #target_method = param['hdnFormMethod']

    head = {
        'Referer':'https://www.jinair.com/BookFlight/FlightSearchBridge.aspx',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    req = sess.post(target_url,param,headers=head)
    print('End crawling')
    return req.text
## 현지 출발인 경우 모바일 사이트 이용, currency 는 현지 기본 통화로 처리
def crawling_LJ_int_local(dpt,arr,dpt_date):
    print('Crawling jinair mobile page schedule site')
    print('Param : ',dpt,arr,dpt_date)
    today = datetime.today().strftime('%Y-%m-%d')
    ## 영문페이지 접속 세션 생성
    url = 'https://m.jinair.com/MobileWeb/Default.aspx?Language=ENG|USD'
    head = {
        #'Referer':'https://m.jinair.com/RSV/BookingIntro.aspx?Language=KOR|KRW&IsMobileWeb=Y',
        'Referer':'https://m.jinair.com/MobileWeb/Default.aspx?Language=KOR|KRW',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    sess = requests.Session()
    req = sess.get(url,headers=head)
    ## 국제선 예매사이트 1차 접속
    url = 'https://m.jinair.com/RSVInternational/BookingStep01.aspx?IsMobileWeb=Y'
    head = {
        #'Referer':'https://m.jinair.com/RSV/BookingIntro.aspx?Language=KOR|KRW&IsMobileWeb=Y',
        'Referer':'https://m.jinair.com/RSV/BookingIntro.aspx?Language=ENG|USD&IsMobileWeb=Y',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    #sess = requests.Session()
    req = sess.get(url,headers=head)
    soup = BeautifulSoup(req.text,'lxml')
    ## 국제선 예매사이트 viewstate 값얻기 위한 2차 접속, 출발지 선택시 웹페이지에서 호출됨
    head = {
        'Referer':'https://m.jinair.com/RSVInternational/BookingStep01.aspx?IsMobileWeb=Y',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    param = {
        'ctl00$ScriptManager1':'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$ddlGDeparture',
        '__EVENTTARGET':'ctl00$ContentPlaceHolder1$ddlGDeparture',
        '__EVENTARGUMENT':'',
        '__LASTFOCUS':'',

        '__VIEWSTATE':soup.select('#__VIEWSTATE')[0]['value'],
        '__VIEWSTATEGENERATOR':'F0ABB8D1',
        'ctl00$ContentPlaceHolder1$rblItinerary':'OW',
        'ctl00$ContentPlaceHolder1$ddlGDeparture':dpt,
        'ctl00$ContentPlaceHolder1$ddlCDeparture':'',
        'ctl00$ContentPlaceHolder1$wdcDepDate':today,## today로 처리
        'ctl00$ContentPlaceHolder1$wdcArrDate':today,
        'ctl00$ContentPlaceHolder1$ddlAdult':'1',
        'ctl00$ContentPlaceHolder1$ddlChild':'0',
        'ctl00$ContentPlaceHolder1$ddlInfant':'0',
        'ctl00$ContentPlaceHolder1$hdnDepRgnName':'/Korea/Korea/Korea//Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia//China/China/China/China/China//Japan/Japan/Japan/Japan/Japan/Japan//Oceania/Oceania//America',
        'ctl00$ContentPlaceHolder1$hdnArrRgnName':'/Korea',
        #'ctl00$ContentPlaceHolder1$hdnDepRgnName':'/한국/한국/한국//동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//중국/중국/중국/중국/중국//일본/일본/일본/일본/일본/일본//대양주/대양주//미주',
        #'ctl00$ContentPlaceHolder1$hdnArrRgnName':'/동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//중국/중국//일본/일본/일본/일본/일본/일본//대양주/대양주/대양주//미주',
        'ctl00$ContentPlaceHolder1$hdnDepDate':today,
        'ctl00$ContentPlaceHolder1$hdnArrDate':'',
        '__ASYNCPOST':'true',
    }
    req = sess.post(url,param,headers=head)
    #soup = BeautifulSoup(req.text,'lxml')
    hiddenfields = req.text.split()[-1].split('|')
    ## 국제선 예매사이트 최종 검색 단계 진행
    param = {
        '__EVENTTARGET':'ctl00$ContentPlaceHolder1$btnNext',
        '__EVENTARGUMENT':'',
        '__LASTFOCUS':'',
        '__VIEWSTATE':hiddenfields[hiddenfields.index('__VIEWSTATE')+1],
        '__VIEWSTATEGENERATOR':'F0ABB8D1',
        'ctl00$ContentPlaceHolder1$rblItinerary':'OW',
        'ctl00$ContentPlaceHolder1$ddlGDeparture':dpt,
        'ctl00$ContentPlaceHolder1$ddlCDeparture':arr,
        'ctl00$ContentPlaceHolder1$wdcDepDate':dpt_date,  ## 검색 날짜
        'ctl00$ContentPlaceHolder1$ddlAdult':'1',
        'ctl00$ContentPlaceHolder1$ddlChild':'0',
        'ctl00$ContentPlaceHolder1$ddlInfant':'0',
        'ctl00$ContentPlaceHolder1$hdnDepRgnName':'/Korea/Korea/Korea//Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia/Southeast Asia//China/China/China/China/China//Japan/Japan/Japan/Japan/Japan/Japan//Oceania/Oceania//America',
        'ctl00$ContentPlaceHolder1$hdnArrRgnName':'/Korea',
        #'ctl00$ContentPlaceHolder1$hdnDepRgnName':'/한국/한국/한국//동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아/동남아//중국/중국/중국/중국/중국//일본/일본/일본/일본/일본/일본//대양주/대양주//미주',
        #'ctl00$ContentPlaceHolder1$hdnArrRgnName':'/한국',
        'ctl00$ContentPlaceHolder1$hdnDepDate':dpt_date,
        'ctl00$ContentPlaceHolder1$hdnArrDate':'',
    }
    req = sess.post(url,param,headers=head)
    ## 다음 페이지 이동 필요 없음??
    #url = 'https://m.jinair.com/RSVInternational/BookingStep02.aspx?IsMobileWeb=Y'
    #req = sess.get(url,headers=head)
    print('End crawling')
    return req.text
## 에어부산
def crawling_BX_dom(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling airbusan homepage schedule site')
    url = "https://www.airbusan.com/web/bookingApi/domesticAvail"
    head = {
        'Referer':'https://www.airbusan.com/web/individual/booking/domestic',
    }
    param ={
    'depDate':dpt_date,
    'depCity':dpt,
    'arrCity':arr,
    'bookingCategory':'Individual',
    'foc':'N',
    'bookingClass':'ES'
    }

    return simple_crawling(url,param,head=head,method='get',json=False)
def crawling_BX_int(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    print('Crawling airbusan homepage schedule site')
    url = "https://www.airbusan.com/web/bookingApi/internationalOnewayAvail"
    head = {
        'Referer':'https://www.airbusan.com/web/individual/booking/international',
    }
    param ={## depDate 포맷 체크 필요 YYYY-MM-DD
    'jsonString':'{"bookingCategory":"Individual","tripType":"OW","listItinerary":\
    [{"itinNo":"1","depCity":"'+dpt+'","arrCity":"'+arr+'","depDate":"'+dpt_date+'","itineraryType":"Going"}],\
    "focYN":"N","openReturnYN":"","paxCountCorp":0,"paxCountAd":1,"paxCountCh":0,"paxCountIn":0,"itinNo":"1"}'
    }

    return simple_crawling(url,param,head=head,method='post',json=False)
## 이스타항공
def get_ZE_payload(flightSearch):
    payLoad={
        "id": 2, "method": "DataService.service",
        "params": [{
            "javaClass": "com.jein.framework.connectivity.parameter.RequestParameter",
            "requestUniqueCode": "PGWBA00002", "requestExecuteType": "BIZ",
            "DBTransaction": False, "sourceName": None, "sourceExtension": None,
            "functionName": "DTWBA00022", "panelId": None, "methodType": None,
            "inParameters": {
                "javaClass": "java.util.List",
                "list": [{
                    "javaClass": "com.jein.framework.connectivity.parameter.InParameter",
                    "paramName": "flightSearch", "ioType": "IN", "structureType": "FIELD",
                    "data": {
                        "javaClass": "java.util.List",
                        "list": [{
                            "map": {
                                "flightSearch": flightSearch
                            },
                            "javaClass": "java.util.Map"}]
                        }
                }]
            },
            "filterParameter": {"javaClass": "java.util.Map", "map": {}}
        }]
    }
    return payLoad
def crawling_ZE_dom_int(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling eastarjet homepage schedule site')
    session_url = "https://www.eastarjet.com/newstar/PGWBA00001"
    session_head = {
        'Referer':'https://www.eastarjet.com/newstar/PGWBA00001',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    sess = requests.Session()
    sess.get(session_url,headers=session_head)
    time.sleep(1) ## 1초가 지연 처리    
    url = 'https://www.eastarjet.com/json/dataService'
    head = {
        'Referer':'https://www.eastarjet.com/newstar/PGWBA00002',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }

    flightSearch='{"viewType":"","fly_type":"2","person1":"1","person2":"0","person3":"0",\
    "residentCountry":"KR","currency":"","promotion_cd":"",\
    "flySection":[{"departure_cd":"{departure_cd}","arrival_cd":"{arrival_cd}","departure_date_cd":"{departure_date_cd}"}]}'
    #req = requests.post(url,json=payload,headers=head)
    payload = get_ZE_payload(flightSearch.replace('{departure_cd}',dpt).replace('{arrival_cd}',arr).replace('{departure_date_cd}',dpt_date))
    return jsonpayload_crawling(url, payload, session=sess, head=head, method='post', json=False)
## 대한항공
def crawling_KE_dom(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    log('Crawling koreanair homepage schedule site')
    session_url = "https://www.koreanair.com/korea/ko/booking/booking-gate.html#bookingChange"
    session_head = {
        'Referer':'https://kr.koreanair.com/korea/ko.html',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    
    ## Rest Full 방식 https://www.koreanair.com/api/fly/revenue/from/GMP/to/CJU/on/05-25-2017-0000
    url = "https://www.koreanair.com/api/fly/revenue/from/{dpt}/to/{arr}/on/{mm}-{dd}-{yyyy}-0000"
    url_param = {
        'dpt':dpt,    'arr':arr,
        'yyyy':dpt_date[:4],
        'mm':dpt_date[4:6],
        'dd':dpt_date[6:]
    }
    url = url.format(**url_param)
    head = {
        'page-id':'/booking/dow.html', ## 필수 항목
        'uidd':'83^51%8638461@384712', ## 필수 항목
        'Referer':'https://www.koreanair.com/korea/ko/booking/dow.html',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    param ={## 파라미터는 고정, _ 부분만 조회 시점 타임스탬프 적용
        'flexDays':'2',
        'scheduleDriven':'false',
        'purchaseThirdPerson':'',
        'domestic':'true',
        'isUpgradeableCabin':'false',
        'adults':'1',    'children':'0',    'infants':'0',
        'cabinClass':'ECONOMY',
        'adultDiscounts':'',    'adultInboundDiscounts':'',
        'childDiscounts':'',    'childInboundDiscounts':'',
        'infantDiscounts':'',   'infantInboundDiscounts':'',
        '_':str(int(datetime.now().timestamp())),
    }
    return session_crawling(session_url,url,param,session_head=session_head,head=head,method='get',json=False)
def crawling_KE_int(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    print('Crawling koreanair homepage schedule site')
    session_url = "https://www.koreanair.com/korea/ko/booking/booking-gate.html?intl#international"
    session_head = {
        'Accept-Language':'ko-KR',
        'Referer':'https://www.koreanair.com/korea/ko.html',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    
    '''
    session_url = "https://www.koreanair.com/korea/ko/booking/xiow.html"
    session_head = {
        'Referer':'https://www.koreanair.com/korea/ko/booking/booking-gate.html?intl',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    '''
    ## Rest Full 방식 https://www.koreanair.com/api/fly/revenue/from/ICN/to/NRT/on/06-15-2017-0000
    url = "https://www.koreanair.com/api/fly/revenue/from/{dpt}/to/{arr}/on/{mm}-{dd}-{yyyy}-0000"
    url_param = {
        'dpt':dpt,    'arr':arr,
        'yyyy':dpt_date[:4],
        'mm':dpt_date[4:6],
        'dd':dpt_date[6:]
    }
    url = url.format(**url_param)
    head = {
        'Accept-Language':'ko-KR', ## 중요, 영문사이트는 capcha 를 요구함
        'page-id':'/booking/xiow.html', ## 필수 항목
        'uidd':'83^51%8638461@384712',  ## 필수 항목
        'Referer':'https://www.koreanair.com/korea/ko/booking/xiow.html',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    param ={## 파라미터는 고정, _ 부분만 조회 시점 타임스탬프 적용
        'flexDays':'0',    'scheduleDriven':'false',
        'purchaseThirdPerson':'',
        'domestic':'false','isUpgradeableCabin':'false',
        'currency':'',     'bonusType':'SKYPASS',
        'countryCode':'',
        'adults':'1',    'children':'0',    'infants':'0',
        'cabinClass':'ECONOMY',
        'adultDiscounts':'',    'adultInboundDiscounts':'',
        'childDiscounts':'',    'childInboundDiscounts':'',
        'infantDiscounts':'',   'infantInboundDiscounts':'',
        '_':str(int(datetime.now().timestamp())),
    }

    return session_crawling(session_url,url,param,session_head=session_head,head=head,method='get',json=False)
## 아시아나
def crawling_OZ_dom(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    print('Crawling asiana homepage schedule site')
    url = "https://flyasiana.com/I/ko/RevenueDomesticFareDrivenFlightSelect.do"
    head = {
        'Referer':'https://flyasiana.com/I/ko/RevenueDomesticTravelRegist.do',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    param ={
        'hidPageType':'',      'departureAirportC':'',
        'arrivalAirportC':'',  'departureDateC':'',
        'arrivalDateC':'',     'officeId':'',
        'entType':'',          'corporateCode':'',
        'couponDesc':'',       'cServiceType':'',
        'couponCode':'',       'query':'',
        'CallPage':'RevenueDomesticTravelRegist',
        #'sessionUniqueKey':'ec5fd537-302d-48f0-fee5-f4b649026ecf',
        'domIntType':'D',               'tripType':'OW',
        'departureAirport':dpt,       'arrivalAirport':arr,
        'openDepartureAirport1':dpt,  'openArrivalAirport1':arr,
        'openDepartureAirport2':arr,  'openArrivalAirport2':dpt,
        'departureDate':dpt_date,   'arrivalDate':dpt_date,
        '__strSDate':dpt_date,      '__strEDate':dpt_date,
        'adultCount':'1',      'childCount':'0',
        'infantCount':'0',     'ageCalYear':'2017',
        'ageCalMonth':'1',     'ageCalDay':'0',    
    }

    raw_text = simple_crawling(url,param,head=head,method='post',json=False)
    start_txt = "var depFareFamilyWithAllAvail = eval('"
    end_txt = "');"
    return find_between(raw_text,start_txt,end_txt)
def crawling_OZ_int(dpt,arr,dpt_date):
    ##출발지, 도착지, 출발일을 기준으로 국내선(국제선) 편도 가격 읽어오기
    print('Crawling asiana homepage schedule site')
    url = "https://flyasiana.com/I/ko/RevenueInternationalFareDrivenFlightSelect.do"
    head = {
        'Referer':'https://flyasiana.com/I/ko/RevenueInternationalFareDrivenCalendarSelect.do',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    param ={
        'hidPageType':'',           'domIntType':'I',
        'tripType':'OW',            'departureAirportC':'',
        'arrivalAirportC':'',       'departureDateC':'',
        'arrivalDateC':'',          'openDepartureAirportC':'',
        'openArrivalAirportC':'',   'multiSegInfo':'',
        #'sessionUniqueKey:a8c45052-bbf9-4d67-9c66-bd4614ed034b
        'officeId':'',              'entType':'',
        'corporateCode':'',         'couponDesc':'',
        'cServiceType':'',          'couponCode':'',
        'query':'',
        'departureArea':'KR',       'departureAirport':dpt,
        'arrivalArea':'JP',         'arrivalAirport':arr,
        'departureDate':dpt_date,#'2017-06-15',
        'adultCount':'1',     'childCount':'0',     'infantCount':'0',
        'ageCalYear':'2017',  'ageCalMonth':'1',    'ageCalDay':'0',
        'cabinClass':'T',     'fareViewType':'L',
    }

    text = simple_crawling(url,param,head=head,method='post',json=False)
    start_txt = "var fareFamilyWithAllAvail = eval('"
    end_txt = "');"
    return find_between(text,start_txt,end_txt)