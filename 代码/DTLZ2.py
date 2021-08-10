'''
求解问题部分
'''

import numpy as np
import math

# 函数的维度（目标维度不一致的自行编写目标函数）
Dimention = 10
# 函数目标个数
Func_num = 4
# 函数的变量的边界
Bound = [[0, 1] for i in range(0, Dimention)]
Pi = math.pi


def Func(D, T, Num, Dis, w):
    # 3目标函数
    f1 = F1(Dis)
    f2 = F2(Num)
    f3 = F3(D, w)
    f4 = F4(T)
    return [f1, f2, f3, f4]


def F1(Dis):
    f = Dis
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

#一个函数越接近5000越好计算钱
#def F5():

#加重红色权重
#def F6()