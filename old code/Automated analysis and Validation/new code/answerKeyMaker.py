# takes in a single array and allows user to place circles down
# on the image. the program then will take all the pixels
# within that circle and average them to find the brightness value
# which will be output for the user.


import cv2
import numpy as np
from operator import itemgetter

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("           click identified at: " +str([x,y])+ " with " +str(len(arrayCoords)+1)+" coordinates saved")
        arrayCoords.append([x,y])

def pullElementsFromList(datList,argument): # use this when you have a 2d list and want a specific element from each entry
    return [thatSpecificArgument[argument] for thatSpecificArgument in datList]

def circlePixelID(circleData): # output pixel locations within a circle given it's [x- coordinate, y-coordinate, radius]
    pixelLocations = []
    xCoordCirc = circleData[0] # separates the x and y coordinates of the center of the circles and the circle radius 
    yCoordCirc = circleData[1]
    radiusCirc = circleData[2]
    for exesInCircle in range(( xCoordCirc - radiusCirc ),( xCoordCirc + radiusCirc )):
        whyRange = np.sqrt(pow(radiusCirc,2) - pow((exesInCircle - xCoordCirc),2)) #calculates the y-coordinates that define the top and bottom bounds of a slice (at x position) of the circle 
        discreteWhyRange = int(whyRange) 
        for whysInCircle in range(( yCoordCirc - discreteWhyRange),( yCoordCirc + discreteWhyRange)):
            pixelLocations.append([exesInCircle,whysInCircle])
    return pixelLocations

def cvWindow(nameOfWindow, imageToShow, keypressBool):
    print("----------Displaying: "
          + str(nameOfWindow)
          + "    ----------")
    cv2.namedWindow(nameOfWindow, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(nameOfWindow, mouseLocationClick)
    cv2.imshow(nameOfWindow, imageToShow)
    pressedKey = cv2.waitKey(0)
    cv2.destroyAllWindows()
    if keypressBool:
        return pressedKey

def circleDistanceSorter(circleArray,position,numberofCaptSpots):
    # originally used "position" arg to sort circles based on their closeness to the center of the array. not needed in this build.
    # originally used "numberofCaptSpots too for this, but not needed anymore. This function serializes capture spot locations
    dist = []
    # print(circleArray)
    for i in circleArray: # calculates the distance from each circle to the center of the array
        distanceFromCenter = np.sqrt( pow((i[0] - position[0]),2) + pow((i[1] - position[1]),2) )
        dist.append(distanceFromCenter) # stores those values into an array
    pointers = range(len(circleArray)) # makes a pointer array that matches the pointers in the "circle" list
    closestCirclesPointers = sorted(zip(dist,pointers),reverse=False) # sorts and returns the sorted list [distance,pointers]
    # print(closestCirclesPointers)
    sortedCirclesFromCenter = []
    for eachIterator in range(len(circleArray)):
        sortedCirclesFromCenter.append(circleArray[closestCirclesPointers[eachIterator][1]]) #sorts!!
    #print(sortedCirclesFromCenter)
    #sortedCirclesFromCenter = circleArray[pullElementsFromList(closestCirclesPointers,1)] # returns the circle List entries sorted by distance using the pointers to the circle List
    captureSpots = sortedCirclesFromCenter[:numberofCaptSpots]
    sortedCaptureSpotsByWhy = sorted(captureSpots, key = itemgetter(1))
    maxCircleRadius = max(pullElementsFromList(sortedCaptureSpotsByWhy,2))
    yCoordinateRowOfCircles= sortedCaptureSpotsByWhy[0][1]
    fullySortedList = []
    rowCircleList = []
    for eachCircle in sortedCaptureSpotsByWhy:
        #print(eachCircle)
        if (abs(eachCircle[1]-yCoordinateRowOfCircles) < maxCircleRadius):
            #if the circle's y coordinate is within 1 radius of the y coordinate of the row of circles, then add to that row
            rowCircleList.append(eachCircle)
            #print(str(eachCircle) + " added")
        else:
            #if the next circle isn't, then sort the row of circles by X and add to the fully sorted list, and then iterate the ycoordinate of the next row
            rowCirclesSortedByX = sorted(rowCircleList, key = itemgetter(0))
            fullySortedList = fullySortedList + rowCirclesSortedByX
            #print(str(rowCircleList) + " flushed")
            rowCircleList = [] 
            yCoordinateRowOfCircles = eachCircle[1]
            rowCircleList.append(eachCircle)
    rowCirclesSortedByX = sorted(rowCircleList, key = itemgetter(0))
    fullySortedList = fullySortedList + rowCirclesSortedByX
    #print(str(rowCircleList) + " flushed")
#    print(fullySortedList)        
    return fullySortedList

fileName = input("what is the file name? ") #A1_subdivided_1

rawImageInput = cv2.imread(fileName, 0)

cvWindow("zoom in on capture spots only. click two corners", rawImageInput, False)
bottomRight = arrayCoords.pop()
topLeft = arrayCoords.pop()
cropXCoords = sorted([bottomRight[0],topLeft[0]])
cropYCoords = sorted([bottomRight[1],topLeft[1]])
captureArrayCoords = [cropYCoords[0],cropYCoords[1],cropXCoords[0],cropXCoords[1]] # y top, top bot, xleft, x right
zoomedImage = rawImageInput[captureArrayCoords[0]:captureArrayCoords[1],
                            captureArrayCoords[2]:captureArrayCoords[3]]

cvWindow("click on all circle centers, then press any key.", zoomedImage, False)

numberOfCircles = int(input("how many capture circles in image? "))

rawCircleLocations = []
for eachLocation in range(numberOfCircles):
    zoomedImgCoords = arrayCoords.pop()
    fullImgCoords = [zoomedImgCoords[0] + captureArrayCoords[2],
                     zoomedImgCoords[1] + captureArrayCoords[0]]
    rawCircleLocations.append(fullImgCoords)

cvWindow("click top and bottom of ONE capt circle (2) to define diameter", zoomedImage, False)
diameterTop = arrayCoords.pop()[1]
diameterBot = arrayCoords.pop()[1]
roughRadius = round( abs(diameterBot - diameterTop) / 2)
print("Radius : " + str(roughRadius))

fullCircleInfo = []
for eachCircle in rawCircleLocations:
    eachCircle = eachCircle + [roughRadius]
    fullCircleInfo.append(eachCircle)
    
fullCircleInfo = circleDistanceSorter(fullCircleInfo,
                                     [round(rawImageInput.shape[1]/2),round(rawImageInput.shape[0]/2)],
                                     numberOfCircles)

verificationImg = cv2.cvtColor(rawImageInput.copy(),cv2.COLOR_GRAY2BGR)

finalCircleInfo = []
for eachCircle in fullCircleInfo:
    cv2.circle(verificationImg, (eachCircle[0],eachCircle[1]),eachCircle[2],[0,0,255],1)
    circlePixels = circlePixelID(eachCircle)
    pixelIntensities = []
    for eachPixel in circlePixels:
        pixelIntensities.append(rawImageInput[eachPixel[1],eachPixel[0]])
    avgIntensity = np.array(pixelIntensities).mean()
    eachCircle = eachCircle + [avgIntensity]
    finalCircleInfo.append(eachCircle)
cvWindow("verify circle placement and radius", verificationImg, False)
cv2.imwrite("verification_image_" + fileName,verificationImg)
print(finalCircleInfo)

    
