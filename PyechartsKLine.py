# encoding: utf-8
"""
author=fenglelanya
learn more
"""
import pyecharts
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import talib
import numpy as np
import pandas as pd
import tushare as ts
from pyecharts import Grid,Bar,Line,Kline,Overlap,Candlestick

class PyechartsKLine(object):
    def __init__(self, df, title, overWidth, overHeight):
        super(PyechartsKLine, self).__init__()
        self.N1 = 10
        self.N2 = 30
        self.data = df
        self.title = title
        self.overWidth = overWidth
        self.overHeight = overHeight
        self.dataGet()

    def dataGet(self):
        """获取行情"""
        data = self.data
        #print "data1111=", data
        #data.sort_values('date', inplace=True)
        ochl = data[['openPrice', 'lastPrice', 'hightPrice', 'lowPrice']]
        ochl_tolist = [ochl.ix[i].tolist() for i in range(len(ochl))]
        close_df = data['lastPrice']
        sma_N1 = talib.SMA(np.array(close_df), self.N1)
        sma_N2 = talib.SMA(np.array(close_df), self.N2)
        date_df = data.index
        kline = Candlestick()
        # datazoom_orient='vertical'  dataZoom效果加到纵坐标上
        kline.add(self.title, date_df, ochl_tolist, mark_point=['max', 'min'], is_datazoom_show=True, mark_point_symbolsize=80, mark_line_valuedim=['highest', 'lowest'])

        line = Line()
        line.add(u'{}日均线'.format(self.N1), date_df, sma_N1, is_fill=False, line_opacity=0.8, is_smooth=True, line_color='b')
        line.add(u'{}日均线'.format(self.N2), date_df, sma_N2, is_fill=False, line_opacity=0.8, is_smooth=True, line_color='g')

        overlap = Overlap(page_title=self.title, width=self.overWidth, height=self.overHeight)
        overlap.add(kline)
        overlap.add(line)
        KLine_path = r'KLine.html'
        overlap.render(KLine_path)
        # 自动打开HTML
        #self.driver = webdriver.Firefox()
        #self.driver.get(KLine_path)



#if __name__ == '__main__':
    #PyechartsKLine()