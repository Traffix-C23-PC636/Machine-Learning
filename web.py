from flask import Flask, request, redirect, jsonify
from tasks import celery, startStream, startDetection
from v4l2loopback import V4l2loopback
from utils import videoToDeviceInt

v4l2 = V4l2loopback()
v4l2.createInstance(10)

tasktodevice = {}
task1totask2 = {}
tasks = []

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
        tasks.append(videoStreamTask.id)

        detectionTask = startDetection.delay(videoToDeviceInt(deviceid),3*60,idatcs, 'https://api.traffix.my.id/api/statistik',)
        task_id.append(detectionTask.id)
        tasks.append(detectionTask.id)

        #mapping task1 to task2
        task1totask2[videoStreamTask.id] = detectionTask.id 

        return jsonify({"task_id": task_id,"deviceid":deviceid}), 202

    @app.route('/stop',methods=["POST"])
    def stop_task():
        task_id = request.form['task_id']
        celery.AsyncResult(task_id).revoke(terminate=True)

        if task_id in tasks:
            tasks.remove(task_id)

        if task_id in task1totask2.keys():
            v4l2.releaseDevice(tasktodevice[task_id])
            del tasktodevice[task_id]

            task2 = task1totask2[task_id]
            celery.AsyncResult(task2).revoke(terminate=True)
            del task1totask2[task_id]
            if(task2 in tasks):
                tasks.remove(task2)

        return jsonify({"status":"ok"}),200
    
    @app.route('/stopAll',methods=["POST"])
    def stopAllTask():
        for task_id in tasks:
            celery.AsyncResult(task_id).revoke(terminate=True)
            tasks.remove(task_id)

            if task_id in task1totask2.keys():
                v4l2.releaseDevice(tasktodevice[task_id])
                del tasktodevice[task_id]

                task2 = task1totask2[task_id]
                celery.AsyncResult(task2).revoke(terminate=True)
                del task1totask2[task_id]
                if(task2 in tasks):
                    tasks.remove(task2)
        return jsonify({"status":"ok"}),200
    
    @app.route('/purge', methods=["POST"])
    def purge_queue():
        i = celery.control.inspect()
        for queues in (i.active(), i.reserved(), i.scheduled()):
            for task_list in queues.values():
                for task in task_list:
                    task_id = task.get("request", {}).get("id", None) or task.get("id", None)
                    celery.control.revoke(task_id,terminate=True)
        return jsonify({"status":"ok"}),200
     
    @app.route('/queues', methods=["GET"])
    def get_queue():
        i = celery.control.inspect()
        return jsonify({
            "scheduled" : i.scheduled(),
            "active" : i.active(),
            "reserved" : i.reserved(),
        }),200

    @app.route("/tasks", methods=["GET"])
    def list_known_tasks():
        return jsonify({
            'tasks' : tasks,
            'tasktodevice':tasktodevice,
            'task1totask2':task1totask2
        }),200

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