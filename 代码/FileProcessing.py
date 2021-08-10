def write_file(file_name, P):
    file_handle = open(file_name, mode='w')
    a = [[1, 2, 3], [2, 3, 4]]
    for i in range(len(P)):
        file_handle.write(str(i) + "  ")
        file_handle.write(str(P[i].travelDis) + "  ")
        file_handle.write("四个目标值 ")
        for j in range(len(P[i].M)):
            file_handle.write(str(P[i].M[j]) + ' ')
        file_handle.write("规划路径 ")
        for j in range(len(P[i].travellist)):
            file_handle.write(str(P[i].travellist[j]) + ' ')
        file_handle.write("规划时间 ")
        for j in range(len(P[i].Timelist)):
            file_handle.write('[' + str(P[i].Timelist[j][0]) + ',' + str(P[i].Timelist[j][1]) + ']')

    file_handle.write('\n')
    file_handle.close()
