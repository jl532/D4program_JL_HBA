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


# python script must be in the same directory as the image you are importing, excluding the extension ".tif"
fileNameNoExt = input("enter file name of the full slide image you want to divide: ")
fileName = fileNameNoExt + ".tif"
rawImageInput = cv2.imread(fileName, 0)
subArrayList = subArrayGeneration(rawImageInput)

includedArrays = []
iterator = 1
pseudoIter = 1
for eachSubArray in subArrayList:
    #pressedKey = cvWindow("Array number " + str(iterator) + " x to include, c to ignore", eachSubArray, True)
    #if pressedKey == ord("x"):
    print("Array number " + str(iterator) + " included")
    #includedArrays.append(eachSubArray)
    cv2.imwrite(fileNameNoExt + "_subdivided_" + str(pseudoIter) + ".tif", eachSubArray)
    pseudoIter = pseudoIter + 1
    iterator = iterator + 1












          
    
