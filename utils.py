import requests

def videoToDeviceInt(device):
    return int(device.split('video')[1])

def upload(url, data):
    req = requests.post(url, json=data)
    if(req.status_code==200):
        req = req.json()
        if(req['status'] == 201):
            print('Berhasil DataID:', req['data']['id'])
        else:
            print('Error :', req)
    else:
        print('Gagal upload, Error :', req.text)