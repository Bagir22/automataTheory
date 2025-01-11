import re
import sys

singleComment = "//"
multiCommentStart = "/*"
multiCommentEnd = "*/"

multilineCommentMode = False

operators = {
    "==": "Relational operation",
    "!=": "Relational operation",
    "<=": "Relational operation",
    ">=": "Relational operation",
    "<": "Relational operation",
    ">": "Relational operation",
    "+": "Arithmetic operator",
    "-": "Arithmetic operator",
    "/": "Arithmetic operator",
    "*": "Arithmetic operator",
    "=": "Assignment operator",
}

separators = {
    "(": "Parenthesis separator",
    ")": "Parenthesis separator",
    "[": "Square bracket",
    "]": "Square bracket",
    ":": "Colon separator",
    ",": "Comma separator",
    ";": "Semicolon separator",
}

keywords = {
    "and": "Keyword",
    "as": "Keyword",
    "break": "Keyword",
    "class": "Keyword",
    "continue": "Keyword",
    "def": "Keyword",
    "elif": "Keyword",
    "else": "Keyword",
    "finally": "Keyword",
    "for": "Keyword",
    "from": "Keyword",
    "if": "Keyword",
    "import": "Keyword",
    "in": "Keyword",
    "not": "Keyword",
    "or": "Keyword",
    "return": "Keyword",
    "try": "Keyword",
    "while": "Keyword",
    "with": "Keyword",
    "bool": "Keyword",
    "int": "Keyword",
    "True": "Keyword",
    "False": "Keyword",
    "double": "Keyword",
}

nums = {
    r'\b\d+[eE][-+]?\d+\b': "Exponential number",
    r'\b\d+\.\d+\b': "Float number",
    r'\b\d+\b': "Integer number",
    r'\b0b[01]+\b': "Binary number",
    r'\b0x[0-9a-fA-F]+\b': "Hexadecimal number"
}

def isString(item):
    return (len(item) > 1 and
            (item.startswith("\"") and item.endswith("\"") and item.count("\"") % 2 == 0) or
             (item.startswith("\'") and item.endswith("\'") and item.count("\'") % 2 == 0))
def makeToken(item, lineIdx, position, outFile):
    global multilineCommentMode

    if not item:
        return

    if multilineCommentMode:  # Если включен режим многострочного комментария
        commentIdx = item.find(multiCommentEnd)
        if commentIdx != -1:  # Найден конец
            multilineCommentMode = False
            outFile.write(f"Multiline Comment Close: {item[:commentIdx + 2]} line:{lineIdx} position:{position + commentIdx}\n")
            makeToken(item[commentIdx + 2:], lineIdx, position + commentIdx + 2, outFile)
            return
        else:  # продолжается
            outFile.write(f"{item} line:{lineIdx} position:{position}\n")
            return
    else:
        commentIdx = item.find(multiCommentStart)
        if commentIdx != -1:  # Найдено начало
            makeToken(item[:commentIdx], lineIdx, position, outFile)
            multilineCommentMode = True
            endCommentIdx = item.find(multiCommentEnd, commentIdx + 2)
            if endCommentIdx != -1:  # Найден конец в той же строчке
                multilineCommentMode = False
                outFile.write(f"Multiline Comment Start And Close: {item[commentIdx:endCommentIdx + 2]} line:{lineIdx} position:{position + endCommentIdx}\n")
                makeToken(item[endCommentIdx + 2:], lineIdx, position + endCommentIdx + 2, outFile)
                return
            else: # Не найден конец в той же строчке
                outFile.write(f"Multiline Comment Start: {item[commentIdx:]} line:{lineIdx} position:{position + commentIdx}\n")
            return

    commentIdx = item.find(singleComment)
    if commentIdx != -1:
        prev = item[:commentIdx]
        makeToken(prev, lineIdx, position, outFile)
        outFile.write(f"Single Comment: {item[commentIdx:]} line:{lineIdx} position:{commentIdx+1}\n")
        return

    for key, value in nums.items():
        match = re.search(key, item)
        if match:
            outFile.write(f"{value}: {item} line:{lineIdx} position:{position}\n")
            return

    for k, v in operators.items():
        idx = item.find(k)
        if idx != -1:
            prev = item[:idx]
            next = item[idx++len(k):]
            makeToken(prev, lineIdx, position, outFile)
            outFile.write(f"{v}: {k} line:{lineIdx} position:{position + len(prev)}\n")
            makeToken(next, lineIdx, position + len(k), outFile)
            return

    for k, v in separators.items():
        idx = item.find(k)
        if idx != -1:
            prev = item[:idx]
            next = item[idx++len(k):]
            makeToken(prev, lineIdx, position, outFile)
            outFile.write(f"{v}: {k} line:{lineIdx} position:{position + len(prev)}\n")
            makeToken(next, lineIdx, position + len(k), outFile)
            return

    for k, v in keywords.items():
        pattern = r'\b' + re.escape(k) + r'\b'
        match = re.search(pattern, item)
        if match:
            idx = match.start()
            prev = item[:idx]
            next = item[idx + len(k):]
            makeToken(prev, lineIdx, position, outFile)
            outFile.write(f"{v}: {k} line:{lineIdx} position:{position + len(prev)}\n")
            makeToken(next, lineIdx, position + len(prev) + len(k), outFile)
            return

    curr = ""
    validIdentificator = item[0].isalpha() or item[0] == "_"

    for i, ch in enumerate(item):
        if validIdentificator:
            if ch.isalnum() or ch == '_':
                curr += ch
            else:
                validIdentificator = False
        else:
            break


    if validIdentificator:
        outFile.write(f"Identificator: {curr} line:{lineIdx} position:{position}\n")
    elif isString(item):
        outFile.write(f"String: {item} line:{lineIdx} position:{position}\n")
    else:
        outFile.write(f"Error: {item} line:{lineIdx} position:{position}\n")

    return

def processLine(line, lineIdx, outFile):
    position = 1
    for item in line.split():
        makeToken(item, lineIdx, position, outFile)
        position += len(item) + 1

    return
def lexer(inputFile, outputFile):
    global multilineCommentMode

    inFile = open(inputFile, "r")
    outFile = open(outputFile, "w")

    lineIdx = 1
    for line in inFile:
        processLine(line.strip(), lineIdx, outFile)
        lineIdx += 1

    if multilineCommentMode:
        outFile.write(f"Error closing multiline comment\n")

    return

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid arguments len")
        sys.exit()

    inputFile = sys.argv[1]
    outputFile = sys.argv[2]

    lexer(inputFile, outputFile)