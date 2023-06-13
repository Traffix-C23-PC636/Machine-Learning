import os

from flask import Flask, request, redirect, jsonify
from tasks import celery, startStream
from v4l2loopback import V4l2loopback

v4l2 = V4l2loopback()
v4l2.createInstance(10)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route('/')
    def index():
        return 'API Server is UP'
    
    @app.route('/start', methods=['POST'])
    def start_task():
        idatcs = request.form['id_atcs']
        streamurl = request.form['stream_url']
        deviceid = v4l2.getFreeDevices()
        
        task_id = []

        videoStreamtask = startStream.delay(streamurl, deviceid)
        task_id.append(videoStreamtask.id)

        
        
        return jsonify({"task_id": task_id,"deviceid":deviceid}), 202

        
    @app.route('/stop/',methods=["POST"])
    def stop_task():
        task_id = request.form['task_id']
        celery.AsyncResult(task_id).revoke(terminate=True)
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