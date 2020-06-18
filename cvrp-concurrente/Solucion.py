from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math

class Solucion(Grafo):
    def __init__(self, M, sumDemanda):
        super(Solucion, self).__init__(M)
        self.__capacidad = 0
        self.__demandaTotal = sumDemanda

    def __str__(self):
        ult_vert = self.getV()[-1]
        ult_arista = Arista(ult_vert, self.getV()[0], self._matrizDistancias[0][ult_vert.getValue()-1])
        A = self.getA()+[ult_arista]
        cad = "\nRecorrido de la solución: " + str(self.getV()) + "\n" + "Aristas de la solución: "+ str(A)
        cad += "\nCosto Asociado: " + str(round(self.getCostoAsociado(),3)) + "        Capacidad: "+ str(self.__capacidad)
        return cad
    def __repr__(self):
        return str(self.getV())
    def __eq__(self, otro):
        return (self._costoAsociado == otro._costoAsociado and self.__class__ == otro.__class__)
    def __ne__(self, otro):
        return (self._costoAsociado != otro._costoAsociado and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return self._costoAsociado > otro._costoAsociado
    def __lt__(self, otro):
        return self._costoAsociado < otro._costoAsociado
    def __ge__(self, otro):
        return self._costoAsociado >= otro._costoAsociado
    def __le__(self, otro):
        return self._costoAsociado <= otro._costoAsociado
    def __len__(self):
        return len(self._V)
    def setCosto(self, costo):
        self._costoAsociado = costo
    def setDemandaTotal(self, demanda):
        self.__demandaTotal = demanda
    def setCapacidad(self, capacidad):
        self.__capacidad = capacidad
    def getCapacidad(self):
        return self.__capacidad

    def getCopyVacio(self):
        ret = Solucion(Grafo([]), 0)
        ret.setMatriz(self.getMatriz())
        return ret

    #Longitud que debería tener cada solucion por cada vehiculo
    def longitudSoluciones(self, length, nroVehiculos):
        if(nroVehiculos == 0):
            return length
        length = (length/nroVehiculos)
        decimales = math.modf(length)[0]
        if decimales < 5.0:
            length = int(length)
        else:
            length = int(length)+1
        return length

    #Rutas iniciales o la primera solucion
    def rutasIniciales(self, strSolInicial, nroVehiculos, demanda, capacidad):
        rutas = []

        if(strSolInicial==0):
            secuenciaInd = random.sample(range(1,len(self.getV())) , len(self.getV())-1)
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
            print("secuencia de indices de los vectores (random): "+str(secuenciaInd))
        elif(strSolInicial==1):
            self.solInicial_VecinoCercano(nroVehiculos, capacidad, demanda, rutas)
        else:
            secuenciaInd = list(range(1,len(self._matrizDistancias)))
            print("secuencia de indices de los vectores (secuencial): "+str(secuenciaInd))
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
        
        return rutas

    #
    def cargar_secuencia(self, secuencia, nroVehiculos, demanda, capacidad, rutas):
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,nroVehiculos):
            #Sin contar la vuelta (x,1)
            #nroVehiculos = 3
            #[1,2,3,4,5,6,7,8,9,10] Lo ideal seria: [1,2,3,4] - [1,5,6,7] - [1,8,9,10]
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd, capacidad, demanda, nroVehiculos)
            S = Solucion(self._matrizDistancias, self.__demandaTotal)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
            rutas.append(S)
            secuenciaInd = [x for x in secuenciaInd if x not in set(sub_secuenciaInd)]
            i
        if len(secuenciaInd) > 0:
            print("La solucion inicial no es factible. Implementar luego....")

    #secuenciaInd: secuencia de Indices
    #capacidad: capacidad maxima de los vehiculos
    #demanda: demanda de cada cliente
    def solucion_secuencia(self, secuenciaInd, capacidad, demanda, nroVehiculos):
        acum_demanda = 0
        sub_secuenciaInd = []
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demanda[value] <= capacidad):
                acum_demanda += demanda[value]
                sub_secuenciaInd.append(x)
                if (acum_demanda > self.__demandaTotal/nroVehiculos):
                    break
        
        return sub_secuenciaInd

    def solInicial_VecinoCercano(self, nroVehiculos, capacidad, demanda, rutas):
        visitados = []
        recorrido = []
        visitados.append(0)    #Agrego el vertice inicial
        
        for j in range(0, nroVehiculos):
            recorrido = []
            masCercano=0
            acum_demanda = 0
            for i in range(0,len(self._matrizDistancias)-len(visitados)):
                masCercano = self.vecinoMasCercano(masCercano, visitados, acum_demanda, demanda, capacidad) #obtiene la posicion dela matriz del vecino mas cercano
                if(masCercano != 0):
                    acum_demanda += demanda[masCercano]
                    recorrido.append(masCercano)
                    visitados.append(masCercano)
                if(acum_demanda > self.__demandaTotal/nroVehiculos):
                    break
                i
            j
            S = Solucion(self._matrizDistancias, self.__demandaTotal)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido))
            S.setCapacidad(acum_demanda)
            rutas.append(S)
        
        return recorrido

    def vecinoMasCercano(self, pos, visitados, acum_demanda, demanda, capacidad):
        masCercano = self._matrizDistancias[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(self._matrizDistancias)):
            costo = self._matrizDistancias[pos][i]
            if(costo<masCercano and i not in visitados and demanda[i]+acum_demanda <= capacidad):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano

    #[(1,2);(2,3);(3,4);(1,9);(9,5);(5,6);(1,7);(7,8);(8,10)]
    #2-opt:
    #DROP = (2,3); ADD = (2,5) --> [(1,2);(2,5);(5,4);(1,9);(9,3);(3,6);(1,7);(7,8);(8,10)]
    #[(1,2);(2,5);(5,4);(1,3);(3,9);(9,6);(1,7);(7,8);(8,10)]
    def swap(self, a1, a2):
        A = []
        V = self.getV()[0]
        for a in self._A:
            print("a: "+str(a))
            a1_Destino = a1.getDestino()
            a2_Destino = a2.getDestino()
            if(a.getOrigen == a1_Destino):
                a.setOrigen(a1_Destino)
            elif(a.getOrigen == a2_Destino):
                a.setOrigen(a2_Destino)
            
            if (a.getDestino() == a1_Destino):
                a.setDestino(a1_Destino)
            elif(a.getDestino() == a2_Destino):
                a.setDestino(a2_Destino)
            print(str(a))
            A.append(a)
            V.append(a.getDestino())
        
        S = Solucion([], self.__demandaTotal)
        S.setA(A)
        S.setV(V)
        S.setMatriz(self._matrizDistancias)

        return S
    
    def swapp(self, v1, v2):
        copiaV = copy.deepcopy(self._V)

        copiaV[self._V.index(v1)]=v2
        copiaV[self._V.index(v2)]=v1

        gNuevo = Grafo([])
        gNuevo.setMatriz(self.getMatriz())
        gNuevo.cargarDesdeSecuenciaDeVertices(copiaV)
        return gNuevo

