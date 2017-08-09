import numpy as np
import pandas as pd
from flatten_dict import flatten

## JSON Data 를 Dict 형태로 리턴 처리
## parse_info 는 key와 Json에서 읽어올 필드를 [a][b][{}][0][c] 형태로 지정하여야함, {} 부분은 루프를 돌면서 인덱스로 처리할 부분
## loop_field는 실제 처리되어야할 Json의 필드를 명확히 지정하여야함 예) [a][b][0] 혹은 [a][b]
def parsing_json_data_to_dict(json_data, loop_field, parse_info):
    parsedList = []
    for i in range(len(eval('json_data'+loop_field))):
        lineDict = {}
        for k,v in parse_info.items():
            #lineList.append(eval('raw_data'+v))
            try:
                lineDict[k] = eval(('json_data'+v).format(i))
            except:
                lineDict[k] = None
        parsedList.append(lineDict)
    return parsedList

## DataFrame 가격 정보를 받아 해당 필드에 대해 최소값, 최대값, 평균값 구하기
def stat_fare(fare_data,columns=['fare1','fare2']):
    ## 최소값 최대값 평균 계산
    fare_arr = fare_data[columns].values ## fare 만 구해오기
    fare_arr = fare_arr.flatten() ## shape 1차원으로 변경
    fare_arr = np.unique(fare_arr) ## 중복값 제거
    if '' in fare_arr or '0' in fare_arr:
        fare_arr = fare_arr[1:] ## 0 값 제거
    if len(fare_arr) == 0: ## 빈값일 경우 - 0만 있는 경우로 처리
        return 0,0,0
    fare_arr = fare_arr.astype('float') ## 수치형으로 변경
    return fare_arr.min(),fare_arr.max(),fare_arr.mean()

## JSON 데이터를 DICT 변환한 DICT 자료형을 평형한 형태의 DICT로 변환하기 위한 유틸
def comma_reducer(k1, k2):
    if k1 is None:
        return k2
    else:
        return k1 + "," + k2

def r_flatten(json_dict):
    f_dict = flatten(json_dict,reducer=comma_reducer)

    while any(type(v) == list for v in f_dict.values()):
        for k,v in f_dict.items():
            if type(v) == list:
                f_dict[k] = dict(('#'+str(p),e) for p,e in enumerate(v))
        f_dict = flatten(f_dict,reducer=comma_reducer)
    return f_dict

## json 포맷을 dict으로 로드한 객체에서 마지막 키의 이름을 이용해 해당 값을 dict 형태로 가져오기
## raw_json_dict : dict object,  key_fields : 마지막 키이름 리스트
def mining_value_by_last_field_name(raw_json_dict, key_fields):
    flat_json = r_flatten(raw_json_dict)
    result_dict = {}
    for k in sorted(flat_json.keys()):
        k_field = k.split(',')[-1]
        if k_field in key_fields:
        #if k_field == key_fields:# 해당 필드 값 읽어오기
            result_dict[k_field] = result_dict.get(k_field,[])
            result_dict[k_field].append(flat_json[k])
    return result_dict