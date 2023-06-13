from celery import Celery
import os
import subprocess

celery = Celery("tasks",)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", )
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", 'db+sqlite:///results.db')

@celery.task
def startStream(url, device):
    print('starting stream on device', device)
    subprocess.run(['ffmpeg', '-re', '-i', url, '-pix_fmt', 'yuyv422', '-f', 'v4l2', '/dev/'+device])
    return 0

@celery.task
def startDetection(cctvid, device):
    print('starting detection...')