import re
import pandas as pd
import requests
import json
import numpy as np

# 提取OCR导出文件中的地名
with open('loc_name_from_ocr.txt', 'r') as file:
    loc_name = file.read().replace('\n', '')
    file.close()
pattern=re.compile("[\u4e00-\u9fa5]+")
loc_list = pattern.findall(loc_name)

# 将地名和地理编码变为结构化文本
df = pd.DataFrame(loc_list, columns=['location_name'])
df.index = np.arange(1, len(df) + 1)

# 高德地图web API正地理编码查询
key = '0b8fa63575fef96b50e752c13241852b'
base = 'https://restapi.amap.com/v3/geocode/geo'
# 测试1
parameters = {'address': '故宫博物院', 'key': key, 'city':'北京'}
test = requests.get(base, parameters)
json_test = json.loads(test.text)
json_test
loc_test = json_test['geocodes'][0]['location']
print(loc_test)

# 批量查询
location_list = []

for i in loc_list:
    para = {'address': i, 'key': key, 'city':'北京'}
    try:
        reqs = requests.get(base, para)
        json_info = json.loads(reqs.text)
        loc = json_info['geocodes'][0]['location']
        location_list.append(loc)
    except:
        location_list.append('null')

df['geocodes_location']= location_list
df.to_csv('raw.csv')

# 删除没有坐标的题目 + 添加缺失值
df = pd.read_csv('raw.csv')
df.set_index('location_name', inplace=True)
df.drop(['人儿','油画','剪贴','彩墨','邮','缘','东陵','怀仁堂','献花','西市'], axis=0, inplace=True)
df.drop(labels='Unnamed: 0', axis=1, inplace=True)
df.at['故宫','geocodes_location']='116.397026,39.918058' #故宫博物院
df.at['象来街','geocodes_location']='116.365138,39.899030' #象来街招待所
# df.to_csv('cleaned.csv')

# 分开经纬度放入独立行
l = df['geocodes_location'].values.tolist()

# - 测试
coords = '116.350808,39.906608'
x = coords.split(",")
print(x[1])

# - 循环
x_list = []
y_list = []
for i in l:
    x = i.split(',')[0]
    y = i.split(',')[1]
    x_list.append(x)
    y_list.append(y)

df['x'] = x_list
df['y'] = y_list
df.to_csv('cleaned_with_xy.csv')