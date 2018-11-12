import os
import copy
from math import radians, cos, sin, asin, sqrt
import ght_pro


class Route_merge():

    def __init__(self):
        print('开始处理！')
        self.path = 'F:/04_Cateye/02_data/QZHD_merge/data'
        self.ky = input('输入合并测线阈值：')
        os.chdir(self.path)
        # 获取文件夹下的文件列表并排序
        self.filelist = []
        allfiles = os.listdir(os.path.join(self.path, 'ght'))
        for var in allfiles:
            if os.path.isdir(var)==False:
                self.filelist.append(int(var[0:-4]))
            else:
                print('存在目录')

        self.filelist = list(set(self.filelist)) #去重
        self.filelist.sort()  #排序

        # 创建output文件夹
        if os.path.isdir(self.path + '/' + self.ky) == False:
            print(self.ky+'文件夹不存在！')
            os.mkdir(self.path + '/' + self.ky)
            print(self.ky+'文件夹创建成功！')
        print('allfile:', self.filelist)

    # 通过经纬度计算距离
    def haversine(self, lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # 将十进制度数转化为弧度
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球平均半径，单位为公里
        return (c * r * 1000)

    def readtxt(self, filename, filepath, splitstr):
        path = filepath
        name = filename
        path_name = os.path.join(path, name)
        data_list = []
        fn = open(path_name)
        for line in fn:
            temp = line.split(splitstr)
            data_list.append(temp)
        fn.close()
        return (data_list)

    def read_ght(self, name):
        data = self.readtxt(name, os.path.join(self.path,'ght'), ' ')
        skw = []
        other = []

        for i in range(3, len(data)-6):
            line = data[i]
            # print(line)
            if 'A1' in line[0] or 'B1' in line[0]:
                skw_line = ['%.5f'%float(line[2]), '%.5f'%float(line[1]), int(line[3]), 100, 0, 0, 0, 0, 0, 0, 0]
                skw.append(skw_line)
            elif 'A2' in line[0]:
                skw_line = ['%.5f'%float(line[2]), '%.5f'%float(line[1]), int(line[3]), 1, 0, 0, 0, 0, 0, 0, 0]
                skw.append(skw_line)
            elif 'B2' in line[0]:
                skw_line = ['%.5f'%float(line[2]), '%.5f'%float(line[1]), int(line[3]), 0, 0, 0, 0, 0, 0, 0, 0]
                skw.append(skw_line)
            else:
                other_line = [line[0], '%.5f'%float(line[2]), '%.5f'%float(line[1]), int(line[3]), int(line[4])]
                other.append(other_line)
        return(data, skw, other)  #返回ght,skw,txt三个文件

    def route_dis(self, name):
        # 读取文件内容
        ght = []
        skw = []
        txt = []
        ght,skw,txt = self.read_ght(name)
        # print(len(ght))
        # print(len(skw))
        # print(len(txt))
        dis = 0.0
        for i in range(3,len(ght)-7):
            # print('i=', i)
            lon1 = float(ght[i][2])
            lat1 = float(ght[i][1])
            lon2 = float(ght[i+1][2])
            lat2 = float(ght[i+1][1])
            dis_temp = self.haversine(lon1, lat1, lon2, lat2)
            dis = dis + dis_temp
        # print(name+'路线长度为：',dis/1000,'km')
        return(dis/1000)

    def savetxt(self, datalist, savename, savepath):
        path = savepath
        name = savename
        datacopy = copy.deepcopy(datalist)
        file = open(os.path.join(path, savename), 'w')
        for line in datacopy:
            line_str = str(line)
            # print(line_str)
            try:
                line_str0 = line_str.replace("'", "")
                line_str1 = line_str0.replace(',', '')
            except:
                pass
            line_str2 = line_str1.replace('[', '')
            line_str3 = line_str2.replace(']', '\n')
            file.write(line_str3)
        file.close()
        print(savename + '保存成功！')

    # ght合并
    def ght_merge(self, filelist, savename):
        name_0 = filelist[0]
        data_start = self.readtxt(name_0, os.path.join(self.path, 'ght'), ' ')
        head = data_start[0:3]
        end = data_start[-6:]
        merge_list = []
        for val in filelist:
            data_temp = self.readtxt(val, os.path.join(self.path, 'ght'), ' ')
            del data_temp[0:3]
            del data_temp[-6:]
            merge_list = merge_list + data_temp
        merge_list = head + merge_list + end
        # 去掉行末的\n
        for i in range(len(merge_list)):
            # print(merge_list[i])
            merge_list[i][-1] = merge_list[i][-1][:-1]
        # print(len(merge_list))
        # 保存合并后的ght文件
        self.savetxt(merge_list, savename, os.path.join(self.path, self.ky))

    # 计算合并文件(待完善),#filelist:排序好之后的文件名，每个路线的长度字典{3：71.000}
    def merge_file(self, filelist, dis_list):
        ky = int(self.ky)    #阈值为280km
        list_pro = []   # 存储处理之后的数据
        merge_list = []
        temp_start = 0
        for i in range(len(dis_list)-1):
            # print('filelist:', filelist[temp_start:i+1])
            # print('dislist:', dis_list[temp_start:i+1])
            sumi = sum(dis_list[temp_start:i+1])
            if sumi >= ky:
                temp_start = i
                list_pro.append(i-1)
                merge_list.append(filelist[i-1])
        merge_list.insert(0, filelist[0])
        merge_list.append(filelist[-1])
        # print(merge_list)
        # print(list_pro)
        merge_list = []    # 合并后的文件名列表
        for i in range(len(list_pro)-1):
            start_index = list_pro[i]+1
            end_index = list_pro[i+1]
            # print('start=%d,end=%d' % (start_index, end_index))
            temp_filename = str(filelist[start_index]) + '-' + str(filelist[end_index])
            merge_list.append(temp_filename)
        merge_list.insert(0, str(filelist[0])+'-'+str(filelist[list_pro[0]]))
        merge_list.append(str(filelist[list_pro[-1]+1])+'-'+str(filelist[-1]))
        return(merge_list)

    def pro(self):
        # filelist=[3,4,5,6,7,8,9,10,11,12,13,14,15]
        filelist = self.filelist
        dis_dict = {}    # 文件名：距离 字典
        dis_list = []    # 文件名列表
        for val in filelist:
            filename = str(val)+'.ght'
            dis_temp = self.route_dis(filename)
            dis_dict[val] = dis_temp
            # list_temp = [val, dis_temp]
            dis_list.append(dis_temp)
        # print(filelist)
        print(dis_list)
        merge_list = self.merge_file(filelist, dis_list)
        for val in merge_list:
            start = int(val.split('-')[0])
            end = int(val.split('-')[1])
            start_index = filelist.index(start)

            end_index = filelist.index(end)
            part_filelist = filelist[start_index:(end_index+1)]
            part_namelist = []
            for var in part_filelist:
                part_namelist.append(str(var)+'.ght')
            self.ght_merge(part_namelist, val+'.ght')


if __name__ == '__main__':
    ex = Route_merge()
    ex.pro()
    ex1 = ght_pro.Ght_pro()
    ex1.pro()

