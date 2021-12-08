from flask import Flask, request
import threading
from .grading import gradingProcess
from .queryComparison import dataGen

app = Flask(__name__)

@app.route("/")
def index():
    return "SQLGrader API"

# route for running the grading process by grading_process_id
@app.route("/grading/<int:grading_process_id>", methods=["POST"])
def grading(grading_process_id):
    data = request.get_json()
    apikey = request.headers.get("apikey")

    # do the grading stuff
    grading_thread = threading.Thread(target=gradingProcess.rungradingprocess, kwargs={"grading_process_id": grading_process_id, "apikey": apikey, "post_body": data})
    grading_thread.start()

    return "Grading process started", 200

# route for query data generation
@app.route("/datagen/<int:environment_instance_id>", methods=["POST"])
def datagen(environment_instance_id):
    data = request.get_json()
    apikey = request.headers.get("apikey")

    # do datagen
    datagen_thread = threading.Thread(target=dataGen.startdatagen, kwargs={"environment_instance_id": environment_instance_id, "apikey": apikey, "post_body": data})
    datagen_thread.start()

    return "Data gen started", 200