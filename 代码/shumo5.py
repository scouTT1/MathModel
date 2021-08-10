import os
import math
import random
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import time
import FileProcessing

# from utils import evaluate_EA as eva
import DTLZ1 as problems
import xlrd

object_name = 'DTLZ1'

obj_num = 5
N = 50
INF = 1e6
eps = 1e-6
v1 = 50
v0 = 90
o1 = 0.6
sleepmoney = 60  # 每晚住宿费
shopmoney = 50  # 每天消费
citymoney = 50  # 城市消费
parkmoney = 30  # 停车消费
minsight = 7
o0 = 1.0
money = 5000
bound = problems.Bound
dim = problems.Dimention  # dim of the solution vector
max_gen = 500
pm = 2.0 / N  # mutation probability， 论文中采用pm=1/N或1/dim
maxepoch = 100000  # 初始化做多循环次数
SightName = []  # 景区名称
sleeptime = 9.0  # 睡觉休息时间
D = [[0.0 for i in range(80)] for i in range(80)]  # 距离矩阵
b = [[0 for i in range(17)] for i in range(80)]  # 丛书矩阵
Food = [[0, 0, 0.0, 0.0, 0, 0, 0.0] for i in range(80)]  # 标签矩阵美食和红色  美食 红色 开门 关门 学生票价 老人票价


# Open = [[0.0, 0.0] for i in range(82)]  # 各大景点开放时间


def loaddata():
    workbook = xlrd.open_workbook(r'./pre_data.xls')
    sheet_name1 = workbook.sheet_names()[0]
    dis = workbook.sheet_by_name(sheet_name1)
    belong = workbook.sheet_by_name('belong')
    label = workbook.sheet_by_name('label')
    for i in range(dis.nrows - 1):
        # 距离矩阵
        temp1 = dis.row_values(i + 1)
        temp1.pop(0)
        D[i] = temp1
        SightName.append(dis.row_values(i + 1)[0])
        # 从属矩阵
        temp2 = belong.row_values(i + 1)
        temp2.pop(0)
        b[i] = temp2
        # 标签矩阵美食和红色
        temp3 = label.row_values(i + 1)
        temp3.pop(0)
        Food[i] = temp3
        Food[i][2] *= 24
        Food[i][3] *= 24  # 时间格式转化


sightNum = 80
loaddata()


class Individual:
    def __init__(self):
        """
        Initialize the individual.
        param id: id of the individual.
        param solution: solution of the individual.
        param M: The individual's object function value on problems.
        param rank: The rank of individual.
        param n: The number of other individual that dominate this individual.
        param S: The set of parents that this individual dominate.
        """
        self.money = 0
        self.M = [INF for i in range(0, obj_num)]
        self.rank = 0
        self.n = 0
        self.S = []
        self.dis = 0
        self.mo=0
        self.travelDis = 0
        self.solution = []
        self.zichan = 5000
        self.travelnum = 0
        self.travellist = []
        self.Dm = [[0 for i in range(82)] for i in range(82)]
        self.Timelist = [[0.0, 0.0] for i in range(43)]
        # for i in range(0, dim):
        #   self.solution.append(random.uniform(bound[i][0], bound[i][1]))

    def cal_object_value(self):
        """
        Calculate object value
        """
        self.M[0], self.M[1], self.M[2], self.M[3], self.M[4] = problems.Func(D=self.Dm, T=self.Timelist,
                                                                              Num=self.travelnum,
                                                                              Dis=self.travelDis,
                                                                              Tra=self.travellist,
                                                                              w=Food)

    def plan(self):
        # 如何规划生成序列 根据timelist规划
        self.travelnum = len(self.travellist)
        randSight = self.travellist
        sightNum = self.travelnum
        Pos = 0
        allS=0
        flag = True
        citylist = []
        for i in range(sightNum):
            self.Dm[Pos][randSight[i]] = 1
            self.travelDis += D[Pos][randSight[i]]
            Pos = randSight[i]
            citylist.append(b[Pos].index(1))
        self.Dm[Pos][0] = 1
        self.travelDis += D[Pos][0]
        # 计算每个城市的消费
        citynum = int(len(set(citylist)))
        self.money += citynum * citymoney
        self.money += sightNum * 30

        # 杭州arrive回来 leave 出发
        self.Timelist[0] = [0, 7]
        lastPos = 0
        # v  # 采取的速度
        driveTime = 0
        s1 = 0  # 油费
        s2 = 0  # 住宿费
        s3 = 0  # 停车费
        s4 = 0  # 吃饭费用
        s5 = 0  # 旅游消费
        s6 = 0  # 门票消费
        S = 0  # 总消费
        cityset = []
        tianshu = 0
        shouyi = 50
        for i in range(sightNum):
            nowPos = randSight[i]
            # 一个人门票钱先付了
            self.money += Food[nowPos][4]
            # 两个人
            # self.money +=Food[nowPos][4]+Food[nowPos][5]
            # 先判断是否再同一个市内s
            if (b[nowPos].index(1) == b[lastPos].index(1)):
                v = v1
                o = o1
            else:
                v = v0
                o = o0
            driveTime = round(D[lastPos][nowPos] / v, 1)
            self.money += D[lastPos][nowPos] * o
            # 这时候要 进行很多的判断
            # 判断1：正常的到达 在门前1小时 并且是睡觉前一小时
            if (self.Timelist[i][1] % 24 + driveTime <= min(Food[nowPos][3] - 1, 21)):
                temp = len(set(cityset))
                cityset.append(b[nowPos].index(1))
                # 旅游费用第一次来这个城市

                if (len(set(cityset)) > temp):
                    s5 += citymoney
                s1 += D[nowPos][lastPos] * o
                s6 += Food[nowPos][4]
                s3 += 30
                arrive = self.Timelist[i][1] + driveTime
                self.Timelist[i + 1][0] = arrive
                arrive = arrive % 24
                playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
                self.Timelist[i + 1][1] = self.Timelist[i + 1][0] + playtime
                # 判断2：开不到终点
            elif (self.Timelist[i][1] % 24 + driveTime >= 22):
                # istime=22-self.Timelist[i][1]%24
                # notime=driveTime-istime
                tianshu = tianshu + 1
                # 开始结算
                s1 += D[nowPos][lastPos] * o
                s2 = sleepmoney
                s4 = shopmoney
                S = s1 + s2 + s3 + s4 + s5 + s6
                s1 = 0  # 油费
                s2 = 0  # 住宿费
                s3 = 0  # 停车费
                s4 = 0  # 吃饭费用
                s5 = 0  # 旅游消费
                s6 = 0  # 门票消费
                allS+=S
                self.zichan = self.zichan - S + shouyi
                # self.money +=S
                if (self.zichan <= 0):
                    return False
                # 第二天去了
                s6 += Food[nowPos][4]
                s3 += 30
                temp = len(set(cityset))
                cityset.append(b[nowPos].index(1))
                # 旅游费用第一次来这个城市
                if (len(set(cityset)) > temp):
                    s5 += citymoney

                arrive = self.Timelist[i][1] + driveTime + sleeptime
                self.Timelist[i + 1][0] = arrive
                arrive = arrive % 24
                if min(8, 22 - arrive, Food[nowPos][3] - arrive) < 1:
                    print("!!!!!!!!!!!!!!!!!!!!")
                playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
                self.Timelist[i + 1][1] = self.Timelist[i + 1][0] + playtime
                if (self.Timelist[i + 1][1] < self.Timelist[i + 1][0]):
                    print("判断2")
            # 判断3 开到了终点但是没时间玩 直接睡觉 明早开始玩  一定是开得到的
            elif (self.Timelist[i][1] % 24 + driveTime > Food[nowPos][3] - 1 and self.Timelist[i][
                1] % 24 + driveTime % 24 < 22):
                # 开始结算
                s1 += D[nowPos][lastPos] * o
                s2 = sleepmoney
                s4 = shopmoney
                S = s1 + s2 + s3 + s4 + s5 + s6
                s1 = 0  # 油费
                s2 = 0  # 住宿费
                s3 = 0  # 停车费
                s4 = 0  # 吃饭费用
                s5 = 0  # 旅游消费
                s6 = 0  # 门票消费
                allS += S
                self.zichan = self.zichan - S + shouyi
                if (self.zichan <= 0):
                    return False
                # self.money +=S

                # 第二天去了
                s6 += Food[nowPos][4]
                s3 += 30
                temp = len(set(cityset))
                cityset.append(b[nowPos].index(1))
                # 旅游费用第一次来这个城市
                if (len(set(cityset)) > temp):
                    s5 += citymoney

                arrive = self.Timelist[i][1] + (22 - self.Timelist[i][1] % 24) + sleeptime
                waittime = max(0, Food[nowPos][2] - 7)
                arrive = arrive + waittime
                self.Timelist[i + 1][0] = arrive
                arrive = arrive % 24
                if min(8, 22 - arrive, Food[nowPos][3] - arrive) < 1:
                    print("!!!!!!!!!!!!!!!!!!!!????????")
                playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
                self.Timelist[i + 1][1] = self.Timelist[i + 1][0] + playtime
                if (self.Timelist[i + 1][1] < self.Timelist[i + 1][0]):
                    print("判断3")
            elif (self.Timelist[i][1] % 24 + driveTime > 21 and self.Timelist[i][1] % 24 + driveTime <= 22):
                # 开始结算
                s1 += D[nowPos][lastPos] * o
                s2 = sleepmoney
                s4 = shopmoney
                S = s1 + s2 + s3 + s4 + s5 + s6
                s1 = 0  # 油费
                s2 = 0  # 住宿费
                s3 = 0  # 停车费
                s4 = 0  # 吃饭费用
                s5 = 0  # 旅游消费
                s6 = 0  # 门票消费
                allS += S
                self.zichan = self.zichan - S + shouyi
                if (self.zichan <= 0):
                    return False
                # self.money += S
                # 第二天去了
                s6 += Food[nowPos][4]
                s3 += 30
                temp = len(set(cityset))
                cityset.append(b[nowPos].index(1))
                # 旅游费用第一次来这个城市
                if (len(set(cityset)) > temp):
                    s5 += citymoney

                waittime = max(0, Food[nowPos][2] - 7)
                waitsleep = 22 - self.Timelist[i][1] % 24 - driveTime
                # print(waittime,waitsleep)
                self.Timelist[i + 1][0] = self.Timelist[i][1] + waitsleep + sleeptime + waittime + driveTime
                playtime = random.uniform(1, min(8, Food[nowPos][3] - self.Timelist[i + 1][0] % 24,
                                                 22 - self.Timelist[i + 1][0] % 24))
                self.Timelist[i + 1][1] = self.Timelist[i + 1][0] + playtime
                # if playtime<4:
                #  print(playtime,22-self.Timelist[i+1][0]%24)
                if (self.Timelist[i + 1][1] < self.Timelist[i + 1][0]):
                    print("判断4")
                    # print(playtime,Food[nowPos][3]-self.Timelist[i+1][0]%24,22-self.Timelist[i+1][0]%24)
            else:
                print('1134srtw534s')
                # print(self.Timelist[i][1], driveTime)

            lastPos = nowPos
        # 最后开回去
        driveTime = round(D[lastPos][0] / v0, 1)
        # 直接开回去
        # 直接到家
        self.money += D[lastPos][0] * o0
        if (self.Timelist[sightNum][1] % 24 + driveTime % 24 <= 22):
            # 结算了
            s1 += D[lastPos][0] * o0
            s4 = shopmoney
            S = s1 + s2 + s3 + s4 + s5 + s6
            # self.money +=S
            allS += S
            self.zichan = self.zichan - S + shouyi
            if (self.zichan <= 0):
                return False

            self.Timelist[0][0] = self.Timelist[sightNum][1] + driveTime
        # 睡一晚再回家
        if (self.Timelist[sightNum][1] % 24 + driveTime % 24 > 22):
            # 结算了
            s1 += D[lastPos][0] * o0
            s4 = shopmoney
            s2 = sleepmoney
            S = s1 + s2 + s3 + s4 + s5 + s6
            # self.money +=S
            allS += S
            self.zichan = self.zichan - S + shouyi
            if (self.zichan <= 0):
                return False
            self.Timelist[0][0] = self.Timelist[sightNum][1] + driveTime + sleeptime
        self.money += int(self.Timelist[0][0] / 24) * sleepmoney
        self.money += (int(self.Timelist[0][0] / 24) + 1) * shopmoney
        self.mo=allS

        # 第一题的约束
        flag = judge(self)

        """if(self.Timelist[0][0]/24<13):
            flag=False
        if (self.Timelist[0][0] / 24 >= 14):
            flag = False"""
        return flag


def judge(X):
    travellist = X.travellist
    Timelist = X.Timelist
    travelnum = X.travelnum
    money = X.money
    flag = True

    # 判断是否满足规划要求
    # 判断1时间是否满足要求1
    travellist = X.travellist
    """ if Timelist[0][0]/24>14:
        flag=False
        return False
    """
    # 再要求两个礼拜时才需要
    if Timelist[0][0] / 24 < 5:
        flag = False
        return False
    # 判断2旅游序列是否不重复
    if (len(set(travellist)) < len(travellist)):
        flag = False
        return False
    # return flag
    """
    #判断3是否满足美食要求
    score=travelnum
    citylist=[]
    foodlist=[]

    for i in range(travelnum):
        #print(travelnum)
        sight=travellist[i]
       # print(sight)
        way=[1 for i in range(travelnum)]
        
        city=b[sight].index(1) #找到对应的城市编号
        if(city==14):
           # print("马鞍山")
            way[i]=0
            score = score -1
            continue
        citylist.append(city)

        if(Food[sight][0]==1 and way[i]==1):
            foodlist.append(b[sight].index(1))
            #print("他是美食")
            #flag=True
            for k in range(travelnum):
                if b[travellist[k]].index(1) == city and way[k]==1:
                    #remT=travellist[k]
                    #templist.remove(remT)
                   # print("找到城市")
                    score= score-1
                    way[k]=0
            continue
    
    if(len(set(citylist))-len(set(foodlist))<3):
        print(len(set(citylist)),len(set(foodlist)))
    #print("score:"+str(score))
    if(1 in way):
        flag=False
        return flag
    return flag
    #ravellist=X.travellist
    #判断4 是否满足红色要求 
    for i in range(travelnum):
            sight=travellist[i]
            templist=travellist
            way=[1 for i in range(travelnum)]
            #flag=False
            city=b[sight].index(1) #找到对应的城市编号
            if(city==14):
                way[i]=0
            if(Food[sight][1]==1 and way[i]==1):
                #flag=True
                for k in range(travelnum):
                    if b[travellist[k]].index(1) == city:
                        #remT=travellist[k]
                        #templist.remove(remT)
                        way[k]=0
                continue
    if(1 in way):
            flag=False
            return False
    #travellist=X.travellist
    """

    # 判断5 是否超出金钱规划
    lastPos = 0
    for i in range(len(travellist)):
        # 一个人的情况
        money += Food[travellist[i]][4]
        ##两个人的情况
        ##money +=Food[travellist[i]][4]+Food[travellist[i]][5]
        nowPos = travellist[i]
        if (b[lastPos].index(1) == b[nowPos].index(1)):  # 同一个市
            money += D[lastPos][nowPos] * o1
        else:
            money += D[lastPos][nowPos] * o0
        lastPos = nowPos
    money += D[lastPos][0] * o0
    money += int(Timelist[0][0] / 24) * sleepmoney  # 住宿消费
    money += (int(Timelist[0][0] / 24) + 1) * shopmoney  # 日常消费
    # print("消费为"+str(money))
    # if(money > 5000):
    #   flag=False
    #  return False
    #X.money = money
    return flag


class Population:
    def __init__(self, pop_size):
        """
        Create Population.
        param pop_size: size of population
        param parents: list of parents
        param front: nondomination front, dim1: rank, dim2: list of nondomination individual
        """
        self.pop_size = pop_size
        self.parents = []
        self.offspring = []
        self.front = []
        self.SEED = 0

    def create_son(self):
        """
        Create son population.
        Crossover using intermediate recombination.
        Mutate using flipover.
        """
        # crossover SBX算法
        self.offspring = []
        for idx in range(0, int(N / 2)):
            son1 = Individual()
            son2 = Individual()
            p = random.sample(self.parents, 2)  # random sample 2 parents
            self.SEED += 1
            # 这部分就是说选取两个父代来进行交叉生成子代
            min_value = min(p[0].travelnum, p[1].travelnum)
            if min_value < 2:
                continue
            randPos = random.sample(range(1, min_value), 1)[0]

            templist = 0
            son1.travellist = p[1].travellist[0:randPos]
            son1.travellist.extend(p[0].travellist[randPos:-1])
            son2.travellist = p[0].travellist[0:randPos]
            son2.travellist.extend(p[1].travellist[randPos:-1])
            son1.travelnum = len(son1.travellist)
            son2.travelnum = len(son2.travellist)
            flag1 = True
            flag2 = True
            # 判断所到地点有没有重复
            if (len(set(p[0].travellist)) is not len((p[0].travellist))):
                flag1 = False
            if (len(set(p[1].travellist)) is not len((p[1].travellist))):
                flag2 = False

            # 变异
            if (flag1 == True):
                for i in range(len(son1.travellist)):
                    self.SEED += 1
                    random.seed(self.SEED)
                    r = random.random()
                    if (r <= pm):
                        son1.travellist[i] = random.randint(1, 79)
                result = son1.plan()
                if (result == True):
                    son1.cal_object_value()
                    self.offspring.append(son1)
            if (flag2 == True):
                for i in range(len(son2.travellist)):
                    self.SEED += 1
                    random.seed(self.SEED)
                    r = random.random()
                    if (r <= pm):
                        son2.travellist[i] = random.randint(1, 79)
                result = son2.plan()
                if result:
                    son2.cal_object_value()
                    self.offspring.append(son2)

    def is_dominate_with_n(a, b):
        pass

    def is_dominate(self, a, b):
        """
        Judge if a dominate b.
        """
        flag = True
        for i in range(0, obj_num):
            if (b.M[i] < a.M[i]):
                flag = False
                break
        return flag

    def cal_nondomination(self):
        # initialize 
        for p in self.parents:
            p.n = p.rank = 0
            p.S = []
        self.front = []
        self.front.append([])

        for p in self.parents:
            for q in self.parents:
                if (p is q):
                    continue
                if (self.is_dominate(p, q)):
                    p.rank = 1
                    p.S.append(q)
                elif (self.is_dominate(q, p)):
                    p.n = p.n + 1
            if (p.n == 0):
                p.rank = 1
                self.front[0].append(p)
        i = 0
        while (len(self.front[i]) > 0):
            Q = []
            for p in self.front[i]:
                for q in p.S:
                    q.n = q.n - 1
                    if (q.n == 0):
                        q.rank = i + 1
                        Q.append(q)
            i = i + 1
            self.front.append(Q)
        self.front.pop(-1)  # !!! 计算到最后会将空集加入到self.front中，需要将其删除

    def cal_distance(self, F):
        """
        Caculating crowding distance assignment of nondominated sets
        """
        for p in F:  # initialize distance
            p.dis = 0

        for m in range(0, obj_num):  # for each object m
            if (len(F) <= 2):
                continue
            else:
                F.sort(key=lambda p: p.M[m])  # sort using each objective value
                I = Individual()
                I.dis = INF
                F.append(I)
                I.dis = -INF  # 左边为负无穷大（不是正无穷），右边为正无穷大，边缘点都能被选择到
                F.insert(0, I)  # so that boundary points are always selected
                l = len(F)
                # print(l)
                # print(m)
                # print(F[l-2].M)
                # print(F[1].M)
                norm = F[l - 2].M[m] - F[1].M[m]
                if (norm > eps):
                    infactor = 1.0 / norm
                else:
                    infactor = 1
                for j in range(1, l - 1):
                    F[j].dis = F[j].dis + (F[j + 1].M[m] - F[j - 1].M[m]) * infactor

                F.pop(0)
                F.pop(-1)
        return F

test=Individual()
test.travellist=[11,45,58,49,48,10,74,71,54,59,39,47,8,7,70]
test.plan()
pop = Population(pop_size=N)
# 初始化种群 50个解
for i in range(maxepoch):
    flag = True
    sightNum = random.randint(7, 42)
    randSight = L1 = random.sample(range(1, 80), sightNum)

    I = Individual()
    I.travellist = randSight
    I.travelnum = sightNum
    """Pos = 0
    citylist=[]
    for i in range(sightNum):
        I.Dm[Pos][randSight[i]] = 1
        citylist.append(b[randSight[i]].index(1))
        I.travelDis += D[Pos][randSight[i]]
        Pos = randSight[i]

    I.Dm[Pos][0] = 1
    I.travelDis += D[Pos][0]

    # 杭州arrive回来 leave 出发
    I.Timelist[0] = [0, 7]
    lastPos = 0
    # v  # 采取的速度
    driveTime = 0
    for i in range(sightNum):
        nowPos = randSight[i]
        #一个人门票钱先付了
        I.money +=Food[nowPos][4]
        #两个人
        #self.money +=Food[nowPos][4]+Food[nowPos][5]
        # 先判断是否再同一个市内s
        if (b[nowPos].index(1) == b[lastPos].index(1)):
            v = v1
            o=o1
        else:
            v = v0
            o=o0
        driveTime = round(D[lastPos][nowPos] / v, 1)
        I.money += D[lastPos][nowPos] * o
        # 这时候要 进行很多的判断
        # 判断1：正常的到达 在门前1小时 并且是睡觉前一小时
        if (I.Timelist[i][1] % 24 + driveTime <= min(Food[nowPos][3] - 1, 21)):
            arrive = I.Timelist[i][1] + driveTime
            I.Timelist[i + 1][0] = arrive
            arrive = arrive % 24
            if min(8, 22 - arrive, Food[nowPos][3] - arrive) < 1:
                print("!!!!!!!!??????!!")
            playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
            I.Timelist[i + 1][1] = I.Timelist[i + 1][0] + playtime

            if (I.Timelist[i + 1][1] < I.Timelist[i + 1][0]):
                print("判断1")
        # 判断2：开不到终点
        elif (I.Timelist[i][1] % 24 + driveTime >= 22):
            # istime=22-I.Timelist[i][1]%24
            # notime=driveTime-istime
            arrive = I.Timelist[i][1] + driveTime + sleeptime
            I.Timelist[i + 1][0] = arrive
            arrive = arrive % 24
            if min(8, 22 - arrive, Food[nowPos][3] - arrive) < 1:
                print("!!!!!!!!!!!!!!!!!!!!")
            playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
            I.Timelist[i + 1][1] = I.Timelist[i + 1][0] + playtime
            if (I.Timelist[i + 1][1] < I.Timelist[i + 1][0]):
                print("判断2")
        # 判断3 开到了终点但是没时间玩 直接睡觉 明早开始玩  一定是开得到的
        elif (I.Timelist[i][1] % 24 + driveTime > Food[nowPos][3] - 1 and I.Timelist[i][
            1] % 24 + driveTime % 24 < 22):
            arrive = I.Timelist[i][1] + (22 - I.Timelist[i][1] % 24) + sleeptime
            waittime = max(0, Food[nowPos][2] - 7)
            arrive = arrive + waittime
            I.Timelist[i + 1][0] = arrive
            arrive = arrive % 24
            if min(8, 22 - arrive, Food[nowPos][3] - arrive) < 1:
                print("!!!!!!!!!!!!!!!!!!!!????????")
            playtime = random.uniform(1, min(8, 22 - arrive, Food[nowPos][3] - arrive))
            I.Timelist[i + 1][1] = I.Timelist[i + 1][0] + playtime
            if (I.Timelist[i + 1][1] < I.Timelist[i + 1][0]):
                print("判断3")
        elif (I.Timelist[i][1] % 24 + driveTime > 21 and I.Timelist[i][1] % 24 + driveTime <= 22):
            waittime = max(0, Food[nowPos][2] - 7)
            waitsleep = 22 - I.Timelist[i][1] % 24 - driveTime
            # print(waittime,waitsleep)
            I.Timelist[i + 1][0] = I.Timelist[i][1] + waitsleep + sleeptime + waittime + driveTime
            playtime = random.uniform(1, min(8, Food[nowPos][3] - I.Timelist[i + 1][0] % 24,
                                             22 - I.Timelist[i + 1][0] % 24))
            I.Timelist[i + 1][1] = I.Timelist[i + 1][0] + playtime
            # if playtime<4:
            #  print(playtime,22-I.Timelist[i+1][0]%24)
            if (I.Timelist[i + 1][1] < I.Timelist[i + 1][0]):
                print("判断4")
                # print(playtime,Food[nowPos][3]-I.Timelist[i+1][0]%24,22-I.Timelist[i+1][0]%24)ƒse
        lastPos = nowPos
    # 最后开回去
    driverTime = round(D[lastPos][0] / v0, 1)

    # 直接开回去
    # 直接到家
    ##车费
    I.money +=D[lastPos][0]*o0
    if (I.Timelist[sightNum][1] % 24 + driveTime % 24 <= 22):
        I.Timelist[0][0] = I.Timelist[sightNum][1] + driveTime
    # 睡一晚再回家
    if (I.Timelist[sightNum][1] % 24 + driveTime % 24 > 22):
        I.Timelist[0][0] = I.Timelist[sightNum][1] + driveTime + sleeptime
    days=I.Timelist[0][0]/24
    #住宿费
    money +=int(days)*sleepmoney
    money +=(int(days)+1)*shopmoney
    flag=judge(I)
    """
    flag = I.plan()
    if (flag == True):
        flag1 = judge(I)
        if (flag1 == True):
            print('采用')
            pop.parents.append(I)
            print("种群数：" + str(len(pop.parents)))
            I.cal_object_value()
    if (len(pop.parents) == N):
        print("初始化完毕")
        break

# eva.evaluate_DTLZ(pop.parents, bound, problems.Func, object_name, eva = False, draw = True)
tott = 0
for generation in range(1, max_gen):
    t1 = time.time()
    # create offspring
    pop.create_son()
    # combine parent and offspring population->Rt
    pop.parents.extend(pop.offspring)

    # calculate all nondominate front of Rt
    pop.cal_nondomination()
    # for f in pop.front:
    #     print(len(f))
    # select next generation
    P = []
    for F in pop.front:
        F = pop.cal_distance(F)
        if (len(P) + len(F) <= N):
            P.extend(F)
        else:
            F.sort(key=lambda p: -p.dis)
            for p in F:
                if (len(P) >= N):
                    break
                P.append(p)
            break
    pop.parents = P
    t2 = time.time()
    tott = tott + t2 - t1
    if (generation % 20 == 0):
        print('gen:', generation)
    #FileProcessing.write_excel("M5.xls", P)
    FileProcessing.write_file("out5_1.txt", P)
    #FileProcessing.write_file2("M1_5.txt", P)

    # eva.evaluate_DTLZ(pop.parents, bound, problems.Func, object_name, eva = False, draw = True)
print('NSGA_t:', tott / max_gen)
# eva.evaluate_DTLZ(pop.parents , bound, problems.Func, object_name, eva = True, draw = True)
