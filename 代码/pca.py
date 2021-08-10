import numpy as np
import xlrd


def standardize(data):
    mu = data.mean(axis=0)
    st = data.std(axis=0)
    return (data - mu) / st


def pca(a):
    a = standardize(np.array(a))
    #cor = np.corrcoef(a.transpose())  # 相关系数
    cor = np.cov(a.transpose())  # 协方差
    e, v = np.linalg.eig(cor)
    rate = e / np.sum(e)
    y = np.dot(a, v)
    ans = np.dot(y, rate)
    return ans


if __name__ == '__main__':
    workbook = xlrd.open_workbook("./备选景点信息详细版.xlsx")
    sheet1 = workbook.sheet_by_name("黄山")
    data = np.zeros(shape=(sheet1.nrows - 1, 4))
    pos_l = []
    for i in range(sheet1.nrows - 1):
        pos_l.append(sheet1.cell_value(i + 1, 1))  # 获取景点名称，注意位置
        for j in range(4):
            data[i, j] = sheet1.cell_value(i + 1, 2 + j)  # 获取景点指标信息，注意位置
    #ans = pca(data)
    a = standardize(np.array(data))
    # cor = np.corrcoef(a.transpose())  # 相关系数
    cor = np.cov(a.transpose())  # 协方差
    e, v = np.linalg.eig(cor)
    rate = e / np.sum(e)
    y = np.dot(a, v)
    ans = np.dot(y, rate)
    for i in range(len(pos_l)):
        print(pos_l[i], ans[i])
    # a = [[4, 3, 2], [2, 1, 5], [6, 3, 2], [6, 3, 1]]  # 4*3
