import tkinter as tk
import re
import math
import time
from CVRP import CVRP
from Vertice import Vertice
import tkinter.filedialog
import os
from tkinter import ttk
from os import listdir
from os.path import isfile, join
import ntpath

class Ventana(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("450x500+350+130")
        self.title("Buqueda tabu aplicada a CVRP")
        self.__demanda = []
        self.__nroVehiculos = []
        self.__nro = 0
        self.__openFolder = False

        self.__tabs = ttk.Notebook(self)
        self.elementosGUI()
        self.__frames = []

        self.barraMenus()
    
    def barraMenus(self):
        self.__menu = tk.Menu(self)
        self.__menuArchivo = tk.Menu(self.__menu)
        self.__menuArchivo.add_command(label="Open File", command=self.openFile)
        self.__menu.add_cascade(label="File", menu=self.__menuArchivo)
        self.__menuArchivo.add_command(label="Open Folder", command=self.openFolder)

        self.config(menu = self.__menu)
    
    def elementosGUI(self):
        self.__labelSolInicial = []
        self.__labelEstadoGrafo = []
        self.__eSolInicial = []
        self.__combo1 = []
        self.__labelNroIntercambios = []
        self.__spinboxNroIntercambios = []
        self.__eOpt = []
        self.__comboOpt = []
        self.__nroIntercambios = []
        self.__labelTenureADD = []
        self.__labelTenureDROP = []
        self.__boxADD = []
        self.__spinboxDROP = []
        self.__spinboxADD = []
        self.__boxDROP = []
        self.__labelTiempoEjecucion = []
        self.__eTime = []
        self.__entryTiempoEjecucion = []
        self.__labelTEmin = []
        self.__areaDatos = []
        self.__label_RecomiendacTiempo = []
        self.__matrizDistancias = []
        self.__optimo = []
        self.__capacidad = []
        self.__cantidadResolver =[]
        self.__labelCantidadResolver = []
        self.__labelRecomienda =[]
        self.__spinboxCantidadResolver = []
    
    def menuConfig(self,frame,i):
        self.__labelEstadoGrafo.append(tk.Label(frame, text = "No se ha cargado Grafo"))
        self.__labelEstadoGrafo[i].place(relx=0.4,rely=0.05)
        #Pestañas            
        
        #Solucion inicial
        self.__labelSolInicial.append(tk.Label(frame, text = "Solucion inicial"))
        self.__labelSolInicial[i].place(relx=0.2, rely=0.10)
        
        self.__combo1list=['Secuencial','Vecino mas cercano', 'Al azar']
        self.__eSolInicial.append(tk.StringVar())
        self.__combo1.append(ttk.Combobox(frame, textvariable=self.__eSolInicial[i], values=self.__combo1list, width = 29, state = "disabled"))
        self.__combo1[i].place(relx=0.4, rely=0.10)
        
        #Nro de intercambios
        self.__labelNroIntercambios.append(tk.Label(frame, text= "Max Intercambios"))
        self.__labelNroIntercambios[i].place(relx=0.2, rely = 0.20)
        self.__nroIntercambios.append(tk.IntVar())
        self.__spinboxNroIntercambios.append(tk.Spinbox(frame, from_ = 1, to = 2, width = 5, state = "disabled", textvariable = self.__nroIntercambios[i]))
        self.__spinboxNroIntercambios[i].place(relx=0.45, rely=0.20)
        
        self.__combo2list=['2-opt', '3-opt']
        self.__eOpt.append(tk.StringVar())
        self.__comboOpt.append(ttk.Combobox(frame, textvariable=self.__eOpt, values=self.__combo2list, width = 5, state = "disabled"))
        self.__comboOpt[i].place(relx=0.60, rely=0.20)      
        
        #Tenure ADD
        self.__labelTenureADD.append(tk.Label(frame, text = "Tenure ADD"))
        self.__labelTenureADD[i].place(relx=0.2, rely=0.27)
        self.__boxADD.append(tk.IntVar())
        self.__spinboxADD.append(tk.Spinbox(frame, from_ = 1, to = 100, width = 5, state = "disabled", textvariable = self.__boxADD))
        self.__spinboxADD[i].place(relx=0.35, rely=0.27)

        #Tenure DROP
        self.__labelTenureDROP.append(tk.Label(frame, text = "Tenure DROP"))
        self.__labelTenureDROP[i].place(relx=0.50, rely=0.27)
        self.__boxDROP.append(tk.IntVar())
        self.__spinboxDROP.append(tk.Spinbox(frame, from_ = 1, to = 100, width = 5, state = "disabled", textvariable = self.__boxDROP))
        self.__spinboxDROP[i].place(relx=0.70, rely=0.27)
        
        #Condicion de parada
        self.__labelTiempoEjecucion.append(tk.Label(frame, text = "Tiempo de ejecución"))
        self.__labelTiempoEjecucion[i].place(relx=0.2, rely=0.4)
        self.__eTime.append(tk.StringVar())
        self.__entryTiempoEjecucion.append(tk.Entry(frame, textvariable = self.__eTime, width = 25, state = "disabled"))
        self.__entryTiempoEjecucion[i].place(relx=0.5, rely=0.4,relwidth=0.20)
        self.__labelTEmin.append(tk.Label(frame, text = "(min)"))
        self.__labelTEmin[i].place(relx=0.75, rely=0.4)

        #Cantidad de Veces a resolver 
        self.__labelCantidadResolver.append(tk.Label(frame, text= "Cantidad de Veces a resolver"))
        self.__labelCantidadResolver[i].place(relx=0.3, rely = 0.5)
        self.__cantidadResolver.append(tk.IntVar())
        self.__spinboxCantidadResolver.append(tk.Spinbox(frame, from_ = 1, to = 100, width = 5, state = "readonly", textvariable = self.__cantidadResolver[i]))
        self.__spinboxCantidadResolver[i].place(relx=0.7, rely=0.50)

        #Mostrar datos
        self.__areaDatos.append(tk.Text(frame, state ="disabled"))
        self.__areaDatos[i].place(relx=0.2, rely=0.6, relwidth=0.6, relheight=0.4)

    def cargarDatos(self):
        for i in range(0,len(self.__listaInstancias)):
            self.__nombreArchivo = self.__listaInstancias[i]
            print("Se resolverá "+ str(self.__cantidadResolver[i].get())+" veces "+ self.__nombreArchivo)
            for j in range(0,self.__cantidadResolver[i].get()):
                print("RESOLVIENDO ------------------> "+str(self.__nombreArchivo))
                self.__cvrp = CVRP(self.__matrizDistancias[i], self.__demanda[i], self.__nroVehiculos[i], self.__capacidad[i],
                        self.__nombreArchivo+"_"+str(self.__eTime[i].get())+"min", self.__eSolInicial[i].get(),  self.__nroIntercambios[i].get(),
                        self.__eOpt[i].get(), self.__boxADD[i].get(), self.__boxDROP[i].get(), self.__eTime[i].get(), self.__optimo[i])
                j

    def calcularDatos(self,i):
        if(self.__openFolder):
            self.__labelEstadoGrafo[i].configure(text = "Grafos Cargados")
        else:
            self.__labelEstadoGrafo[i].configure(text = "Grafo Cargado")
            
        self.__labelRecomienda.append(tk.Label(text = "Se recomienda los siguientes valores..."))
        self.__labelRecomienda[i].place(relx=0.3,rely=0.05)        
        
        tenureADD = int(len(self.__matrizDistancias[i])*0.1)
        tenureDROP = int(len(self.__matrizDistancias[i])*0.1)+1

        self.__combo1[i].configure(state = "readonly")
        self.__combo1[i].set('Vecino mas cercano')
        self.__comboOpt[i].configure(state = "readonly")
        self.__comboOpt[i].set('2-opt')

        #Nro intercambios
        cantIntercambios = 2

        self.__nroIntercambios[i].set(cantIntercambios)
        self.__spinboxNroIntercambios[i].configure(state = "readonly", textvariable = self.__nroIntercambios[i])

        #Tenure ADD y DROP
        self.__boxADD[i].set(tenureADD)
        self.__spinboxADD[i].configure(state = "readonly", textvariable=self.__boxADD[i])

        self.__boxDROP[i].set(tenureDROP)
        self.__spinboxDROP[i].configure(state = "readonly", textvariable=self.__boxDROP[i])
        
        self.__label_RecomiendacTiempo.append(tk.Label(text = "Se recomienda como minimo"))
        self.__label_RecomiendacTiempo[i].place(relx=0.4, rely=0.35)
        self.__eTime[i].set(25.0)
        self.__entryTiempoEjecucion[i].configure(state = "normal", textvariable = self.__eTime[i])
        return 

    def listToString(self, s): 
        str1 = ""  
        for ele in s:  
            str1 += ele   

        return str1

    def tabs(self, instancias):
        for i in range(0,len(instancias)):
            print(instancias[i])
            self.__frames.append(tk.Frame(self)) 
            self.menuConfig(self.__frames[i],i)
            self.__tabs.add(child=self.__frames[i],text=instancias[i])
            self.cargarDesdeFile(self.__mypath+"/"+self.__listaInstancias[i])
            self.calcularDatos(i)
            
        self.__tabs.pack(expand=1, fill="both")
        self.__Ok = tk.Button(self, text = "Calcular", command=self.cargarDatos, width = 10, height =2, state="normal")
        self.__Ok.pack(after=self.__tabs)

    def openFolder(self):
        self.__mypath = tk.filedialog.askdirectory(initialdir = ".", title='Seleccione directorio con instancias')
        self.__listaInstancias = [f for f in listdir(self.__mypath) if isfile(join(self.__mypath, f))]
        self.__openFolder = True
        print(self.__listaInstancias)
        self.tabs(self.__listaInstancias)
        self.__nombreArchivo = os.path.splitext(self.__listaInstancias[0])[0]
        print("Primera instancia: "+str(self.__nombreArchivo))
        
    def openFile(self):
        self.__listaInstancias = tk.filedialog.askopenfilenames(initialdir = ".",title = "Seleccione Intancia/s CVRP",filetypes = (("all files","*.*"),("VRP files","*.vrp")))
        self.__listaInstancias = list(self.__listaInstancias)
        self.__mypath = ntpath.split(self.__listaInstancias[0])[0]
        self.__listaInstancias = [ntpath.split(f)[1] for f in self.__listaInstancias]
        self.tabs(self.__listaInstancias)    
        self.__nombreArchivo = os.path.splitext(os.path.basename(self.__listaInstancias[0]))[0]
    
    #Obtengo los datos de mis archivos .vrp
    def cargarDesdeFile(self,pathArchivo):
        #+-+-+-+-+-Para cargar la distancias+-+-+-+-+-+-+-+-
        archivo = open(pathArchivo,"r")
        lineas = archivo.readlines()
        
        #Busco la posiciones de...
        indSeccionCoord = lineas.index("NODE_COORD_SECTION \n")
        lineaEOF = lineas.index("DEMAND_SECTION \n")
        
        #Linea optimo y nro de vehiculos
        lineaOptimo = [x for x in lineas[0:indSeccionCoord] if re.search(r"COMMENT+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaOptimo)
        
        self.__nroVehiculos.append(int(float(parametros[0])))
        self.__optimo.append(float(parametros[1]))

        #Cargo la capacidad
        lineaCapacidad = [x for x in lineas[0:indSeccionCoord] if re.search(r"CAPACITY+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaCapacidad)

        self.__capacidad.append(float(parametros[0]))
        print("Capacidad: "+str(self.__capacidad))

        #Lista donde irán las coordenadas (vertice, x, y)
        coordenadas = []
        #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
        for i in range(indSeccionCoord+1, lineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split(" ") #Divide la línea por " " 
            if(splitLinea[0]==""):
                coordenadas.append([splitLinea[1],splitLinea[2],splitLinea[3]]) #[[v1,x1,y1], [v2,x2,y2], ...]
            else:
                coordenadas.append([splitLinea[0],splitLinea[1],splitLinea[2]]) #[[v1,x1,y1], [v2,x2,y2], ...]
        self.cargaMatrizDistancias(coordenadas)
        
        #+-+-+-+-+-+-+-Para cargar la demanda+-+-+-+-+-+-+-
        seccionDemanda = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEMAND_SECTION+",x)][0]
        indSeccionDemanda = lineas.index(seccionDemanda)
        
        seccionEOF = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEPOT_SECTION+",x)][0]
        indLineaEOF = lineas.index(seccionEOF)

        demanda = []
        for i in range(indSeccionDemanda+1, indLineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split(" ") #Divide la línea por " " 
            demanda.append(float(splitLinea[1]))

        self.__demanda.append(demanda)
    
    def cargaMatrizDistancias(self, coordenadas):
        matriz = []
        #Arma la matriz de distancias. Calculo la distancia euclidea
        for coordRow in coordenadas:
            fila = []            
            for coordCol in coordenadas:
                x1 = float(coordRow[1])
                y1 = float(coordRow[2])
                x2 = float(coordCol[1])
                y2 = float(coordCol[2])
                dist = self.distancia(x1,y1,x2,y2)
                
                #Para el primer caso. Calculando la distancia euclidea entre si mismo da 0
                if(dist == 0):
                    dist = 999999999999 #El modelo no debería tener en cuenta a las diagonal, pero por las dudas
                fila.append(dist)

            #print("Fila: "+str(fila))    
            matriz.append(fila)
        self.__matrizDistancias.append(matriz)

    def distancia(self, x1,y1,x2,y2):
        return round(math.sqrt((x1-x2)**2+(y1-y2)**2),3)
    
ventana = Ventana()
ventana.mainloop()