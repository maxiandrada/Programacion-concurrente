from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math

class Solucion(Grafo):
    def __init__(self, M):
        super(Solucion, self).__init__(M)
    
    def __str__(self):
        ult_vert = self.getV()[-1]
        ult_arista = Arista(ult_vert, self.getV()[0], self._matrizDistancias[0][ult_vert.getValue()-1])
        A = self.getA()
        A.append(ult_arista)
        return "Recorrido de la solución: " + str(self.getV()) + "\n" + "Aristas de la solución: "+ str(A) + " \nCosto Asociado: " + str(self.getCostoAsociado())
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
        self._costoAsociado=costo
    
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

        #Secuencias de indices(entero) para luego asignar una solucion. Empezamos con una facil [0.1,2,3,4,5,...] secuencial
        secuenciaInd = list(range(0,len(self._matrizDistancias)))
        


        if(strSolInicial==0): #Solución al Azar
            random.shuffle(secuenciaInd[1:])
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)

        elif(strSolInicial==1): #Solución Vecino Cercano
            secuenciaInd = self.solInicial_VecinoCercano(nroVehiculos, demanda, capacidad, rutas)
            secuenciaInd = secuenciaInd[1:]
            print("secuencia de vectores: "+str(secuenciaInd))
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
        elif(strSolInicial==2):
            secuenciaInd = list(range(1,len(self._matrizDistancias)))
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
        return rutas

    def cargar_secuencia(self, secuencia, nroVehiculos, demanda, capacidad, rutas):
        #Secuencias de indices(entero) para luego asignar una solucion. Empezamos con una facil [0.1,2,3,4,5,...] secuencial
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,nroVehiculos):
            #Sin contar la vuelta (x,1)
            #[(1,2);(2,3);(3,4)] - [(1,5);(5,6);(6,7)] - [(1,7);(7,8);(8,9);(9,10)]
            #length = 3, nroVehiculos = 3
            #i=0    ini = 0, fin = 0+3 -1 = 2
            #i=1    ini = 3, fin = 3+3 -1 = 5
            #i=2    ini = 6, fin = [-1]
            #i=3    --> no ingresa al for pero ini = 11
            length = self.longitudSoluciones(len(secuenciaInd), nroVehiculos-i)
            fin = length
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd[0:fin], capacidad, demanda)
            print(sub_secuenciaInd)
            S = Solucion(self._matrizDistancias)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
            rutas.append(S)
            secuenciaInd = [x for x in secuenciaInd if x not in set(sub_secuenciaInd)]
        if len(secuenciaInd) > 0:
            print("La solucion inicial no es factible. Implementar luego....")

    def solInicial_VecinoCercano(self, nroVehiculos, demanda, capacidad, rutas):
        #Secuencias de indices(entero) para luego asignar una solucion. Empezamos con una facil [0.1,2,3,4,5,...] secuencial
        recorrido = []
        visitados = []
        
        recorrido.append(0)    #Agrego el vertice inicial
        visitados.append(0)    #Agrego el vertice inicial
        masCercano=0
        for i in range(0,len(self._matrizDistancias)-1):
            masCercano = self.vecinoMasCercano(masCercano, visitados) #obtiene la posicion dela matriz del vecino mas cercano
            recorrido.append(masCercano)
            visitados.append(masCercano)
            i
        return recorrido

    def vecinoMasCercano(self, pos, visitados):
        masCercano = self._matrizDistancias[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(self._matrizDistancias)):
            costo = self._matrizDistancias[pos][i]
            if(costo<masCercano and i not in visitados):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano 

    #secuenciaInd: secuencia de Indices
    #capacidad: capacidad maxima de los vehiculos
    #demanda: demanda de cada cliente
    def solucion_secuencia(self, secuenciaInd, capacidad, demanda):
        tam = 0                 #Tamaño de la solInicial, depende si la suma de las demandas cumple la restriccion de capacidad
        acum_demanda = 0
        sub_secuenciaInd = secuenciaInd
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demanda[value] <= capacidad):
                acum_demanda += demanda[value]
                tam+=1
            else:
                sub_secuenciaInd.pop(x)
        return sub_secuenciaInd
    
    def solInicial_1(self, secuenciaInd, capacidad, demanda):
        v_ini = self.getV()[0]
        v_sig = self.getV()[secuenciaInd[1]]
        peso = self._matrizDistancias[v_ini.getValue()][v_sig.getValue()]
        aristaIni = Arista(v_ini, v_sig, peso)

        recorrido = []      #Va a ser una lista de aristas
        aristasVisitadas = []

        recorrido.append(aristaIni)
        aristasVisitadas.append([v_ini.getValue(),v_sig.getValue()])

        masCercano=0
        for i in range(0,len(secuenciaInd)-1):
            masCercano = self.vecinoMasCercano_cvrp(masCercano, aristasVisitadas, secuenciaInd) #obtiene la posicion en la matriz del vecino mas cercano
            recorrido.append(Vertice(masCercano+1))
            aristasVisitadas.append(masCercano)
            i

        return recorrido

    def vecinoMasCercano_cvrp(self, pos, visitados, secuenciaInd):
        costoMinimo = 999999999
        ind_costoMinimo = 0

        for e in secuenciaInd:
            #vertSig = e.get
            costo = self._matrizDistancias[pos][e]
            if(costo<costoMinimo and e not in visitados):
                costoMinimo = costo
                ind_costoMinimo = e
        
        return ind_costoMinimo
    
    def solucionVecinosCercanos(self):
        inicio = self.getV()[0]
        matrizDist = self.getMatriz()

        recorrido = []
        visitados = []
        
        recorrido.append(inicio)    #Agrego el vertice inicial
        visitados.append(0)     #Agrego el vertice inicial
        masCercano=0
        for i in range(0,len(matrizDist)-1):
            #masCercano = self.vecinoMasCercano(matrizDist,masCercano, visitados) #obtiene la posicion dela matriz del vecino mas cercano
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