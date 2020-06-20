from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math

class Solucion(Grafo):
    def __init__(self, M, Demanda, sumDemanda):
        super(Solucion, self).__init__(M, Demanda)
        self.__capacidad = sumDemanda
        self.__capacidadMax = 0

    def __str__(self):
        cad = "\nRecorrido de la solución: " + str(self.getV()) + "\n" + "Aristas de la solución: "+ str(self.getA())
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
    def setCapacidadMax(self, capMax):
        self.__capacidadMax = capMax
    def setCapacidad(self, capacidad):
        self.__capacidad = capacidad
    def getCapacidad(self):
        return self.__capacidad

    def getCopyVacio(self):
        ret = Solucion([], [], 0)
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
            S = Solucion(self._matrizDistancias, self._demanda, 0)
            S.setCapacidadMax(capacidad)
            cap = S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
            S.setCapacidad(cap)
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
            if(acum_demanda + demanda[value] <= self.__capacidadMax):
                acum_demanda += demanda[value]
                sub_secuenciaInd.append(x)
                if (acum_demanda > self.__capacidad/nroVehiculos):
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
                if(acum_demanda > self.__capacidad/nroVehiculos):
                    break
                i
            j
            S = Solucion(self._matrizDistancias, self._demanda, 0)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido))
            S.setCapacidad(acum_demanda)
            S.setCapacidadMax(capacidad)
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

    def getPosiciones(self, V_origen, V_destino, rutas):
        ind_verticeOrigen = -1
        ind_verticeDestino = -1
        ind_rutaOrigen = -1
        ind_rutaDestino = -1
        #arista_azar = (3,7)    => V_origen = 3 y V_destino = 7
        #Sol:   
        #       1-2-3-4-5 1-6-7-8-9-10   
        #      (1,2)(2,3)(3,4)(4,5)(5,1)    (1,6)(6,7)(7,8)(8,9)(9,10)(10,1)
        #ind_VertOrigen = 2     ind_VertDest = 6
        for i in range(0,len(rutas)):
            for j in range(0, len(rutas[i].getV())):
                v = rutas[i].getV()[j]
                if (V_origen == v):
                    ind_verticeOrigen = j
                    ind_rutaOrigen = i
                elif (V_destino == v):
                    ind_verticeDestino = j-1
                    ind_rutaDestino = i
                if (ind_verticeOrigen != -1 and ind_verticeDestino != -1):
                    break
            if (ind_rutaOrigen != -1 and ind_rutaDestino != -1):
                if (ind_rutaOrigen == ind_rutaDestino and ind_verticeOrigen > ind_verticeDestino):
                    ind = ind_verticeOrigen
                    ind_verticeOrigen = ind_verticeDestino + 1
                    ind_verticeDestino = ind - 1
                break

        return [ind_rutaOrigen, ind_rutaDestino],[ind_verticeOrigen, ind_verticeDestino]

    #2-opt:
    def swap_2opt(self, lista_permitidos, ind_random, rutas_orig, demandas):
        sol_factible = False
        rutas = []
        print("\nswap 2-opt")
        
        while(not sol_factible and len(ind_random)>=1):
            ADD = []
            DROP = []
            arista_ini = lista_permitidos[ind_random[-1]]
            print("arista azar: "+str(arista_ini))
            ind_random.pop()
            ADD.append(arista_ini)

            V_origen = arista_ini.getOrigen()
            V_destino = arista_ini.getDestino()
            
            rutas = copy.deepcopy(rutas_orig)
            print("rutas: "+str(rutas))

            ind_rutas, ind_A = self.getPosiciones(V_origen, V_destino, rutas_orig)
            
            if(ind_rutas[0]!=ind_rutas[1]):
                r1 = rutas[ind_rutas[0]]
                r2 = rutas[ind_rutas[1]]
                #print("r1 antes: "+str(r1))
                #print("r2 antes: "+str(r2))

                A_r1_left = r1.getA()[:ind_A[0]]
                A_r1_drop = r1.getA()[ind_A[0]]
                A_r1_right = r1.getA()[ind_A[0]+1:]
                
                A_r2_left = r2.getA()[:ind_A[1]]
                A_r2_drop = r2.getA()[ind_A[1]]
                A_r2_right = r2.getA()[ind_A[1]+1:]
                
                DROP.append(A_r1_drop)
                DROP.append(A_r2_drop)

                #print("\nA_r1_l: "+str(A_r1_left))
                #print("A_r1_r: "+str(A_r1_right))
                #print("A_r2_l: "+str(A_r2_left))
                #print("A_r2_r: "+str(A_r2_right))
                #print("A_r1_drop: "+str(A_r1_drop))
                #print("A_r2_drop: "+str(A_r2_drop))

                ##arista_azar = (3,7)    => V_origen = 3 y V_destino = 7
                #Sol:   
                #       1-2-3-4-5   1-6-7-8-9-10   
                #      (1,2)(2,3)(3,4)(4,5)(5,1)    (1,6)(6,7)(7,8)(8,9)(9,10)(10,1)
                #ind_VertOrigen = 2     ind_VertDest = 1
                #new_Sol:
                #       1-2-3-7-8-9-10     1-6-4-5   
                #      (1,2)(2,3)(3,7)(7,8)(8,9)(9,10)(10,1)    (1,6)(6,4)(4,5)(5,1)
                #       ADD     DROP
                #       (6,4)   (3,4)
                #       (3,7)   (6,7)
                if(A_r2_left!=[]):
                    V_origen = A_r2_left[-1].getDestino()    # => (6, )
                #En caso de que la arista al azar se encuentra al principio
                else:
                    V_origen = Vertice(1,0)
                if(A_r1_right!=[]):
                    V_destino = A_r1_right[0].getOrigen()   # => ( ,4)
                #En caso de que la arista al azar se encuentra al final
                else:
                    V_destino = Vertice(1,0)
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                arista_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
                ADD.append(arista_add)

                A_r1_left.append(ADD[0])
                A_r1_left.extend(A_r2_right)
                A_r2_left.append(ADD[1])
                A_r2_left.extend(A_r1_right)
                
                cap_r1 = r1.cargaDesdeAristas(A_r1_left)
                cap_r2 = r2.cargaDesdeAristas(A_r2_left)
                r1.setCapacidad(cap_r1)
                r2.setCapacidad(cap_r2)
                
                print("DROP: "+str(DROP))
                print("ADD: "+str(ADD))
                
                print("r1 ahora: "+str(r1))
                print("r2 ahora: "+str(r2))
                print("cap_r1: %f       cap_r2: %f      cap_max: %f" %(cap_r1, cap_r2, self.__capacidadMax))
                
                if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                    print("Sol no factible, repito proceso")
                    rutas = []
                else:
                    print("Sol factible continuo")
                    sol_factible = True
            else:
                #1-15-17-18-21-22-25-27     (25,18) equiv (18,25)
                #(1,15)-(15,17)-(17,18)     (21,22)   (27,1)
                #(1,15)-(15,17)-(17,18)-(18,25)-(25,22)-(22,21)-(21,27)-(27,1)
                #   ADD         DROP  
                #   (18,25)     (18,21)
                #   (21,27)     (25,27)
                r = rutas[ind_rutas[0]]
                #print("r antes: "+str(r))
                V_r_left = r.getV()[:ind_A[0]+1]
                V_r_middle = r.getV()[ind_A[0]+1:ind_A[1]+1]
                V_r_middle = V_r_middle[::-1]               #invierto el medio
                V_r_right = r.getV()[ind_A[1]+1:]
                V_r_right = V_r_right[1:]
                V_r_right.append(Vertice(1,0))

                A_r_drop1 = r.getA()[ind_A[0]]
                A_r_drop2 = r.getA()[ind_A[1]+1]

                #print("V_r_l: "+str(V_r_left))
                #print("V_r_m: "+str(V_r_middle))
                #print("V_r_r: "+str(V_r_right))
                #print("V_r_drop1: "+str(A_r_drop1))
                #print("V_r_drop2: "+str(A_r_drop2))

                #Obtengo la otra arista ADD (27,21) o (21,27)
                V_origen = V_r_middle[-1]    # => (6, )
                V_destino = V_r_right[0]
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                arista_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)

                ADD.append(arista_add)                
                DROP.append(A_r_drop1)
                DROP.append(A_r_drop2)

                print("DROP: "+str(DROP))
                print("ADD: "+str(ADD))

                V_r_left.append(r.getV()[ind_A[1]+1])
                V_r_left.extend(V_r_middle)
                V_r_left.extend(V_r_right)
                V_r = V_r_left[:-1]
                
                cap = r.cargarDesdeSecuenciaDeVertices(V_r)
                r.setCapacidad(cap)
                print("r ahora: "+str(r))
                print("capacidad: ",cap)
                if(cap > self.__capacidadMax):
                    print("Sol no factible, repito proceso")
                    rutas = []
                else:
                    print("Sol factible continuo")
                    sol_factible = True
        #Fin del while (se encontro una solucion factible)
        
        return rutas, ADD, DROP
