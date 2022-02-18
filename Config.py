import cv2
import numpy as np
import datetime

from AIModule.ObjectUtils import BBox
from Camera import perspective_transform

class ConfigType:
	action = "action_config"
	hand = "hand_config"
	console = "console_config"

class ServiceConfig:

	@staticmethod
	def write_config(data, type):
		with open('config/{}.txt'.format(type), 'w') as f:
			f.write('\n'.join(data[type]))

	#動作流程座標框
	@staticmethod
	def get_bbox_config():
		result = []
		with open('config/{}.txt'.format(ConfigType.action),'r') as f:
			for line in f.readlines():
				content = line.split(" ")
				result.append(BBox.get_from_list(content[0], int(content[1]), int(content[2]), int(content[3]), int(content[4])))
			return result

    #透視變換四個點
	@staticmethod
	def get_4_coordinate():
		result = []
		with open('config/{}.txt'.format(ConfigType.hand), 'r') as f:
			for line in f.readlines():
				temp = line.split(" ")
				result.append([int(temp[0]), int(temp[1])])
			return result

	#獲得console內容
	@staticmethod
	def get_console_config():
		with open('config/{}.txt'.format(ConfigType.console), 'r') as f:
			result = ''
			contents = f.readlines()       #讀取全部行
			for content in contents:       #顯示一行	
				EventDays = datetime.datetime.strptime(content.split(' ')[0], '%Y/%m/%d')	
				ReserveDays = datetime.datetime.today().date() + datetime.timedelta(days = -0)
				if EventDays.date() >= ReserveDays:
					result += content
			return result

class DrawingFrame:

	def __init__(self): 
		#動作流程的初始
		self.BBoxInfo = ServiceConfig.get_bbox_config()
		# 手部的初始
		self.roiPts = ServiceConfig.get_4_coordinate()

	@staticmethod
	def draw_rectangle(frame, zoneName, startPoint, endPoint):
		cv2.rectangle(frame, (startPoint.x, startPoint.y), (endPoint.x, endPoint.y), (255, 0, 0), 3)
		cv2.putText(frame, zoneName, (startPoint.x, startPoint.y), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 3, cv2.LINE_AA)
    
	#流程動作的camera函數
	def get_motion_frame(self, camera):

		frame = camera.get_frame()
		frame = cv2.resize(frame, (1280, 720))

		# AI MODEL
		#畫圖
		for BBox in self.BBoxInfo:
			DrawingFrame.draw_rectangle(frame, BBox.zoneName, BBox.startPoint, BBox.endPoint)

		return frame
		#需要壓縮編碼成bite
		# frame = cv2.imencode('.png', frame)[1].tobytes()
		# return (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

	#透視變換的camera函數
	def get_hands_frame(self, camera):
		
		frame = camera.get_frame()
		frame = cv2.resize(frame, (1280, 720))

		# 前端(主頁面)的透視變換
		frame = perspective_transform(frame, self.roiPts) #透視變換函數
		return frame
		#需要壓縮編碼成bite
		# frame = cv2.imencode('.png', frame)[1].tobytes()
		# yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
