# encoding: utf-8
"""
author=fenglelanya
learn more
"""
from TextKLine import *
import pandas as pd
import numpy as np
import requests as rq
import json as js
from EnumType import *
from eventType import *
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import datetime
from PyechartsKLine import *
from matplotlib.pylab import date2num

class SpreadUI(object):
    parameter = {'code1': 'L', 'code2': 'PP', 'startDate': '2018-01-01', 'endDate': '2018-03-28',
                 'overMapWidth': 1500, 'overMapHeight': 600, 'ax_high': 7.8, 'ax_width': 18.0, 'spread_Ratio': '1:1',
                 'mult_Code1': 1, 'mult_Code2': 1, 'kuaqi': False}    # False
    def __init__(self):
        super(SpreadUI, self).__init__()
        self.code1DataDict = {}
        self.code2DataDict = {}
        self.eachCodePositionDict = {}
        self.spreadList = []  # 价差的List
        self.stockCode_list = ['002572', '300296', '600340']
        self.boolTrade = False
        self.boolPlot = False
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/45.0.2454.101 Safari/537.36'}
        self.hist_code1_last_df = pd.DataFrame()
        self.hist_code2_last_df = pd.DataFrame()
        self.histCode1, self.histCode2 = self.getHistCode()
        #print 'self.histCode1,self.histCode2==', self.histCode1,self.histCode2
        self.initStrategy()

    def initStrategy(self):
        """初始化策略"""
        # 订阅代码
        dict_histCode1 = self.subMarketData(self.histCode1, EVENT_MAINFUTURE_HIST_SINA_MARKETDATA)
        dict_histCode2 = self.subMarketData(self.histCode2, EVENT_MAINFUTURE_HIST_SINA_MARKETDATA)
        fields_ = ['TradeDate', 'OpenPrice', 'HightestPrice', 'LowestPrice', 'LastPrice']
        if self.histCode1 in dict_histCode1:
            df_hist_code1 = dict_histCode1[self.histCode1]
            self.hist_code1_last_df = df_hist_code1[fields_]
            self.hist_code1_last_df = self.rename_col(self.hist_code1_last_df, self.histCode1)

        if self.histCode2 in dict_histCode2:
            df_hist_code2 = dict_histCode2[self.histCode2]
            self.hist_code2_last_df = df_hist_code2[fields_]
            self.hist_code2_last_df = self.rename_col(self.hist_code2_last_df, self.histCode2)
            # self.hist_code2_last_df.rename(columns={"LastPrice": "LastPrice_{}".format(self.histCode2)}, inplace=True)

        if len(self.hist_code1_last_df) > 0 and len(self.hist_code2_last_df) > 0:
            df = pd.DataFrame(dtype='float')
            if not self.boolPlot:
                try:
                    print 'daozheli'
                    hist_code_ratio = self.parameter['spread_Ratio'].split(':')
                    result = pd.merge(self.hist_code1_last_df, self.hist_code2_last_df, on='TradeDate', how='inner')
                    result.set_index('TradeDate', inplace=True)
                    df['LastPrice_Spread'] = self.spreadPrice(result, "LastPrice_{}".format(self.histCode1),
                                                              "LastPrice_{}".format(self.histCode2), hist_code_ratio)
                    df['OpenPrice_Spread'] = self.spreadPrice(result, "OpenPrice_{}".format(self.histCode1),
                                                              "OpenPrice_{}".format(self.histCode2), hist_code_ratio)
                    df['HightestPrice_Spread'] = self.spreadPrice(result, "HightestPrice_{}".format(self.histCode1),
                                                                  "HightestPrice_{}".format(self.histCode2),
                                                                  hist_code_ratio)
                    df['LowestPrice_Spread'] = self.spreadPrice(result, "LowestPrice_{}".format(self.histCode1),
                                                                "LowestPrice_{}".format(self.histCode2),
                                                                hist_code_ratio)
                    #array = self.winsorize(df.values)
                    #df['date'] = df.index
                    self.boolPlot = True
                except:
                    pass
            if not df.empty:
                try:
                    dateNow = datetime.datetime.today()   # 今天
                    endDate_yes = (dateNow + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')  # 昨天
                    dateNow = datetime.datetime.strftime(dateNow, '%Y-%m-%d')
                    if self.parameter['endDate'] is not None:
                        paramEndDate = self.parameter['endDate']    # 参数:endDate
                        if paramEndDate >= dateNow:
                            endDate = endDate_yes
                        else:
                            endDate = paramEndDate
                    else:
                        endDate = endDate_yes
                    selectData_df = df.loc[self.parameter['startDate']:endDate, :]
                except Exception, E:
                    selectData_df = pd.DataFrame()
                    print u'获取{}至{}时段数据出问题,请检查==>{}'.format(self.parameter['startDate'], self.parameter['endDate'], E)
                """
                dataList_0 = []
                for n in df.values:
                    date__ = n[-1:][0]
                    #print 'date__==', date__
                    date_time = datetime.datetime.strptime(date__, '%Y-%m-%d')
                    t = date2num(date_time)
                    open, high, low, close = n[:4]
                    dataList_0.append((t, open, high, low, close))
                print 'dataList000==', dataList_0
                self.plot_(dataList_0)
                """
                if not selectData_df.empty:   # 如果传来的df不是空的则开始去极值化、绘图
                    df_new = pd.DataFrame()
                    one_col = selectData_df.iloc[:, 0]
                    one_array = self.winsorize(one_col)
                    df_new['lastPrice'] = one_array
                    two_col = selectData_df.iloc[:, 1]
                    two_array = self.winsorize(two_col)
                    df_new['openPrice'] = two_array
                    three_col = selectData_df.iloc[:, 2]
                    three_array = self.winsorize(three_col)
                    df_new['hightPrice'] = three_array
                    four_col = selectData_df.iloc[:, 3]
                    four_array = self.winsorize(four_col)
                    df_new['lowPrice'] = four_array
                    df_new['date'] = selectData_df.index
                    #print df_new.head(10)
                    #print df_new.tail(10)
                    title_ = u"{}-{} HistSpreadPrice".format(self.histCode1, self.histCode2)
                    #KLine(df_new, title_)           ## 这种方式是用pyqtgrph来本地显示的
                    overWidth = self.parameter['overMapWidth']
                    overHeight = self.parameter['overMapHeight']
                    PyechartsKLine(df_new, title_,overWidth, overHeight)   # 这种是使用了pyecharts来在线显示的
                    """
                    dataList = []
                    df_new_array = df_new.values
                    for n in df_new_array:
                        date__ = n[-1:][0]
                        date_time = datetime.datetime.strptime(date__, '%Y-%m-%d')
                        t = date2num(date_time)
                        open, high, low, close = n[:4]
                        dataList.append((t, open, high, low, close))
                    self.plot_(dataList)
                    plt.show()
                    """

    def plot_(self, list):
        """利用plot画K线"""
        fig = plt.figure(facecolor='#07000d', figsize=(self.parameter['ax_width'], self.parameter['ax_high']))
        ax = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, axisbg='#07000d')
        #fig, ax = plt.subplots(facecolor='#07000d', figsize=(self.parameter['ax_width'], self.parameter['ax_high']))
        fig.subplots_adjust(bottom=0.2)
        # 设置X轴刻度为日期时间
        ax.xaxis_date()
        # 设置legend
        plt.legend(labels=['a', 'b'], loc='best')
        plt.title(u"{}-{} HistSpreadPrice".format(self.histCode1, self.histCode2), color='r')
        plt.ylabel("spreadPrice")
        plt.xticks(rotation=45)  # 45°
        plt.yticks()
        ax.yaxis.label.set_color("b")   # Y轴图例文字蓝色
        # 边框上色
        ax.spines['top'].set_color('#5998ff')
        ax.spines['right'].set_color('#5998ff')
        ax.spines['left'].set_color("#5998ff")
        ax.spines['bottom'].set_color("#5998ff")
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        # ax 绘图Axes的实例
        # width    图像中红绿矩形的宽度,代表天数
        # alpha    矩形的颜色的透明度
        # colorup  收盘价格大于开盘价格时的颜色
        mpf.candlestick_ochl(ax, list, width=.9, colorup='g', colordown='r', alpha=.9)
        plt.grid()

    def spreadPrice(self, df, col_1, col_2, hist_code_ratio):
        """分别计算OHLP的价差"""
        df[col_1 + "mult"] = map(lambda x: float(x) * int(hist_code_ratio[0]) * int(self.parameter['mult_Code1']), df[col_1])
        df[col_2 + "mult"] = map(lambda x: float(x) * int(hist_code_ratio[1]) * int(self.parameter['mult_Code2']), df[col_2])
        spread_df = df[col_1 + "mult"] - df[col_2 + "mult"]
        return spread_df

    def rename_col(self, df=None, code=None):
        """修改列名"""
        df.rename(columns={"LastPrice": "LastPrice_{}".format(code),
                                                "OpenPrice": "OpenPrice_{}".format(code),
                                                "HightestPrice": "HightestPrice_{}".format(code),
                                                "LowestPrice": "LowestPrice_{}".format(code)}, inplace=True)
        return df

    def log(self, log):
        """打印log"""
        print log

    def winsorize(self, array):
        """去极值"""
        """param array:<type> numpy.array"""
        sigma_ = np.std(array)
        mean_ = np.mean(array)
        array[array > mean_+3*sigma_] = mean_+3*sigma_
        array[array < mean_-3*sigma_] = mean_-3*sigma_
        return array

    def getHistCode(self):
        """截取需要订阅历史行情的Code"""
        try:
            hist_code1 = str(self.parameter['code1'].upper())
            hist_code2 = str(self.parameter['code2'].upper())
            if self.parameter['kuaqi']:
                pass
            else:
                hist_code1 = filter(lambda x: not str.isdigit(x), hist_code1)
                hist_code2 = filter(lambda x: not str.isdigit(x), hist_code2)
            return hist_code1, hist_code2
        except Exception, e:
            print 'e==', e

    def subMarketData(self, instrumentid, exchangeid):
        # 订阅行情
        CFFEX_code_list = ['IC', 'IH', 'IF', 'TF', 'T']
        instrumentid = instrumentid.upper()
        up_Code = filter(lambda x: not str.isdigit(x), instrumentid)
        # 此处exchangeid充当一个type(区分是即时行情还是历史行情)
        if exchangeid == EVENT_FUTURE_SINA_MARKETDATA:
            #获取新浪期货当前行情(合约代码格式如:RB1805,合约字母大写+时间)
            url = "http://hq.sinajs.cn/list={}".format(instrumentid)
            dict_ = self.requestURL(url, instrumentid, exchangeid)
        else:  # if exchangeid == EVENT_MAINFUTURE_HIST_SINA_MARKETDATA:
            #获取新浪主力期货历史行情数据(合约代码格式如:RB0,合约字母大写+数字0)
            url_InnerFuture = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService." \
                  "getInnerFuturesDailyKLine?symbol={}"
            url_CffexFuture = "http://stock2.finance.sina.com.cn/futures/api/json.php/CffexFuturesService." \
                        "getCffexFuturesDailyKLine?symbol={}"

            if self.parameter['kuaqi']:
                digit_ = filter(lambda x: x.isdigit, instrumentid)
                if len(digit_) >= 4:
                    if up_Code in CFFEX_code_list:
                        url = url_CffexFuture.format(instrumentid)
                    else:
                        url = url_InnerFuture.format(instrumentid)
                    dict_ = self.requestURL(url, instrumentid, exchangeid)
                else:
                    dict_ = {}
            else:
                print 'instrumentid==>',instrumentid
                digit = filter(lambda x: x.isdigit(), instrumentid)
                if digit:
                    self.log(u'合约输入有误,可能是合约代码加入了年月份，请检查后再操作!')
                    dict_ = {}
                else:
                    if instrumentid in CFFEX_code_list:
                        url = url_CffexFuture.format(instrumentid + "0")
                    else:
                        url = url_InnerFuture.format(instrumentid + "0")
                    dict_ = self.requestURL(url, instrumentid, exchangeid)
        return dict_

    def requestURL(self, url, code, type=None):
        # 根据URL获取新浪期货API中的数据
        #resultDataDF = pd.DataFrame()
        try:
            respon = rq.get(url, headers=self.headers).text
            if type == EVENT_FUTURE_SINA_MARKETDATA:
                respon = respon.split(',')
                print '即时respon==', respon
                data = self.onRtnNowCodeMarketdatas(respon, code)
            else:#if type == EVENT_MAINFUTURE_HIST_SINA_MARKETDATA:
                data = self.onRtnHistCodeMarketDatas(respon, code)
            return data
        except Exception, E:
            self.log(str(E))

    def onRtnNowCodeMarketdatas(self, responList, code):
        """解析数据"""
        self.futureDatadic = {}  # 用于存放新浪期货接口解析出来的数据
        self.futureDatadic[EnumSinaFutureDataType.Code.name] = code
        self.futureDatadic[EnumSinaFutureDataType.OpenPrice.name] =responList[2]
        self.futureDatadic[EnumSinaFutureDataType.HightestPrice.name] = responList[3]
        self.futureDatadic[EnumSinaFutureDataType.LowestPrice.name] = responList[4]
        self.futureDatadic[EnumSinaFutureDataType.PreClosePrice.name] = responList[5]
        self.futureDatadic[EnumSinaFutureDataType.Bid1_Price.name] = responList[6]
        self.futureDatadic[EnumSinaFutureDataType.Ask1_Price.name] = responList[7]
        self.futureDatadic[EnumSinaFutureDataType.LastPrice.name] = responList[8]
        self.futureDatadic[EnumSinaFutureDataType.SettlementClosePrice.name] = responList[9]
        self.futureDatadic[EnumSinaFutureDataType.LastSettlementClosePrice.name] = responList[10]
        self.futureDatadic[EnumSinaFutureDataType.Bid1_Vol.name] = responList[11]
        self.futureDatadic[EnumSinaFutureDataType.Ask1_Vol.name] = responList[12]
        self.futureDatadic[EnumSinaFutureDataType.GetNum.name] = responList[13]
        self.futureDatadic[EnumSinaFutureDataType.TradeNum.name] = responList[14]
        self.futureDatadic[EnumSinaFutureDataType.ExchangeName.name] = responList[15]
        self.futureDatadic[EnumSinaFutureDataType.FutureName.name] = responList[16]
        self.futureDatadic[EnumSinaFutureDataType.TradeDate.name] = responList[17]
        return self.futureDatadic

    def onRtnHistCodeMarketDatas(self, responList, code):
        """获取主力合约历史数据"""
        mainFutureHistDatadic = {}  # 用于存放新浪期货接口解析出来的主力期货历史数据
        try:
            rsp = js.loads(responList)
            array_ = np.array(rsp)
            col = [EnumSinaMainFutureHistDataType.TradeDate.name, EnumSinaMainFutureHistDataType.OpenPrice.name,
                   EnumSinaMainFutureHistDataType.HightestPrice.name, EnumSinaMainFutureHistDataType.LowestPrice.name,
                   EnumSinaMainFutureHistDataType.LastPrice.name, EnumSinaMainFutureHistDataType.TradeVol.name]
            df = pd.DataFrame(data=array_, columns=col)
            mainFutureHistDatadic[code] = df
            return mainFutureHistDatadic
        except Exception, E:
            self.log(str(E))

if __name__ == '__main__':
    SpreadUI()