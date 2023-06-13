from celery import Celery
from detect import main as detectStart

import os
import subprocess
import supervision as sv
from time import sleep

celery = Celery("tasks",)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", )
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", 'db+sqlite:///results.db')

@celery.task
def startStream(url, device):
    print('starting stream on device', device)
    subprocess.run(['ffmpeg', '-re', '-i', url, '-pix_fmt', 'yuyv422', '-f', 'v4l2', '/dev/'+device])
    return 0

@celery.task
def startDetection(source,timer,cctvid, postURL,):
    sleep(15) # wait until ffmpeg ready
    print('starting detection...')
    detectStart(source,timer,cctvid,postURL,sv.Point(0, 0),sv.Point(640, 640))
    return 0