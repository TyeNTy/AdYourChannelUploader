import os

def splitPropNameAndPropValue(prop: str, separator : str) -> tuple[str, str]:
    splittedLine = prop.split(separator)
    return splittedLine[0], '='.join(splittedLine[1::])

def loadTranslations(language : str, pathFile : str, basePath : str = "resources") -> dict[str, str]:
    fullPath = os.path.join(basePath, pathFile, language)
    with open(fullPath, "r", encoding="utf-8") as f:
        allLines = f.readlines()
    translations = {}
    for line in allLines:
        lineTrimmed = line.replace("\n", "")
        if(lineTrimmed != "" and lineTrimmed[0] != "#"):
            translationName, translationValue = splitPropNameAndPropValue(lineTrimmed, "=")
            translations[translationName] = translationValue
    return translations