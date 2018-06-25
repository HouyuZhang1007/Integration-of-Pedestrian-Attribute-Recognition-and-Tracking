# -*- coding: utf-8 -*-
from track.multracker import multracker
from attribute.attribute_rec import AttributeRec
import cv2

def draw_boundingbox(event, x, y, flags, param):
	global selectingObject, initTracking, onTracking, ix, iy, cx,cy, w, h, regi_x, regi_y, regi_w, regi_h, frame
	
	if event == cv2.EVENT_LBUTTONDOWN:
		selectingObject = True
		#onTracking = False
		ix, iy = x, y
		cx, cy = x, y
		
	elif event == cv2.EVENT_MOUSEMOVE:
		cx, cy = x, y
	
	elif event == cv2.EVENT_LBUTTONUP:
		selectingObject = False
		if(abs(x-ix)>10 and abs(y-iy)>10):
			w, h = abs(x - ix), abs(y - iy)
			regi_w.append(w)
			regi_h.append(h)
			ix, iy = min(x, ix), min(y, iy)
			regi_x.append(ix)
			regi_y.append(iy)

			cv2.rectangle(frame, (ix, iy), (cx, cy), (0,255,255), 1)
			cv2.imshow('tracking', frame)
			initTracking = True
		else:
			pass#onTracking = False
	
	elif event == cv2.EVENT_RBUTTONDOWN:
		#onTracking = False
		if(w>0):
			ix, iy = x-w/2, y-h/2
			initTracking = True

def detection():
	global regi_x,regi_y,regi_w,regi_h, regi_pos

	for i in range(len(regi_x)):
		regi_pos.append([regi_x[i], regi_y[i], regi_w[i], regi_h[i]])
	
	return regi_pos

def regi_clear():
	global regi_x,regi_y,regi_w,regi_h,regi_pos
	regi_pos = []
	regi_x = []
	regi_y = []
	regi_w = []
	regi_h = []

def pd_crop(frame, regi_pos):
	pd_image = []
	for i in range(len(regi_pos)):
		img = frame[regi_pos[i][1]:(regi_pos[i][1] + regi_pos[i][3]), regi_pos[i][0]:(regi_pos[i][0] + regi_pos[i][2])]
		pd_image.append(img)
	return pd_image


if __name__ == '__main__':
	regi_clear() #全局变量初始化
	mode_device = -1
	refresh_count = 50

	my_attr_rec = AttributeRec(mode_device, model = 'VESPA_PA100K_26') #属性识别器初始化
	count = 1
	videofile = './input/1.avi'
		

	cv2.namedWindow('tracking')
	cap = cv2.VideoCapture(videofile)
	ret,frame = cap.read()
	
	#框人，加入检测后注释掉
	cv2.imshow('tracking', frame)
	cv2.setMouseCallback('tracking',draw_boundingbox) #框人
	cv2.waitKey(0)


	regi_pos = detection()
	

	if not ret:
		raise RuntimeError('frame read error')

	my_multracker = multracker(frame,regi_pos) #跟踪


	#进行属性识别
	img_attr = pd_crop(frame, regi_pos) #将第一帧图片当中的行人框剪裁出来存储于list中

	attr, orig_pred = my_attr_rec.attr_rec(img_attr) #获得属性识别结果，attr表示每个属性的有无，orig_pred为每个属性原始概率	

	while(cap.isOpened()):
		count = count + 1
		ret, frame = cap.read()
		
		if not ret:
			break
		
		if (count%refresh_count == 0):#every 50 frames having a detection adjusting
			regi_clear()
			cv2.imshow('tracking', frame)
			cv2.setMouseCallback('tracking',draw_boundingbox)
			cv2.waitKey(0)

			print count
			del my_multracker
			regi_pos = detection()#This way to 	detection adjusting

			img_attr = pd_crop(frame, regi_pos)
			attr, orig_pred = my_attr_rec.attr_rec(img_attr)
			#regi_pos = []
			#multracker.clear()
			my_multracker = multracker(frame,regi_pos)
		
		attr_image_list = my_attr_rec.show_attr(attr)
		
		my_multracker.my_update(frame, attr_image_list)
		
		c = cv2.waitKey(10) & 0xFF
		if c==27 or c==ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows()
