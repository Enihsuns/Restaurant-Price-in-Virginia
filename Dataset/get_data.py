# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(Wanyu Du)s
"""

import pandas as pd
import re

with open('restaurants_VA.json', 'r', encoding='utf8') as f:
  data = f.readlines()

r=r'[\n",  ]'
items=[]
for i, line in enumerate(data):
  if line=='{\n':
    item={}
    idx=0
  if idx!=0 and ':' in line:
    key=line.split(':')[0]
    key=re.sub(r, '', key)
    value=line.split(':')[1]
    value=re.sub(r, '', value)
    if value=='[' or value=='{':
      continue 
    else:
      if key in item.keys():
        value_before=item[key]
        item[key]=value_before+' | '+value
      else:
        item[key]=value
  if line=='}\n':
    items.append(item)
  idx+=1

df=pd.DataFrame(items)
df['price']=df['price'].fillna('99999')
df=df[df['price']!='99999']
outs=df[['id', 'distance', 'latitude', 'longitude', 'rating', 'review_count', 'price']]
outs.to_csv('restaurants_va_numeric.csv', index=False)