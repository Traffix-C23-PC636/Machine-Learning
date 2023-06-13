import subprocess
import os
from tasks import startStream

class V4l2loopback:
    def __init__(self):
        self.devices = []
        self.used_devices = []
    
    def getDevices(self):
        devices = []
        try:
            devices = os.listdir('/sys/devices/virtual/video4linux/')
            devices = [x for x in devices if x.startswith('video')]
        except:
            pass
        self.devices = devices
        

    def createInstance(self, num_of_instances=20):
        #releasing module v4l2loopback
        try:
            p = subprocess.run(['sudo', 'modprobe', '-r', 'v4l2loopback'])
            if(p.returncode == 0):
                print('Success releasing module')
        except Exception as e:
            print(e)
        
        #insert module v4l2loopback
        try:
            p = subprocess.run(['sudo', 'modprobe', 'v4l2loopback', 'devices='+str(num_of_instances)])
            if(p.returncode == 0):
                print('Success inserting module')
        except Exception as e:
            print(e)

        #update devices array
        self.getDevices()
    
    def getFreeDevice(self):
        not_used_devices =  [ x for x in self.devices if x not in self.used_devices]
        if(len(not_used_devices) == 0):
            print('No device left, cancelled')
            return 0
        device = not_used_devices[0]
        self.used_devices.append(device)
        return device
    
    def releaseDevice(self, device):
        for i in range(len(self.used_devices)):
            if(self.used_devices[i] == device):
                del self.used_devices[i]

    def startForwardStream(self,url, device=None):
        if(device == None):
            device = self.getFreeDevice()
        try:
            startStream.delay(url, device)
        except Exception as e:
            print(e)


# v4l2 = V4l2loopback()
# v4l2.createInstance(5)
# device = v4l2.getFreeDevice()
# device = v4l2.getFreeDevice()
# device = v4l2.getFreeDevice()
# device = v4l2.getFreeDevice()
# device = v4l2.getFreeDevice()
# v4l2.releaseDevice(device)
# print(v4l2.used_devices)
# v4l2.startForwardStream('https://atcs-dishub.bandung.go.id:1990/DjuandaBarat/stream.m3u8')
