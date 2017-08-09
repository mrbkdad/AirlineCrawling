import os
import shutil
import logging
import json
import copy
from json import JSONDecodeError
from common.log_util import log

## Series 에서 0을 제외한 가장 작은 값을 찾아준다.
def series_chk_min(s):
    return top_n(s.values,top=2)
    #for v in sorted(row.values):
    #    if v > 0:
    #        return v
    #return v

## Iterable 에서 상위 n 번째 값, 중복된 값 제외한 결과 리턴
def top_n(iterable,top=1,unique=True,reverse=False):
    sorted_i = sorted(iterable,reverse=reverse)
    result_num = sorted_i[0]
    check_num = 0
    for e in sorted_i[1:]:
        if not unique:
            check_num += 1
        elif result_num != e:
            check_num += 1
        if check_num == top:
            break
        result_num = e
    return result_num

## numpy ndarray 를 지정한 축에 따른 평균값을 뺀 array 리턴
def demean_axis(arr,axis=0):
    means = arr.mean(axis)
    # [:,:,np.newaxis] : 일반화 시키는 과정
    indexer = [slice(None)] * arr.ndim
    indexer[axis] = np.newaxis
    return arr - means[indexer]


## list를 length 크기로 변경, 변경시 list 가 None 거나 len이 0 이면 None 리스트 리턴
## method가 ffill이면 리스트뒤로 마지막 값을 가지고 채우며
## bfill 이면 리스트 앞으로 처음 값을 가지고 채운다.
## length 가 list 보다 적으면 그대로 리턴한다.
def fill_list(src_list,length,method=None):
    if src_list is None or len(src_list) == 0:
        return [None] * length
    elif len(src_list) < length:
        if method == None:
            fill_value = None
        elif method == 'bfill':
            fill_value = src_list[-1]
        elif method == 'ffill':
            fill_value = src_list[0]
        fill_list = [fill_value] * (length - len(src_list))
        if method is None or method == 'bfill':
            return src_list + fill_list
        elif method =='ffill':
            return fill_list + src_list
    return src_list[:]

# 사이 문자열 잘라내기
def find_between( s, first, last ):
    start = s.rfind( first )
    if start >= 0:
        start += len( first )
    else:
        start = 0
    end = s.find( last, start )
    if end < 0:
        return ''
    return s[start:end]

## 파일 처리 함수
## 파일 저장 처리, 파일에 첫부분에 헤더정보를 저장후 다음라인이후 raw_data 저장
def save_raw_data(file, raw_data, head=None):
    with open(file,'wt',encoding='utf-8') as fp:
        if head is not None:
            fp.write(head+"\n")
        fp.write(raw_data)

## 해당 폴더에서 파일 리스트 생성, check로 시작하는 파일만.
def get_files(fold,check=''):
    file_list = []
    for entry in os.scandir(fold):
        if entry.is_file() and entry.name.startswith(check):
            file_list.append(entry.name)
    return file_list

## 해당 폴더에서 디렉토리 리스트 생성, check로 시작하는 폴더만.
def get_dirs(fold,check=''):
    dir_list = []
    for entry in os.scandir(fold):
        if entry.is_dir() and entry.name.startswith(check):
            dir_list.append(entry.name)
    return dir_list

## 해당폴더의 파일을 다음 폴더로 이동 처리
def move_file(file,fold):
    return shutil.move(file,fold)
## Json 문자열을 DICT 형태로 전환, Decode Error 시 None 리턴
def json_loads(json_str):
    try:
        return json.loads(json_str)
    except JSONDecodeError as je:
        log(je,logging.ERROR)
        return None
## 특정 문자 사이의 텍스트 추출시 사용, By - RE
def re_search(pattern_start,pattern_end,text):
    pattern = pattern_start + '(.+?)' + pattern_end
    matched = re.search(pattern, text, re.S)
    searched_str = None
    if matched:
        searched_str = matched.group(1).strip()
    return searched_str
## 문자형 숫자 , 처리
def num_format(s):
    try:
        return '{:,}'.format(int(s))
    except ValueError as ve:
        return s
## HHMM 형식을 HH:MM 형식으로
def time_format(hhmm):
    return '{}:{}'.format(hhmm[:2],hhmm[2:])

## 리스트를 unique 하게 만들기
def unique_list(alist):
    u_list = []
    for td in alist:
        if td not in u_list:
            u_list.append(td)
    return u_list
## 리스트의 각 필드를 포맷에 맞게 변경 처리
## formats : [대상 인덱스, format 함수] 리스트
def list_formatter(raw_list,formats):
    fmt_list = copy.deepcopy(raw_list)
    for td in fmt_list:
        for fmt in formats:
            td[fmt[0]] = fmt[1](str(td[fmt[0]]))
    return fmt_list