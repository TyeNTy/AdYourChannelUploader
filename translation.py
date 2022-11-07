import os

class Translation(dict):
    def __init__(self, language : str, pathFile : str, basePath = "resources") -> None:
        self.language = language
        self.pathFile = pathFile
        self.basePath = basePath
        self.dictTranslations : dict[str, str] = None
        self.loadTranslations(language, pathFile, basePath)
        
    def __splitPropNameAndPropValue(self, prop: str, separator : str) -> tuple[str, str]:
        splittedLine = prop.split(separator)
        return splittedLine[0], '='.join(splittedLine[1::])

    def loadTranslations(self, language : str, pathFile : str, basePath : str = "resources") -> dict[str, str]:
        self.language = language
        self.pathFile = pathFile
        self.basePath = basePath
        fullPath = os.path.join(self.basePath, self.pathFile, self.language)
        if(os.path.exists(fullPath)):
            with open(fullPath, "r", encoding="utf-8") as f:
                allLines = f.readlines()
            self.dictTranslations = {}
            for line in allLines:
                lineTrimmed = line.replace("\n", "")
                if(lineTrimmed != "" and lineTrimmed[0] != "#"):
                    translationName, translationValue = self.__splitPropNameAndPropValue(lineTrimmed, "=")
                    self.dictTranslations[translationName] = translationValue
    
    def __getitem__(self, __key: str) -> str:
        if(self.dictTranslations is None):
            return __key
        else:
            if(__key in self.dictTranslations):
                return self.dictTranslations[__key]
            else:
                return __key