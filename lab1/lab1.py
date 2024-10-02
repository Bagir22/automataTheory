import re
import sys
import csv

def writeToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)
def fillResult(currState, nextState, matrix, result):
    for t in range(1, len(matrix[0])):
        if nextState == matrix[0][t]:
            for s in range(1, len(matrix)):
                result[s + 1][int(currState)] = matrix[s][t]
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
        s = line.split(';')
        stateMatrix.append([0]*len(s))
        if lineCount == 0:
            for i in s:
                i = i.strip('\n')
                i = i.strip('\t')
                if i != "":
                    transitions.append(i)
        else:
            for i in range(len(s)):
                if i == 0:
                    inStates.append(s[i])
                else:
                    a = s[i].split('/')
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

    for t in range(len(transitions)):
        stateMatrix[0][t+1] = transitions[t]


    for state in range(1, len(result[1])):
        currState = result[1][state]
        nextState = outStates[currState][1]
        fillResult(state, nextState, stateMatrix, result)

    writeToFile(outFile, result)

def mooreToMealy(inFile, outFile):
    f = open(inFile, 'r')

    matrix = []

    for line in f:
        s = line.split(';')
        s[-1] = s[-1].strip('\n').strip('\t')
        matrix.append(s)

    for i in range(2, len(matrix)):
        for s in range(1, len(matrix[i])):
            currState = matrix[i][s]
            t = re.sub('\D','', currState)
            exit = matrix[0][int(t)+1]
            matrix[i][s] = currState + "/" + exit

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
