from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math
from Ingreso import Ingreso
import os
from Grafico import Grafico


class Ruta(Grafo):
    def __init__(self, M,seq=None):
        super(Ruta, self).__init__(M)
        if(not seq is None):
            self.cargarDesdeSecuenciaDeVertices(seq)
            self.setCosto()
    
    
    def __str__(self):
        A=self.getA()
        return "Recorrido de la ruta: " + str(self.getV()) + "\n" + "Aristas de la ruta: "+ str(A) + " \nCosto Asociado: " + str(round(self.getCostoAsociado(),3))
   
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

    def getCosto(self):
        return self._costoAsociado

   
    def getCopyVacio(self):
        ret = Ruta(Grafo([]))
        ret.setMatriz(self.getMatriz())
        return ret


    def addCliente(self,C):
        self._V.append(C)




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
        
        S = Ruta([])
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




class Solucion():
    def __init__(self,S=None,D=None,NV=None,C=None,I=None):
        if(isinstance(S,Solucion)):
            self.__matriz = S.getMatriz()
            self.__grado = len(self.__matriz)
            self.__V = copy.deepcopy(S.getV())
            self.__A = copy.deepcopy(S.getA())
            self.__demanda = S.getDemanda()
            self.__capacidad = S.getCapacidad()
            self.__nroVehiculos = S.getNroVehiculos()
            self.__rutas = copy.deepcopy(S.getRutas())
            self.__costoTotal = S.getCostoTotal()

        elif(isinstance(S,Grafo)):
            if(not D is None and not NV is None and not C is None):
                self.__matriz = S.getMatriz()
                self.__grado = len(self.__matriz)
                self.__costoTotal = S.getCostoAsociado()
                self.__V = copy.deepcopy(S.getV())
                self.__A = copy.deepcopy(S.getA())
                self.__capacidad = C
                self.__demanda = D
                self.__nroVehiculos = NV
            else:
                print("Faltan argumentos")
        else:
            print("Solución Vacía")
               
    
        if(not S is None and not I is None):
            self.__rutas = []
            self.__costoTotal = 0
            self.rutasIniciales(I,self.__nroVehiculos,self.__demanda,self.__capacidad)
            #self.rutaDePrueba()
            self.crearDictBusqueda()
            self.mostrarDictBusqueda()
            self.setCostoTotal()



    def crearDictBusqueda(self):
        self.__dict = {}
        #print(self.__rutas[1])
        for r in range(0,len(self.__rutas)):
            #print("r: ",r)
            V = self.__rutas[r].getV()
            for i in range(len(V)):
                self.__dict.update({V[i].getValue():[r,i]}) #[r,v] lista con el indice de la ruta y del vértice
            
    def mostrarDictBusqueda(self):
        print(self.__dict)

    #Actualiza todos los vértices de la ruta
    def actualizarDictBusqueda(self,r1):
        V = self.__rutas[r1].getV()
        for i in range(len(V)):
            self.__dict.update({V[i].getValue():[r1,i]})


    def buscar(self, v):
        if(isinstance(v,int)):
            return self.__dict.get(v)     
        elif(isinstance(v,Vertice)):
            return self.__dict.get(v)

    def getRutas(self):
        return self.__rutas
    
    def setRutas(self,R):
        self.__rutas = R

    def addRuta(self,R):
        self.__rutas.append(R)
        self.setCostoTotal()
    def __getitem__(self,key):
        return self.__rutas[key]

    def getMatriz(self):
        return self.__matriz

    def getGrado(self):
        return self.__grado

    def setA(self, A):
        self.__A = A
    def setV(self, V):
        self.__V = V
    def getA(self):
        return self.__A
    def getV(self):
        return self.__V

    def getDemanda(self):
        return self.__demanda
    
    def setDemanda(self,D):
        self.__demanda = D

    def getCapacidad(self):
        return self.__capacidad

    def setCapacidad(self,C):
        self.__capacidad = C

    def getNroVehiculos(self):
        return self.__nroVehiculos

    def setNroVehiculos(self,NV):
        self.__nroVehiculos = NV

    def rutaDePrueba(self):
        seq1 = []
        seq2 = [Vertice(1)]
        for i in range(1,self.__grado+1):
            if(i < self.__grado/2):
                seq1.append(Vertice(i))
            else:
                seq2.append(Vertice(i))

        self.__rutas.append(Ruta(self.getMatriz(),seq1))
        self.__rutas.append(Ruta(self.getMatriz(),seq2))
            
    def __str__(self):
        ret = ""
        for i in range(0, len(self.__rutas)):
            ret += "\nRuta del vehiculo "+str(i+1)+":\n"+str(self.__rutas[i]) + "\n"
        ret += "\nCosto total: "+str(self.getCostoTotal())
        return ret

    def setCostoTotal(self,costo=None):
        if(not costo  is None):
            self.__costoTotal = costo
        else:
            ret = 0
            for r in self.__rutas:
                ret += r.getCosto()
            self.__costoTotal = ret


    def getCostoTotal(self):
        return self.__costoTotal

    #Longitud que debería tener cada solucion por cada vehiculo
    def longitudRutas(self, length, nroVehiculos):
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
            secuenciaInd = random.sample( range(1,len(self.getV())), len(self.getV())-1)
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
            self.__rutas = rutas
        elif(strSolInicial==1):
            # secuenciaInd = self.solInicial_VecinoCercano(nroVehiculos, capacidad,demanda,rutas)
            # print("secuencia de indices de los vectores: "+str(secuenciaInd))
            # secuenciaInd = secuenciaInd[1:]
            # self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
            self.algoritmoConstructivo(nroVehiculos,demanda,capacidad)
        elif(strSolInicial==2):
            secuenciaInd = list(range(1,len(self.__matriz)))
            print("secuencia de indices de los vectores: "+str(secuenciaInd))
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
            self.__rutas = rutas

    #

    def penalizarSolucion(self,alfa):
        capacMax = self.__capacidad
        print("capac:"+ str(capacMax))
        dem = self.__demanda
        costoActual = self.__costoTotal
        print(dem)
        sumaDemRutas = []
        for Rr in self.getRutas():
            suma = 0
            for v in Rr.getV():
                print("-----> ",dem[v.getValue()-1])
                suma += dem[v.getValue()-1]
            print(suma)
            suma = suma - capacMax
            print(suma)
            sumaDemRutas.append(suma)
        maxSum = max(sumaDemRutas)
        print(sumaDemRutas)
        self.setCostoTotal(costoActual + alfa*maxSum) 

    def cargar_secuencia(self, secuencia, nroVehiculos, demanda, capacidad, rutas):
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,nroVehiculos):
            #Sin contar la vuelta (x,1)
            #nroVehiculos = 3
            #[1,2,3,4,5,6,7,8,9,10] - [1,2,3,4] - [1,5,6,7] - [1,8,9,10]
            length = self.longitudRutas(len(secuenciaInd), nroVehiculos-i)
            fin = length
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd[0:fin], capacidad, demanda)
            S = Ruta(self.__matriz)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
            S.setCosto()
            rutas.append(S)
            secuenciaInd = [x for x in secuenciaInd if x not in set(sub_secuenciaInd)]
        if len(secuenciaInd) > 0:
            print("La solucion inicial no es factible. Implementar luego....")

    def solInicial_VecinoCercano(self, nroVehiculos, capacidad, demanda, rutas):
        visitados = []
        recorrido = []
        visitados.append(0)    #Agrego el vertice inicial
        
        for j in range(0, nroVehiculos):
            recorrido = []
            masCercano=0
            acum_demanda = 0
            for i in range(0,len(self.__matriz)-len(visitados)):
                masCercano = self.vecinoMasCercano(masCercano, visitados, acum_demanda, demanda, capacidad) #obtiene la posicion dela matriz del vecino mas cercano
                if(masCercano != 0):
                    acum_demanda += demanda[masCercano]
                    recorrido.append(masCercano)
                    visitados.append(masCercano)
                if(acum_demanda > self.__capacidad/nroVehiculos):
                    break
                i
            j
            S = Ruta(self.__matriz)
            print(recorrido)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido))
            self.__rutas.append(S)
        
        return recorrido




    def vecinoMasCercano(self, pos, visitados, acum_demanda, demanda, capacidad):
        masCercano = self.__matriz[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(self.__matriz)):
            costo = self.__matriz[pos][i]
            if(costo<masCercano and i not in visitados and demanda[i]+acum_demanda <= capacidad):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano

        

    #secuenciaInd: secuencia de Indices
    #capacidad: capacidad maxima de los vehiculos
    #demanda: demanda de cada cliente
    def solucion_secuencia(self, secuenciaInd, capacidad, demanda):
        tam = 0                 #Tamaño de la solInicial, depende si la suma de las demandas cumple la restriccion de capacidad
        acum_demanda = 0
        sub_secuenciaInd = []
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demanda[value] <= capacidad):
                acum_demanda += demanda[value]
                sub_secuenciaInd.append(x)
                tam+=1
        
        return sub_secuenciaInd
        

    #def pVecindario(self):

    def algoritmoConstructivo(self, nroVehiculos, demanda, capacidad):
        RutaRef = Ruta(self.getMatriz())
        self.addRuta(RutaRef)
        visitados = [Vertice(1)]
        for i in range(1,nroVehiculos+1):
            origen = 1
            R = [Vertice(1)] 
            cAcum = 0
            superoMaximo = False
            k=0
            while(cAcum<capacidad and not superoMaximo):
                j = 0            
                destinos = list(self[0][origen][None]) 
                min = destinos[origen-1].getPeso() 
                jMin =0  
                while(j<len(destinos)):
                    if(destinos[j].getDestino() not in visitados):
                        if(destinos[j].getPeso()<min):
                            if(cAcum+demanda[destinos[j].getDestino().getValue()-1] < capacidad):
                                min = destinos[j].getPeso()
                                origen = destinos[j].getDestino().getValue()
                                jMin=j
                    j+=1
                k+=1
                if(k==len(destinos)):
                    superoMaximo = True
                if(jMin!=0):
                    R += [destinos[jMin].getDestino()]
                    visitados.append(destinos[jMin].getDestino())
                    cAcum += demanda[jMin]
                #print(origen)

            ruta = Ruta(self.__matriz,R)
            #print("R: "+str(R))
            #print("Ruta: "+str(ruta))
            self.addRuta(ruta)
        self.__rutas.pop(0)





    def twoExchange(self,v1,v2):
        indV1 = self.buscar(v1) #[r1,v1] indice de la ruta y del vértice
        indV2 = self.buscar(v2)
        R = self.__rutas
        
        #Para el caso de que los vértices estén en la misma rutas
        if(indV1[1]+1 == len(R[indV1[0]]) and  indV2[1]+1 == len(R[indV2[0]])):  
            aux = self[indV1[0]].getV()[indV1[1]]
            self[indV1[0]].getV()[indV1[1]] = self[indV2[0]].getV()[indV2[1]]
            self[indV2[0]].getV()[indV2[1]] = aux
            self[0].cargarDesdeSecuenciaDeVertices(self[0].getV())
            self[1].cargarDesdeSecuenciaDeVertices(self[1].getV())            
        else:
            inferiorR1 = self[indV1[0]].getV()[:indV1[1]+1]
            superiorR1 = self[indV1[0]].getV()[indV1[1]+1:]
            inferiorR2 = self[indV2[0]].getV()[:indV2[1]]
            superiorR2 = self[indV2[0]].getV()[indV2[1]:]
            if(superiorR1==[]):
                print("No se puede este caso por ahora ¬¬")
            else:
                r1 = inferiorR1 + superiorR2
                r2 = inferiorR2 + superiorR1
                self[0].cargarDesdeSecuenciaDeVertices(r1)
                self[1].cargarDesdeSecuenciaDeVertices(r2)
        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self[0].setCosto()
        self[1].setCosto()
        self.setCostoTotal()

    def customerInsertion(self,v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2
        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]        

        a = self[r1].getA()[c1]  
        anteriorA = self[r1].getA()[c1-1]
        b = self[r2].getA()[c2]
        anteriorB = self[r2].getA()[c2-1]

        anteriorA.setDestino(a.getDestino())
        anteriorA.setPeso(self[r1][anteriorA.getOrigen()][a.getDestino()])
        a.setDestino(b.getOrigen())
        anteriorB.setDestino(a.getOrigen())

        a.setPeso(self[r1][a.getOrigen()][b.getOrigen()])
        anteriorB.setPeso(self[r1][anteriorB.getOrigen()][a.getOrigen()])
        
        self[r2].getA().insert(c2,a)
        self[r1].getA().remove(a)

        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()

    #PENDIENTE ACTUALIZAR PESOS
    def exchange(self,v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2
        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]

        a = self[r1].getA()[c1]  
        b = self[r2].getA()[c2]
        anteriorB = self[r2].getA()[c2-1]
        siguienteB = self[r2].getA()[c2+1]

        anteriorB.setDestino(siguienteB.getDestino())
        siguienteB.setDestino(a.getDestino())
        a.setDestino(b.getOrigen())

        self[r1].getA().insert(c1+1,b)
        self[r1].getA().insert(c1+2,siguienteB)
        self[r2].getA().remove(b)
        self[r2].getA().remove(siguienteB)



        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()


    #PENDIENTEEEEE
    def customerSwap(self, v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2

        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]

        a = self[r1].getA()[c1]  
        b = self[r2].getA()[c2]
        siguienteA = self[r1].getA()[c1+1]
        siguienteB = self[r2].getA()[c2+1]
        anteriorB = self[r2].getA()[c2-1]

        anteriorB.setDestino(a.getDestino())
        b.setDestino(siguienteA.getDestino())
        a.setDestino(b.getOrigen())
        siguienteA.setDestino(siguienteB.getOrigen())

        self[r1].getA().remove(siguienteA)
        self[r2].getA().remove(b)

        a.setPeso(self[r1][a.getOrigen()][a.getDestino()])
        anteriorB.setPeso(self[r1][anteriorB.getOrigen()][anteriorB.getDestino()])
        siguienteA.setPeso(self[r1][siguienteA.getOrigen()][siguienteA.getDestino()])
        b.setPeso(self[r1][b.getOrigen()][b.getDestino()])


        self[r1].getA().insert(c1+1,b)
        self[r2].getA().insert(c2,siguienteA)

        
        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()
       

    def solucionToList(self):
        rutas =[]
        for r in self.getRutas():
            ruta = []
            for v in r.getV():
                ruta.append(v.getValue())
            rutas.append(ruta)
        return rutas


if __name__ == "__main__":
    
    arg = Ingreso(sys.argv)
    
    G = Grafo(arg.M)
    #D demanda; NV nro de vehículos; C capacidad. G: Grafo, podría ser una matriz también
    S = Solucion(G,arg.D,arg.NV,arg.C,arg.I)
    print(S)
    g1 = Grafico(arg.coordenadas,S.solucionToList(),arg.nombreArchivo)
    S.customerSwap(3,8)
    print(S)
    g2 = Grafico(arg.coordenadas,S.solucionToList(),arg.nombreArchivo)

















    #g = Ruta(arg.M)
    #v1 = Vertice(4)
    #v2 = Vertice(2)

    # print(g[None][v1])
    # print(" ")
    # print(g[v2][None])
    # print(" ")
    # print(g[None][None])
    # print(g[2][5])  #6
    # print(g[v1][3]) #7
    # print(g[2][v2]) #4
    # print(g[v1][v2])#5 
