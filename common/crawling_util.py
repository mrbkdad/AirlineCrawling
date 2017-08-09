import requests
import urllib
import time

_user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'

def print_param(param):
    print('>> Parameters')
    for k,v in param.items():
        print('{}:{}'.format(k,v),end=' , ')
    print()
    
## 기본 크롤링 유틸
def simple_crawling(url, param, head=None, method='get', json=False):
    print('Start Simple crawling : ', url)
    print_param(param)
    if head is None:
        head = {
            'User-Agent':_user_agent
        }
    if method == 'get':
        req = requests.get(url+'?'+urllib.parse.urlencode(param),headers=head)
        #req = requests.get(url,param,headers=head)
    else:
        req = requests.post(url,param,headers=head)
    ## request error 혹은 결과가 올바르지 않을 경우 처리 로직 추가??(3회 반복 후 리턴??)
    print('End Simple crawling')
    if json:
        return req.json()
    else:
        return req.text
    
## session 정보 필요한 형태 크롤링 유팅
def session_crawling(session_url,url,param,payload=False, 
                     session_head=None,head=None,method='get',json=False):
    print('Start Session crawling')
    print('make session : ', session_url)
    sess = requests.Session()
    if session_head is None:
        session_head = {
            'User-Agent':_user_agent
        }
    print('crawling : ',url)
    print_param(param)
    req = sess.get(session_url,headers=session_head)
    time.sleep(1) ## 처리중 지연 현상 처리를 위해 1초간 sleep
    if head is None:
        head = {
            'User-Agent':_user_agent
        }
    if method == 'get':
        req = sess.get(url+'?'+urllib.parse.urlencode(param),headers=head)
    else:
        req = sess.post(url,param,headers=head)
    ## request error 혹은 결과가 올바르지 않을 경우 처리 로직 추가??(3회 반복 후 리턴??)
    print('End Session crawling')
    if json:
        return req.json()
    else:
        return req.text
    
## param 형태가 JSON 이외의 형태로 전달하는 경우
## payload : str
## 세션을 유지하며 처리 하기 위해 sess 전달 받음, 만약 필요 없을 경우 None 전달
def payload_crawling(url, payload, session=None, head=None, method='post', json=False):
    print('Start Payload crawling : ', url)
    print('payload : ', payload)
    if session is None:
        session = requests
    if head is None:
        head = {
            'User-Agent':_user_agent
        }
    if method == 'get':
        req = session.get(url+'?'+urllib.parse.urlencode(param),headers=head)
    else:
        req = session.post(url,data=payload,headers=head)
    ## request error 혹은 결과가 올바르지 않을 경우 처리 로직 추가??(3회 반복 후 리턴??)
    print('End Payload crawling')
    if json:
        return req.json()
    else:
        return req.text

## param 형태가 JSON 형태로 전달하는 파라미터는 DICT를 받아 내부적으로 JSON 변환 하여 전달하는 경우
## paload : DICT
## 세션을 유지하며 처리 하기 위해 sess 전달 받음, 만약 필요 없을 경우 None 전달
def jsonpayload_crawling(url, payload, session=None, head=None, method='post', json=False):
    print('Start Json Payload crawling : ', url)
    print_param( payload)
    if session is None:
        session = requests
    if head is None:
        head = {
            'User-Agent':_user_agent
        }
    if method == 'get':
        req = session.get(url+'?'+urllib.parse.urlencode(param),headers=head)
    else:
        req = session.post(url,json=payload,headers=head)
    ## request error 혹은 결과가 올바르지 않을 경우 처리 로직 추가??(3회 반복 후 리턴??)
    print('End Json Payload crawling')
    if json:
        return req.json()
    else:
        return req.text
