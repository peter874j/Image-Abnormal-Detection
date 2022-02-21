from flask import Flask, render_template, send_from_directory, Response, request, json, send_file
from pathlib import Path
from Camera import Camera, perspective_transform
from Logger import *
from datetime import datetime
import time
import cv2
import copy
from Config import Frame, ServiceConfig, ConfigType
from AIModule.SystemDetection import Motion, Hands
from AIModule.detect import AbnormalModel

### Log Module Config
Logger.config(
    logTypes=LogType.Console | LogType.File,
    consoleLogConfig=ConsoleLogConfig(
        level=LogLevel.WARNING,
        ),
    fileLogConfig=FileLogConfig(
        level=LogLevel.INFO,
        newline=False,
        dirname="record",
        suffix="events",
        )
    )

app = Flask(__name__)

def InitGlbVar():
    global currentMotionFrame

### 主頁面進入點
@app.route("/", methods=['GET'])
def entrypoint():
    Frame.initialize_label()
    return render_template("index.html", user_time=system_time_info())

### 跳轉子頁面
@app.route("/sec_page", methods=['GET'])
def second_entrypoint():
    Logger.info("Requested /second_page")
    return render_template("sec_page.html")

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering or Chrome Frame,
    and also to cache the rendered page for 10 minutes
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers["Cache-Control"] = "public, max-age=0"
    return r

### 取得系統時間
@app.route("/now_time.txt")
def system_time_info():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

### 回傳動作流程camera的frame
@app.route("/video_feed_0")
def video_feed_0():
	global currentMotionFrame
	currentMotionFrame = camera0.get_motion_frame()
	frame = copy.deepcopy(currentMotionFrame)
	Frame.draw_rectangle_in_zone(frame) # 畫作業區框框
	frame = Frame.encode(frame)
	return Response(frame, mimetype="multipart/x-mixed-replace; boundary=frame")

### 第1個camera的串流含式(手部)
@app.route("/video_feed_1")
def video_feed_1():
    frame = camera1.get_hands_frame()
    frame = handsDetection.run(frame)
    frame = Frame.encode(frame)
    return Response(frame, mimetype="multipart/x-mixed-replace; boundary=frame")

### 跳子頁面要傳當前圖片
@app.route("/currentFrame", methods=['GET'])
def get_currentFrame():
	global currentMotionFrame
	frame = copy.deepcopy(currentMotionFrame)
	file_object = Frame.transform_virtual_file(frame)
	return send_file(file_object, mimetype='image/PNG')
### 前端(子頁面)的透視變換
@app.route("/perspective_transformation", methods=['GET', 'POST'])
def perspective_transformation():
    coordinates = ServiceConfig.get_4_coordinate()
    image = cv2.imread("static/test1.jpg")
    warpedImg = perspective_transform(image, coordinates)
    file_object = Frame.transform_virtual_file(warpedImg)
    return send_file(file_object, mimetype='image/PNG')


### 取得動作狀態的函數，給前端使用(前端會一直呼叫這個函數)
@app.route("/motion_result", methods=['POST'])
def motion_result():
    if request.method == "POST":
        isAnomalyStep, numOfCurrentStep = motionDetection.run(currentMotionFrame)
        return json.dumps({'step_result':isAnomalyStep, 'step_num':numOfCurrentStep})

### 作業區矩形座標寫入txt
@app.route("/action_submit", methods=["POST"])
def action_submit():
    if request.method == "POST":
        data = request.get_json(force=True)
        ServiceConfig.write_config(data, ConfigType.action)
        return "OK"
    else:
        return "OK"

### 手部座標點寫入txt
@app.route("/hand_submit", methods=["POST"])
def hand_submit():
    if request.method == "POST":
        data = request.get_json(force=True)
        ServiceConfig.write_config(data, ConfigType.hand)
        return "OK"
    else:
        return "OK"

### (子頁面)console寫入txt
@app.route("/download_console", methods=["POST"])
def download_console():
    if request.method == "POST":
        data = request.get_json(force=True)
        ServiceConfig.write_config(data, ConfigType.console)
        return "OK"
    else:
        return "OK"

### (子頁面)console讀取consoleInf.txt
@app.route("/read_console_config", methods=['POST'])
def read_consoleInfo():
    if request.method == "POST":
        data = ServiceConfig.get_console_config()
        return json.dumps(data)
    else:
        return "OK"

### (子頁面)讀取action_config.txt 資料傳到前端
@app.route("/read_action_config", methods=['POST'])
def read_action_config():
    if request.method == "POST":
        datas = ServiceConfig.get_bbox_config()
        temp = []
        for data in datas:
            temp.append(data.__dict__)
        return json.dumps(temp)
    else:
        return "OK"

### (子頁面)讀取 hand_config.txt 資料傳到前端
@app.route("/read_hand_config", methods=['POST'])
def read_hand_config():
    if request.method == "POST":
        data = ServiceConfig.get_4_coordinate()
        return json.dumps(data)
    else:
        return "OK"




if __name__=="__main__":

    ### set parameter
    InitGlbVar()
    motionWeight = r'weights/motion_yolov5s.pt'
    handsWeight = r'weights/hands_yolov5s.pt'
    motionSource = r'motion.avi'
    handsSource = r'hand_check.avi'
    port = 5000
    host = '0.0.0.0'
    
    ### set AI model
    AIModel = AbnormalModel()
    Logger.info("AI Model Build...")
    AIModel.load_motion_model(motionWeight)
    Logger.info(f"Loading Motion AI Model from {motionWeight}...OK")
    AIModel.load_hands_model(handsWeight)
    Logger.info(f"Loading Hands AI Model from {handsWeight}...OK")
    motionDetection = Motion(AIModel, ServiceConfig.get_bbox_config())
    handsDetection = Hands(AIModel)

    ### 初始化兩個camera
    camera0 = Camera(video_source=motionSource)
    camera0.run() # thread 1
    Logger.info(f"Loading Camera0 from {motionSource}")
    camera1 = Camera(video_source=handsSource)
    camera1.run() # thread 2
    Logger.info(f"Loading Camera1 from {handsSource}")
    ### Build Web Server
    Logger.info("Starting Web Server...")
    app.run(host=host, port=port)