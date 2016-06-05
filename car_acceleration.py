#!/usr/bin/python3.5
# coding: UTF-8

from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from bisect import bisect
import multiprocessing

torqueCurve=[]
powerCurve=[]
#起步转速
startRpm=1300

class Transmission():
    def __init__(self,gears,efficiency=0.9,nowGear=1):
        self.gears=gears
        self.efficiency=efficiency
        #当前档位
        self.nowGear=nowGear
        self.disableShift=False

class Engine():
    def create_torque_curve_edition2(self,torqueRpmPoint):
        length=len(torqueRpmPoint)
        slopeList=[]
        if torqueRpmPoint[0][1]>0:
            for i in range(torqueRpmPoint[0][1]):
                self.torqueCurve.append(0)
        self.torqueCurve.append(torqueRpmPoint[0][0])
        for i in range(1,length):
            slope=(torqueRpmPoint[i][0]-torqueRpmPoint[i-1][0])/(torqueRpmPoint[i][1]-torqueRpmPoint[i-1][1])
            slopeList.append((torqueRpmPoint[i-1][1],torqueRpmPoint[i][1],slope))
        for rpm in range(torqueRpmPoint[0][1]+1,torqueRpmPoint[-1][1]):
            for lowRpm,hightRpm,slope in slopeList:
                if lowRpm<=rpm<=hightRpm:
                    torque=self.torqueCurve[-1]+slope
                    self.torqueCurve.append(torque)
                    break

    def create_power_curve_edition2(self):
        for i,t in enumerate(self.torqueCurve):
            power=t/9550*i
            self.powerCurve.append(power)

    def get_max_torque_rpm_range_edition2(self):
        tempTorqueRpmPoint=[]
        maxTorque=max(self.torqueCurve)
        lowRpmPoint=self.torqueCurve.index(maxTorque)-1
        highRpmPoint=len(self.torqueCurve)-self.torqueCurve[::-1].index(maxTorque)-2
        if lowRpmPoint != highRpmPoint:
            return (lowRpmPoint,highRpmPoint)
        else:
            relativeMaxTorque=round(maxTorque*0.9,2)
            for i,t in enumerate(self.torqueCurve):
                if round(t,2)==relativeMaxTorque:
                    tempTorqueRpmPoint.append(i)
            insertIndex=bisect(tempTorqueRpmPoint,self.torqueCurve.index(maxTorque))
            if insertIndex==len(tempTorqueRpmPoint):
                return (tempTorqueRpmPoint[0],len(self.torqueCurve)-1)
            else:
                return (tempTorqueRpmPoint[insertIndex-1],tempTorqueRpmPoint[insertIndex])

    def get_max_power_rpm_range_edition2(self):
        tempPowerRpmPoint=[]
        maxPower=max(self.powerCurve)
        maxPowerRpmPoint=self.powerCurve.index(maxPower)
        for i,p in enumerate(self.powerCurve):
            if round(p)==round(maxPower*0.98):
                tempPowerRpmPoint.append(i)
        insertIndex=bisect(tempPowerRpmPoint,maxPowerRpmPoint)
        if insertIndex==len(tempPowerRpmPoint):
            return (tempPowerRpmPoint[0],len(self.torqueCurve)-1)
        else:
            return (tempPowerRpmPoint[insertIndex-1],tempPowerRpmPoint[insertIndex])

    #创建发动机扭矩曲线
    def create_torque_curve_edition(self,torqueRpmPoint):
        length=len(torqueRpmPoint)
        slopeList=[]
        self.torqueCurve.append(torqueRpmPoint[0])
        for i in range(1,length):
            slope=(torqueRpmPoint[i][0]-torqueRpmPoint[i-1][0])/(torqueRpmPoint[i][1]-torqueRpmPoint[i-1][1])
            slopeList.append((torqueRpmPoint[i-1][1],torqueRpmPoint[i][1],slope))
        for rpm in range(torqueRpmPoint[0][1]+1,torqueRpmPoint[-1][1]+1):
            for lowRpm,hightRpm,slope in slopeList:
                if lowRpm<=rpm<=hightRpm:
                    torque=self.torqueCurve[-1][0]+slope
                    self.torqueCurve.append((torque,rpm))
                    break

    #根据发动机扭矩曲线创建发动机功率曲线，9550为系数，从网上查得
    def create_power_curve(self):
        for (t,r) in self.torqueCurve:
            power=t/9550*r
            self.powerCurve.append((power,r))

    def get_max_torque_rpm_range(self):
        tempTorqueRpmPoint=[]
        highRpmPoint=self.maxTorque[1]
        for (t,r) in self.torqueCurve:
            if t==self.maxTorque[0] and r != highRpmPoint:
                lowRpmPoint=r
                return (lowRpmPoint,highRpmPoint)
        for (t,r) in self.torqueCurve:
            if round(t)==round(self.maxTorque[0]*0.9):
                tempTorqueRpmPoint.append(r)
        for i in range(len(tempTorqueRpmPoint)-1):
            if tempTorqueRpmPoint[i]<self.maxTorque[1]<tempTorqueRpmPoint[i+1]:
                return (tempTorqueRpmPoint[i],tempTorqueRpmPoint[i+1])
        return (tempTorqueRpmPoint[0],self.maxTorque[1])

    def get_max_power_rpm_range(self):
        tempPowerRpmPoint=[]
        for (p,r) in self.powerCurve:
            if round(p)==round(self.maxPower[0]*1):
                tempPowerRpmPoint.append(r)
        for i in range(len(tempPowerRpmPoint)-1):
            if tempPowerRpmPoint[i]<self.maxPower[1]<tempPowerRpmPoint[i+1]:
                return (tempPowerRpmPoint[i],tempPowerRpmPoint[i+1])
        return (tempPowerRpmPoint[0],self.maxPower[1])

    #初始化发动机参数
    #rpm 发动机当前转速
    #maxTorque 发动机最大扭矩
    #maxPower 发动机最大功率
    #maxPowerRpmRange 发动机最大功率转速区间（换挡用）
    def __init__(self,torqueRpmPoint):
        self.powerCurve=[]
        self.torqueCurve=[]
        self.rpm=0
        self.create_torque_curve_edition2(torqueRpmPoint)
        self.create_power_curve_edition2()
        self.maxTorque=max(self.torqueCurve)
        self.maxPower=max(self.powerCurve)
        self.maxPowerRpmRange=self.get_max_power_rpm_range_edition2()
        self.maxTorqueRpmRange=self.get_max_torque_rpm_range_edition2()

#车类定义
#transmission 变速箱类实例
#engine 发动机类实例
#weight 车辆重量
#cw 空气阻力系数
#tireRadius 车轮半径
#speed 车速
#isTopPowerShift 换挡策略，True:最高功率转速区间换挡，False:最大扭矩转速区间换挡
class Car():
    def __init__(self,name,transmission,engine,weight,cw,tireArgument='235/40/18',speed=0,isTopPowerShift=False):
        self.name=name
        tireWidth,tireAspectRatio,wheelSize=[ int(x) for x in tireArgument.split('/') ]
        self.transmission=transmission
        self.engine=engine
        self.weight=weight
        self.cw=cw
        self.tireRadius=round((tireWidth*tireAspectRatio/100+wheelSize*25.4/2)/1000,2)
        self.speed=speed
        self.isTopPowerShift=isTopPowerShift
        self.time=0
        self.speedRecord=[]
        self.torqueRecord=[]
        self.powerRecord=[]
        self.rpmRecord=[]
        self.timeRecord=[]

    #获取变速箱当前档位的齿比
    def get_now_gear(self):
        return self.transmission.gears[self.transmission.nowGear-1]

    def get_torque(self):
        try:
            return self.engine.torqueCurve[round(self.engine.rpm)]
        except:
            return 0

    def get_power(self):
        try:
            return self.engine.powerCurve[round(self.engine.rpm)]
        except:
            return 0

    #获取当前车辆的合力，驱动力-空气阻力-轮胎滚动阻力,空气阻力计算方法较为简单
    def get_drive_force(self):
        torque=self.get_torque()
        gear=self.get_now_gear()
        #驱动车辆的合力=当前扭矩×齿比/轮胎半径×变速箱传动效率-速度的平方×空气阻力系数-整车质量×引力系数×滚动阻力系数
        driverForce=torque*gear/self.tireRadius*self.transmission.efficiency-self.speed*self.speed*self.cw-self.weight*9.8*0.018
        return driverForce

    #更新车速
    def update_speed(self):
        driverForce=self.get_drive_force()
        #车速差值=驱动车辆的合力/车重×0.01秒（以0.01秒为单位来更新，也可以更细分）
        self.speed+=driverForce/self.weight*0.01
        #更新计时
        self.time+=0.01

    #根据新的车速更新转速
    def update_rpm(self):
        #新的转速=车速/车轮周长×当前齿比×60秒（因为rpm为每分钟转速）
        self.engine.rpm=self.speed/(2*3.14*self.tireRadius)*self.get_now_gear()*60
        #起步时不考虑转速下降情况，确保最低转速不低于起步转速
        if self.engine.rpm<startRpm:
            self.engine.rpm=startRpm
        
    #升档
    def shift(self):
        self.transmission.nowGear+=1  

    #降档
    def downshift(self):
        self.transmission.nowGear-=1

    #换挡逻辑,根据是否在最大功率区换挡来决定
    def shift_or_downshift(self):
        #最大功率区换挡方式
        if self.isTopPowerShift:
            #如果发动机转速区高于最大功率输出区间并且没有到最高档则升档
            if not self.transmission.disableShift:
                if self.engine.rpm>self.engine.maxPowerRpmRange[1] and self.transmission.nowGear<len(self.transmission.gears):
                    self.shift()
                elif self.engine.rpm>len(self.engine.powerCurve)-1 and self.transmission.nowGear==len(self.transmission.gears):
                    self.engine.rpm=len(self.engine.powerCurve)
                elif round(self.get_drive_force())<=0:
                    selfCopy=deepcopy(self)
                    selfCopy.downshift()
                    selfCopy.update_rpm()
                    selfCopy.update_speed()
                    if selfCopy.get_power()>self.get_power():
                        self.downshift()
                        self.transmission.disableShift=True
        #最大扭矩区换挡方式
        else:
            #如果发动机转速高于最大扭矩输出区间并且不是最高档则升档
            if self.engine.rpm>self.engine.maxTorqueRpmRange[1] and self.transmission.nowGear<len(self.transmission.gears):
                self.shift()
            #如果发动机转速低于最大扭矩输出区间并且不是最低档则降档
            elif self.engine.rpm<self.engine.maxTorqueRpmRange[0] and self.transmission.nowGear>1:
                self.downshift()

    def show_figure_edition2(self):
        speedArray=np.array(self.speedRecord)
        torqueArray=np.array(self.torqueRecord)
        powerArray=np.array(self.powerRecord)
        rpmArray=np.array(self.rpmRecord)
        timeArray=np.array(self.timeRecord)
        powerCurveArray=np.array([ p for p in self.engine.powerCurve ])
        torqueCurveArray=np.array([ t for t in self.engine.torqueCurve ])
        rpmCurveArray=np.arange(0,len(self.engine.powerCurve),1)

        fig=plt.figure()
        axSpeed=fig.add_subplot(321)
        axTorque=fig.add_subplot(322)
        axPower=fig.add_subplot(323)
        axRpm=fig.add_subplot(324)
        axPowerCurve=fig.add_subplot(325)
        axTorqueCurve=fig.add_subplot(326)
        axSpeed.plot(timeArray,speedArray)
        axTorque.plot(timeArray,torqueArray)
        axPower.plot(timeArray,powerArray)
        axRpm.plot(timeArray,rpmArray)
        axPowerCurve.plot(rpmCurveArray,powerCurveArray)
        axTorqueCurve.plot(rpmCurveArray,torqueCurveArray)
        axSpeed.set_xlabel('time s')
        axSpeed.set_ylabel('speed km/h')
        axTorque.set_xlabel('time s')
        axTorque.set_ylabel('torque Nm')
        axPower.set_xlabel('time s')
        axPower.set_ylabel('power kw')
        axRpm.set_xlabel('time s')
        axRpm.set_ylabel('rpm')
        axPowerCurve.set_xlabel('rpm')
        axPowerCurve.set_ylabel('power kw')
        axTorqueCurve.set_xlabel('rpm')
        axTorqueCurve.set_ylabel('torque Nm')
        fig.suptitle('{}'.format(self.name),fontsize=20)
        plt.show()

        

    def show_result_edition2(self):
        print('{} 时速:{}km/h,用时:{}s'.format(self.name,round(self.speedRecord[-1]),round(self.timeRecord[-1],2)),end=' ')
        print('最大功率:{0}kw 最大功率转速:{1}rpm 最大扭矩:{2}Nm'.format(round(self.engine.maxPower),round(self.engine.powerCurve.index(self.engine.maxPower)),round(self.engine.maxTorque)))
        self.show_figure_edition2()

    #Car类加速方法 
    def accelerate(self,endSpeed,printDetail=False):
        self.engine.rpm=startRpm
        while self.time<200:
            self.speedRecord.append(self.speed*3.6)
            self.torqueRecord.append(self.get_torque())
            self.powerRecord.append(self.get_power())
            self.rpmRecord.append(self.engine.rpm)
            self.timeRecord.append(self.time)
            self.shift_or_downshift()
            self.update_rpm()
            self.update_speed()
            if printDetail:
                print('time:',round(self.time,2),'\trpm:',round(self.engine.rpm),'\tspeed:',round(self.speed*3.6),'km/h','\tgear:',self.transmission.nowGear,'\tdrive force:',round(self.get_drive_force()),'\tpower:',round(self.get_power()))
            #速度单位为米/秒，乘以3.6换算成千米/小时
            if self.speed*3.6>endSpeed:
                self.speedRecord.append(self.speed*3.6)
                self.torqueRecord.append(self.get_torque())
                self.powerRecord.append(self.get_power())
                self.rpmRecord.append(self.engine.rpm)
                self.timeRecord.append(self.time)
                self.time=0
                self.speed=0
                self.transmission.nowGear=1
                self.show_result_edition2()
                return
        self.time=0
        self.speed=0
        self.transmission.nowGear=1
        self.show_result_edition2()


if __name__=='__main__':
    gears7=[9,8,7,6,5,4,3]
    gears6=[9,7,6,5,4.5,4]
    M133=Engine(((230,1250),(250,1500),(310,1750),(400,2000),(450,2250),(450,5000),(440,5500),(430,5750),(420,6000),(370,6500)))
    EA888=Engine(((170,1000),(280,1800),(280,5000),(190,6800)))
    DCT7G=Transmission(gears7,efficiency=0.9)
    AT6G=Transmission(gears6,efficiency=0.9)
    A45AMG=Car('A45AMG',DCT7G,M133,weight=1585,cw=0.27,tireArgument='235/40/18',isTopPowerShift=True)
    Tiguan=Car('Tiguan',AT6G,EA888,weight=1720,cw=0.3,tireArgument='235/55/17',isTopPowerShift=True)
    for c in (A45AMG,Tiguan):
        p=multiprocessing.Process(target=c.accelerate,args=(200,))
        p.start()
