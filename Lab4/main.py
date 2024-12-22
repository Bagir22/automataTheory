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


def GeteTransitions(transitions):
    eTransitions = {}

    for k, v in transitions.items():
        eTransitions[k] = [k]
        if v.get('ε'):
            eTransitions[k].extend(v['ε'])

    return eTransitions

def MakeDFA(original, states, terminals, transitions):
    count = 0
    dfaTransitions = defaultdict(dict)
    dfaTerminals = [t for t in terminals if t != 'ε']
    dfaStates = {f"S{count}": [states[0]]}
    queue = deque([(f"S{count}")])
    count += 1

    eTransitions = GeteTransitions(transitions)
    print("E transitions", eTransitions)

    while queue:
        current = queue.popleft()
        currentStates = dfaStates[current]

        currentTransitions = []
        for states in [currentStates]:
            for state in states:
                currentTransitions.extend(eTransitions[state])

        for terminal in dfaTerminals:
            nextStates = set()

            for state in currentTransitions:
                if terminal in transitions[state]:
                    nextStates.update(transitions[state][terminal])

            if nextStates:
                eclosureStates = set()
                for nextState in nextStates:
                    eclosureStates.update(eTransitions[nextState])

                existingState = None
                for dfaState, dfaStateTransitions in dfaStates.items():
                    if set(dfaStateTransitions) == eclosureStates:
                        existingState = dfaState
                        break

                if existingState is None:
                    newState = f"S{count}"
                    dfaStates[newState] = list(eclosureStates)
                    queue.append(newState)
                    count += 1
                    dfaTransitions[current][terminal] = newState
                else:
                    dfaTransitions[current][terminal] = existingState

        print("Current ", current, currentStates, currentTransitions)


    result = [['' for _ in range(len(dfaTransitions) + 1)] for _ in range(len(dfaTerminals) + 2)]

    print()
    print(dfaStates.items())
    print(dfaTerminals)
    print(dfaTransitions)

    for i in range(len(dfaTerminals)):
        result[i + 2][0] = dfaTerminals[i]

    for i, v in enumerate(dfaTransitions.items()):
        result[1][i + 1] = v[0]
        for next in v[1].items():
            for j in range(2, len(result)):
                if result[j][0] == next[0]:
                    result[j][i + 1] = next[1]

    for idx in range(1, len(result[1])):
        state = result[1][idx]
        for next in dfaTransitions[state].values():
            nextStatesInOriginal = dfaStates[next]
            for nextState in nextStatesInOriginal:
                if original[0][original[1].index(nextState)] == 'F':
                    result[0][idx] = 'F'

    return result


if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    original = GetOriginalMealy(inFile)
    states, terminals, transitions = ReadNFA(original)
    print("States\n", states)
    print("Terminals\n",terminals)
    print("Transitions\n", transitions, "\n")
    result = MakeDFA(original, states, terminals, transitions)

    for i in result:
        print(i)

    WriteToFile(outFile, result)