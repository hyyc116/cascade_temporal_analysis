#coding:utf-8

'''
    Tasks in this script:

        1. analyze the result from our facets

'''
## task 1

# from basic_config import *

import chart_studio.plotly as py
import plotly

data = dict(
    type='sankey',
    node = dict(
      label = ["原料1", "原料2", "中间产物1", "中间产物2", "成果", "损耗"],
      color = ["blue", "blue", "green", "green", "black", "red"]
    ),
    link = dict(
      source = [0,1,0,2,3,3,2],
      target = [2,3,3,4,4,5,5],
      value = [8,4,2,6,4,2,2]
  ))

layout =  dict(title = "原料转化路径图")
fig = dict(data=[data],layout=layout)     # 注意这里的data被转化为数据，可以支持同时绘制多个图形
py.image.save_as(fig, filename='a-simple-plot.png')




