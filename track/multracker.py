# -*- coding: utf-8 -*-
import numpy as np 
import cv2
import sys
from time import time

import kcftracker
#import KCF
	#if you use hog feature, there will be a short pause after you draw a first boundingbox, that is due to the use of Numba.

class multracker:

	def __init__(self,frame,regi_pos):
		self.trackers = []
		self.duration = 0.01
		if(len(regi_pos)>0):
			for index in range(len(regi_pos)):
				self.trackers.append(kcftracker.KCFTracker(True, True, True))
				cv2.rectangle(frame,(regi_pos[index][0],regi_pos[index][1]), (regi_pos[index][0]+regi_pos[index][2],regi_pos[index][1]+regi_pos[index][3]), (0,255,255), 2)
				self.trackers[index].init([regi_pos[index][0],regi_pos[index][1],regi_pos[index][2],regi_pos[index][3]], frame)
	
	def my_update(self, frame, attr_image_list):
		if len(self.trackers)>0:
			t0 = time()
			
			
			k = 0	
			for tracker in self.trackers:
				boundingbox = tracker.update(frame)
				boundingbox = map(int, boundingbox)
				cv2.rectangle(frame,(boundingbox[0],boundingbox[1]), (boundingbox[0]+boundingbox[2],boundingbox[1]+boundingbox[3]), (0,255,255), 1)
				j = 0
				if type(attr_image_list) != int:
					for i in attr_image_list[k]:   #在行人框旁边打印属性
						cv2.putText(frame, i, (boundingbox[0]+boundingbox[2],boundingbox[1]+20*j), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 2)
						j = j + 1
				k = k + 1
			t1 = time()	
			self.duration = 0.8*self.duration + 0.2*(t1-t0)
			#duration = t1-t0
			cv2.putText(frame, 'FPS: '+str(1/self.duration)[:4].strip('.'), (8,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

			
		cv2.imshow('tracking', frame)
		



	def __del__(self):
		print "clear trackrs"
if __name__ == '__main__':
	videofile = 'test.avi'
	regi_pos = [[0,0,100,100],[100,100,100,100]]
	mulTracker(regi_pos,videofile)

