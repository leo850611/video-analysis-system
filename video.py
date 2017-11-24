#!/usr/bin/python 
# -*- coding: utf-8 -*-
import time
import numpy as np
import cv2
import dlib
import argparse
import os
import pickle
import sys
import numpy as np
np.set_printoptions(precision=2)
from sklearn.mixture import GMM
import openface

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

def getRep(bgrframe):
	
	# cv2 使用 BGR dlib 使用RGB 需要互相轉戶 使用cv2.cvtColor去做轉換
	if bgrframe is None:
		raise Exception("Unable to load frame")
	# RGB 是需要給dlib做 align 與 detect 
	rgbframe = cv2.cvtColor(bgrframe, cv2.COLOR_BGR2RGB)
	
	#align 產生的box
	boundingBox = align.getAllFaceBoundingBoxes(rgbframe)
	if len(boundingBox) == 0:
		return None
	alignedFaces = []
	for box in boundingBox:
		alignedFaces.append(
		align.align(
		args.imgDim,
		rgbframe,
		box,
		landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE))
	if alignedFaces is None:
		raise Exception("Unable to align the frame")
	reps = []
	for alignedFace in alignedFaces:
		reps.append(net.forward(alignedFace))
    	# print (reps)
	return reps
def rectangle(bgrframe,persons):
	rgbframe = cv2.cvtColor(bgrframe, cv2.COLOR_BGR2RGB)
	i = 0
	#align 產生的box
	boundingBox = align.getAllFaceBoundingBoxes(rgbframe)
	if len(boundingBox) == 0:
		return
	for b in boundingBox:
		(x,y,w,h) = (b.left(), b.top(), b.right(), b.bottom())
		cv2.rectangle(bgrframe, (x, y), (w, h), (0, 255, 0), 2)
		cv2.putText(bgrframe, persons[i],(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
		i += 1
def infer(frame, args):
	with open(args.classifierModel, 'r') as f:
		if sys.version_info[0] < 3:
			(le, clf) = pickle.load(f)  # le - label and clf - classifer
		else:
			(le, clf) = pickle.load(f, encoding='latin1')  # le - label and clf - classifer
	reps = getRep(frame)
	#當reps 回傳 None 代表裡面沒有定位人臉
	if reps is None:
		print ("No Face detected.")
		return (None, None)
	persons = []
	confidences = []
	# 開始分類
	for rep in reps:
		try:
			rep = rep.reshape(1, -1)
		except:
			pass
		predictions = clf.predict_proba(rep).ravel()
        	# print (predictions)
		maxI = np.argmax(predictions)
        	# max2 = np.argsort(predictions)[-3:][::-1][1]
		persons.append(le.inverse_transform(maxI))
        	# print (str(le.inverse_transform(max2)) + ": "+str( predictions [max2]))
       		# ^ prints the second prediction
		confidences.append(predictions[maxI])
        	# print("Predict {} with {:.2f} confidence.".format(person.decode('utf-8'), confidence))
		if isinstance(clf, GMM):
			dist = np.linalg.norm(rep - clf.means_[maxI])
			print("  + Distance from the mean: {}".format(dist))
			pass
	return (persons, confidences)
def getVideo():
	#video 處理部分 
	
	video = cv2.VideoCapture(args.Video)
	fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
	total = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	print (int(total/fps))
	confidenceList = []
	times = 1
	total = 0
	fp = open("result.txt", "a")
	#cv2.imwrite('output/'+str(s) + '.jpg',frame)
	while True:
		ret, frame = video.read()
		total += 1
		if ret == True:
			if total % fps != 0:
				continue
	
			persons, confidences = infer(frame, args)
		
			try:
				# append with two floating point precision
				confidenceList.append('%.2f' % confidences[0])
			except:
				# If there is no face detected, confidences matrix will be empty.
				# We can simply ignore it.
				times += 1
				continue
			print ("Person: " + str(persons) + " Confidence: " + str(confidences))
			for i, c in enumerate(confidences):
				if c <= args.threshold:  # 0.5 is kept as threshold for known face.
					persons[i] = "unknown"

                	# Print the person name and conf value on the frame
			rectangle(frame, persons)
			cv2.imwrite('static/result/' + str((args.Video.split("/")[1]).split(".avi")[0]) + '/' +str(times) + '.jpg',frame)
			#cv2.imshow('', frame)
			
		else:
			print ("Video is over.")
			break
		#cv2.waitKey(fps) # 1000MS = 1S
		fp.write(str(persons) + str(times) + '\n')
		times = times + 1
        	# quit the program on the press of key 'q'
		#if cv2.waitKey(1) & 0xFF == ord('q'):
		#	break
    	# When everything is done, release the capture
	fp.close()
	video.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	
	parser.add_argument(
		'--dlibFacePredictor',
		type=str,
		help="Path to dlib's face predictor.",
		default=os.path.join(
			dlibModelDir,
			"shape_predictor_68_face_landmarks.dat"))
			
	parser.add_argument(
		'--networkModel',
		type=str,
		help="Path to Torch network model.",
		default=os.path.join(
			openfaceModelDir,
			'nn4.small2.v1.t7'))
			
	parser.add_argument('--imgDim', type=int,
		help="Default image dimension.", default=96)
		
	parser.add_argument(
		'--captureDevice',
		type=int,
		default=0,
		help='Capture device. 0 for latop webcam and 1 for usb webcam')
	
	parser.add_argument('--threshold', type=float, default=0.5)
	parser.add_argument('--cuda', action='store_true')
	parser.add_argument('--verbose', action='store_true')
	parser.add_argument(
		'classifierModel',
		type=str,
		help='The Python pickle representing the classifier. This is NOT the Torch network model, which can be set with 	--		networkModel.')
	parser.add_argument('Video',type=str,help='plz enter the video name')	
	args = parser.parse_args()
	align = openface.AlignDlib(args.dlibFacePredictor)
	
	
	net = openface.TorchNeuralNet(
		args.networkModel,
		imgDim=args.imgDim,
		cuda=args.cuda)
	if not os.path.exists("static/result"):
		os.mkdir("static/result")
	videoname = args.Video.split("/")[1].split(".avi")[0]
	print videoname
	if not os.path.exists("static/result/" + videoname):
		os.mkdir("static/result/" + videoname)
	
	getVideo()