import cv2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy
import glob
import sklearn
from sklearn.cluster import KMeans
def replace_cluster_label(d):
	"""close to camera player is A"""
	first_label = d[4].tolist()[0]
	if first_label == 0:
		d[4] = d[4].map({1:"A",0:'B'})
	else:
		d[4] = d[4].map({0:"A",1:'B'})
	return d
def manual_label_video(video_file,outLabel):
	"""
	
	This function will return all frames as a list, for faster video subtraction
	
	
	"""
	cap = cv2.VideoCapture(video_file)
	fps = cap.get(cv2.CAP_PROP_FPS)
	print (fps)
	frame_number_count=0
	log_list = []
	def draw_circle(event,x,y,flags,param):
		global mouseX,mouseY
	#	 if event == cv2.EVENT_LBUTTONDBLCLK: # if user likes double click, use this line
		if event == cv2.EVENT_FLAG_LBUTTON:	
			mouseX,mouseY = x,y
	cv2.namedWindow('image')
	cv2.setMouseCallback('image',draw_circle)
	frame_list = []
	while cap.isOpened():
		# Read video capture
		frame_number_count+=1
		ret, frame = cap.read()
		cv2.imshow("image", frame)
		frame_list.append(frame_list)
		key = cv2.waitKey(0)
		if key == ord('\n'):
			continue
		if key == ord('+'):
			frame_number_count+=int(fps)
			for i in range(int(fps)):
				cap.read()
		if key in [ord(str(x)) for x in range(10)]:
			log_list.append([frame_number_count/fps,key,mouseX,mouseY])
			print (frame_number_count/fps,key,mouseX,mouseY)
		if key == ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows() # destroy all opened windows
	df = pd.DataFrame(log_list)
	out = []
	for s,d in df.groupby(1):
		n=int(chr(s))
		# in case of outlier, use this code
#		 if n<7:
#			 d=d[d[3]<900]
		cls = KMeans(2)
		cls.fit(np.array(d[3]).reshape(-1,1))
		d[4] = cls.labels_
		d = d.sort_values(3)
		d = replace_cluster_label(d)
		out.append(d)
	df2 = pd.concat(out)
	df2[5] = [chr(x) for x in df2[1]]
	df2['f_name'] = df2[0]*fps
	df2['f_name'] = df2['f_name'].astype(int)
	df3 = pd.DataFrame(df2.groupby([5,4]).size()).reset_index()
	df3.head()
	sns.barplot(data=df3,x=5,y=0,hue=4)
	plt.savefig(f"{outLabel}.return_position_distribution.png",bbox_inches='tight')
	df2 = df2.sort_values(0)
	df2.to_csv(f"{outLabel}.stats.csv")
	return frame_list,df
def to_frame_list2(video_file):
	cap = cv2.VideoCapture(video_file)
	frame_list = []
	while cap.isOpened():
		ret, frame = cap.read()
		cv2.imshow("image", frame)
		key = cv2.waitKey(0)
		frame_list.append(frame_list)
		if key == ord('\n'):
			continue
		if key == ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows() # destroy all opened windows   
	return frame_list
def to_frame_list(video_file):
	cap = cv2.VideoCapture(video_file)
	frame_list = []
	frame_number_count=0
	while cap.isOpened():
		ret, frame = cap.read()
		# cv2.imshow("image", frame)
		# key = cv2.waitKey(0)
		if frame_number_count>20000:
			break
			
		if ret:
			height, width, layers = frame.shape
			new_h = height / 2
			new_w = width / 2
			# print (new_h,new_w)
			resize = cv2.resize(frame, (int(new_w), int(new_h)))
			frame_number_count+=1
			frame_list.append(resize)
			# print (frame_number_count)
		else:
			break
		# if key == ord('\n'):
			# continue
		# if key == ord('q'):
			# break
	cap.release()
	# cv2.destroyAllWindows() # destroy all opened windows   
	return frame_list
def extract_return_video(frame_list,df2,people,from_x,to_y,outLabel):
	outfile = f'{outLabel}_{people}_{from_x}_{to_y}.mp4'
	fourcc = cv2.VideoWriter_fourcc(*'MP4V')
	out = cv2.VideoWriter(outfile, fourcc,30,(int(1920/2),int(1080/2)))
	# get frame number
	user_frame_list = []
	for i in range(1,df2.shape[0]):
		try:
			pre_frame = df2.at[i-1,"f_name"]
			current_frame = df2.at[i,"f_name"]
			after_frame = df2.at[i+1,"f_name"]   
		except Exception as e:
			print (e)
			continue
		current_hit = df2.at[i,5]
		after_hit = df2.at[i+1,5]
		current_play = df2.at[i,4]
		if current_play == people and int(current_hit) == from_x and int(after_hit) == to_y:
			user_frame_list.append([pre_frame,after_frame])	
	print ("User frame list")
	print (user_frame_list)
	written_frame_list_index_counter=0
	for i in range(len(frame_list)):
		if user_frame_list[written_frame_list_index_counter][0]<=i<=user_frame_list[written_frame_list_index_counter][1]:
			out.write(frame_list[i])
			if i==user_frame_list[written_frame_list_index_counter][1]:
				written_frame_list_index_counter+=1
				if written_frame_list_index_counter == len(user_frame_list):
					break
		
	out.release()
# import importlib
# import utils
# importlib.reload(utils)
# from utils import *

# df2 = pd.read_csv("Li_vs_liang.m1.csv",index_col=0)
# df2.columns = [0,1,2,3,4,5,'f_name']
# df2.head()
# video_file="IMG_3411.mov"
# frame_list = to_frame_list(video_file)

# extract_return_video(frame_list,df2,"A",7,3,"Li_liang_M1")

