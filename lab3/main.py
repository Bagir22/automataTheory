import re
import sys
import csv

leftRegrex = r'^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$'
rightRegex = r'^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$'
findNonTerminal = r'<(.*?)>'
findTerminal = r'\b(?!<)(\w+)(?!>)\b'

def WriteToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)

def GetType(inFile):
    with open(inFile, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if re.match(leftRegrex, line):
                return 'left'
            elif re.match(rightRegex, line):
                return 'right'

    return None


def GetRules(inFile):
    rules = {}
    lastRule = ""

    with open(inFile, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split("->")
            if len(parts) != 2 and lastRule != "":
                rightSide = parts[0].strip()
                productions = [prod.strip() for prod in rightSide.split("|")]
                productions = [prod for prod in productions if prod]
                rules[lastRule].extend(productions)
                continue

            leftSide = parts[0].strip()
            lastRule = leftSide
            rightSide = parts[1].strip()

            productions = [prod.strip() for prod in rightSide.split("|")]
            productions = [prod for prod in productions if prod]

            if not productions:
                continue

            if leftSide in rules:
                rules[leftSide].extend(productions)
            else:
                rules[leftSide] = productions

    return rules

def GetTerminals(rules):
    terminals = []

    for v in rules.values():
        for val in v:
            val = val.split()
            for i in val:
                if '<' not in i and '>' not in i and i not in terminals:
                    terminals.append(i)

    return terminals

def FillStateMapping(rules, type):
    rulesStatesMap = dict()

    if type == 'left':
        rulesStatesMap["H"] = "q0"
        state_counter = 1

        for left, right in reversed(rules.items()):
            left_state = f"q{state_counter}"
            rulesStatesMap[left] = left_state
            state_counter += 1

    elif type == 'right':
        state_counter = 0
        for left, right in rules.items():
            left_state = f"q{state_counter}"
            rulesStatesMap[left] = left_state
            state_counter += 1
        rulesStatesMap["F"] = f"q{len(rules)}"

    return rulesStatesMap

def ToStates(rules, statesMap, type):
    terminals = sorted(GetTerminals(rules))

    result = [["" for _ in range(len(rules) + 2)] for _ in range(len(terminals) + 2)]

    for i in range(2, len(result)):
        result[i][0] = terminals[i-2]

    result[0][len(result[0])-1] = "F"
    for i in range(1, len(result[1])):
        result[1][i] = list(statesMap.values())[i-1]


    for rule in rules.items():
        currState = statesMap[rule[0]]
        for i in range(1, len(rule)):
            if type == "left":
                for val in rule[i]:
                    if '<' in val and '>' in val:
                        ruleIdx = result[1].index(statesMap[f'<{re.search(findNonTerminal, val).group(1)}>'])
                        columnIdx = terminals.index(re.search(findTerminal, val).group(1))
                        if result[columnIdx+2][ruleIdx] == "":
                            result[columnIdx + 2][ruleIdx] = currState
                        else:
                            result[columnIdx + 2][ruleIdx] += f',{currState}'
                    else:
                        lineIdx = terminals.index(val)
                        if result[lineIdx+2][1] == "":
                            result[lineIdx + 2][1] = currState
                        else:
                            result[lineIdx + 2][1] += f',{currState}'
            elif type == "right":
                for val in rule[i]:
                    currRule = result[1].index(currState)
                    currLine = terminals.index(re.search(findTerminal, val).group(1))
                    nonTerminal = re.search(findNonTerminal, val)
                    if nonTerminal != None:
                        nonTerminal= statesMap[f'<{nonTerminal.group(1)}>']
                        if '<' in val and '>' in val:
                            if result[currLine+2][currRule] == "":
                                result[currLine+2][currRule] = nonTerminal
                            else:
                                result[currLine+2][currRule] += f',{nonTerminal}'
                    else:
                        if result[currLine+2][currRule] == "":
                            result[currLine+2][currRule] = statesMap["F"]
                        else:
                            result[currLine+2][currRule] += f',{statesMap["F"]}'

    return result

def GrammarToNKA(inFile, outFile):
    type = GetType(inFile)
    if not type:
        return

    rules = GetRules(inFile)
    statesMap = FillStateMapping(rules, type)
    states = ToStates(rules, statesMap, type)
    WriteToFile(outFile, states)

if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]
    GrammarToNKA(inFile, outFile)
