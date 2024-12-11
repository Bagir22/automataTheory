import sys
import csv
from collections import deque
from collections import defaultdict

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
                original[lineCount][i] = item

        lineCount += 1

    print("Original")
    for i in range(len(original)):
        print(original[i])
    print()

    return original

def ReadNFA(original):
    states = []
    terminals = []
    transitions = dict()

    for i in range(1, len(original[1])):
        states.append(original[1][i])

    for i in range(2, len(original)):
        terminals.append(original[i][0])

    for stateIdx in range(len(states)):
        transitions[original[1][stateIdx+1]] = dict()
        for i in range(2, len(original)):
            if original[i][stateIdx+1] != '':
                if ',' in original[i][stateIdx+1]:
                    nextState = original[i][stateIdx+1].split(',')
                else:
                    nextState = [original[i][stateIdx+1]]
                transitions[original[1][stateIdx+1]][original[i][0]] = nextState

    return states, terminals, transitions


def eTransitions(state, transitions):
    eTransitions = [state]

    queue = []
    queue.append(state)

    while queue:
        current = queue[0]
        queue = queue[1:]
        if 'ε' in transitions.get(current, {}):
            for next_state in transitions[current]['ε']:
                if next_state not in eTransitions:
                    queue.append(next_state)
                    eTransitions.append(next_state)

    return eTransitions

def MakeDFA(original, states, terminals, transitions):
    dfaTerminals = []
    for t in terminals:
        if t != 'ε':
            dfaTerminals.append(t)

    e = eTransitions(original[1][1], transitions)

    count = 0
    queue = deque()
    dfaStates = dict()
    dfaTransitions = defaultdict(dict)
    if e:
        dfaStates[frozenset(e)] = f"S{count}"
        count += 1
        queue.appendleft(frozenset(e))

    while queue:
        current = queue.pop()
        currentState = dfaStates[frozenset(current)]

        for terminal in dfaTerminals:
            transitionsSet = set()
            for prev in current:
                if terminal in transitions[prev]:
                    next_states = transitions[prev][terminal]
                    for next_state in next_states:
                        transitionsSet.update(eTransitions(next_state, transitions))

            if transitionsSet:
                if frozenset(transitionsSet) not in dfaStates:
                    newState = f"S{count}"
                    dfaStates[frozenset(transitionsSet)] = newState
                    queue.append(transitionsSet)
                    count += 1

                dfaTransitions[currentState][terminal] = dfaStates[frozenset(transitionsSet)]

    result = [['' for _ in range(len(dfaTransitions) + 1)] for _ in range(len(dfaTerminals) + 2)]

    for i in range(len(dfaTerminals)):
        result[i+2][0] = dfaTerminals[i]

    finalStates = dict()
    for k, v in dfaStates.items():
        for state in set(k):
            stateIdx = original[1].index(state)
            if original[0][stateIdx] == 'F':
                finalStates[v] = "F"

    for i, v in enumerate(dfaTransitions.items()):
        result[1][i+1] = v[0]
        if finalStates.get(v[0]) and finalStates[v[0]] == "F":
            result[0][i + 1] = "F"

        for next in v[1].items():
            for j in range(2, len(result)):
                if result[j][0] == next[0]:
                    result[j][i+1] = next[1]

    return result


if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    original = GetOriginalMealy(inFile)
    states, terminals, transitions = ReadNFA(original)

    result = MakeDFA(original, states, terminals, transitions)

    for i in result:
        print(i)

    WriteToFile(outFile, result)