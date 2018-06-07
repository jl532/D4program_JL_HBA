## this is the second attempt at making a more optimized circle ID program
## the last one was focused on non-trehalose pads

# import libraries
import cv2
import numpy as np
import sys
import csv
from operator import itemgetter

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("           click identified at: " +str([x,y])+ " with " +str(len(arrayCoords)+1)+" coordinates saved")
        arrayCoords.append([x,y])

def pullElementsFromList(datList,argument): # use this when you have a 2d list and want a specific element from each entry
    return [thatSpecificArgument[argument] for thatSpecificArgument in datList]

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
    # print(sortedCirclesFromCenter)
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

def circlePixelID(circleData): # output pixel locations of all circles within the list,
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

listOfSlideNames = ["p1",
                    "p3",
                    "A1",
                    "A2",
                    "ContrlSpots"]
                    
singleArrayFileNames = []
for eachSlideName in listOfSlideNames:
    for arrayNumber in range(24):
        singleArrayFileNames.append(eachSlideName + "_subdivided_" + str(arrayNumber + 1) + ".tif")

template_fileName = "template_array.tif"
arrayTemplate = cv2.imread(template_fileName, 0)
    
for eachFileName in singleArrayFileNames:
        
    fileName = eachFileName
    imgRaw = cv2.imread(fileName, 0)
    verImg = cv2.cvtColor(imgRaw.copy(), cv2.COLOR_GRAY2RGB)

    #cvWindow("img Raw", imgRaw, False)

    # template match the ideal with the array
    crossCorResults = cv2.matchTemplate(imgRaw, arrayTemplate, cv2.TM_CCORR_NORMED)
    indexOfMax = np.unravel_index(np.argmax(crossCorResults, axis=None),
                                      crossCorResults.shape)

    arrayCrop = imgRaw[indexOfMax[0] + 55:(indexOfMax[0] + arrayTemplate.shape[0] - 55),
                       indexOfMax[1] + 55:(indexOfMax[1] + arrayTemplate.shape[1] - 55)]

    ## draw rectangles on the verification image to show the isolation of the array and capture areas

    # draw rectangle around the full array area (including detection spots)
    cv2.rectangle(verImg,
               (indexOfMax[1], indexOfMax[0]),
               (indexOfMax[1] + arrayTemplate.shape[1], indexOfMax[0] + arrayTemplate.shape[0]),
               (255,0,0),3)

    # draw rectangle around the capture area
    # capture array area is defined by two corners: [55,55] and [484,478] RELATIVE to the indexOfMax
    cv2.rectangle(verImg,
                  (indexOfMax[1] + 55 , indexOfMax[0] + 55),
                  (indexOfMax[1] + 478, indexOfMax[0] + 478),
                  (0,255,0),3)

    # cvWindow("verification Image", verImg, False)

    # do circle detection on the capture area only
    medianBlurArg = 3
    arrayCropSmoothed = cv2.medianBlur(arrayCrop.copy(), medianBlurArg)
    minDistBetweenCircles = 27
    houghParam1 = 1
    houghParam2 = 9
    radiusLowerBound = 7 # given the 10um resolution. 5um would have radius of 14 min
    radiusUpperBound = 9 # given 10um resolution. 5um would have a radius of 18 max

    circlesRaw = cv2.HoughCircles(arrayCropSmoothed,
                                  cv2.HOUGH_GRADIENT,
                                  1,
                                  int(minDistBetweenCircles),
                                  param1=houghParam1,
                                  param2=houghParam2,
                                  minRadius=int(radiusLowerBound),
                                  maxRadius=int(radiusUpperBound))

    circlesRaw = np.uint32(np.around(circlesRaw))
    numberOfCirclesFound = len(circlesRaw[0])
    print("Preliminary default search found " + str(numberOfCirclesFound) + " spots")

    sortedCircles = circleDistanceSorter(circlesRaw[0],
                                         (int(arrayCrop.shape[1]/2) , int(arrayCrop.shape[0]/2)),
                                         numberOfCirclesFound)

    # plot each found circle on the verification image
    for eachCircle in sortedCircles:
        cv2.circle(verImg,
                   ((eachCircle[0] + indexOfMax[1] + 55),
                    (eachCircle[1] + indexOfMax[0] + 55)),
                   eachCircle[2],
                   (0,0,255),
                   1)

    # cvWindow("verification Image", verImg, False)

    # generate compare-able output to the answer key format

    finalCircleInfo = []
    for eachCircle in sortedCircles:
        circlePixels = circlePixelID(eachCircle)
        pixelIntensities = []
        for eachPixel in circlePixels:
            pixelIntensities.append(arrayCrop[eachPixel[1],eachPixel[0]])
        avgIntensity = np.array(pixelIntensities).mean()
        eachCircle = eachCircle + [avgIntensity]
        finalCircleInfo.append(eachCircle)
    cv2.imwrite("algorithm_output+" + fileName, verImg)
    print(finalCircleInfo)




