# Main.py
import time
import datetime
#import argparse
import cv2
import numpy as np
import os
import imutils
import DetectChars
import DetectPlates
import PossiblePlate
from PIL import Image, ImageDraw, ImageFont
import _thread
# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
VERIF = 3 # number for verification the plate license
point = 30 # ขนาดของป้ายทะเบียนแนวตั้ง
showSteps = False
# Main ##################################################################################################
ptLowerLeftTextOriginX = 0
ptLowerLeftTextOriginY = 0
A=0

def main():
	feture = 0
	# argument for input video/image/calibration
	"""
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video",
		help = "path to video file")

	ap.add_argument("-i", "--image",
		help = "Path to the image")

	ap.add_argument("-c", "--calibration",
		help = "image or video or camera")
	args = vars(ap.parse_args())

	if args.get("calibration", True):
		#global imgOriginalScene 
		imgOriginalScene = cv2.imread(args["calibration"])
		if imgOriginalScene is None:
			print("Please check again the path of image or argument !")
		imgOriginalScene  = imutils.resize(imgOriginalScene, width = 720)
		cal.calibration(imgOriginalScene)
		return

	if args.get("video", True):
		camera = cv2.VideoCapture(args["video"])
		if camera is None:
			print("Please check again the path of video or argument !")
		loop = True

	elif args.get("image", True):
		imgOriginalScene = cv2.imread(args["image"])
		if imgOriginalScene is None:
			print("Please check again the path of image or argument !")
			loop = False
	else:
		camera = cv2.VideoCapture("9.mp4")
		loop = True
	"""
	camera = cv2.VideoCapture("9.mp4")
	loop = True
	# add knn library for detect chars
	blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()             # attempt KNN training

	if blnKNNTrainingSuccessful == False:                                       # if KNN training was not successful
		print("\nerror: KNN traning was not successful\n")                      # show error message
		return
	count = 0
	# not very important, just iterating for license array haha
	license = []
	VER = np.zeros(VERIF)
	for x in VER:
		license.append("")
	global numlicense
	numlicense = ""
	knn = 0

	# Looping for Video
	while (loop):
		fetures = int(time.time())
		# grab the current frame
		(grabbed, frame) = camera.read()
		if grabbed == True:
			#roi = frame [213:434,200:400]
			#cv2.rectangle(imgOriginalScene,(200,434),(400,213),(0,0,255),1)
			"""
			if args.get("video") and not grabbed:
				break
			"""
			# resize the frame and convert it to grayscale
			imgOriginalScene  = imutils.resize(frame, width = 720)
			global OriginalScene 
			OriginalScene = imgOriginalScene.copy()
			##imgGrayscale, imgThresh = pp.preprocess(imgOriginalScene)
			#cv2.imshow("threshold", imgThresh)
			imgOriginalScene, licenses = searching(imgOriginalScene,loop)
			# only save 5 same license each time
			license[count+1] = licenses
			if (license[count] == license[count+1]):
				license[count]=license[count+1]
				count = count + 1
			elif (license[count] != license[count+1]):
				coba = license[count+1]
				count = 0
				license[count] = coba
			if count == (VERIF-1):
				#if (license[VERIF-1] == ""):
				 #   print("no characters were detected\n")
				if (license[VERIF-1] != "" ):
					#if number license same, not be saved
					if numlicense == license[VERIF-1] and fetures > feture+5 and point_plate > point: #fetures > fetures+5 เวลาหลัง เทียบกับ เวลาแรก+5
						feture = int(time.time())
						#print("เวลาแรก"+str(feture))
						#print("เวลาหลัง"+str(fetures))

						#print("still = " + numlicense)
						#print("license plate read from image = " + numlicense)
						global timestampname
						timestampname = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
						global timestamp
						timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

						#print("Inspection time = " + timestamp +"\n")
						font = ImageFont.truetype('Sarun_ThangLuang.ttf', 80)
						img_pil = Image.fromarray(imgOriginalScene)
						draw = ImageDraw.Draw(img_pil)
						draw.text((ptLowerLeftTextOriginX, ptLowerLeftTextOriginY-50),  numlicense, font = font, fill = (0, 255, 255))
						imgOriginalScene = np.array(img_pil)
						
						#cv2.imshow("license plate", imgOriginalScene)
						namefile = "license plate.png"
						cv2.imwrite(namefile, OriginalScene)	
						Scene  = cv2.imread(namefile)               # open image
						listOfPossiblePlates = DetectPlates.detectPlatesInScene(Scene)           # detect plates
						listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

						print("\nInspection time = " + timestamp)
						font = ImageFont.truetype('Sarun_ThangLuang.ttf', 80)
						img_pil = Image.fromarray(Scene)
						draw = ImageDraw.Draw(img_pil)
						draw.text((ptLowerLeftTextOriginX, ptLowerLeftTextOriginY-50),  numlicense, font = font, fill = (0, 255, 255))
						Scene = np.array(img_pil)
						cv2.imshow("Scene", Scene)            # show scene image

						if len(listOfPossiblePlates) == 0:                          # if no plates were found
							print("\nno license plates were detected\n")  # inform user no plates were found
						else:                                                       # else
									# if we get in here list of possible plates has at leat one plate
									# sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
							listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
									# suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
							licPlate = listOfPossiblePlates[0]
							global text_image
							text_image = licPlate.imgPlate
							cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
							cv2.imshow("imgThresh", licPlate.imgThresh)
							# end if
							drawRedRectangleAroundPlate(Scene, licPlate)             # draw red rectangle around plate
							print("license plate read from image = " + licPlate.strChars)  # write license plate text to std out
							print("----------------------------------------\n")







						#_thread.start_new_thread( license_no, () )
						# Display the resulting frame
						#cv2.imshow("license plate", imgOriginalScene)
						
					else:
						numlicense = license[VERIF-1]
						print("A new license plate read from image = " + license[VERIF-1] + "\n")




				count = 0
			print(license)
			# re-show scene image
			#imgOriginalScene = cv2.blur(imgOriginalScene,(12,12))
			#cv2.putText(imgOriginalScene,"Press 's' to save frame to be 'save.png', for calibrating",(10,30),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,bottomLeftOrigin = False)
			#drawRedRectangleAroundPlate(imgOriginalScene, imgOriginalScene)

			#cv2.rectangle(imgOriginalScene,((imgOriginalScene.shape[1]//2-230),(imgOriginalScene.shape[0]//2-80)),((imgOriginalScene.shape[1]//2+230),(imgOriginalScene.shape[0]//2+80)),SCALAR_GREEN,3)
			
			font = ImageFont.truetype('Sarun_ThangLuang.ttf', 80)
			img_pil = Image.fromarray(imgOriginalScene)
			draw = ImageDraw.Draw(img_pil)
			draw.text((ptLowerLeftTextOriginX, ptLowerLeftTextOriginY-50),  license[VERIF-1], font = font, fill = (0, 255, 255))
			imgOriginalScene = np.array(img_pil)

			cv2.imshow("imgOriginalScene", imgOriginalScene)
			#cv2.imshow("ori", frame)

			key = cv2.waitKey(5) & 0xFF
			"""if key == ord('s'):
				knn = str(knn)
				savefileimg = "calib_knn/img_"+ knn +".png"
				savefileThr = "calib_knn/Thr_"+ knn +".png"
				#cv2.saveimage("save.png", imgOriginalScene)
				cv2.imwrite(savefileimg, frame)
				cv2.imwrite(savefileThr, imgThresh)
				print("image save !")
				knn = int(knn)
				knn = knn + 1"""
			if key == 27: # if the 'q' key is pressed, stop the loop
				break
				camera.release() # cleanup the camera and close any open windows
		# Break the loop
		else: 
			break

	# For image only
	if (loop == False):
		imgOriginalScene  = imutils.resize(imgOriginalScene, width = 720)
		cv2.imshow("original",imgOriginalScene)
		#imgGrayscale, imgThresh = pp.preprocess(imgOriginalScene)
		#cv2.imshow("threshold",imgThresh)
		imgOriginalScene = imutils.transform (imgOriginalScene)
		imgOriginalScene,license = searching(imgOriginalScene,loop)
		#imgOriginalScene = imutils.detransform(imgOriginalScene)

		cv2.waitKey(0)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	return

def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
	
	p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect
	global point_plate

	p2fRectPoints_point1 = tuple(p2fRectPoints[3])
	p2fRectPoints_point2 = tuple(p2fRectPoints[2])

	point_plate = p2fRectPoints_point1[1]-p2fRectPoints_point2[1]
	#print("point_plate"+str(p2fRectPoints_point1[1]-p2fRectPoints_point2[1]))
	"""
	print("p2fRectPoints0"+str(tuple(p2fRectPoints[0])))
	print("p2fRectPoints1"+str(tuple(p2fRectPoints[1])))
	print("p2fRectPoints2"+str(tuple(p2fRectPoints[2])))
	print("p2fRectPoints3"+str(tuple(p2fRectPoints[3])))
	"""
	x=tuple(p2fRectPoints[0])
	x1=int(list(x)[0])
	x2=int(list(x)[1])

	y=tuple(p2fRectPoints[1])
	y1=int(list(y)[0])
	y2=int(list(y)[1])

	h=tuple(p2fRectPoints[2])
	h1=int(list(h)[0])
	h2=int(list(h)[1])

	w=tuple(p2fRectPoints[3])
	w1=int(list(w)[0])
	w2=int(list(w)[1])

	cv2.line(imgOriginalScene, (x1,x2), (y1,y2), SCALAR_RED, 2)         # draw 4 red lines
	cv2.line(imgOriginalScene, (y1,y2), (h1,h2), SCALAR_RED, 2)
	cv2.line(imgOriginalScene, (h1,h2), (w1,w2), SCALAR_RED, 2)
	cv2.line(imgOriginalScene, (w1,w2), (x1,x2), SCALAR_RED, 2)

	#cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
	#cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
	#cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
	#cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
	ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
	ptCenterOfTextAreaY = 0

	global ptLowerLeftTextOriginX 
	global ptLowerLeftTextOriginY

	ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
	ptLowerLeftTextOriginY = 0

	sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
	plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

	intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
	fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
	intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

	textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

			# unpack roatated rect into center point, width and height, and angle
	( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

	intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
	intPlateCenterY = int(intPlateCenterY)

	ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

	if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
		ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
	else:                                                                                       # else if the license plate is in the lower 1/4 of the image
		ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
	# end if

	textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

	ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
	ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

			# write the text on the image
	#cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)



# end function
# searching the plate license ##################################################################################################
def searching(imgOriginalScene,loop):
	licenses = ""
	if imgOriginalScene is None:                            # if image was not read successfully
		print("error: image not read from file \n")      # print error message to std out
		os.system("pause")                                  # pause so user can see error message
		return
		# end if
	listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates
	time.sleep(0.02)
	listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates
	time.sleep(0.05)

	if (loop == False):
		cv2.imshow("imgOriginalScene", imgOriginalScene)

	if len(listOfPossiblePlates) == 0:
		if (loop == False):                          # if no plates were found
			print("no license plates were detected\n")             # inform user no plates were found
	else:                                                       # else
					# if we get in here list of possible plates has at leat one plate

					# sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
		listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
					# suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
		licPlate = listOfPossiblePlates[0]

		if (loop == False):
			cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
			cv2.imshow("imgThresh", licPlate.imgThresh)

		if len(licPlate.strChars) == 0:                     # if no chars were found in the plate
			if (loop == False):
				print("no characters were detected\n")
				return       # show message
			# end if
		drawRedRectangleAroundPlate(imgOriginalScene, licPlate)
		#print("\nlicense plate read from image = " + licPlate.strChars + "\n")    
		writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)
		licenses = licPlate.strChars
		# if ((licenses[0] and licenses[len(licenses)-1])  == ('0' or '1' or '2' or '3' or '4' or  '5' or '6' or '7' or '8' or '9')):
		#     licenses = ""
		#     print("license plate False !! \n and ")
						  # draw red rectangle around plate
		#print (licenses)
		#print(licPlate)
		if (loop == False):
			print("license plate read from image = " + licPlate.strChars + "\n")       # write license plate text to std out
				  # write license plate text on the image

		if (loop == False):
			cv2.imshow("imgOriginalScene", imgOriginalScene)                # re-show scene image
			cv2.imwrite("imgOriginalScene.png", imgOriginalScene)

	return imgOriginalScene, licenses

###################################################################################################
if __name__ == "__main__":
	main()


















