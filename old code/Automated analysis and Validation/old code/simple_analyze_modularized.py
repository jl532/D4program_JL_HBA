## add in labels of serialization of circle groupings, and then also debug overflow
## test plotting too somehow
## continue modularization of functions so they can be tested
## add in modular circle location/radius modification function



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
    radiusCirc = circleData[2] + 2
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
    

def subArrayGeneration(rawFullArrayImage):
    verImg = cv2.cvtColor(rawFullArrayImage.copy(), cv2.COLOR_GRAY2RGB)

    heightOfImage = rawFullArrayImage.shape[0] # row number
    widthOfImage = rawFullArrayImage.shape[1] # column number

    cvWindow("Raw, full image of all arrays. click to add 2 column dividers", rawFullArrayImage, False)
    verticalLineRight = arrayCoords.pop()[0]
    verticalLineLeft = arrayCoords.pop()[0]
    cv2.line(verImg, (verticalLineLeft, 0), (verticalLineLeft, heightOfImage), (255,0,0), 25)
    cv2.line(verImg, (verticalLineRight, 0),(verticalLineRight, heightOfImage), (255,0,0), 25)

    cvWindow("Raw, full image of all arrays. click to add 9 row dividers", rawFullArrayImage, False)
    yBounds = []
    for eachRowLine in range(9):
        horizontalLine = arrayCoords.pop()[1]
        yBounds.append(horizontalLine)
        cv2.line(verImg, (0, horizontalLine), (widthOfImage, horizontalLine), (0,255,0), 25)

    # cvWindow("final lined Image", verImg, False)

    yBounds = sorted(yBounds)
    xBounds = sorted([0, verticalLineLeft, verticalLineRight, widthOfImage])

    subdividedArrayList = []
    count = 0
    for eachColumn in range(3):
        for eachRow in range(8):
            count = count + 1
            # print("count: " + str(count) + " || column: " +str(eachColumn+1) + " || row: " +str(eachRow+1))
            leftBound = xBounds[eachColumn]
            rightBound = xBounds[eachColumn + 1]
            topBound = yBounds[eachRow]
            lowBound = yBounds[eachRow+1]
            
            cv2.putText(verImg, str(count),(xBounds[eachColumn] + 10, yBounds[eachRow+1]-30) , cv2.FONT_HERSHEY_SIMPLEX, 22,(255,120,120), 20, cv2.LINE_AA)
            
            subdividedArrayList.append(rawImageInput[topBound:lowBound,leftBound:rightBound])

                ###        testing purposes
    ##        cv2.namedWindow("subImage of " + str(count), cv2.WINDOW_NORMAL)
    ##        cv2.imshow("subImage of " + str(count), subArrayList[count-1])
    ##        cv2.waitKey(0)
    ##        cv2.destroyAllWindows()

    cvWindow("labeled verification image of subdivided Array", verImg, False)
    return subdividedArrayList # crops the raw image columnwise, going from top to bottom.

def circleParameterOptimization(templateArray):
    # outputs [circleParameters, captureRegionCoordinates, defaultCircles]
    print("Using the template array to calibrate circle finding algorithm")
    numberOfSpots = 6 # int( input("how many capture spots are there?  "))

    cvWindow("template Array: select CENTERS of two vertically adjacent circles (2)", templateArray, False)
    distBot = arrayCoords.pop()[1]
    distTop = arrayCoords.pop()[1]
    lowerBoundMinDistance = 5
    minDistBetweenCircles = abs(distBot - distTop) - lowerBoundMinDistance
    print("Minimum Distance Between Circles: " + str(minDistBetweenCircles))

    cvWindow("template Array: select top and bottom of ONE capt circle (2)", templateArray, False)
    diameterTop = arrayCoords.pop()[1]
    diameterBot = arrayCoords.pop()[1]
    roughRadius = round( abs(diameterBot - diameterTop) / 2)
    radiusBounds = 2
    radiusLowerBound = roughRadius - radiusBounds
    radiusUpperBound = roughRadius + radiusBounds
    print("Radius bounds: " + str(radiusLowerBound) + " with " + str(radiusUpperBound))

    print("Eliminate detection spots from standard/template array")
    cvWindow("select capture spot area, excluding the detection/trehalose pads. top left, then bottom right (2)", templateArray, False)
    bottomRight = arrayCoords.pop()
    topLeft = arrayCoords.pop()

    cropXCoords = sorted([bottomRight[0],topLeft[0]])
    cropYCoords = sorted([bottomRight[1],topLeft[1]])
    captureArrayCoords = [cropYCoords[0],cropYCoords[1],cropXCoords[0],cropXCoords[1]] # y top, top bot, xleft, x right
    templateCaptureArrayOnly = templateArray[captureArrayCoords[0]:captureArrayCoords[1],
                                             captureArrayCoords[2]:captureArrayCoords[3]]

    # initial circle finding algo applied to template capture array
    print("Optimizing circle finding algorithm based on template array")

    medianBlurArg = 3
    circleAlgoImageSmoothed = cv2.medianBlur(templateCaptureArrayOnly.copy(), medianBlurArg)
    houghParam1 = 40
    houghParam2 = 13
    print("current parameters--------------------------------------------------")
    print("Minimum distance between circles:   " + str(minDistBetweenCircles))
    print("parameter 1 (edge detection thres): " + str(houghParam1))
    print("parameter 2 (circle center thres):  " + str(houghParam2))
    print("radius lower bound:                 " + str(radiusLowerBound))
    print("radius upper bound:                 " + str(radiusUpperBound))

    circlesRaw = cv2.HoughCircles(circleAlgoImageSmoothed,
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

    firstPassCirclesImage = cv2.cvtColor(templateCaptureArrayOnly.copy(),cv2.COLOR_GRAY2BGR)
    templateCaptureArrayOnlyCenter = (int(templateCaptureArrayOnly.shape[1] / 2),
                                      int(templateCaptureArrayOnly.shape[0] / 2))
    sortedCircles = circleDistanceSorter(circlesRaw[0],
                                         templateCaptureArrayOnlyCenter,
                                         numberOfSpots)
    for j in sortedCircles:
        cv2.circle(firstPassCirclesImage,(j[0],j[1]),j[2],(0,0,255),1)
    
    print("options:")
    print("x - program found all circles correctly")
    print("m - manually enter hough parameters")
    print("p - manually place circles down")

    modifiedCircleParamsImg = firstPassCirclesImage.copy()
    
    circleParametersNeedOptimization = True
    
    while circleParametersNeedOptimization:
        pressedKey = cvWindow("circle finding algorithm results. (x) to continue. m manual entry. p place additional circles.", modifiedCircleParamsImg,True)
        if pressedKey == ord("x"):
            print("circle parameters have been optimized")
            circleParametersNeedOptimization = False
        if pressedKey == ord("m"):
            print("manual entry for parameters selected")
            minDistBetweenCircles = int( input("minDistBetweenCircles current value: "
                                              + str(minDistBetweenCircles)
                                              + ". input new value: "))
            houghParam1 = int( input("houghParam1 current value: "
                                            + str(houghParam1)
                                            + ". input new value: "))
            houghParam2 = int( input("houghParam2 current value: "
                                            + str(houghParam2)
                                            + ". input new value: "))
            radiusLowerBound = int( input("radiusLowerBound current value: "
                                          + str(radiusLowerBound)
                                          + ". input new value: "))
            radiusUpperBound = int( input("radiusUpperBound current value: "
                                          + str(radiusUpperBound)
                                          + ". input new value: "))
            medianBlurArg = int( input("medianBlurArg current value: "
                                      + str(medianBlurArg)
                                      + ". input new value (needs to be odd): "))
            roughRadius = int( input("optimal circle radius current value: "
                                     + str(roughRadius)
                                     + ". input new value: " ))
                                
            circleAlgoImageSmoothed = cv2.medianBlur(templateCaptureArrayOnly.copy(), medianBlurArg)
            circlesRaw = cv2.HoughCircles(circleAlgoImageSmoothed,
                                  cv2.HOUGH_GRADIENT,
                                  1,
                                  int(minDistBetweenCircles),
                                  param1=houghParam1,
                                  param2=houghParam2,
                                  minRadius=int(radiusLowerBound),
                                  maxRadius=int(radiusUpperBound))
            circlesRaw = np.uint32(np.around(circlesRaw))
            numberOfCirclesFound = len(circlesRaw[0])
            print("Additional search found " + str(numberOfCirclesFound) + " spots given manual entry")
            modifiedCircleParamsImg = cv2.cvtColor(templateCaptureArrayOnly.copy(),cv2.COLOR_GRAY2BGR)
            sortedCircles = circleDistanceSorter(circlesRaw[0],
                                                 templateCaptureArrayOnlyCenter,
                                                 numberOfSpots)            
            for j in sortedCircles:
                cv2.circle(modifiedCircleParamsImg,(j[0],j[1]),j[2],(0,0,255),1)
            cvWindow("Manually changed circle parameters result.", modifiedCircleParamsImg, True)            
        if pressedKey == ord("p"):
            additionalCircles = int(input("How many circles must be manually entered?  "))
            cvWindow("click where you would like to place a circle", modifiedCircleParamsImg, False)
            extraCircleLocList = []
            for each in range(additionalCircles):
                extraCircleLocList.append(arrayCoords.pop() + [roughRadius])
                print("        Extra circle assigned at position: " + str(extraCircleLocList[each]))
                sortedCircles.append(np.asarray(extraCircleLocList[each],
                                                dtype = np.uint16))
                cv2.circle(modifiedCircleParamsImg,(extraCircleLocList[each][0],extraCircleLocList[each][1]),
                           extraCircleLocList[each][2],(0,255,255),1)
                cv2.circle(modifiedCircleParamsImg,(extraCircleLocList[each][0],extraCircleLocList[each][1]),
                           1,(0,255,255),1)
            pressedKey = cvWindow("additional Circle additions, x to confirm selection, any other key to redo",
                                  modifiedCircleParamsImg, True)
            if pressedKey == ord("x"):
                sortedCircles = circleDistanceSorter(sortedCircles, templateCaptureArrayOnlyCenter, numberOfSpots)
                circleParametersNeedOptimization = False
                
    listOfCircleParams = [minDistBetweenCircles,
                          houghParam1,
                          houghParam2,
                          radiusLowerBound,
                          radiusUpperBound,
                          medianBlurArg,
                          roughRadius]
                          
    return [listOfCircleParams, captureArrayCoords, sortedCircles, modifiedCircleParamsImg]

    
########################################## main body here

fileName = "slide1.tif" #input("what is the file name? Must be in the same directory as analyzer.py:   ")
outputCSVFileName = "simple_analyze_output.csv"
rawImageInput = cv2.imread(fileName, 0)

subArrayList = subArrayGeneration(rawImageInput)

bestArray = int( input("Type in the array with the strongest capture spot intensities, to form the template array. enter number:  "))

cvWindow("select Ideal Array Area. Select top left and bottom right corner (2)", subArrayList[bestArray-1], False)
arrayBotRigCoords = arrayCoords.pop()
arrayTopLefCoords = arrayCoords.pop()
cropXCoords = sorted([arrayBotRigCoords[0],arrayTopLefCoords[0]])
cropYCoords = sorted([arrayBotRigCoords[1],arrayTopLefCoords[1]])
template = subArrayList[bestArray-1][cropYCoords[0]:cropYCoords[1],
                                          cropXCoords[0]:cropXCoords[1]]

[circleParameters, captureRegionCoordinates, defaultCircles, templateCircleOverlay] = circleParameterOptimization(template)

#captureRegionCoordinates = [y top, top bot, xleft, x right] in relation to the cropped Template array (with detection spots)
    
circleGroupingBool = True
print("group circles based on replicates")

groupGroupCircles = []
groupCircles = []

# establish first image of the template array
templateCaptureOnly = template[captureRegionCoordinates[0]:captureRegionCoordinates[1],
                               captureRegionCoordinates[2]:captureRegionCoordinates[3]]
templateCaptureOnly = cv2.cvtColor(templateCaptureOnly,cv2.COLOR_GRAY2BGR)
drawnCaptureOnly = templateCaptureOnly.copy()

while circleGroupingBool:
    
    pressedKey = cvWindow("group/edit the circles. c to select, x to confirm group, z to end", drawnCaptureOnly, True)
    
    if pressedKey == ord("c"):
        print("circle selected")
        clickLocation = arrayCoords.pop()
        # find closest circle to given location
        
        distanceCollator = []
        for eachCircle in defaultCircles:
            distanceFromClick = np.sqrt( pow((eachCircle[0] - clickLocation[0]),2)
                                         + pow((eachCircle[1] - clickLocation[1]),2) )
            distanceCollator.append(distanceFromClick)
        pointers = range(len(defaultCircles))
        closestCirclePointers = sorted(zip(distanceCollator,pointers),reverse = False)
        selectedCircle = defaultCircles[pullElementsFromList(closestCirclePointers,1)[0]]
        
        # punch in circle on verification image to show that it has been considered
        cv2.circle(drawnCaptureOnly, (selectedCircle[0], selectedCircle[1]), selectedCircle[2], (0,0,255), 1)
        
        # allow edits to the selected circle 
        circleEditBool = True
        while circleEditBool:
            pressedKey = cvWindow("verify circle position and radius. c to confirm and add to current group, p to change position, r to change radius",
                                  drawnCaptureOnly, True)
            if pressedKey == ord("c"):
                print("circle verified and added to current grouping")
                circleEditBool = False
            if pressedKey == ord("p"):
                # reset drawnCapture image
                #drawnCaptureOnly = templateCaptureOnly.copy()

                # let user select new location of this circle 
                cvWindow("Click to adjust position of the circle", templateCaptureOnly, False)
                clickLocation = arrayCoords.pop()
                # cvWindow("circle placed in new location", drawnCaptureOnly, False)
                selectedCircle = np.asarray([clickLocation[0], clickLocation[1], circleParameters[6]], dtype = np.uint16) # applies new location and default radius (avg of hough id)
                defaultCircles[pullElementsFromList(closestCirclePointers,1)[0]] = selectedCircle
                print("circle information updated: " + str(selectedCircle))
            if pressedKey == ord("r"):
                newRadiusEntry = int(input("Current Circle Radius: " + str(selectedCircle[2])+ ". Enter new radius: "))
                #drawnCaptureOnly = templateCaptureOnly.copy()
                # cvWindow("circle radius adjusted", drawnCaptureOnly, False)
                selectedCircle = np.asarray([selectedCircle[0], selectedCircle[1], newRadiusEntry], dtype = np.uint16) # inputs new radius given user input
                defaultCircles[pullElementsFromList(closestCirclePointers,1)[0]] = selectedCircle
                print("circle information updated: " + str(selectedCircle))
                
            # draw in the newly edited circle in drawnCaptureOnly
            drawnCaptureOnly = templateCaptureOnly.copy()
            if groupCircles:                
                for eachCirclePointer in groupCircles:
                    cv2.circle(drawnCaptureOnly, (defaultCircles[eachCirclePointer][0], defaultCircles[eachCirclePointer][1]),
                               defaultCircles[eachCirclePointer][2], (255,0,0), 1)
            cv2.circle(drawnCaptureOnly, (selectedCircle[0], selectedCircle[1]), selectedCircle[2], (0,200,0), 1)
        groupCircles.append(pullElementsFromList(closestCirclePointers,1)[0])
        
    if pressedKey == ord("x"):
        print("CIRCLES GROUPED")
        groupGroupCircles.append(groupCircles)
        
        for eachGroupedCircle in groupCircles:
            cv2.circle(drawnCaptureOnly, (defaultCircles[eachGroupedCircle][0], defaultCircles[eachGroupedCircle][1]),
                       defaultCircles[eachGroupedCircle][2], (255,255,0), 1)
            
        groupCircles = []
    if pressedKey == ord("z"):
        print("GROUPS ESTABLISHED")
        circleGroupingBool = False
    cv2.destroyAllWindows()

### can be used later to optimize runtime-- setting default pixel locations first so don't need to recalculate each time
##defaultPixelLocations = []
##for eachGroup in groupGroupCircles:
##    circleInfoCollatorList = []
##    for eachPointerInGroup in eachGroup:
##        circleInfoCollatorList.append(sortedCircles[eachPointerInGroup])
##    defaultPixelLocations.append(circlePixelID(circleInfoCollatorList))


print("default pixel locations established")
print("------------------------------------------------------------------")
print("groups assigned, iterating over all arrays now.")

# circle accepts coordinates as (x,y). indexOfMax is reported as (y,x) and templateArray.shape is also (y,x)

#indicesListArrayNorms = []
count = 0
outputList = []
for eachArray in subArrayList:
    print("array number: " + str(count+1))
    count = count + 1
    crossCorResults = cv2.matchTemplate(eachArray, template, cv2.TM_CCORR_NORMED)
    indexOfMax = np.unravel_index(np.argmax(crossCorResults, axis=None),
                                  crossCorResults.shape)
    eachArrayTemplateMatch = eachArray[indexOfMax[0]:(indexOfMax[0] + template.shape[0]),
                                    indexOfMax[1]:(indexOfMax[1] + template.shape[1])]

    # correction to re-crop each array to just include capture area of array only.
    eachArrayCapture = eachArrayTemplateMatch[captureRegionCoordinates[0]:captureRegionCoordinates[1],
                                           captureRegionCoordinates[2]:captureRegionCoordinates[3]]
    
    circleImageSmoothed = cv2.medianBlur(eachArrayCapture, circleParameters[5])
    circlesRaw = cv2.HoughCircles(circleImageSmoothed,
                                  cv2.HOUGH_GRADIENT,
                                  1,
                                  circleParameters[0],
                                  param1=circleParameters[1],
                                  param2=circleParameters[2],
                                  minRadius=circleParameters[3],
                                  maxRadius=circleParameters[4])
    if circlesRaw is None:
        defaultCircleLocations = True
        print("no circles identified... default locations applied")
        sortedCirclesEachArray = defaultCircles
    else:
        circles = np.uint16(np.around(circlesRaw))
        
        defaultCircleLocations = False
        eachArrayCaptureCenter = (int(eachArrayCapture.shape[1] / 2),
                           int(eachArrayCapture.shape[0] / 2))
        sortedCirclesEachArray = circleDistanceSorter(circles[0],
                                                      eachArrayCaptureCenter,
                                                      len(defaultCircles))
        if len(circles[0]) < len(defaultCircles): # if not enough circles are found in each array, just go for the default circle locations
            defaultCircleLocations = True
            print("too few circles identified: " + str(len(circles[0])) + " -- default circle locations applied")
            sortedCirclesEachArray = defaultCircles
        else:
            for eachPointer in range(len(defaultCircles)):
                print("pointer of circle: " + str(eachPointer))
                print("x val diff: " + str(defaultCircles[eachPointer][0] - sortedCirclesEachArray[eachPointer][0]) )
                print("y val diff: " + str(defaultCircles[eachPointer][1] - sortedCirclesEachArray[eachPointer][1]))
                distanceComparison = (abs(defaultCircles[eachPointer][0] - sortedCirclesEachArray[eachPointer][0])
                                      + abs(defaultCircles[eachPointer][1] - sortedCirclesEachArray[eachPointer][1]))
                print("distance between template location and observed circle:  " + str(distanceComparison))
                print("radius of circle at given position:  " + str(defaultCircles[eachPointer][2]))
                if distanceComparison > defaultCircles[eachPointer][2]: # if any detected circle is outside the radius of the template circles, set this array's circle locations to default locations (according to the template)
                    defaultCirclexLocations = True
                    print("circle locations too different from template locations-- default circle locations applied")
                    sortedCirclesEachArray = defaultCircles # insert default/template circle locations
                    break
            if defaultCircleLocations == False:
                print("circle locations consistent with template location")
  # verification purposes
    verImg = cv2.cvtColor(eachArrayCapture.copy(),cv2.COLOR_GRAY2BGR)
    for i in sortedCirclesEachArray:
        cv2.circle(verImg,(i[0],i[1]),circleParameters[6],(0,255,0),1)
        cv2.circle(verImg,(i[0],i[1]),1,(0,0,255),1)
    cvWindow("verification of circle placement", verImg, False)

    # pull and average intensities
    outputEachArrayList = []
    for eachGroup in groupGroupCircles: # [0, 3, 6, 9 ,12] [1, 4, 7, 10, 13]
        outputSubgroupList = []
        for eachPointer in eachGroup: # individual numbers
            captureIntensities = []
            pixelLocationsPerCircle = circlePixelID(sortedCirclesEachArray[eachPointer])
            for eachPixelLocationInCircles in pixelLocationsPerCircle:
                captureIntensities.append(eachArrayCapture[eachPixelLocationInCircles[1],
                                                           eachPixelLocationInCircles[0]])
            avgIntensity = np.array(captureIntensities).mean()
            outputSubgroupList.append([eachPointer, avgIntensity])
        outputEachArrayList.append([count, outputSubgroupList])
        print("group output success")
    outputList.append(outputEachArrayList)
            
            
            
    #indicesListArrayNorms.append(indexOfMax)
print("output List generated, csv output generating now")

with open(outputCSVFileName, 'w', newline='') as outputCSV:
    csvWriter = csv.writer(outputCSV, delimiter= ",", quotechar = "|" , quoting = csv.QUOTE_MINIMAL)
    for eachArray in outputList:
        for eachCaptureGroup in eachArray:
            for eachCaptureSpot in eachCaptureGroup[1]:
                csvWriter.writerow( [eachCaptureGroup[0]] + [eachCaptureSpot[0]] + [eachCaptureSpot[1]])
        

print("program terminated with no errors.")


