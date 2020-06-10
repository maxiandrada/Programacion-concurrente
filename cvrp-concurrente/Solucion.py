from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import random

class Solucion(Grafo):
    def __init__(self, M):
        super(Solucion, self).__init__(M)
        self.__costoAsociado = 0

    def __str__(self):
        return "Recorrido de la solución: " + str(self.getV()) + "\n" + "Aristas de la solución: "+ str(self.getA()) + " \nCosto Asociado: " + str(self.__costoAsociado)
    def __repr__(self):
        return str(self.getV())
    def __eq__(self, otro):
        return (self.__costoAsociado == otro.__costoAsociado and self.__class__ == otro.__class__)
    def __ne__(self, otro):
        return (self.__costoAsociado != otro.__costoAsociado and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return self.__costoAsociado > otro.__costoAsociado
    def __lt__(self, otro):
        return self.__costoAsociado < otro.__costoAsociado
    def __ge__(self, otro):
        return self.__costoAsociado >= otro.__costoAsociado
    def __le__(self, otro):
        return self.__costoAsociado <= otro.__costoAsociado
    def __len__(self):
        return len(self._V)
    def setCosto(self, costo):
        self.__costoAsociado=costo
    
    def solInicial(self, secuenciaInd, capacidad):
        

    def vecinoMasCercano(self, matrizDist: list, pos: int, visitados: list):
        masCercano = matrizDist[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(matrizDist)):
            costo = matrizDist[pos][i]
            if(costo<masCercano and i not in visitados):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano 
    
    def solucionVecinosCercanos(self):
        inicio = self.getV()[0]
        matrizDist = self.getMatriz()

        recorrido = []
        visitados = []
        
        recorrido.append(inicio)    #Agrego el vertice inicial
        visitados.append(0)     #Agrego el vertice inicial
        masCercano=0
        for i in range(0,len(matrizDist)-1):
            masCercano = self.vecinoMasCercano(matrizDist,masCercano, visitados) #obtiene la posicion dela matriz del vecino mas cercano
            recorrido.append(Vertice(masCercano+1))
            visitados.append(masCercano)
            i

        return recorrido

    def solucionAlAzar(self):
        inicio = self.getVerticeInicio()
        indices_azar = random.sample( range(2,len(self.getV())+1), len(self.getV())-1)
        
        alAzar = []
        alAzar.append(inicio)
        for i in indices_azar:
            alAzar.append(Vertice(i))

        return alAzar