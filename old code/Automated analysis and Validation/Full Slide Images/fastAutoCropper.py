## this script will allow the user to crop full slide images
## using the opencv library, dividing it into single array images.
## the program will also allow the user to manually circle spots
## and the program will output the avg spot brightness. 


import cv2

arrayCoords = []
def mouseLocationClick(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("           click identified at: " +str([x,y])+ " with " +str(len(arrayCoords)+1)+" coordinates saved")
        arrayCoords.append([x,y])

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

## this function will allow the user to manually divide the full slide image into 24 individual areas
def subArrayGeneration(rawFullArrayImage, template):
    verImg = cv2.cvtColor(rawFullArrayImage.copy(), cv2.COLOR_GRAY2RGB)

    heightOfImage = rawFullArrayImage.shape[0] # row number
    widthOfImage = rawFullArrayImage.shape[1] # column number



    
##    if widthOfImage < 3000 and widthOfImage > 1800:
##        # resolution is 10um
##        print("resolution autodetection: 10 um")
##        verticalLineRight = 1480
##        verticalLineLeft = 680
##        yBounds = [0, 743, 1687, 2542, 3444, 4368, 5285, 6160, heightOfImage]
    
    fullArrayDS2 = cv2.pyrDown(cv2.pyrDown(rawFullArrayImage.copy()))
    templateArrayDS2 = cv2.pyrDown(cv2.pyrDown(template.copy()))+
    
    width_template, height_template = templateArrayDS2.shape[::-1]
    res = cv2.matchTemplate(fullArrayDS2,templateArrayDS2,cv2.TM_CCORR_NORMED)

    threshold = 0.6
    locations = np.where( res >= threshold)
    neighborRadius = max(width_template, height_template)
    rawPotentialArrays = zip(*locations[::-1])

    stagedManyArrays = []
    arrayIterator = 0
    bestCitizens = []
    
    for each in range(24): # there should be 24 arrays in a slide image
        bestCitizens.append([0,[0,0],0])
    for eachRawPotArray in rawPotentialArrays:
        # stage the first array in the potential arrays
        if len(stagedManyArrays) == 0:
            stagedManyArrays.append([ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator])
            # temporarily set the first array as a "best citizen"
            bestCitizens[arrayIterator] = ([ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator])
        else:
            # from the second potential array onward
            storageSpace = []
            # compare these arrays with the staged arrays
            for eachStagedArray in stagedManyArrays:
                # if a newly presented potential array is within the neighborhood of previously staged array, STORE the newly presented array
                if ((eachRawPotArray[0] < eachStagedArray[1][0] + neighborRadius) and (eachRawPotArray[0] > eachStagedArray[1][0] - neighborRadius)):
                    if ((eachRawPotArray[1] < eachStagedArray[1][1] + neighborRadius) and (eachRawPotArray[1] > eachStagedArray[1][1] - neighborRadius)):
                        #print(str([eachRawPotArray[0],eachRawPotArray[1]]) + " close to " + str([eachStagedArray[1][0], eachStagedArray[1][1]]))
                        storageSpace = [res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]], eachStagedArray[2]]
                        # if the newly presented potential array is within the neighborhood, and has a better RES score, replace it as the best citizen
                        if (res[eachRawPotArray[1],eachRawPotArray[0]] > bestCitizens[eachStagedArray[2]][0]):
                            bestCitizens[eachStagedArray[2]] = [ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , eachStagedArray[2]]
            # if the newly presented array isn't within the neighborhood of a staged array, open a new neighborhood and iterate to a new best citizen
            if (len(storageSpace) ==  0 ):
                #print(str([eachRawPotArray[0],eachRawPotArray[1]]) + " NOT close to " + str([eachStagedArray[1][0], eachStagedArray[1][1]]))
                arrayIterator = arrayIterator + 1
                storageSpace= [res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]], arrayIterator]
                if (res[eachRawPotArray[1],eachRawPotArray[0]] > bestCitizens[arrayIterator][0]):
                    bestCitizens[arrayIterator] = [ res[eachRawPotArray[1],eachRawPotArray[0]], [eachRawPotArray[0],eachRawPotArray[1]] , arrayIterator]
            stagedManyArrays.append(storageSpace)
    
    



    for eachRowLine in yBounds:
        cv2.line(verImg, (0, eachRowLine), (widthOfImage, eachRowLine), (0,255,0), 25)
    cv2.line(verImg, (verticalLineLeft, 0), (verticalLineLeft, heightOfImage), (255,0,0), 25)
    cv2.line(verImg, (verticalLineRight, 0),(verticalLineRight, heightOfImage), (255,0,0), 25)

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
            
            cv2.putText(verImg, str(count),(xBounds[eachColumn] + 10, yBounds[eachRow+1]-30) , cv2.FONT_HERSHEY_SIMPLEX, 12,(255,120,120), 20, cv2.LINE_AA)
            
            subdividedArrayList.append(rawImageInput[topBound:lowBound,leftBound:rightBound])

                ###        testing purposes
    ##        cv2.namedWindow("subImage of " + str(count), cv2.WINDOW_NORMAL)
    ##        cv2.imshow("subImage of " + str(count), subArrayList[count-1])
    ##        cv2.waitKey(0)
    ##        cv2.destroyAllWindows()

    cvWindow("labeled verification image of subdivided Array", verImg, False)
    return subdividedArrayList # crops the raw image columnwise, going from top to bottom.


# python script must be in the same directory as the image you are importing, excluding the extension ".tif"
fileNameNoExt = input("enter file name of the full slide image you want to divide: ")
fileName = fileNameNoExt + ".tif"
templateName = "templateDS.tif"
rawImageInput = cv2.imread(fileName, 0)
templateInput = cv2.imread(templateName,0)
subArrayList = subArrayGeneration(rawImageInput,templateInput)

##includedArrays = []
##iterator = 1
##pseudoIter = 1
##for eachSubArray in subArrayList:
##    #pressedKey = cvWindow("Array number " + str(iterator) + " x to include, c to ignore", eachSubArray, True)
##    #if pressedKey == ord("x"):
##    print("Array number " + str(iterator) + " included")
##    #includedArrays.append(eachSubArray)
##    cv2.imwrite(fileNameNoExt + "_subdivided_" + str(pseudoIter) + ".tif", eachSubArray)
##    pseudoIter = pseudoIter + 1
##    iterator = iterator + 1


# HS1 was 7200, 2185
# HS2 was 7200, 2185
# HS3 was 7200, 2185
# FBS1 was 6994, 2189
# FBS2 was 6994, 2189
# TB1 was 6994, 2189
# TB2 was 6994, 2189

# A1 was 6966, 2200
# Faris was 14285, 4358
















          
    
