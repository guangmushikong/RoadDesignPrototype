from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import os
import sys
import math
import pandas as pd
import numpy as np
# import DeepMotion_pro.myfun as myfun
import sxg_python.myfun as myfun
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False

class line_raster_pro():
    def __init__(self):
        print('开始处理！')
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        ogr.RegisterAll()
        self.driver = ogr.GetDriverByName('ESRI Shapefile')

        ##古交
        self.path = 'F:/Cateye/data/contour_50-100-200'
        self.name = 'sectionline.shp'
        self.rastername = 'gujiaodem.tif'
        self.save_name = 'gujiao'
        self.epsg = 32649

        ##静庄
        # self.path = 'E:/cateye/data/jingzhuang'
        # self.name = 'jinzhuang_pro.shp'
        # self.rastername = 'TIN_raster6.tif'
        # self.save_name = 'jinzhuang'
        # self.epsg = 2423

        # os.chdir(self.path)
        self.length = 50

    def ReadLineshp(self):
        data_path = self.path
        data_name = self.name
        ds = ogr.Open(os.path.join(data_path, data_name), 0)
        # ds = ogr.Open(data_name, 0)
        if ds == None:
            print('打开文件%s失败！' % os.path.join(data_path, data_name))
        else:
            print('打开文件%s成功！' % os.path.join(data_path, data_name))
        lyr = ds.GetLayer(0)
        spatialref = lyr.GetSpatialRef()
        # epsg = 2432
        feanum = lyr.GetFeatureCount()
        if feanum != 1:
            print('数据个数不为1，请检查数据"%s"' %data_name)
            sys.exit()
        feature = lyr.GetNextFeature()
        ft_geo = feature.geometry()
        points = ft_geo.GetPoints()   #获取点坐标
        # print(ft_geo)
        # print(points)
        if ft_geo.GetGeometryName() != 'LINESTRING':    #返回要素类型
            print('要素类型错误，请检查数据！')
            sys.exit()
        point_num = len(points)
        print('点个数为%d'%point_num)
        output_points = []   #存储分割后的点坐标（投影后）
        contour_length = self.length   #间隔距离
        for i in range(point_num-1):
            start_x = points[i][0]
            start_y = points[i][1]
            end_x = points[i+1][0]
            end_y = points[i+1][1]
            # print(start_x,start_y,end_x,end_y)
            dis = math.sqrt(pow((end_y-start_y),2)+pow((end_x-start_x),2))
            # print('dis=%f' % dis)
            if dis<=contour_length:
                output_points.append((start_x, start_y))
                # output_points.append((end_x, end_y))
                continue

            if start_x!=end_x:
                k = (end_y-start_y)/(end_x-start_x)
                n = (end_x - start_x)/abs(end_x - start_x) #判断减价,+1表示开始点在前，结束点在后
                # print('n=',n)
                m = contour_length/math.sqrt(1+pow(k,2))
                dx = m*n
                dy = m*k*n
                # print('斜率=%f,dx=%f,dy=%f'%(k,dx,dy))
                while dis > contour_length:
                    # print('dis=%f,x=%f,y=%f'%(dis,start_x,start_y))
                    output_points.append((start_x, start_y))
                    start_x = start_x + dx
                    start_y = start_y + dy
                    dis = math.sqrt(pow((end_y-start_y),2)+pow((end_x-start_x),2))
                output_points.append((end_x,end_y))
            elif start_x==start_y:
                n = (end_y - start_y) / abs(end_y - start_y)  # 判断减价,+1表示开始点在前，结束点在后
                # print('n=', n)
                dx = 0
                dy = contour_length*n
                while dis > contour_length:
                    # print('dis=%f,x=%f,y=%f'%(dis,start_x,start_y))
                    output_points.append((start_x, start_y))
                    start_x = start_x + dx
                    start_y = start_y + dy
                    dis = math.sqrt(pow((end_y-start_y),2)+pow((end_x-start_x),2))

            # print('lastpoint:', output_points[len(output_points) - 1])
        output_points.append((points[len(points)-1][0],points[len(points)-1][1]))
        print('allpoints_num=',len(output_points))
        return(output_points)

    def ReadRaster(self):
        points = self.ReadLineshp()
        # for i in range(100):
        #     print(points[i])
        in_ds = gdal.Open(os.path.join(self.path, self.rastername))
        in_band = in_ds.GetRasterBand(1)
        in_transform = in_ds.GetGeoTransform()
        in_projection = in_ds.GetProjection()
        nodata = in_band.GetNoDataValue()
        print(in_transform)
        print(in_projection)
        print('nodata:', nodata)
        inv_transform = gdal.InvGeoTransform(in_transform)
        final_output = []
        for i in range(len(points)):
            offsets = gdal.ApplyGeoTransform(inv_transform, points[i][0], points[i][1])
            xoff, yoff = map(int, offsets)
            if xoff>=31250 or yoff>=51213:
                print('xoff=%d,yoff=%d,i=%d,超出栅格范围'%(xoff,yoff,i))
                sys.exit()
            value = in_band.ReadAsArray(xoff,yoff,1,1)[0,0]
            if value == nodata:
                continue
            else:
                final_output.append([points[i][0],points[i][1],float(value)])
        # for i in range(20):
        #     print(final_output[i],type(final_output[i]))
        final_output_tr = myfun.cor_tr2(final_output,self.epsg,4326,0,1,2)
        myfun.savecsv(final_output_tr, 'wgs84'+self.save_name+'.csv', os.path.join(self.path,'output'))
        return(final_output_tr)

    def savejson(self):
        data = self.ReadRaster()
        f = open(os.path.join(self.path,'output',self.save_name+str(self.length)+'间隔.json'), 'w')
        f.write('[')
        for val in data:
            strval = str(val)
            f.write(strval)
            f.write(',')
        f.write(']')
        f.close()

    def data_plot(self):
        data = self.ReadRaster()
        list_name = ['lon','lat','alt']
        data_df = pd.DataFrame(data, columns=list_name)
        print(data_df.describe())
        fig_hei = plt.figure(figsize=(14, 5))
        ax1 = fig_hei.add_subplot(1, 1, 1)
        data_df['alt'].plot()
        # data_df['Z_fans'].plot()
        ax1.set_ylabel('高程/m')
        ax1.legend(loc='best')
        ax1.set_title('纵断面')
        plt.subplots_adjust(bottom=0.10, top=.90, left=.06, right=.94)
        plt.savefig(os.path.join(self.path, 'output', self.save_name+str(self.length)+'米间隔纵断面.png'))
        plt.show()

    def pro(self):
        print('程序处理！')

def main():
    ex = line_raster_pro()
    ex.savejson()
    ex.data_plot()

main()
