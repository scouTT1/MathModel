import numpy as np
import requests
import json
import xlrd
import xlwt

API_KEY = 'ce4b19a6d271ab0ca6470e50e9d34b4e'  # API_KEY为高德地图接口密钥


def get_location(county):  # 设置函数转换经纬度
    url = 'https://restapi.amap.com/v3/geocode/geo'  # 高德API地理编码服务地址
    params = {'key': API_KEY,  # 参数1：个人申请的高德密钥
              'address': county}  # 参数2：需要转换经纬度的位置名称
    try:
        response = requests.get(url, params)  # 使用requests模块的get方法请求网址数据
        jd = json.loads(response.text)  # 数据json格式化
        return jd['geocodes'][0]['location']  # 读取需要的location值
    except:
        return '未获取经纬度'  # 利用try-except设置防呆机制


def get_distance(origin, destination):  # 设置函数计算两经纬度间驾车距离
    url = 'https://restapi.amap.com/v3/direction/driving'  # 高德API驾车路径规划服务地址
    params = {'key': API_KEY,  # 参数1：个人申请的高德密钥
              'origin': origin,  # 参数2：起始点的经纬度坐标
              'destination': destination,  # 参数3：目的地的经纬度坐标
              'extensions': 'base'}  # 参数4：返回结果控制选项，必填项，base:返回基本信息；all：返回全部信息
    try:
        response = requests.get(url, params)  # 使用requests模块的get方法请求网址数据
        jd = json.loads(response.text)  # 数据json化
        return jd['route']['paths'][0]['distance']  # 读取需要的distance值
    except:
        return 0  # 利用try-except设置防呆机制，这里设置距离0表示未成功获取两地间的距离


if __name__ == '__main__':
    workbook = xlrd.open_workbook("./长江三角洲景点信息_1517.xlsx")
    sheet1 = workbook.sheet_by_index(2)
    nrows = sheet1.nrows  # 获取sheet工作表的行数
    ncols = sheet1.ncols  # 获取sheet工作表的列数
    position_list = []
    city_list = ['杭州']
    city_dict = {}
    food_dict = {}
    red_dict = {}
    for i in range(1, nrows):
        pos = sheet1.cell_value(i, 1)  # 获取景点名
        city = sheet1.cell_value(i, 0)  # 获取城市名
        if city not in pos:
            pos = city + pos
        position_list.append(pos)
        if city not in city_list:
            city_list.append(city)
        city_dict[pos] = city
        food_dict[pos] = sheet1.cell_value(i, 8)
        red_dict[pos] = sheet1.cell_value(i, 9)
    position_list.insert(0, '杭州')

    # 计算距离矩阵，0位置为杭州
    dist = np.zeros(shape=(len(position_list), len(position_list)))
    location_dict = {}
    for i in range(len(position_list)):
        location_dict[position_list[i]] = get_location(position_list[i])
    print("成功储存所有景点位置")
    # length = int(len(position_list) / 3)
    # for i in range(length): # 第一个人
    # for i in range(length, len(position_list)): #第二个人
    for i in range(len(position_list)):
        for j in range(i + 1, len(position_list)):
            res = float(get_distance(location_dict[position_list[i]], location_dict[position_list[j]])) / 1000
            print(position_list[i], position_list[j], res)
            dist[i, j] = res
            dist[j, i] = res

    # 计算景点所属城市矩阵
    belong = np.zeros(shape=(len(position_list), len(city_list)))
    for i in range(1, len(position_list)):
        for j in range(len(city_list)):
            if city_dict[position_list[i]] == city_list[j]:
                belong[i, j] = 1

    f = xlwt.Workbook()
    sheet1 = f.add_sheet('dist')
    for i in range(len(position_list)):
        for j in range(len(position_list)):
            if i == 0:
                sheet1.write(i, j + 1, position_list[j])
            if j == 0:
                sheet1.write(i + 1, j, position_list[i])
            sheet1.write(i + 1, j + 1, dist[i, j])

    sheet2 = f.add_sheet('belong')
    for i in range(len(position_list)):
        for j in range(len(city_list)):
            if i == 0:
                sheet2.write(i, j + 1, city_list[j])
            if j == 0:
                sheet2.write(i + 1, j, position_list[i])
            sheet2.write(i + 1, j + 1, belong[i, j])

    sheet3 = f.add_sheet('label')
    sheet3.write(0, 0, '景点')
    sheet3.write(0, 1, '美食')
    sheet3.write(0, 2, '红色')
    for i in range(1, len(position_list)):
        sheet3.write(i + 1, 0, position_list[i])
        sheet3.write(i + 1, 1, food_dict[position_list[i]])
        sheet3.write(i + 1, 2, red_dict[position_list[i]])

    f.save('pre_data1.xls')

    # result = int(get_distance(get_location('上海东方明珠'), get_location('北京天安门'))) / 1000  # 距离单位转换为公里
    # print('两地距离为:' + str(result) + '公里')  # 显示两地间距离
