from flask import Flask, request
import threading
from .grading import gradingProcess

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
