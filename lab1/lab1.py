import re
import sys
import csv

def writeToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)

def fillResult(currState, nextState, matrix, result):
    for i in range(1, len(matrix[0])):
        if nextState == matrix[0][i]:
            for j in range(1, len(matrix)):
                result[j + 1][int(currState)] = matrix[j][i]

def mealyToMoore(inFile, outFile):
    f = open(inFile, 'r')

    transitions = []
    inStates = []
    outStates = {}
    lineCount = 0
    statesSet = set()
    transitionsState = {}
    stateMatrix = []

    for line in f:
        splited = line.split(';')
        stateMatrix.append([0]*len(splited))
        if lineCount == 0:
            for item in splited:
                item = item.strip('\n').strip('\t')
                if item != "":
                    transitions.append(item)
        else:
            for i in range(len(splited)):
                if i == 0:
                    inStates.append(splited[i])
                else:
                    a = splited[i].split('/')
                    a[1] = a[1].strip('\n').strip('\t')
                    currState = "S" + str(len(outStates.keys()))
                    currString = str(a[0]) + "/" + str(a[1])
                    if currString not in statesSet:
                        stateMatrix[lineCount][i] = currState
                        statesSet.add(currString)
                        transitionsState[currString] = currState
                        outStates[currState] = [a[1], a[0]]
                    else:
                        currState = transitionsState[currString]
                        stateMatrix[lineCount][i] = currState
        lineCount += 1

    result = [["" for _ in range(len(outStates) + 1)] for _ in range(len(inStates) + 2)]

    for i in range(len(outStates.items())):
        result[0][i+1] = list(outStates.items())[i][1][0]
        result[1][i+1] = list(outStates.items())[i][0]

    for i in range(len(inStates) + 2):
        if i > 1:
            result[i][0] = inStates[i-2]

    for i in range(len(transitions)):
        stateMatrix[0][i+1] = transitions[i]


    for state in range(1, len(result[1])):
        currState = result[1][state]
        nextState = outStates[currState][1]
        fillResult(state, nextState, stateMatrix, result)

    writeToFile(outFile, result)

def mooreToMealy(inFile, outFile):
    f = open(inFile, 'r')

    matrix = []

    for line in f:
        splited = line.split(';')
        splited[-1] = splited[-1].strip('\n').strip('\t')
        matrix.append(splited)

    for i in range(2, len(matrix)):
        for j in range(1, len(matrix[i])):
            currState = matrix[i][j]
            stateNum = re.sub('\D','', currState)
            exit = matrix[0][int(stateNum)+1]
            matrix[i][j] = currState + "/" + exit

    matrix.pop(0)
    writeToFile(outFile, matrix)

if __name__ == "__main__":
    algorithm = sys.argv[1]
    inFile = sys.argv[2]
    outFile = sys.argv[3]
    if algorithm == "mealy-to-moore":
        mealyToMoore(inFile, outFile)
    elif algorithm == "moore-to-mealy":
        mooreToMealy(inFile, outFile)
    else:
        print("Invalid algorithm")
