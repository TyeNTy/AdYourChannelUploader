class Entity:
    def __init__(self, id : str):
        self.id = id
    
    def getProperties(self) -> dict:
        return vars(self)