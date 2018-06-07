## takes the CSV of the full answer key and the algorithm output

import csv
import ast
import numpy as np
from scipy.stats.stats import pearsonr

inputCSVFileName = "whateverOutput.csv"

inputAnsKeyFile = "AnswerKey.csv"

algoOutputList = []
ansKeyList = []
with open(inputCSVFileName, 'r') as inputCSV:
    csvreader = csv.reader(inputCSV, quoting=csv.QUOTE_NONNUMERIC)
    for eachRow in csvreader:
        rowString = eachRow[0]
        rowList = ast.literal_eval(rowString)
        algoOutputList.append(rowList)

with open(inputAnsKeyFile, 'r') as inputAnsCSV:
    csvreader = csv.reader(inputAnsCSV, delimiter='"')
    for eachRow in csvreader:
        rowString = eachRow[0]
        rowList = ast.literal_eval(rowString)
        ansKeyList.append(rowList)
        
print("program imported CSVs properly... comparing now")

circlesNotFound = 0
circleCountMismatch = 0
pearsonCoefs = []
for eachTest in range(len(ansKeyList)):
    # if -99 in either, skip.
    # if length of found circles =/= ans Key, report and add to circles missing statistics
    # if length of found circles ==!!, use correlation to compare found circles

    if (ansKeyList[eachTest][0][0] == -99 ) or (algoOutputList[eachTest][0][0] == - 99):
        print("circles not able to be found in this image: " + algoOutputList[eachTest][0][4])
        circlesNotFound = circlesNotFound + 1
    else:
        if len(ansKeyList[eachTest]) != len(algoOutputList[eachTest]):
            print("Circle counts are mismatched, anskey circles: "
                  + str(len(ansKeyList[eachTest])) + " algo output circles: "
                  + str(len(algoOutputList[eachTest])) + " file name: "
                  + algoOutputList[eachTest][0][4])
            circleCountMismatch = circleCountMismatch + 1
        else:
            print("circles found and identical, applying Pearson Correlation")
            for eachCircleIndex in range(len(ansKeyList[eachTest])):
                pearsonCo = pearsonr(ansKeyList[eachTest][eachCircleIndex], algoOutputList[eachTest][eachCircleIndex][0:4])
                pearsonCoefs.append(pearsonCo[0])

print("arrays where circles were not identifiable: " + str(circlesNotFound))
print("arrays where not all circles found: " + str(circleCountMismatch))
print("Pearson Correlation Avg Coefficient: " + str(np.mean(pearsonCoefs)))
            
        
