from panorama import Panorama
import sys
import numpy
import imutils
import cv2

def readImages(imageString):
	images = []

	# Get images from arguments.
	for i in range(0, len(imageString)):
		img = cv2.imread(imageString[i])
		images.append(img)

	return images

def findAndDescribeFeatures(image):
	#Getting gray image
	grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	#Find and describe the features.
	# Fast: sift = cv2.xfeatures2d.SURF_create()
	sift = cv2.xfeatures2d.SIFT_create()

	#Find interest points.
	keypoints = sift.detect(grayImage, None)

	#Computing features.
	keypoints, features = sift.compute(grayImage, keypoints)

	#Converting keypoints to numbers.
	keypoints = numpy.float32([kp.pt for kp in keypoints])


	return keypoints, features

def matchFeatures(featuresA, featuresB):

	# Slow: featureMatcher = cv2.DescriptorMatcher_create("BruteForce")
	featureMatcher = cv2.DescriptorMatcher_create("FlannBased")
	matches = featureMatcher.knnMatch(featuresA,featuresB, k=2)
	return matches

def generateHomography(allMatches, keypointsA, keypointsB, ratio, ransacRep):
	if not allMatches:
		return None
	matches = []

	for match in allMatches:
		# Lowe's ratio test
		if len(match) == 2 and (match[0].distance/match[1].distance) < ratio:
			matches.append(match[0])

	pointsA = numpy.float32([keypointsA[m.queryIdx] for m in matches])
	pointsB = numpy.float32([keypointsB[m.trainIdx] for m in matches])

	if len(pointsA)>4:
		H, status = cv2.findHomography(pointsA, pointsB, cv2.RANSAC,ransacRep)
		return matches, H, status
	else:
		return None


images = readImages(sys.argv[1::])

while len(images)>1:
	imgR = images.pop()
	imgL = images.pop()

	interestsR, featuresR = findAndDescribeFeatures(imgR)
	interestsL, featuresL = findAndDescribeFeatures(imgL)

	allMatches = matchFeatures(featuresR, featuresL)
	_, H, _ = generateHomography(allMatches, interestsR, interestsL, 0.75, 4.0)

	result = cv2.warpPerspective(imgR, H, 
		(imgR.shape[1]+imgL.shape[1], imgR.shape[0]))
	result[0:imgL.shape[0], 0:imgL.shape[1]] = imgL
	images.append(result)

result = imutils.resize(images[0], height=260)
cv2.imshow("Result", result)
cv2.imwrite("Result.jpg", result)

cv2.waitKey(0)