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
        self._G = Grafo(M, D)       #Grafo original
        print(len(M))
        self.__S = Solucion(M, D, sum(D))    #Solucion general del CVRP
        self.__Distancias = M
        self.__Demandas = D         #Demandas de los clientes
        self.__capacidadMax = capac #Capacidad max por vehiculo
        self.__rutas = []           #Soluciones por vehiculo
        self.__costoTotal = 0
        self.__nroVehiculos = nroV
        self.__tipoSolucionIni = solI
        self.__beta = 1

        self.__nroIntercambios=intercamb*2    #corresponde al nro de vertices los intercambios. 1intercambio => 2 vertices
        self.__opt=opt
        self.__optimo = optimo
        self.__tenureADD =  tADD
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        self.__txt = clsTxt(str(archivo))
        self.__tiempoMaxEjec = float(tiempo)
        self.__frecMatriz = []
        
        #Iniciliza una matriz de frecuencias
        for i in range(0, len(self._G.getMatriz())):
            fila = []
            for j in range(0, len(self._G.getMatriz())):
                fila.append(0)
                j
            self.__frecMatriz.append(fila)
            i

        self.escribirDatos()
        self.__rutas = self.__S.rutasIniciales(self.__tipoSolucionIni, self.__nroVehiculos, self.__Demandas, self.__capacidadMax)
        self.__S = self.cargaSolucion(self.__rutas)
        

        print("\nSolucion general:" + str(self.__S))
        self.tabuSearch()

    #Escribe los datos iniciales: el grafo inicial y la demanda
    def escribirDatos(self):
        self.__txt.escribir("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ GRAFO CARGADO +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        self.__txt.escribir(str(self._G))
        cad = "\nDemandas:"
        print(cad)
        for v in self._G.getV():
            cad_aux = str(v)+": "+str(v.getDemanda())
            print(cad_aux) 
            cad+="\n"+ cad_aux
        self.__txt.escribir(cad)
        print("SumDemanda: ",sum(self.__Demandas))
        print("Nro vehiculos: ",self.__nroVehiculos)
        self.__txt.escribir("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ SOLUCION INICIAL +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")

    #Carga la solucion general a partir de las rutas
    def cargaSolucion(self, rutas):
        A = []
        V = []
        S = Solucion(self.__Distancias, self.__Demandas, sum(self.__Demandas))
        cap = 0
        costoTotal = 0
        sol_ini = ""
        for i in range(0, len(self.__rutas)):
            s = rutas[i]
            costoTotal += s.getCostoAsociado()
            cap += s.getCapacidad()
            A.extend(s.getA())
            V.extend(s.getV())
            sol_ini+="\nRuta #"+str(i+1)+": "+str(self.__rutas[i].getV())
            sol_ini+="\nCosto asociado: "+str(self.__rutas[i].getCostoAsociado())+"      Capacidad: "+str(self.__rutas[i].getCapacidad())+"\n"
        sol_ini+="--> Costo total: "+str(costoTotal)+"          Capacidad total: "+str(cap)
        self.__txt.escribir(sol_ini)
        S.setA(A)
        S.setV(V)
        S.setCostoAsociado(costoTotal)
        S.setCapacidad(cap)
        S.setCapacidadMax(self.__capacidadMax)

        return S

    def masVisitados(self):
        masVisitada = self.__S.getA()[0]
        for a in self.__S.getA()[1:]:
            if(a.getFrecuencia() > masVisitada.getFrecuencia()):
                masVisitada = a

    #Umbral de granularidad: phi = Beta*(c/(n+k))
    #Beta = 1  parametro de dispersion. Sirve para modificar el grafo disperso para incluir la diversificación y la intensificación
    #          durante la búsqueda.
    #c = valor de una sol. inicial
    #k = nro de vehiculos
    #n = nro de clientes
    def calculaUmbral(self, costo):
        c = costo
        k = self.__nroVehiculos
        n = len(self.__Distancias)-1
        phi = c/(n+k)
        phi = phi*self.__beta
        return round(phi,3)

    #+-+-+-+-+-+-+- Empezamos con Tabu Search +-+-+-+-+-+-+-+-+#
    #lista_tabu: tiene objetos de la clase Tabu (una arista con su tenure)
    #Lista_permitidos: o grafo disperso tiene elementos del tipo Arista que no estan en la lista tabu y su distancia es menor al umbral
    #nuevas_rutas: nuevas rutas obtenidas a partir de los intercambios
    #nueva_solucion: nueva solucion obtenida a partir de los intercambios
    #rutas_refer: rutas de referencia que sirve principalmente para evitar estancamiento, admitiendo una solucion peor y hacer los intercambios
    #             a partir de esas
    #solucion_refer: idem al anterior
    #umbral: valor de umbral de granularidad
    #tiempoIni: tiempo inicial de ejecucion - tiempoMax: tiempo maximo de ejecucion - tiempoEjecuc: tiempo de ejecución actual
    #iteracEstancamiento: iteraciones de estancamiento para admitir una solución peor, modificar Beta y escapar del estancamiento
    #iterac: cantidad de iteraciones actualmente
    def tabuSearch(self):
        lista_tabu = []
        lista_permitidos = []
        nuevas_rutas = copy.deepcopy(self.__rutas)
        rutas_refer = copy.deepcopy(nuevas_rutas)
        nueva_solucion = copy.deepcopy(self.__S)
        solucion_refer = copy.deepcopy(nueva_solucion)
        nuevo_costo = self.__S.getCostoAsociado()

        #Atributos de tiempo e iteraciones
        tiempoIni = time()
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEstancamiento = tiempoIni
        tiempoEjecuc = 0
        iteracEstancamiento = 1
        iteracEstancamiento_Opt = 1
        iterac = 1
        umbral = self.calculaUmbral(self.__S.getCostoAsociado())

        porcent_Estancamiento = 1.05

        cond_2opt = True
        cond_3opt = True
        cond_Optimiz = True

        Aristas_Opt = []
        for EP in self._G.getA():
            if(EP.getOrigen() != EP.getDestino() and EP.getDestino()!=1 and EP.getPeso() <= umbral):
                Aristas_Opt.append(EP)
        Aristas = Aristas_Opt
        
        print("Aplicamos 2-opt")
        while(tiempoEjecuc < tiempoMax):
            #self.__txt.escribir(cad)
            lista_permitidos, Aristas = self.getPermitidos(Aristas, lista_tabu, umbral, cond_Optimiz, solucion_refer)    #Lista de elementos que no son tabu
            cond_Optimiz = False
            #self.__txt.escribir(cad)
            ADD = []
            DROP = []
            
            ind_random = [x for x in range(0,len(lista_permitidos))]
            random.shuffle(ind_random)
            
            if(iteracEstancamiento_Opt>50):
                iteracEstancamiento_Opt = 1
                if(cond_2opt):
                    print("Aplicamos 3-opt")
                    cond_2opt = False
                elif(cond_3opt):
                    print("Aplicamos 4-opt")
                    cond_3opt = False
                else:
                    print("Aplicamos 2-opt")
                    cond_2opt = cond_3opt = True
                
            if(cond_2opt):
                nuevas_rutas, aristas_ADD, aristas_DROP, nuevo_costo = nueva_solucion.swap_2opt(lista_permitidos, ind_random, rutas_refer)
            #Para aplicar, cada ruta tiene que tener al menos 3 clientes (o 4 aristas)
            elif(cond_3opt):
                nuevas_rutas, aristas_ADD, aristas_DROP, nuevo_costo = nueva_solucion.swap_3opt(lista_permitidos, ind_random, rutas_refer)
            #Para aplicar, cada ruta tiene que tener al menos 3 clientes (o 4 aristas)
            else:
                nuevas_rutas, aristas_ADD, aristas_DROP, nuevo_costo = nueva_solucion.swap_4opt(lista_permitidos, ind_random, rutas_refer)
            nuevo_costo = round(nuevo_costo, 3)
            tenureADD = self.__tenureADD
            tenureDROP = self.__tenureDROP
            
            #Si encontramos una mejor solucion que la tomada como referencia
            if(nuevo_costo < solucion_refer.getCostoAsociado()):
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                cad += "Lista tabu: "+str(lista_tabu)
                self.__txt.escribir(cad)
                #Si la nueva solucion es mejor que la obtenida hasta el momento
                if(nueva_solucion.getCostoAsociado() < self.__S.getCostoAsociado()):
                    tiempoTotal = time()-tiempoEstancamiento
                    cad += "\nLa solución anterior duró " + str(int(tiempoTotal/60))+"min "+ str(int(tiempoTotal%60))
                    cad += "seg    -------> Nuevo optimo local. Costo: "+str(nueva_solucion.getCostoAsociado())
                    self.__txt.escribir(cad)
                    print(cad)
                    self.__S = nueva_solucion
                    self.__rutas = nuevas_rutas
                    tiempoEstancamiento = time()
                    iteracEstancamiento_Opt = 1
                    self.__beta = 1
                else:
                    cad += "Nuevo optimo. Costo: "+str(nueva_solucion.getCostoAsociado())
                    print(cad)
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                tenureADD = self.__tenureMaxADD
                tenureDROP = self.__tenureMaxDROP
                cond_Optimiz = True
                Aristas = Aristas_Opt
                iteracEstancamiento = 1
                porcent_Estancamiento = 1.05
            #Si se estancó, tomamos la proxima solución peor que difiera un 5% del optimo como referencia
            elif(nuevo_costo < self.__S.getCostoAsociado()*1.1 and (nuevo_costo > self.__S.getCostoAsociado()*porcent_Estancamiento) and (iteracEstancamiento>100)):
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                tiempoTotal = time()-tiempoEstancamiento
                print("Se estancó durante %d min %d seg. Admitimos una solucion peor" %(int(tiempoTotal/60), int(tiempoTotal%60)))
                self.__beta = 1.5
                if(porcent_Estancamiento>=1.03):
                    porcent_Estancamiento -= 0.01
                else:
                    porcent_Estancamiento = 1.1
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                cond_Optimiz = True
                iteracEstancamiento = 1
                Aristas = Aristas_Opt
            else:
                nuevas_rutas = rutas_refer
                nueva_solucion = solucion_refer
            
            ADD.append(Tabu(aristas_ADD[0], tenureADD))
            for i in range(0, len(aristas_DROP)):
                DROP.append(Tabu(aristas_DROP[i], tenureDROP))

            self.decrementaTenure(lista_tabu)
            lista_tabu.extend(DROP)
            lista_tabu.extend(ADD)

            tiempoEjecuc = time()-tiempoIni
            iterac += 1
            iteracEstancamiento += 1
            iteracEstancamiento_Opt += 1
        #Fin del while. Imprimo los valores obtenidos

        print("\nMejor solucion obtenida: "+str(self.__rutas))
        tiempoTotal = time() - tiempoIni
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")
        self.__txt.escribir("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Solucion Optima +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        sol_ini = ""
        for i in range(0, len(self.__rutas)):
            sol_ini+="\nRuta #"+str(i+1)+": "+str(self.__rutas[i].getV())
            sol_ini+="\nCosto asociado: "+str(self.__rutas[i].getCostoAsociado())+"      Capacidad: "+str(self.__rutas[i].getCapacidad())+"\n"
        self.__txt.escribir(sol_ini)
        porcentaje = round(self.__S.getCostoAsociado()/self.__optimo -1.0, 3)
        self.__txt.escribir("\nCosto total:  " + str(self.__S.getCostoAsociado()) + "        Optimo real:  " + str(self.__optimo)+
                            "      Desviación: "+str(porcentaje*100)+"%")
        self.__txt.escribir("\nCantidad de iteraciones: "+str(iterac))
        self.__txt.escribir("Nro de vehiculos: "+str(self.__nroVehiculos))
        self.__txt.escribir("Capacidad Maxima/Vehiculo: "+str(self.__capacidadMax))
        self.__txt.escribir("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        tiempoTotal = time()-tiempoEstancamiento
        self.__txt.escribir("Tiempo de estancamiento: "+str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        self.__txt.imprimir()
    
       
    def getPermitidos(self, Aristas, lista_tabu, umbral, cond_Optimiz, solucion):
        ListaPermit = []           #Aristas permitidas de todas las aristas del grafo original
        AristasNuevas = []
        
        #No tengo en consideracion a las aristas que exceden el umbral y las que pertencen a S
        if(cond_Optimiz):
            for EP in Aristas:
                pertS = False
                for A_S in solucion.getA():
                    if A_S == EP:
                        pertS = True
                        break
                if(not pertS and EP.getPeso() <= umbral):
                    AristasNuevas.append(EP)
        else:
            AristasNuevas = Aristas
        
        #La lista tabu esta vacia, entonces la lista de permitidas tiene todas las aristas anteriores
        if(len(lista_tabu) == 0):
            ListaPermit = AristasNuevas
        #La lista tabu tiene elementos, agrego los que no estan en lista tabu
        else:
            for i in range(0, len(AristasNuevas)):
                EP = AristasNuevas[i]
                cond = True
                j = 0
                while(j < len(lista_tabu) and cond):
                    ET = lista_tabu[j] 
                    if(EP == ET.getElemento()):
                        cond = False
                    j+=1
                if(cond):
                    ListaPermit.append(EP)
            
        return ListaPermit, AristasNuevas

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