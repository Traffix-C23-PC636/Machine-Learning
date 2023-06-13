from flask import Flask, request, redirect, jsonify
from tasks import celery, startStream, startDetection
from v4l2loopback import V4l2loopback
from utils import videoToDeviceInt

v4l2 = V4l2loopback()
v4l2.createInstance(10)

tasktodevice = {}

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route('/')
    def index():
        return 'API Server is UP'
    
    @app.route('/start', methods=['POST'])
    def start_task():
        idatcs = request.form['id_atcs']
        streamurl = request.form['stream_url']
        deviceid = v4l2.getFreeDevice()
        if(deviceid == 0):
            return jsonify({"error": "no device left!"}), 500
        
        task_id = []
        
        videoStreamTask = startStream.delay(streamurl, deviceid)
        tasktodevice[videoStreamTask.id] = deviceid
        task_id.append(videoStreamTask.id)

        detectionTask = startDetection.delay(videoToDeviceInt(deviceid),5*60,idatcs, 'https://api.traffix.my.id/api/statistik',)
        task_id.append(detectionTask.id)

        return jsonify({"task_id": task_id,"deviceid":deviceid}), 202


    @app.route('/stop/',methods=["POST"])
    def stop_task():
        task_id = request.form['task_id']
        celery.AsyncResult(task_id).revoke(terminate=True)
        if task_id in tasktodevice:
            v4l2.releaseDevice(tasktodevice[task_id])
        
        return jsonify({"status":"ok"}),200

    @app.route("/tasks/<task_id>", methods=["GET"])
    def get_status(task_id):
        task_result = celery.AsyncResult(task_id)
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result
        }
        return jsonify(result), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)