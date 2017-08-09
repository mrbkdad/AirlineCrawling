import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import logging
from common.util import json_loads,find_between
from common.log_util import log
from common.parsing_util import parsing_json_data_to_dict,mining_value_by_last_field_name
#from common.crawling_util import simple_crawling,session_crawling,jsonpayload_crawling

'''
크롤링 데이터 스크래핑 처리 함수
- 스크래핑 대상 파일 스크래핑 처리를 위한 함수 모음
- park363 2017-05-29 14:30
'''
## 인터파크
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_IP_dom(head,raw_data):
    ## raw_data 에러체크후 정상 파일 스크래핑 후 리스트 리턴
    log('start scraping Interpark crawled data')
    raw_json = json_loads(raw_data)#json.loads(raw_data)
    if raw_json is None: ## 파싱 에러
        return None
    if raw_json['replyHeader']['errorCode'] == '1': ## 에러
        print('## Error : crawling data not found!')
        return None
    loop_field = "['replyAvailFare']['availFareSet']"
    parse_info = {
        'airline':"['replyAvailFare']['availFareSet'][{}]['segFare']['carCode']",#i
        'date':"['replyAvailFare']['availFareSet'][{}]['segFare']['depDate']",#i
        'flt':"['replyAvailFare']['availFareSet'][{}]['segFare']['mainFlt']",#i
        'dpt':"['replyAvailFare']['availFareSet'][{}]['segFare']['depCity']",#i
        'dpt_time':"['replyAvailFare']['availFareSet'][{}]['segFare']['depTime']",#i
        'arr':"['replyAvailFare']['availFareSet'][{}]['segFare']['arrCity']",#i
        'arr_time':"['replyAvailFare']['availFareSet'][{}]['segFare']['arrTime']",#i
        'fare1':"['replyAvailFare']['availFareSet'][{}]['segFare']['classDetail'][0]['fare']",#i,j
        'fare2':"['replyAvailFare']['availFareSet'][{}]['segFare']['classDetail'][1]['fare']",#i,j+1
        'tax':"['replyAvailFare']['availFareSet'][{}]['segFare']['airTax']",#i
        'fuel':"['replyAvailFare']['availFareSet'][{}]['segFare']['fuelChg']",#i
        'seat1':"['replyAvailFare']['availFareSet'][{}]['segFare']['classDetail'][0]['noOfAvailSeat']",#i,j
        'seat2':"['replyAvailFare']['availFareSet'][{}]['segFare']['classDetail'][1]['noOfAvailSeat']",#i,j+1
    }

    parsed_list = parsing_json_data_to_dict(raw_json,loop_field, parse_info)
    if len(parsed_list) == 0:
        log('scraping data not found!',logging.WARNING)
        return None
    scraped_list = [[d['airline'],d['flt'],d['date'],d['dpt'],d['arr'],d['dpt_time'],d['arr_time'],
                      d['fare1'],d['fuel'],d['tax'],d['seat1']] for d in parsed_list ] +\
                    [[d['airline'],d['flt'],d['date'],d['dpt'],d['arr'],d['dpt_time'],d['arr_time'],
                      d['fare2'],d['fuel'],d['tax'],d['seat2']] for d in parsed_list ]
    log('end scraping Interpark crawled data')
    return scraped_list

def scraping_IP_int(head,raw_data):
    log('start scraping Interpark crawled data')
    raw_json = json_loads(raw_data)#json.loads(raw_data)
    if raw_json is None: ## 파싱 에러
        return None
    if type(raw_json['Responses']['GoodsList']) == str: ## 데이터가 없을 경우 체크
        return None
    raw_list = []
    fare_goods = raw_json['Responses']['GoodsList']['Goods']
    if type(fare_goods) == dict: ##데이터가 하나인 경우 방지용
        fare_goods = [fare_goods]
    for fare_set in fare_goods:
        air_itns = fare_set['AirAvail']['StartAvail']['AirItn']
        if type(air_itns) == dict: ##데이터가 하나인 경우 방지용
            air_itns = [air_itns]
        for air_itn in air_itns:
            seg_detail_t = air_itn['seg_detail_t']
            raw_list.append([seg_detail_t['car_code'],seg_detail_t['main_flt'],fare_set['StartDT'],
                             seg_detail_t['dep_city'],seg_detail_t['arr_city'],seg_detail_t['dep_date_time'][8:],
                             seg_detail_t['arr_date_time'][8:],fare_set['SaleFare'],fare_set['Qcharge'],
                             fare_set['Tax'],seg_detail_t['no_of_avail_seat']])
    log('end scraping Interpark crawled data')
    return raw_list
## 티웨이항공 - 국내선, 국제선 공통
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_TW_dom_int(head,raw_data):
    ## raw_data 에러체크후 정상 파일 스크래핑 후 리스트 리턴
    print('start scraping tway crawled data')
    soup = BeautifulSoup(raw_data,'lxml')
    scraped_list = []
    for tr in soup.select('#tbodyOnward tr'):
        td = tr.select('td')
        ## 편, 출도착 정보 가져오기
        flt_info = [f.text.split()[0].strip() for f in td[:3]]
        
        ## 스마트 운임 처리
        td_list = []
        td_list.append(head['airline'])             ## 대상항공사코드
        td_list.append(flt_info[0])                 ## 플라이트
        td_list.append(head['dpt_date'])            ## 출발일
        td_list.append(head['dpt'])                 ## 출발지
        td_list.append(head['arr'])                 ## 도착지
        td_list.append(flt_info[1].replace(':','')) ## 출발시간
        td_list.append(flt_info[2].replace(':','')) ## 도착시간
        ## 항공료, 유류세, 공항세를 가져온다.
        fares = [f.attrs['value'].split('.')[0] for f in td[4].select('input')
                 if f.attrs['type'] == 'hidden' and f.attrs['name'] in ['fare','surcharge','tax']]
        ## 좌석 체크 하여 매진인 경우 가격 0 처리
        soldout = td[4].select('.txt3')[0].select('.soldout')
        if len(soldout) == 0: #좌석이 많음
            td_list.extend(fares)
            td_list.append('9')
        else:
            soldout_txt = soldout[0].text.strip()
            if '매진' in soldout_txt: ## 매진
                td_list.extend(['0','0','0','0'])
            else:
                td_list.extend(fares)
                td_list.append(soldout_txt.replace('(','').replace('석','').replace(')',''))
        scraped_list.append(td_list)
        
        ## 일반 운임 처리
        td_list = []
        td_list.append(head['airline'])             ## 대상항공사코드
        td_list.append(flt_info[0])                 ## 플라이트
        td_list.append(head['dpt_date'])            ## 출발일
        td_list.append(head['dpt'])                 ## 출발지
        td_list.append(head['arr'])                 ## 도착지
        td_list.append(flt_info[1].replace(':','')) ## 출발시간
        td_list.append(flt_info[2].replace(':','')) ## 도착시간
        ## 항공료, 유류세, 공항세를 가져온다.
        fares = [f.attrs['value'].split('.')[0] for f in td[5].select('input') 
                 if f.attrs['type'] == 'hidden' and f.attrs['name'] in ['fare','surcharge','tax']]
        ## 좌석 체크 하여 매진인 경우 가격 0 처리
        soldout = td[5].select('.txt3')[0].select('.soldout')
        if len(soldout) == 0: #좌석이 많음
            td_list.extend(fares)
            td_list.append('9')
        else:
            soldout_txt = soldout[0].text.strip()
            if '매진' in soldout_txt: #매진
                td_list.extend(['0','0','0','0'])
            else:
                td_list.extend(fares)
                td_list.append(soldout_txt.replace('(','').replace('석','').replace(')',''))
        scraped_list.append(td_list)
    print('end scraping tway crawled data')
    return scraped_list

## 제주항공
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_7C_dom(head,raw_data):
    ## raw_data 에러체크후 정상 파일 스크래핑 후 리스트 리턴
    print('start scraping jejuair crawled data')
    loop_field = "['Result']['data']"
    parse_info = {
        'date':"['Result']['data'][{}]['depDate']",#i
        'flt':"['Result']['data'][{}]['fltNo']",#i
        'dpt':"['Result']['data'][{}]['depStn']",#i
        'arr':"['Result']['data'][{}]['arrStn']",#i
        'dpt_time':"['Result']['data'][{}]['depTime']",#i
        'arr_time':"['Result']['data'][{}]['arrTime']",#i
        'fare1':"['Result']['data'][{}]['specialEquivFare']",#i
        'fare2':"['Result']['data'][{}]['discountEquivFare']",#i
        'fare3':"['Result']['data'][{}]['normalEquivFare']",#i
        'seat1':"['Result']['data'][{}]['specialSeatCount']",#i
        'seat2':"['Result']['data'][{}]['discountSeatCount']",#i
        'seat3':"['Result']['data'][{}]['normalSeatCount']",#i
        'rbd1':"['Result']['data'][{}]['specialRBD']",#i
        'rbd2':"['Result']['data'][{}]['discountRBD']",#i
        'rbd3':"['Result']['data'][{}]['normalRBD']",#i
        'basis1':"['Result']['data'][{}]['specialEquivFareBasis']",#i
        'basis2':"['Result']['data'][{}]['discountEquivFareBasis']",#i
        'basis3':"['Result']['data'][{}]['fareBasis']",#i
    }
    raw_json = json.loads(raw_data)
    ## 읽어온 데이터의 json['Result']['code'] 값이 0000 이 아닌 경우 오류
    if raw_json['Result']['code'] != '0000':
        return None
    ## 기본 정보 읽어오기
    fare_list = parsing_json_data_to_dict(raw_json, loop_field, parse_info)
    ## 기본정보를 이용하여 유류세, 공항세 읽어와 리스트 생성
    scraped_list = []
    for fare_info in fare_list:
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare1']])
        if fare_info['fare1'] != '0':
            tax_info = crawling_7C_tax('1',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare1'],fare_info['rbd1'],fare_info['basis1'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat1'])
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare2']])
        if fare_info['fare2'] != '0':
            tax_info = crawling_7C_tax('2',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare2'],fare_info['rbd2'],fare_info['basis2'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat2'])
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare3']])
        if fare_info['fare3'] != '0':
            tax_info = crawling_7C_tax('3',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare3'],fare_info['rbd3'],fare_info['basis3'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat3'])
        scraped_list.append(td_list)
    print('end scraping jejuair crawled data')
    return scraped_list
def scraping_7C_int(head,raw_data):
    ## raw_data 에러체크후 정상 파일 스크래핑 후 리스트 리턴
    print('start scraping jejuair crawled data')
    loop_field = "['Result']['data']['availData']"
    parse_info = {
        'date':"['Result']['data']['availData'][{}]['depDate']",#i
        'flt':"['Result']['data']['availData'][{}]['fltNo']",#i
        'dpt':"['Result']['data']['availData'][{}]['depStn']",#i
        'arr':"['Result']['data']['availData'][{}]['arrStn']",#i
        'dpt_time':"['Result']['data']['availData'][{}]['depTime']",#i
        'arr_time':"['Result']['data']['availData'][{}]['arrTime']",#i
        'fare1':"['Result']['data']['availData'][{}]['specialEquivFare']",#i
        'fare2':"['Result']['data']['availData'][{}]['discountEquivFare']",#i
        'fare3':"['Result']['data']['availData'][{}]['normalEquivFare']",#i
        'seat1':"['Result']['data']['availData'][{}]['specialSeatCount']",#i
        'seat2':"['Result']['data']['availData'][{}]['discountSeatCount']",#i
        'seat3':"['Result']['data']['availData'][{}]['normalSeatCount']",#i
        'rbd1':"['Result']['data']['availData'][{}]['specialRBD']",#i
        'rbd2':"['Result']['data']['availData'][{}]['discountRBD']",#i
        'rbd3':"['Result']['data']['availData'][{}]['normalRBD']",#i
        'basis1':"['Result']['data']['availData'][{}]['specialEquivFareBasis']",#i
        'basis2':"['Result']['data']['availData'][{}]['discountEquivFareBasis']",#i
        'basis3':"['Result']['data']['availData'][{}]['fareBasis']",#i
    }
    raw_json = json.loads(raw_data)
    ## 읽어온 데이터의 json['Result']['code'] 값이 0000 이 아닌 경우 오류
    if raw_json['Result']['code'] != '0000':
        return None
    ## 기본 정보 읽어오기
    fare_list = parsing_json_data_to_dict(raw_json, loop_field, parse_info)
    ## 기본정보를 이용하여 유류세, 공항세 읽어와 리스트 생성
    scraped_list = []
    for fare_info in fare_list:
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare1']])
        if fare_info['fare1'] != '0':
            tax_info = crawling_7C_tax('1',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare1'],fare_info['rbd1'],fare_info['basis1'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat1'])
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare2']])
        if fare_info['fare2'] != '0':
            tax_info = crawling_7C_tax('2',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare2'],fare_info['rbd2'],fare_info['basis2'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat2'])
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare_info['flt'],fare_info['date'],fare_info['dpt'],fare_info['arr'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare3']])
        if fare_info['fare3'] != '0':
            tax_info = crawling_7C_tax('3',fare_info['dpt'],fare_info['arr'],fare_info['flt'],fare_info['date'],
                       fare_info['dpt_time'],fare_info['arr_time'],fare_info['fare3'],fare_info['rbd3'],fare_info['basis3'])
        else:
            tax_info = ['0','0']
        td_list.extend(tax_info)
        td_list.append(fare_info['seat3'])
        scraped_list.append(td_list)
    print('end scraping jejuair crawled data')
    return scraped_list
## 유류할증료, 공항세 읽어오기
def crawling_7C_tax(type_no,dpt,arr,flt,dpt_date,dpt_time,arr_time,fare,rbd,basis):
    return ['0','0'] ## 사이트 크롤없이 처리 할 수 있도록함, 방향 고민 필요??
    url = 'https://www.jejuair.net/jejuair/com/jeju/ibe/searchFareTax.do'
    head = {
        'Referer':'https://www.jejuair.net/jejuair/com/jeju/ibe/availInit.do',
    }
    param ={
        'DepDate':dpt_date+dpt_time,              'ArrDate':dpt_date+arr_time,
        'DepStn':dpt,        'ArrStn':arr,        'RBD':rbd,
        'FareBasis':basis,   'EquivFare':fare,    'FltNo':flt,
        'FareTypeNo':type_no,## 1 Special, 2 Discount,3 Normal
        'TripType':'OW',     'RouteType':'D', ## 국내선 국제선 구분
        'ReqType':'Price',        'AdultPaxCnt':'1',             'ChildPaxCnt':'0',
        'InfantPaxCnt':'0',       'Language':'KR',
        #'SystemType':'IBE'        #'depDesc':'서울(김포)',        #'arrDesc':'제주',
    }
    req = requests.post(url, param, headers=head)
    raw_tax = req.json()
    #print(raw_tax)
    return [raw_tax['Result']['data'][0]['farePriceTaxDataBeans'][0]['taxAmount'],
            raw_tax['Result']['data'][0]['farePriceTaxDataBeans'][1]['taxAmount']]
## 진에어
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_LJ_dom(head,raw_data):
    ## 읽어온 데이터의 json['Result']['code'] 값이 0000 이 아닌 경우 오류
    soup = BeautifulSoup(raw_data,'lxml')
    scraped_list = []
    data_fields = ['flt_x0023_','dep_date','dep_city','arr_city','dept','arrt','eamt','fuel_amt','tax_amt','e_avail']
    scraped_list.extend([[fare.find(f).text for f in data_fields] for fare in soup.select('ow')])
    data_fields = ['flt_x0023_','dep_date','dep_city','arr_city','dept','arrt','yamt','fuel_amt','tax_amt','y_avail']
    scraped_list.extend([[fare.find(f).text for f in data_fields] for fare in soup.select('ow')])
    return [['LJ',td[0][2:]]+td[1:] for td in scraped_list]
def scraping_LJ_int(head,raw_data):
    if head['dpt'].split('/')[1] == 'KOR': ##국내출발인 경우
        return scraping_LJ_int_kor(head,raw_data)
    else: ##현지출발인 경우
        return scraping_LJ_int_local(head,raw_data)

## 국내출발
def scraping_LJ_int_kor(head,raw_data):
    ## 읽어온 데이터중 필요한 JSON 데이터 부분 추출
    raw_json = raw_data.replace('\n','').replace(' ','').replace('\\"','')
    start_txt = 'plnextv2.utils.pageProvider.PlnextPageProvider.init({config:'
    end_txt = ',pageEngine'
    json_data = json.loads(find_between(raw_json,start_txt,end_txt))

    ## 플라이트 정보 생성
    try:
        raw_flight_info = json_data['pageDefinitionConfig']['pageData']['business']['Availability']['proposedBounds'][0]
        key_fields = ['proposedBoundId', 'beginDate','endDate','flightNumber']
    except Exception as e:
        ## 정보가 없을 경우
        print('****** No Record ******')
        return None
    flight_infos = mining_value_by_last_field_name(raw_flight_info, key_fields)

    ## 가격 정보 생성
    raw_fare_info = json_data['pageDefinitionConfig']['pageData']['business']['Availability']['recommendationList']
    fare_infos = {
        'flightId':[],
        'numberOfSeatsLeft':[],
        'ffCode':[],
        'amountWithoutTax':[],
        'totalAmount':[]
    }
    for fare_info in raw_fare_info:
        for flight_group in fare_info['bounds'][0]['flightGroupList']:
            ## 정보 추출
            fare_infos['flightId'].append(flight_group['flightId'])
            fare_infos['numberOfSeatsLeft'].append('1') ## 해당 정보 필드 삭제됨 ??
            #fare_infos['numberOfSeatsLeft'].append(flight_group['numberOfSeatsLeft'])
            fare_infos['ffCode'].append(fare_info['ffCode'])
            fare_infos['amountWithoutTax'].append(fare_info['recoAmount']['amountWithoutTax'])
            fare_infos['totalAmount'].append(fare_info['recoAmount']['totalAmount'])

    #return flight_infos, fare_infos
    ## proposedBoundId 와 flightId 기준으로 join
    df = pd.merge(pd.DataFrame(flight_infos),pd.DataFrame(fare_infos),left_on='proposedBoundId',right_on='flightId')
    ## 필요한 정보의 형태로 변경
    date_fmt = '%b%d,%Y%I:%M:%S%p'
    df['beginDate']=pd.to_datetime(df['beginDate'],format=date_fmt)
    df['endDate']=pd.to_datetime(df['endDate'],format=date_fmt)
    df['date'] = df['beginDate'].map(lambda x: x.strftime('%Y%m%d'))
    df['dpt_time'] = df['beginDate'].map(lambda x: x.strftime('%H%M'))
    df['arr_time'] = df['endDate'].map(lambda x: x.strftime('%H%M'))
    df['airline'] = head['airline']
    df['dpt'] = head['dpt']
    df['arr'] = head['arr']
    df['tax1'] = 0
    df['tax2'] = df['totalAmount'] - df['amountWithoutTax']
    heads_map = {
        'flightNumber':'flt',
        'amountWithoutTax':'fare',
        'numberOfSeatsLeft':'seat',
    }
    data_heads = ['airline','flt','date','dpt','arr','dpt_time','arr_time','fare','tax1','tax2','seat']
    df.rename(columns=heads_map,inplace=True)
    return [list(v) for v in df[data_heads].values]
## 현지출발
def scraping_LJ_int_local(head,raw_data):
    soup = BeautifulSoup(raw_data,'lxml')
    fare_infos = []
    for rows in soup.select("div#table"):
        if not rows.select("input")[0]['id'].startswith('rboFare'):
            break
        row = rows.select("td")
        info = []
        info.append(row[0].select('input')[0]['value'][:1])
        #info.append(row[1].select('span')[3].text)
        fare_data = row[-2].select('.btn_blue')[0]
        info.append(fare_data['data-fare'])
        info.append(fare_data['data-fuel'])
        info.append(fare_data['data-tax'])
        fare_infos.append(info)
    flt_info = json.loads(soup.select('#ctl00_ContentPlaceHolder1_hidDepartInfo')[0]['value'])
    fare_list = []
    for fare in fare_infos:
        for flt in flt_info:
            if flt[fare[0]] == 'Y':
                info = ['LJ']
                info.append(flt['flightNumber'])
                info.append(flt['arrivalDate'])
                info.append(flt['departureLocation'])
                info.append(flt['arrivalLocation'])
                info.append(flt['departureTime'])
                info.append(flt['arrivalTime'])
                info.extend(fare[1:])
                info.append(flt[fare[0]+'_Seat'])
                fare_list.append(info)
    return fare_list
## 에어부산
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_BX_dom(head,raw_data):
    raw_json = json.loads(raw_data)
    key_fields = ['depDate','flightNo','depCity','arrCity','depTime','arrTime',
                  'fareNetNormal','fareNormal','fuelAD','taxAD','availSeat']
    raw_dict = mining_value_by_last_field_name(raw_json,key_fields)
    scraped_list = []
    for i,td_date in enumerate(raw_dict['depDate']):
        if td_date != head['dpt_date']:
            continue
        scraped_list.append(['BX',raw_dict['flightNo'][i][2:],raw_dict['depDate'][i],
                             raw_dict['depCity'][i],raw_dict['arrCity'][i],raw_dict['depTime'][i],
                             raw_dict['arrTime'][i],raw_dict['fareNormal'][i],raw_dict['fuelAD'][i],
                             raw_dict['taxAD'][i],raw_dict['availSeat'][i]])
        if raw_dict['fareNetNormal'][i] != raw_dict['fareNormal'][i]:
            scraped_list.append(['BX',raw_dict['flightNo'][i][2:],raw_dict['depDate'][i],raw_dict['depCity'][i],
                                 raw_dict['arrCity'][i],raw_dict['depTime'][i],raw_dict['arrTime'][i],
                                 raw_dict['fareNetNormal'][i],raw_dict['fuelAD'][i],raw_dict['taxAD'][i],raw_dict['availSeat'][i]])
    return scraped_list
def scraping_BX_int(head,raw_data):
    data_heads = ['airline','flt','date','dpt','arr','dpt_date','arr_date','fare','tax1','tax2','seat']
    key_fields = ['flightNo','depTime','arrTime','priceAd','avail']
    raw_json = json.loads(raw_data)
    df_list = []
    for list_flight in raw_json['listFareIntAvail'][0]['listFlight']:
        df_dict = mining_value_by_last_field_name(list_flight,key_fields)
        max_len = max(len(d) for d in df_dict.values())
        for k,v in df_dict.items():
            if len(v) < max_len:
                df_dict[k] = fill_list(v,max_len,method='bfill')
        df = pd.DataFrame(df_dict,columns=key_fields)
        df.columns = ['flt','dpt_date','arr_date','fare','seat']
        df_list.append(df)
    result_df = pd.concat(df_list,ignore_index=True)
    result_df['airline'] = head['airline']
    result_df['dpt'] = head['dpt']
    result_df['arr'] = head['arr']
    result_df['date'] = raw_json['listFareIntAvail'][0]['depDate']
    result_df['tax1'] = raw_json['pubTaxFuel']['fuelAd']
    result_df['tax2'] = raw_json['pubTaxFuel']['taxAd']
    return [list(d) for d in result_df[data_heads].fillna(0.0).values]
## 이스타항공
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_ZE_dom_int(head,raw_data):
    raw_json = json.loads(raw_data)
    fare_info = []
    for trip in raw_json['result'][0]['resultData'][0]['FlightSearch']['trips'][0]:
        line = {
            'flt':trip['flightNumber'], ## trip['flightNumberText'],
            'dpt_time':trip['standardTimeOfDeparture'],
            'arr_time':trip['standardTimeOfArrival'],
            'fare1':0, ## 특가
            'fare2':0, ## 할인 - 해피패키지는 e_amount - 제외
            'fare3':0, ## 정상
            'sellkey1':'', ## 운임별 sellkey
            'sellkey2':'',
            'sellkey3':'',
            'sellkey':'',   ## 플라이트 구분 정보용 happySellKey 뒷부분
            'h_sellkey':'', ## 플라이트 구분 정보용 happySellKey 앞부분
            'flightSearchAuthKey':'',
        }
        if 'e_amount' in trip.keys():
            line['fare1'] = trip['e_amount']
        if 'd_amount' in trip.keys():
            line['fare2'] = trip['d_amount']
        if 'y_amount' in trip.keys():
            line['fare3'] = trip['y_amount']
        fare_info.append(line)
    scraped_list = []
    for fare in fare_info:
        td_list = []
        td_list.extend([head['airline'],fare['flt'],head['dpt_date'],head['dpt'],head['arr'],
                       fare['dpt_time'][8:12],fare['arr_time'][8:12],fare['fare1']])
        td_list.extend(crawling_ZE_tax())
        td_list.append('9')
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare['flt'],head['dpt_date'],head['dpt'],head['arr'],
                       fare['dpt_time'][8:12],fare['arr_time'][8:12],fare['fare2']])
        td_list.extend(crawling_ZE_tax())
        td_list.append('9')
        scraped_list.append(td_list)
        td_list = []
        td_list.extend([head['airline'],fare['flt'],head['dpt_date'],head['dpt'],head['arr'],
                       fare['dpt_time'][8:12],fare['arr_time'][8:12],fare['fare3']])
        td_list.extend(crawling_ZE_tax())
        td_list.append('9')
        scraped_list.append(td_list)
        
    return scraped_list

def crawling_ZE_tax():
    return ['2200','4000'] ## 사이트 크롤없이 처리 할 수 있도록함, 방향 고민 필요??
    ## 유류 정보 읽어오기 위한 파라미터값
    ## 추가 정보(유류세,공항세) 읽어올때 세션 정보를 유지하도록 하고 있어 이부분체크 필요, 일단 2200,4000 으로 세팅 처리
    ## 좌석수 정보도 일단 '9' 처리
    map_info = {
        "flightPriceInfo": '{"viewType":"","person1":"1","person2":"0","inFlightSearchAuthKey":"{flightSearchAuthKey}",' +
                '"happySellKey":"{h_sellkey}|{sellkey}","happyInternational":"N","cancelSellKeyList":[],' +
                '"selectedInfo":["{selected_sellkey}}|{sellkey}"]}'
    }
    map_info["flightPriceInfo"] = map_info["flightPriceInfo"].replace('flightSearchAuthKey',
                        'B1496025645912').replace('h_sellkey','0~Z~~ZNNDCH~3015~~1~X').replace('sellkey',
                        'ZE~ 225~ ~~GMP~06/14/2017 18:35~CJU~06/14/2017 19:45~').replace('selected_sellkey','0~Z~~ZNNDC1~3015~~1~X')

## Payload 구조
## map_info 예){"flightSearch":flight_parameter}
def get_ZE_payload(pid,rcode,fname,map_info):
    payLoad={
        "id": pid, "method": "DataService.service",
        "params": [{
            "javaClass": "com.jein.framework.connectivity.parameter.RequestParameter",
            "requestUniqueCode": rcode, "requestExecuteType": "BIZ",
            "DBTransaction": False, "sourceName": None, "sourceExtension": None,
            "functionName": fname, "panelId": None, "methodType": None,
            "inParameters": {
                "javaClass": "java.util.List",
                "list": [{
                    "javaClass": "com.jein.framework.connectivity.parameter.InParameter",
                    "paramName": "flightSearch", "ioType": "IN", "structureType": "FIELD",
                    "data": {
                        "javaClass": "java.util.List",
                        "list": [{
                            "map": map_info,
                            "javaClass": "java.util.Map"}]
                        }
                }]
            },
            "filterParameter": {"javaClass": "java.util.Map", "map": {}}
        }]
    }
    return payLoad
## 대한항공 - 국내선, 국제선 동일
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_KE_dom_int(head,raw_data):
    raw_json = json.loads(raw_data)
    ## 읽어온 데이터의 json['Result']['code'] 값이 0000 이 아닌 경우 오류
    sch_list = []
    for schedule in raw_json['outbound']:
        flt = schedule['flights'][0]
        fares = scraping_KE_fares_with_seat(schedule['key'],schedule['remainingSeatsByBookingClass'],raw_json)
        for fare in fares:
            sch = []
            sch.append(head['airline'])
            sch.append(flt['flightNumber'])
            sch.append(flt['departure'][:4]+flt['departure'][5:7]+flt['departure'][8:10])
            sch.append(flt['departureAirportCode'])
            sch.append(flt['destinationAirportCode'])
            sch.append(flt['departure'][11:16])
            sch.append(flt['arrival'][11:16])
            sch.extend(fare)
            ## ECONOMYY 클래스에 대한 좌석 수 추가 - 노멀 클래스
            ## sch.append(schedule['remainingSeatsByBookingClass'].get('ECONOMYY',0))
            sch_list.append(sch)
    return sch_list
def scraping_KE_fares_with_seat(fare_key,fare_class,raw_json):
    fare_list = []
    for cls,seat in fare_class.items():
        keys = raw_json['tripFareMapper'][fare_key+'-'+cls[:-1]]
        for key in keys:
            if cls[-1] == raw_json['fares'][key]['bookingClass']:
                fare = raw_json['fares'][key]['fares'][0]
                fare_list.append([fare['amount'],fare['fuelSurcharge'],fare['tax'],seat])
    return fare_list
## 아시아나
## 포맷 : 대상항공사코드,플라이트,출발일,출발지,도착지,출발시간,도착시간,가격,유류세,세금,좌석수
def scraping_OZ_dom_int(head,raw_data):
    ## json 형태로 변경 처리
    json_data = {'json_data':eval(raw_data.replace('true',"True").replace('false',"False"))}
    sch_list = []
    for line_data in json_data['json_data']:
        ## fare 정보 찾아
        #fare_data = line_data['fareFamilyAmounts'][0]['itineraryAvailDataOfRecommend']['paxTypeFareDatas'][0]
        ## flight 정보 찾아오기
        for family_info in line_data['fareFamilyAmounts']:
            fare_data = family_info['itineraryAvailDataOfRecommend']['paxTypeFareDatas'][0]
            for flt_info in family_info['itineraryAvailDataOfRecommend']['availDataList'][0]:
                sch = []
                flt_data = flt_info['flightInfoDatas'][0]
                ## flight 정보 추가
                sch.extend([flt_data['carrierCode'],flt_data['flightNo'],flt_data['departureDate'][:8],
                            flt_data['departureAirport'],flt_data['arrivalAirport'],
                            flt_data['departureDate'][8:12],flt_data['arrivalDate'][8:12]])
                ## fare 정보 추가
                sch.extend([fare_data['amountWithoutTax'],fare_data['fuelCharge'],fare_data['totalTax']])
                ## seat 정보 추가
                sch.append(flt_info['seatCount'] if flt_info['seatCount'] != '' else '0')
                sch_list.append(sch)
    return sch_list