import sys
import csv

def WriteToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)

def GetOriginalMealy(infile):
    f = open(inFile, 'r')
    original = []
    lineCount = 0

    for line in f:
        splited = line.split(';')
        original.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            if i == 0 or lineCount <= 1:
                original[lineCount][i] = item
            else:
                '''if ',' in item:
                    original[lineCount][i] = item.split(',')
                else:'''
                original[lineCount][i] = item

        lineCount += 1

    print("Original")
    for i in range(len(original)):
        print(original[i])
    print()

    return original

def ReadNFA(original):
    states = dict()
    terminals = []
    transitions = []

    for i in range(1, len(original[1])):
        states[original[1][i]] = original[0][i]

    for i in range(2, len(original)):
        terminals.append(original[i][0])

    for i in range(1, len(original[0])):
        for j in range(2, len(original)):
            if original[j][i] != '':
                transitions.append([original[1][i], original[j][i], original[j][0]])

    return states, terminals, transitions


def MakeDFA(original, states, terminals, transitions):
    stateCount = 0
    statesMap = dict()
    dfaStates = []
    dfaTransitions = []


    for transition in transitions:
        nextState = ""
        if transition[1] in statesMap:
            nextState = statesMap[transition[1]]
        else:
            nextState = f"S{stateCount}"
            statesMap[transition[1]] = nextState
            stateCount += 1

        #print(transition[0], nextState, transition[2])
    #print(statesMap)

    result = [['' for _ in range(len(statesMap)+1)] for _ in range(len(terminals) + 1 if 'ε' in terminals else len(terminals))]

    i = 1
    for k, v in statesMap.items():
        result[1][i] = v
        for state in k.split(','):
            if states[state] == 'F':
                result[0][i] = 'F'
        i += 1

    i = 2
    for t in terminals:
        if t != 'ε':
            result[i][0] = t
        i += 1

    for i, (stateSet, dfaState) in enumerate(list(statesMap.items()), start=1):
        for j, terminal in enumerate(terminals, start=2):
            if terminal == 'ε':
                continue

            nextStateSet = set()
            for state in stateSet.split(','):
                for transition in transitions:
                    if transition[0] == state and transition[2] == terminal:
                        if isinstance(transition[1], list):
                            for substate in transition[1]:
                                nextStateSet.add(substate)
                        else:
                            nextStateSet.add(transition[1])

            nextStateKey = ','.join(sorted(nextStateSet))
            if nextStateKey:
                if nextStateKey not in statesMap:
                    statesMap[nextStateKey] = f"S{stateCount}"
                    stateCount += 1
                nextState = statesMap[nextStateKey]
                result[j][i] = nextState

    return result


if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    original = GetOriginalMealy(inFile)
    states, terminals, transitions = ReadNFA(original)
    '''print(states)
    print(terminals)
    print(transitions)
    print()'''

    result = MakeDFA(original, states, terminals, transitions)

    for i in result:
        print(i)

    WriteToFile(outFile, result)

