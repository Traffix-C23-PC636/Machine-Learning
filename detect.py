import cv2
import time
from ultralytics import YOLO
import supervision as sv
from linezone import LineZoneFixed
from utils import upload

import time
import schedule
import requests


class ObjectCounter:
    def __init__(self, TIMER, CCTVID, postURL, LINE_START, LINE_END):
        self.CCTVID = CCTVID
        self.postURL = postURL
        self.TIMER = TIMER
        self.LINE_START = LINE_START
        self.LINE_END = LINE_END
        self.starttimer = 0
        self.stoptimer = 0
        self.isRunning = False
        self.job = None
        self.initCounter()

    def initCounter(self):
        self.line_counter = LineZoneFixed(
            start=self.LINE_START, end=self.LINE_END, class_id=[x for x in range(0, 5)])

    def startTimer(self):
        self.isRunning = True
        self.starttimer = time.time()
        self.job = schedule.every(self.TIMER).seconds.do(self.update)

    def update(self):
        print('pushing data to the server ...')
        self.stoptimer = time.time()
        self.composeAndSendRequest()
        self.initCounter()  # reset all counter to 0

    def stopTimer(self):
        self.isRunning = False
        self.stoptimer = time.time()
        schedule.cancel_job(self.job)
        self.update() #pushing last data to the server

    def composeAndSendRequest(self):
        mobil = self.line_counter.getIDCount([1], inCount=True, outCount=True)
        motor = self.line_counter.getIDCount([0, 2], inCount=True, outCount=True)
        bus = self.line_counter.getIDCount([3], inCount=True, outCount=True)
        truck = self.line_counter.getIDCount([4], inCount=True, outCount=True)

        inc = self.line_counter.getIDCount([0, 1, 2, 3, 4], inCount=True)
        outc = self.line_counter.getIDCount([0, 1, 2, 3, 4], outCount=True)

        data = {
            "id_atcs": self.CCTVID,
            "car": mobil,
            "bus": bus,
            "truck": truck,
            "motorcycle":motor,
            "data_in": inc,
            "data_out": outc,
        }
        print("JUMLAH :",mobil, motor, bus, truck, inc, outc)
        upload(self.postURL, data)

def main(device, TIMER=10, CCTVID='', postURL='', LINE_START=sv.Point(0, 0), LINE_END=sv.Point(640, 640)):
    print('Capturing from device', device)
    vcap = cv2.VideoCapture(device)
    model = YOLO('best.onnx') # using exported onnx model
    #model = YOLO('best.pt') 
    
    line_annotator = sv.LineZoneAnnotator(
        thickness=9, text_thickness=1, text_scale=0.5)
    box_annotator = sv.BoxAnnotator(
        thickness=4,
        text_thickness=1,
        text_scale=0.5
    )
    counter = ObjectCounter(TIMER=TIMER, CCTVID=CCTVID,
                            postURL=postURL, LINE_START=LINE_START, LINE_END=LINE_END)

    print('starting the timer ...')
    counter.startTimer()
    print('timer started')

    while True:
        # Capture frame-by-frame
        ret, frame = vcap.read()

        if frame is not None:
            results = model.track(
                frame, stream=True, show=False, verbose=False, tracker="bytetrack.yaml", persist=True, )

            for result in results:
                frame = result.orig_img
                detections = sv.Detections.from_yolov8(result)

                if result.boxes.id is not None:
                    detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

                labels = []

                frame = box_annotator.annotate(
                    scene=frame,
                    detections=detections,
                    labels=labels
                )

                counter.line_counter.trigger(detections=detections)
                line_annotator.annotate(
                    frame=frame, line_counter=counter.line_counter)

                # cv2.imshow('frame', frame)
                print(counter.line_counter.current_frame)

            # Press q to close the video windows before it ends if you want
            if cv2.waitKey(22) & 0xFF == ord('q'):
                break
        else:
            print("Frame is None")
            break

        schedule.run_pending()

    # When everything done, release the capture
    vcap.release()
    cv2.destroyAllWindows()
    print("Video stop")

    counter.stopTimer()


# main("https://atcs-dishub.bandung.go.id:1990/DjuandaBarat/stream.m3u8",)
