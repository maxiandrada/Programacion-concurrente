from Vertice import Vertice
from Arista import Arista
from Grafo import Grafo
from Solucion import Solucion
from Tabu import Tabu
import random 
import sys
import re
import math 
import copy
from clsTxt import clsTxt
from time import time

class CVRP:
    def __init__(self, M, D, nroV, capac, archivo, solI, intercamb, opt, tADD, tDROP, tiempo, optimo):
        self._G = Grafo(M)      #Grafo original
        print(len(M))
        self._S = Solucion(M)
        self.__Distancias = M
        self.__Demanda = D      #Demanda de los clientes
        self.__capacidad = capac
        self.__soluciones = []
        self.__rutas = []   #Solucion general del CVRP
        self.__costoTotal = 0
        self.__nroIntercambios=intercamb*2    #corresponde al nro de vertices los intercambios. 1intercambio => 2 vertices
        self.__opt=opt
        self.__optimo = optimo
        self.__tenureADD =  tADD
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        #self.__txt = clsTxt(str(nombreArchivo))
        self.__txt = None
        self.__tiempoMaxEjec = float(tiempo)
        self.__frecMatriz = []
        self.__nroVehiculos = nroV
        self.__tipoSolucionIni = solI

        print("Se cargo el archivo")
        #Iniciliza una matriz de frecuencias
        for i in range(0, len(self._G.getMatriz())):
            fila = []
            for j in range(0, len(self._G.getMatriz())):
                fila.append(0)
                j
            self.__frecMatriz.append(fila)
            i
        
        print(str(self._G))
        for i in range(0, len(self.__Demanda)):
            print('%i : %s' %(i+1,str(self.__Demanda[i]))) 
        
        print(sum(self.__Demanda))
        print(self.__nroVehiculos)

        self.__rutas = self._S.rutasIniciales(self.__tipoSolucionIni, self.__nroVehiculos, self.__Demanda, self.__capacidad)
        A = []
        V = []
        for s in self.__rutas:
            self.__costoTotal += s.getCostoAsociado()
            A.extend(s.getA())
            V.extend(s.getV())
        for i in range(0, len(self.__rutas)):
            print("\nRuta del vehiculo "+str(i+1)+":\n"+str(self.__rutas[i]))
        
        self._S.setA(A)
        self._S.setV(V)
        self._S.setCosto(self.__costoTotal)
        print("\nSolucion general: ", str(self._S))
        
        self.tabuSearch()

    # Para el Tabu Search Granular
    def vecinosMasCercanosTSG(self, indicesRandom, lista_permitidos, lista_permitidosSol):
        indices = []                #Indices de la lista de permitidos para hacer el swapp
        aristas_permitidas = []     #Lista de permitidos como enteros que corresponden a las aristas = lista_permitidos
        aristas_solucion = []       #La solucion como una lista de enteros que corresponden a las aristas
        
        for A in lista_permitidosSol:
            origen = int(A.getOrigen().getValue())
            destino = int(A.getDestino().getValue())
            peso = A.getPeso()
            aristas_solucion.append([origen, destino, peso])
        print("\naristas solucion: "+str(aristas_solucion))
        
        aristas_permitidasRandom = []
        for x in indicesRandom:
            aristas_permitidasRandom.append(aristas_solucion[x])
        print("aristas permitidas random: "+str(aristas_permitidasRandom))
        
        for A in lista_permitidos:
            origen = int(A.getOrigen().getValue())
            destino = int(A.getDestino().getValue())
            peso = A.getPeso()
            aristas_permitidas.append([origen, destino, peso])
        print("aristas permitidas: "+str(aristas_permitidas))
        
        aristas_restantes = [x for x in aristas_permitidas if x not in aristas_permitidasRandom and x not in aristas_solucion]
        print("aristas permitidas restantes: "+str(aristas_restantes))    
        
        #[(1,2);(2,3);(3,4);(1,9);(9,5);(5,6);(1,7);(7,8);(8,10)]
        #2-opt:
        #ADD = (2,5) y DROP = (2,3) --> [(1,2);(2,5);(5,4);(1,9);(9,3);(3,6);(1,7);(7,8);(8,10)]
        #[(1,2);(2,5);(5,4);(1,3);(3,9);(9,6);(1,7);(7,8);(8,10)]
        #3-opt:
        #ADD = [(2,7),[1,3],[1,9]] y DROP = [(2,3),(1,7)]
        #Antes: [1,2,3,4,1,9,5,6,1,7,8,10] ->(3,9,7) [1,2,7,4,1,3,5,6,1,9,8,10]
        #[(1,2);(2,7);(7,4);(1,3);(3,5);(5,6);(1,9);(9,8);(8,10)]
        #[(1,2);(2,5);(5,4);(1,3);(3,9);(9,6);(1,7);(7,8);(8,10)]
        for i in indicesRandom:
            indices.append(aristas_permitidas.index(aristas_solucion[i]))
            ind = self.vecinoMasCercano(aristas_solucion[i], aristas_restantes, aristas_permitidas)
            indices.append(ind)
            if(aristas_restantes!=[]):
                print("arista add: "+str(aristas_permitidas[ind]))
                aristas_restantes.remove(aristas_permitidas[ind])
        
        return indices

    def vecinoMasCercano(self, arista_seleccionada, aristas_restantes, aristas_permitidas):
        masCercano = 999999999999
        indMasCercano = 0
        lista_aristas = [x for x in aristas_restantes if x[0]==arista_seleccionada[0]]

        print("\narista drop: "+str(arista_seleccionada))
        for A in lista_aristas:
            costo = A[2]
            if(costo < masCercano or len(lista_aristas)==1):
                masCercano = costo
                indMasCercano = aristas_permitidas.index(A)

        return indMasCercano
    
    def vecinosMasCercanosTSG_1(self, indicesRandom: list, lista_permitidos: list, recorrido: list):
        indices = []                #Indices de la lista de permitidos para hacer el swapp
        valores_permitidos = []     #Lista de permitidos como enteros y no como vertices
        valores_recorrido = []              #La solucion como una lista de enteros
        matrizDist = self._G.getMatriz()
        
        for x in lista_permitidos:
            valores_permitidos.append(x.getValue()) #Se carga con los indices que ocupan en el grafo. Lo mismo que en lista_permit solo que
                                                    #ahora son enteros y no vertices
        
        for x in recorrido:
            valores_recorrido.append(x.getValue())
        
        permitRandom = []
        for x in indicesRandom:
            permitRandom.append(valores_permitidos[x])
        
        permitidos = list(set(valores_permitidos)-set(permitRandom))

        for i in indicesRandom:
            indices.append(i)
            ind = self.vecinoMasCercanoV2(matrizDist,valores_permitidos[i], permitidos, valores_permitidos, valores_recorrido)
            indices.append(ind)
            if(permitidos!=[]):
                permitidos.remove(valores_permitidos[ind])

        return indices

    def vecinoMasCercanoV2(self, matrizDist: list, pos: int, permitidos: list, list_permit, recorrido):
        masCercano = 999999999999
        indMasCercano = 0
        posAnterior = recorrido.index(pos) -1
        posAnterior=int(recorrido[posAnterior])
    
        for ind in permitidos:
            costo = matrizDist[posAnterior-1][ind-1]
            if(costo<masCercano or len(permitidos)==1):
                masCercano = costo
                indMasCercano = list_permit.index(ind)

        return indMasCercano

    #Incrementa la frecuencia en cada arista, en caso de que se obtenga un optimo local
    def incrementaFrecuencia(self, sol):
        for x in sol.getA():
            origen = int(x.getOrigen().getValue()-1)
            destino = int(x.getDestino().getValue()-1)
            self.__frecMatriz[origen][destino] = self.__frecMatriz[origen][destino] + 1
            self.__frecMatriz[destino][origen] = self.__frecMatriz[destino][origen] + 1
        
    #Analizamos las aristas mas frecuentadas para mantenerlas estaticas
    def TS_Frecuencia(self, Sol_Optima, lista_tabu, nroIntercambios):      
        aristasSol = Sol_Optima.getA()
        lista_Frecuentados = lista_tabu
        vertADD = None
        vertDROP = None

        #Me fijo si "esta llena" la lista tabu, tal que permita realizar los intercambios que se indicaron
        longitud =  len(Sol_Optima.getV()) - len(lista_tabu)    #Longitud de los permitidos
        longitud -= (4 +1)     #Verifico si hay suficiente permitidos para agregar a la lista tabu, sin contar el V(1)
        
        #print("Lista tabu antes: "+str(lista_tabu))
        #Verifico que se cumpla las condiciones con respecto a longitudes
        if(longitud>=0):
            mayFrecuencia = -1
            
            #Recorro las aristas de la ultima solucion optima obtenida
            for a in aristasSol:
                vert_Origen = a.getOrigen()
                vert_Destino = a.getDestino()
                frec_Actual = self.__frecMatriz[vert_Origen.getValue()-1][vert_Destino.getValue()-1]
                pertenece = self.pertenListaTabu_TSF(vert_Origen, vert_Destino, lista_tabu)
                
                if(frec_Actual > mayFrecuencia and not pertenece):
                    mayFrecuencia = frec_Actual
                    vertADD = vert_Origen
                    vertDROP = vert_Destino 
            #Cargamos los mas frecuentados con un Tenure igual a -1, para que no se eliminen
            if(vertADD != None and vertDROP != None):
                lista_Frecuentados = self.frecuentados(vertADD, vertDROP, lista_tabu)
                #print("vertADD: "+str(vertADD)+"    vertDROP: "+str(vertDROP)+ "       Max Frecuencia: "+str(mayFrecuencia))
                #print("Lista tabu ahora: "+str(lista_Frecuentados))
                return lista_Frecuentados
        
        #Si no se cumple, tengo la lista tabu "llena"
        #Elimino una cantidad suficiente de la lista Tabu para que permita realizar los intercambios
        lista_Frecuentados = self.borraFrecuentados(lista_tabu)
        
        #print("Lista tabu ahora: "+str(lista_Frecuentados))
        
        return lista_Frecuentados

    #Devuelve los frecuentados
    def frecuentados(self, vert_ADD, vert_DROP, lista_tabu):
        lista_Frecuentados = []
        for x in lista_tabu:
            valor = x.getElemento().getValue()
            if(valor != vert_ADD.getValue() and valor != vert_DROP.getValue()):
                lista_Frecuentados.append(x)

        if(vert_ADD.getValue()!= 1):
            Tabu_ADD = Tabu(vert_ADD, -1)
            lista_Frecuentados.append(Tabu_ADD)
    
        if(vert_DROP.getValue()!= 1):
            Tabu_DROP = Tabu(vert_DROP, -1)
            lista_Frecuentados.append(Tabu_DROP)

        return lista_Frecuentados

    #Pertenece o no a la lista tabu
    def pertenListaTabu_TSF(self, v1, v2, lista_tabu):
        lista_ElementosTabu = []
        e1 = v1.getValue()
        e2 = v2.getValue()
        
        if(e1 == 1 or e2 == 1):
            return True

        for x in lista_tabu:
            elem = int(x.getElemento().getValue())
            lista_ElementosTabu.append(elem)
        
        return (e1 in lista_ElementosTabu) or (e2 in lista_ElementosTabu)

    #Borro una cantidad necesaria para realizar los Swapp proximos
    def borraFrecuentados(self, lista_tabu):
        #Borramos al azar
        indices_azar = random.sample(range(0,len(lista_tabu)), 4)
        
        ADD = None
        DROP = None
        print("Lista de frecuentados llena. Borramos algunos")
        for ind in indices_azar:
            lista_tabu[ind].setTenure(1)
            if(ADD == None):
                ADD = lista_tabu[ind].getElemento().getValue() -1
            elif(DROP == None):
                DROP = lista_tabu[ind].getElemento().getValue() -1
            else:
                self.__frecMatriz[int(ADD)][int(DROP)] = 0
                ADD = None
                DROP = None
        self.decrementaTenure(lista_tabu)

        return lista_tabu
    
    
    ####### Empezamos con Tabu Search #########
    def tabuSearch(self):
        lista_tabu = []         #Tiene objetos de la clase Tabu
        lista_permitidos = []   #Tiene objetos de la clase arista
        Sol_Actual = self._S
        
        #Atributos banderas utilizados
        condOptim = False   #En caso de que encontre uno mejor que el optimo lo guardo en el archivo txt
        condTS_Frecuencia = False #Empezamos a utilizar las aristas mas frecuentadas
        cond_3opt = False
        cond_4opt = False

        #Atributos de tiempo y otros
        tiempoIni = time()
        tiempoIniNoMejora = tiempoIni
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEjecuc = 0
        iterac = 1
        nroIntercambios = 4
        #Duarnte 1min de no mejora o si es demasiado, la 1/5 parte del tiempo
        tiempoMaxNoMejora = 2*60
        if(tiempoMaxNoMejora > tiempoMax/4):
            tiempoMaxNoMejora = float(tiempoMax/4)  #La 1/5 parte del tiempo, en caso de que los 1min sea demasiado
        
        while(tiempoEjecuc <= tiempoMax and iterac<=2):
            lista_permitidos, lista_permitidosSol = self.getPermitidos(lista_tabu)    #Lista de elementos que no son tabu
            print("Lista de permitidos: "+str(lista_permitidos))
            ADD = []
            DROP = []
            
            #Verifico si hay vertices disponibles suficientes para el intercambio
            if(len(lista_permitidos)>=4):
                #Controla que el nro de intercambios no supere la longitud de permitidos
                print("Len: "+str(len(lista_permitidos))+"   nroIntercambios: "+str(nroIntercambios))    
                if(len(lista_permitidos)<nroIntercambios):
                    nroIntercambios=len(lista_permitidos)
                    if(nroIntercambios%2!=0):
                        nroIntercambios-=1                    
                
                #+-+-+-+-+-+-+-+- Tabu Search Granular +-+-+-+-+-+-+-+-+-#
                if(cond_3opt):
                    #3-opt
                    ind_random = random.sample(range(0,len(lista_permitidosSol)),1)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permitidos, lista_permitidosSol)
                    ind_aux = self.vecinosMasCercanosTSG(ind_random, lista_permitidos, lista_permitidosSol)
                    ind_random.append(ind_aux[-1])
                elif(cond_4opt):
                    #4-opt
                    ind_random = random.sample(range(0,len(lista_permitidosSol)),2)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permitidos, lista_permitidosSol)
                else:
                    #2-opt    
                    ind_random = random.sample(range(0,len(lista_permitidosSol)),int(nroIntercambios/2))
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permitidos, lista_permitidosSol)
                
                #Crea los elementos ADD y DROP
                for i in range(0,len(ind_random)):
                    if(i%2!=0): #Los impares para ADD y los pares para DROP
                        ADD.append(Tabu(lista_permitidos[ind_random[i]], self.__tenureADD))
                        print("ADD: "+str(ADD))
                    else:
                        DROP.append(Tabu(lista_permitidos[ind_random[i]], self.__tenureDROP))
                        print("DROP: "+str(DROP))
            else:
                print("No hay vertices disponibles para el intercambio. Elimina vertices de la lista Tabu")
                self.borraFrecuentados(lista_tabu)
            
            self.decrementaTenure(lista_tabu)   #Decremento el tenure y elimino algunos elementos con tenure igual a 0
            
            #Agrego los nuevos vertices a la lista tabu o decremento el tiempo de iteracion de TS_Frecuencia
            lista_tabu.extend(ADD)
            lista_tabu.extend(DROP)
            lista_permitidos = []
            iterac += 1
            tiempoEjecuc = time()-tiempoIni
        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        #Fin del while. Imprimo la solucion optima y algunos atributos
        tiempoFin = time()
        tiempoTotal = tiempoFin - tiempoIni

    def getPermitidos(self, lista_tabu: list):
        ListaPermit = []
        ListaPermit_Sol = []
        Aristas = []
        for EP in self._G.getA():
            if(EP.getOrigen() != EP.getDestino() and EP.getDestino()!=1):
                Aristas.append(EP)
        
        if(len(lista_tabu) == 0):
            ListaPermit = Aristas
            ListaPermit_Sol = self._S.getA()[:-1]
            print("[-1]: "+str(self._S.getA()[-1]))
        else:
            for EP in Aristas:
                cond = True
                for ET in lista_tabu:
                    if(EP == ET.getElemento()):
                        cond = False
                        break
                if(cond):
                    ListaPermit.append(EP)
                    pertS = any(x == EP for x in self._S.getA())
                    if(pertS):
                        ListaPermit_Sol.append(EP)
            print("Lista de permitidos: "+str(ListaPermit))
            print("Lista tabu: "+str(lista_tabu))
            print("Lista permitidos solucion: "+str(ListaPermit_Sol))

        return ListaPermit, ListaPermit_Sol

    ####### Empezamos con Tabu Search #########
    def tabuSearch_1(self, strSolInicial):
        lista_tabu = []     #Tiene objetos de la clase Tabu
        lista_permit = []   #Tiene objetos del tipo vertice      
        g1 = self._G.copyVacio()  #La primera solucion corresponde a g1
        
        if(strSolInicial=="Vecino mas cercano"):
            ########Partimos del vecino mas cercano###########
            print("Soluncion inicial por Vecino mas cercano")
            #vecinosCercanos = self.solucionVecinosCercanos() #Obtiene un vector de vértices
            #g1.cargarDesdeSecuenciaDeVertices(vecinosCercanos) #Carga el recorrido a la solución
        else:
            ########Partimos de una solucion al Azar#############
            print("Solucion inicial al azar")
            #solucionAzar = self.solucionAlAzar()
            #g1.cargarDesdeSecuenciaDeVertices(solucionAzar)

        self.__soluciones.append(g1) #Agregar solución inicial
        self.incrementaFrecuencia(g1)
        
        print("Comenzando Tabu Search")
        self.__txt.escribir("############### GRAFO CARGADO #################")
        self.__txt.escribir(str(self._G))
        self.__txt.escribir("################ SOLUCION INICIAL #################")
        self.__txt.escribir("Vertices:        " + str(g1.getV()))
        self.__txt.escribir("Aristas:         " + str(g1.getA()))
        #self.__txt.escribir("Costo asociado:  " + str(g1.getCostoAsociado()))
        
        ##############     Atributos       ################
        #Soluciones a utilizar
        Sol_Actual = self._G.copyVacio()
        Sol_Actual = self.__soluciones[len(self.__soluciones)-1]        #La actual es la Primera solución
        Sol_Optima = copy.deepcopy(Sol_Actual)      #Ultima solucion optima obtenida, corresponde a la primera Solucion
        
        #Atributos banderas utilizados
        condOptim = False   #En caso de que encontre uno mejor que el optimo lo guardo en el archivo txt
        condTS_Frecuencia = False #Empezamos a utilizar las aristas mas frecuentadas
        cond_3opt = False
        cond_4opt = False

        if(self.__opt == "3-opt"):
            cond_3opt = True
            print("Movimiento: 3-opt")

        #Atributos de tiempo y otros
        tiempoIni = time()
        tiempoIniEstancamiento = tiempoIni       
        tiempoIniNoMejora = tiempoIni
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEjecuc = 0
        iterac = 1
        
        #Duarnte 1min de no mejora o si es demasiado, la 1/5 parte del tiempo
        tiempoMaxNoMejora = 2*60
        if(tiempoMaxNoMejora > tiempoMax/4):
            tiempoMaxNoMejora = float(tiempoMax/4)  #La 1/5 parte del tiempo, en caso de que los 1min sea demasiado

        print("Tiempo maximo: "+str(int(tiempoMax/60))+"min "+str(int(tiempoMax%60))+"seg")
        print("Tiempo maximo estancamiento: "+str(int(tiempoMaxNoMejora/60))+"min "+str(int(tiempoMaxNoMejora%60))+"seg")
        print("Optimo real: "+str(self.__optimo))
        print("Solucion inicial: "+str(Sol_Optima.getCostoAsociado()))

        nroIntercambios = 2 #Empezamos con 2 al inicio
        while(tiempoEjecuc <= tiempoMax):
            lista_permit = self.pertenListaTabu_1(lista_tabu)    #Lista de elementos que no son tabu
            ADD = []
            DROP = []
            
            #Verifico si hay vertices disponibles suficientes para el intercambio
            if(len(lista_permit)>=4):
                #Controla que el nro de intercambios no supere la longitud de permitidos
                if(len(lista_permit)<nroIntercambios):
                    nroIntercambios=len(lista_permit)
                    if(nroIntercambios%2!=0):
                        nroIntercambios-=1                    
                
                tiempoRestante = tiempoMax - tiempoEjecuc       #Lo que queda de tiempo
                
                #+-+-+-+-+-+-+- En caso de estancamientos +-+-+-+-+-+-+-+-+-+-+-
                if(time()-tiempoIniEstancamiento > tiempoMaxNoMejora):    
                    tiempoTotal = time()-tiempoIniEstancamiento
                    print("\nDurante " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg no hubo mejora")
                    print("Tiempo restante: "+str(int(tiempoRestante/60))+"min "+str(int(tiempoRestante%60))+ "seg")
                    
                    print("\nAplicamos frecuencia de aristas mas visitadas")
                    lista_tabu = self.TS_Frecuencia(Sol_Optima, lista_tabu, nroIntercambios)                    
                    lista_permit = self.pertenListaTabu_1(lista_tabu)
                    condTS_Frecuencia = not condTS_Frecuencia
                    
                    #Se intercambia movimientos entre 2-opt, 3-opt y 4-opt
                    if(not cond_3opt and not cond_4opt):
                        print("Aplicamos movimientos 3-opt")
                        cond_3opt = True
                    else:
                        cond_3opt = False
                        if(not cond_4opt):
                            print("Aplicamos movimientos 4-opt v2")
                            cond_4opt = True
                        elif(nroIntercambios < self.__nroIntercambios):
                            nroIntercambios += 2
                            cond_4opt = False
                            print("Aplicamos movimientos 4-opt v1")
                        else:
                            cond_4opt = False
                            nroIntercambios = 2
                            print("Aplicamos movimientos 2-opt")

                    #Obtengo 2/3 de lo que resta de tiempo, para que la proxima vez ingrese en menor tiempo cuando no hay mejoria
                    #solo en caso de que el tiempo restante sea menor al tiempo MaxNoMejora, ya que si no, no habra una proxima
                    #vez en que se estanque
                    if(tiempoRestante < tiempoMaxNoMejora and not cond_3opt):
                        tiempoMaxNoMejora = tiempoRestante*2/3
                    elif(tiempoMaxNoMejora > 20 and not cond_3opt):   #Mayor que 20seg
                        tiempoMaxNoMejora = tiempoMaxNoMejora*0.75

                    tiempoIniEstancamiento=time()    #Reiniciamos el tiempo de No mejora
                    
                ######### Tabu Search Granular ##########                
                if(cond_3opt):
                    #3-opt
                    ind_random = random.sample(range(0,len(lista_permit)),1)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                    ind_aux = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                    ind_random.append(ind_aux[-1])
                elif(cond_4opt):
                    #4-opt
                    ind_random = random.sample(range(0,len(lista_permit)),2)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                else:
                    #2-opt    
                    ind_random = random.sample(range(0,len(lista_permit)),int(nroIntercambios/2))
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                
                #Crea los elementos ADD y DROP
                for i in range(0,len(ind_random)):
                    if(i%2==0): #Los pares para ADD y los impares para DROP
                        ADD.append(Tabu(lista_permit[ind_random[i]], self.__tenureADD))
                    else:
                        DROP.append(Tabu(lista_permit[ind_random[i]], self.__tenureDROP))

                #Realiza el intercambio de los vertices seleccionados
                if(cond_3opt):
                    #3-opt
                    Sol_Actual = Sol_Actual.swap_3opt(ADD[0].getElemento(), DROP[0].getElemento(), ADD[1].getElemento())
                elif(cond_4opt):
                    #4-opt v2
                    Sol_Actual = Sol_Actual.swap_4opt(ADD[0].getElemento(), DROP[0].getElemento(), ADD[1].getElemento(), DROP[1].getElemento())
                else:
                    #2-opt y 4-opt v1
                    for i in range(0,len(ADD)):
                        Sol_Actual = Sol_Actual.swapp(ADD[i].getElemento(), DROP[i].getElemento())
                    
                #Si obtengo una nueva solucion optima
                if(Sol_Actual < Sol_Optima):
                    Sol_Optima = Sol_Actual                  #Actualizo la solucion optima
                    self.incrementaFrecuencia(Sol_Optima)    #Incrementa Frecuencia de Aristas visitadas
                    
                    condOptim = True
                    
                    tiempoTotal = time() - tiempoIniNoMejora
                    print("La solución anterior duró " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg    -------> Nuevo optimo encontrado. Costo: "+str(Sol_Optima.getCostoAsociado()))
                    
                    self.__soluciones.append(Sol_Actual) #Cargo las soluciones optimas
                    tiempoIniEstancamiento=time()
                    tiempoIniNoMejora = time()

                    #Actualizo el tenure con el tenureMax de ADD y DROP
                    for i in range(0,len(ADD)):
                        if(i<len(ADD)):
                            ADD[i].setTenure(self.__tenureMaxADD)
                        elif(i<len(DROP)):
                            DROP[i].setTenure(self.__tenureMaxDROP)
                else:
                    #Si no hubo un estancamiento, utilizo la ultima solucion optima obtenida, y sigo aplicando Tabu Search
                    Sol_Actual = Sol_Optima
                
                #Si hemos encontramos un optima local, lo guardamos en el txt
                if(condOptim):
                    self.__txt.escribir("################################ " + str(iterac) + " ####################################")
                    self.__txt.escribir("Vertices:        " + str(Sol_Actual.getV()))
                    self.__txt.escribir("Aristas:         " + str(Sol_Actual.getA()))
                    self.__txt.escribir("Costo asociado:  " + str(Sol_Actual.getCostoAsociado()))
                    self.__txt.escribir("Tiempo actual:   "+ str())
                    self.__txt.escribir("-+-+-+-+-+-+-+-+-+-+-+-+ Lista TABÚ +-+-+-+-+-+-+-+-+-+-+-+-+")
                    self.__txt.escribir("Lista Tabu: "+ str(lista_tabu))
                    condOptim = False
            else:
                print("No hay vertices disponibles para el intercambio. Elimina vertices de la lista Tabu")
                self.borraFrecuentados(lista_tabu)
            
            self.decrementaTenure(lista_tabu)   #Decremento el tenure y elimino algunos elementos con tenure igual a 0
            
            #Agrego los nuevos vertices a la lista tabu o decremento el tiempo de iteracion de TS_Frecuencia
            if(not condTS_Frecuencia):
                lista_tabu.extend(ADD)
                lista_tabu.extend(DROP)
            
            condTS_Frecuencia = False
            
            lista_permit = []
            iterac += 1
            tiempoEjecuc = time()-tiempoIni
        
        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        #Fin del while. Imprimo la solucion optima y algunos atributos
        tiempoFin = time()
        tiempoTotal = tiempoFin - tiempoIni
        self.__txt.escribir("\n################################ Solucion Optima ####################################")
        self.__txt.escribir("Vertices:        " + str(Sol_Optima.getV()))
        self.__txt.escribir("Aristas:         " + str(Sol_Optima.getA()))
        porcentaje = round(Sol_Optima.getCostoAsociado()/self.__optimo -1.0, 3)
        self.__txt.escribir("Costo asociado:  " + str(Sol_Optima.getCostoAsociado()) + "        Optimo real:  " + str(self.__optimo)+"      Desviación: "+str(porcentaje*100)+"%")
        self.__txt.escribir("\nNro Intercambios: " + str(int(self.__nroIntercambios/2)))
        self.__txt.escribir("Cantidad de iteraciones: "+str(iterac))
        self.__txt.escribir("Movimiento Opt inicial: "+self.__opt)
        self.__txt.escribir("Tenure ADD: " + str(self.__tenureADD) + "           Tenure DROP: "+str(self.__tenureDROP))
        self.__txt.escribir("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        self.__txt.imprimir()
        
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")

    #Devuelve una lista con los vertices que no pertenecen a la lista tabu
    def pertenListaTabu_1(self, lista_tabu: list):
        ListaPermit = []
        CopyAristas = copy.deepcopy(self._S.getA())
        cantVert = len(copy.deepcopy(self._G.getV()))
        if(len(lista_tabu) == 0):
            ListaPermit = CopyAristas
        else:
            for i in range(0, cantVert):
                EP = CopyAristas[i]      #EP: Elemento Permitido
                j = 0
                cond = True
                while(j < len(lista_tabu) and cond):
                    ET = lista_tabu[j].getElemento()    #ET: Elemento Tabu
                    if(EP == ET):
                        cond = False
                    j+=1
                if(cond):
                    ListaPermit.append(EP)
        
        ListaPermit.pop(0) #Eliminamos el vertice inicial, el 1
        
        return ListaPermit

    #Decrementa el Tenure en caso de que no sea igual a -1. Si luego de decrementar es 0, lo elimino de la lista tabu
    def decrementaTenure(self, lista_tabu: list):
        i=0
        while (i < len(lista_tabu)):
            elemTabu=lista_tabu[i]
            if(elemTabu.getTenure()!=-1):
                elemTabu.decrementaT()
            if(elemTabu.getTenure()==0):
                lista_tabu.pop(i)
                i-=1
            i+=1
