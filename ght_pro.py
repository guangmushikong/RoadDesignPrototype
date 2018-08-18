import os
import copy


class Ght_pro():
    def __init__(self):
        print('开始处理...')
        self.path = input('输入文件路径：')
        self.name = input('输入文件名：')

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

    def savetxt(self, datalist, savename, savepath):  # 保存deepmotion转换后的数据为txt 参数：保存数据（list），保存文件名（str）,保存路径（str）
        path = savepath
        name = savename
        datacopy = copy.deepcopy(datalist)
        file = open(os.path.join(path, savename), 'w')
        for line in datacopy:
            line_str = str(line)
            try:
                line_str0 = line_str.replace("'", "")
                line_str1 = line_str0.replace(',', ' ')
            except:
                pass
            line_str2 = line_str1.replace('[', '')
            line_str3 = line_str2.replace(']', '\n')
            file.write(line_str3)
        file.close()
        print(savename + '保存成功！')

    def read_ght(self):
        data = self.readtxt(self.name, self.path, ' ')
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
        # print('skw:')
        # for line in skw:
        #     print(line)
        # print('others:')
        # for line in other:
        #     print(line)
        self.savetxt(skw, self.name[0:-4]+'.skw', self.path)
        self.savetxt(other, self.name[0:-4]+'.txt', self.path)

    def pro(self):
        self.read_ght()

def main():
    ex = Ght_pro()
    ex.pro()

main()