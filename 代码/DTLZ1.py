'''
求解问题部分
'''

# import numpy as np
import math

# 函数的维度（目标维度不一致的自行编写目标函数）
Dimention = 10
# 函数目标个数
Func_num = 6
# 函数的变量的边界
Bound = [[0, 1] for i in range(0, Dimention)]
Pi = math.pi


def Func(D, T, Num, Dis, Tra, w):
    # 3目标函数
    f1 = F1(Dis)
    f2 = F2(Num)
    f3 = F3(D, w)
    f4 = F4(T)
    f5 = F5(Tra, w)
    return [f1, f2, f3, f4, f5]


def Func4(D, T, Num, Dis, Tra, w):
    # 3目标函数
    f1 = F1(Dis)
    f2 = F2(Num)
    f3 = F3(D, w)
    f4 = F4(T)
    f5 = F5(Tra, w)
    f6 = F6(Tra, w)
    return [f1, f2, f3, f4, f5, f6]


def F1(Dis):
    f = -Dis
    return f


def F2(Num):
    f = Num
    return f


def F3(D, w):
    f = 0
    for i in range(80):
        for j in range(80):
            if (j != 0):
                f += D[i][j] * w[j][6]
    return f


def F4(T):
    f = 0
    for i in range(1, len(T)):
        f += T[i][1] - T[i][0]
    return f


# 这个是美食部分计算去过的美食景点
def F5(Tra, w):
    f = 0
    for i in range(len(Tra)):
        if (w[Tra[i]][0] == 1):
            f = f + 1
    return f


def F6(Tra, w):
    f = 0
    for i in range(len(Tra)):
        if (w[Tra[i]][1] == 1):
            f = f + 1
    return f
