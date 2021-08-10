import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm


def rsr(data, weight=None, threshold=None, full_rank=True):
    Result = pd.DataFrame()
    n, m = data.shape

    # 对原始数据编秩
    if full_rank:
        for i, X in enumerate(data.columns):
            Result[f'X{str(i + 1)}：{X}'] = data.iloc[:, i]
            Result[f'R{str(i + 1)}：{X}'] = data.iloc[:, i].rank(method="dense")
    else:
        for i, X in enumerate(data.columns):
            Result[f'X{str(i + 1)}：{X}'] = data.iloc[:, i]
            Result[f'R{str(i + 1)}：{X}'] = 1 + (n - 1) * (data.iloc[:, i].max() - data.iloc[:, i]) / (
                    data.iloc[:, i].max() - data.iloc[:, i].min())

    # 计算秩和比
    weight = 1 / m if weight is None else np.array(weight) / sum(weight)
    Result['RSR'] = (Result.iloc[:, 1::2] * weight).sum(axis=1) / n
    Result['RSR_Rank'] = Result['RSR'].rank(ascending=False)

    # 绘制 RSR 分布表
    RSR = Result['RSR']
    RSR_RANK_DICT = dict(zip(RSR.values, RSR.rank().values))
    Distribution = pd.DataFrame(index=sorted(RSR.unique()))
    Distribution['f'] = RSR.value_counts().sort_index()
    Distribution['Σ f'] = Distribution['f'].cumsum()
    Distribution[r'\bar{R} f'] = [RSR_RANK_DICT[i] for i in Distribution.index]
    Distribution[r'\bar{R}/n*100%'] = Distribution[r'\bar{R} f'] / n
    Distribution.iat[-1, -1] = 1 - 1 / (4 * n)
    Distribution['Probit'] = 5 - norm.isf(Distribution.iloc[:, -1])

    # 计算回归方差并进行回归分析
    r0 = np.polyfit(Distribution['Probit'], Distribution.index, deg=1)
    print(sm.OLS(Distribution.index, sm.add_constant(Distribution['Probit'])).fit().summary())
    if r0[1] > 0:
        print(f"\n回归直线方程为：y = {r0[0]} Probit + {r0[1]}")
    else:
        print(f"\n回归直线方程为：y = {r0[0]} Probit - {abs(r0[1])}")

    # 代入回归方程并分档排序
    Result['Probit'] = Result['RSR'].apply(lambda item: Distribution.at[item, 'Probit'])
    Result['RSR Regression'] = np.polyval(r0, Result['Probit'])
    # threshold = np.polyval(r0, [2, 4, 6, 8]) if threshold is None else np.polyval(r0, threshold)
    # Result['Level'] = pd.cut(Result['RSR Regression'], threshold, labels=range(len(threshold) - 2, 0, -1))
    Result['Level'] = Result['RSR Regression']
    return Result, Distribution


def rsrAnalysis(data, file_name=None, **kwargs):
    Result, Distribution = rsr(data, **kwargs)
    file_name = 'RSR 分析结果报告.xlsx' if file_name is None else file_name + '.xlsx'
    Excel_Writer = pd.ExcelWriter(file_name)
    Result.to_excel(Excel_Writer, '综合评价结果')
    Result.sort_values(by='Level', ascending=False).to_excel(Excel_Writer, '分档排序结果')
    Distribution.to_excel(Excel_Writer, 'RSR分布表')
    Excel_Writer.save()

    return Result, Distribution


if __name__ == '__main__':
    for i in range(3, 4):
        temp = pd.read_excel("./GA结果/5M" + str(i + 1) + ".xls", sheet_name=0)
        data = pd.DataFrame({'Func1': list(temp['Func1']),
                             'Func2': list(temp['Func2']),
                             'Func3': list(temp['Func3']),
                             'Func4': list(temp['Func4']),
                             'Func5': list(temp['Func5']),
                             'Func6': list(temp['Func6'])},
                            index=list(temp['序号']),
                            columns=['Func1', 'Func2', 'Func3', 'Func4', 'Func5', 'Func6'])
        res, dist = rsrAnalysis(data, file_name="RSR 分析结果报告_5M" + str(i + 1))
    '''
    file = ['南京', '合肥', '上海', '常州', '镇江', '无锡', '苏州',
            '嘉兴', '宁波', '金华', '湖州', '绍兴',
            '芜湖', '马鞍山', '安庆', '黄山']
    for i in range(len(file)):
        temp = pd.read_excel("./备选景点信息详细版.xlsx", sheet_name=2 + i)
        data = pd.DataFrame({'携程评分': list(temp['携程评分']),
                             '携程评价数量': list(temp['携程评价数量']),
                             '大众点评评分': list(temp['大众点评评分']),
                             '大众点评评价数量': list(temp['大众点评评价数量'])},
                            index=list(temp['景点名称']),
                            columns=['携程评分', '携程评价数量', '大众点评评分', '大众点评评价数量'])

        
        data = pd.DataFrame({'国内旅游（万人次）': list(temp['国内旅游（万人次）']),
                             '国内旅游收入（亿元）': list(temp['国内旅游收入（亿元）']),
                             # '第三产业生产总值（亿元）': list(temp['第三产业生产总值（亿元）']),
                             '人均第三产业产值（万元/人）': list(temp['人均第三产业产值（万元/人）']),
                             '公路密度（公里/平方公里）': list(temp['公路密度（公里/平方公里）'])},
                            index=list(temp['地区']),
                            columns=['国内旅游（万人次）', '国内旅游收入（亿元）', '人均第三产业产值（万元/人）', '公路密度（公里/平方公里）'])
        
        res, dist = rsrAnalysis(data, file_name="RSR 分析结果报告_" + file[i] + ".xlsx")
    '''
