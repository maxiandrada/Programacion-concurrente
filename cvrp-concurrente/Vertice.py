class Vertice():

    def __init__(self,V):
        self._value = V

    def getValue(self):
        return self._value
    
    def setValue(self, V):
        self._value = V

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return str(self)

    def __eq__(self,otro):
        return (self.__class__ == otro.__class__ and str(self.getValue()) == str(otro.getValue()))
    
