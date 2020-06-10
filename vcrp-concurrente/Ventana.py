import tkinter as tk
import re
import math
import time
from TSP import TSP
from Table import Table
from Vertice import Vertice
import tkinter.filedialog
import os
from tkinter import ttk
from os import listdir
from os.path import isfile, join


class Ventana(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("370x410+350+150")
        self.title("TSP Solver con Tabu Search")
        self.__matrizDistancias=[]
        self.__nro = 0
        self.__openFolder = False

        self.barraMenus()
        self.menuConfig()
    
    def barraMenus(self):
        self.__menu = tk.Menu(self)
        self.__menuArchivo = tk.Menu(self.__menu)
        self.__menuArchivo.add_command(label="New File", command=self.newFile)
        self.__menuArchivo.add_separator()
        self.__menuArchivo.add_command(label="Open File", command=self.openFile)
        self.__menu.add_cascade(label="File", menu=self.__menuArchivo)
        self.__menuArchivo.add_command(label="Open Folder", command=self.openFolder)

        self.config(menu = self.__menu)
    
    def menuConfig(self):
        self.__labelEstadoGrafo = tk.Label(self, text = "No se ha cargado Grafo")
        self.__labelEstadoGrafo.place(x=120,y=0)
        
        #Solucion inicial
        self.__labelSolInicial = tk.Label(self, text = "Solucion inicial")
        self.__labelSolInicial.place(x=30, y=50)
        
        self.__combo1list=['Vecino mas cercano', 'Al azar']
        self.__eSolInicial = tk.StringVar()
        self.__combo1=ttk.Combobox(self, textvariable=self.__eSolInicial, values=self.__combo1list, width = 29, state = "disabled")
        self.__combo1.place(x=130, y=50)
        
        #Nro de intercambios
        self.__labelNroIntercambios = tk.Label(self, text= "Max Intercambios")
        self.__labelNroIntercambios.place(x=25, y = 90)
        self.__nroIntercambios = tk.IntVar()
        self.__spinboxNroIntercambios = tk.Spinbox(self, from_ = 1, to = 3, width = 5, state = "disabled", textvariable = self.__nroIntercambios)
        self.__spinboxNroIntercambios.place(x=130, y=90)
        
        self.__combo2list=['2-opt', '3-opt']
        self.__eOpt = tk.StringVar()
        self.__comboOpt=ttk.Combobox(self, textvariable=self.__eOpt, values=self.__combo2list, width = 5, state = "disabled")
        self.__comboOpt.place(x=180, y=88)        
        

        #Tenure ADD
        self.__labelTenureADD = tk.Label(self, text = "Tenure ADD")
        self.__labelTenureADD.place(x=55, y=130)
        self.__boxADD = tk.IntVar()
        self.__spinboxADD = tk.Spinbox(self, from_ = 1, to = 100, width = 5, state = "disabled", textvariable = self.__boxADD)
        self.__spinboxADD.place(x=130, y=130)

        #Tenure DROP
        self.__labelTenureDROP = tk.Label(self, text = "Tenure DROP")
        self.__labelTenureDROP.place(x=205, y=130)
        self.__boxDROP = tk.IntVar()
        self.__spinboxDROP = tk.Spinbox(self, from_ = 1, to = 100, width = 5, state = "disabled", textvariable = self.__boxDROP)
        self.__spinboxDROP.place(x=280, y=130)
        
        #Condicion de parada
        self.__labelTiempoEjecucion = tk.Label(self, text = "Tiempo de ejecución")
        self.__labelTiempoEjecucion.place(x=10, y=180)
        self.__eTime = tk.StringVar()
        self.__entryTiempoEjecucion = tk.Entry(self, textvariable = self.__eTime, width = 25, state = "disabled")
        self.__entryTiempoEjecucion.place(x=130, y=180)
        self.__labelTEmin = tk.Label(self, text = "(min)")
        self.__labelTEmin.place(x=290, y=180)

        #Mostrar datos
        self.__areaDatos = tk.Text(self, height = 9, width = 41, state ="disabled")
        self.__areaDatos.place(x=17, y=220)

        #Calcular
        self.__Ok = tk.Button(self, text = "Calcular", command=self.cargarDatos, width = 7, state="disabled")
        self.__Ok.place(x=290, y=375)

    def cargarDatos(self):
        if(self.__eTime.get()!=''):
            self.__tsp = TSP(self.__matrizDistancias, self.__nombreArchivo+"_"+str(self.__eTime.get())+"min", self.__eSolInicial.get(), self.__nroIntercambios.get(),
            self.__eOpt.get(), self.__boxADD.get(), self.__boxDROP.get(), self.__eTime.get(), self.__optimo)
            
            if(self.__openFolder):
                for inst in self.__listaInstancias[1:]:
                    self.cargarDesdeEUC_2D(self.__mypath+"/"+inst)
                    self.__nombreArchivo = os.path.splitext(inst)[0]
                    print("Siguiente instancia: "+str(self.__nombreArchivo))
                    time_aux = self.__eTime.get()
                    self.calcularDatos()
                    self.__eTime.set(time_aux)
                    self.__tsp = TSP(self.__matrizDistancias, self.__nombreArchivo+"_"+str(self.__eTime.get())+"min", self.__eSolInicial.get(), self.__nroIntercambios.get(),
                    self.__eOpt.get(), self.__boxADD.get(), self.__boxDROP.get(), self.__eTime.get(), self.__optimo)

        else:
            print("No se permite valores vacios")

    def calcularDatos(self):
        if(self.__openFolder):
            self.__labelEstadoGrafo.configure(text = "Grafos Cargados")
        else:
            self.__labelEstadoGrafo.configure(text = "Grafo Cargado")
            
        self.__labelRecomienda = tk.Label(text = "Se recomienda los siguientes valores...")
        self.__labelRecomienda.place(x=70,y=20)        
        
        tenureADD = int(len(self.__matrizDistancias)*0.1)
        tenureDROP = int(len(self.__matrizDistancias)*0.1)+1

        self.__Ok.configure(state="normal")
        self.__combo1.configure(state = "readonly")
        self.__combo1.set('Vecino mas cercano')
        self.__comboOpt.configure(state = "readonly")
        self.__comboOpt.set('2-opt')

        #Nro intercambios
        cantIntercambios = 2

        self.__nroIntercambios.set(cantIntercambios)
        self.__spinboxNroIntercambios.configure(state = "readonly", textvariable = self.__nroIntercambios)

        #Tenure ADD y DROP
        self.__boxADD.set(tenureADD)
        self.__spinboxADD.configure(state = "readonly", textvariable=self.__boxADD)

        self.__boxDROP.set(tenureDROP)
        self.__spinboxDROP.configure(state = "readonly", textvariable=self.__boxDROP)
        
        self.__label_RecomiendacTiempo = tk.Label(text = "Se recomienda como minimo")
        self.__label_RecomiendacTiempo.place(x=100, y=155)
        self.__eTime.set(25.0)
        self.__entryTiempoEjecucion.configure(state = "normal", textvariable = self.__eTime)

    def listToString(self, s): 
        str1 = ""  
        for ele in s:  
            str1 += ele   

        return str1

    def openFolder(self):
        self.__mypath = tk.filedialog.askdirectory(initialdir = ".", title='Seleccione directorio con instancias')
        self.__listaInstancias = [f for f in listdir(self.__mypath) if isfile(join(self.__mypath, f))]
        self.__openFolder = True
        
        self.cargarDesdeEUC_2D(self.__mypath+"/"+self.__listaInstancias[0])
        self.__nombreArchivo = os.path.splitext(self.__listaInstancias[0])[0]
        print("Primera instancia: "+str(self.__nombreArchivo))

        self.calcularDatos()

    def openFile(self):
        nombreArchivo  = tk.filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("all files","*.*"),("jpeg files","*.jpg")))
        self.cargarDesdeEUC_2D(nombreArchivo)
        self.__nombreArchivo = os.path.splitext(os.path.basename(nombreArchivo))[0]
        self.calcularDatos()

    #Convierto mi archivo EUC_2D en una matriz en la cual pueda trabajar
    def cargarDesdeEUC_2D(self,pathArchivo):
        archivo = open(pathArchivo,"r")
        lineas = archivo.readlines()
        #Busco la posiciones de..
        indSeccionCoord = lineas.index("NODE_COORD_SECTION\n")
        lineaEOF = lineas.index("EOF\n")
        
        lineaOptimo = [x for x in lineas[0:indSeccionCoord] if re.findall(r"OPTIMO:[\S 0-9]+",x)][0]
        self.__optimo = re.findall(r"[0-9]+",lineaOptimo)[0]
        self.__optimo = float(self.__optimo)
        print(self.__optimo)
        #Lista donde irán las coordenadas (vertice, x, y)
        coordenadas = []
        #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
        for i in range(indSeccionCoord+1, lineaEOF):
            textoLinea = lineas[i]  
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split(" ") #Divide la línea por " " 
            coordenadas.append([splitLinea[0],splitLinea[1],splitLinea[2]]) #[[v1,x1,y1], [v2,x2,y2], ...]
                
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
        self.__matrizDistancias =  matriz

    def distancia(self, x1,y1,x2,y2):
        return round(math.sqrt((x1-x2)**2+(y1-y2)**2),3)
   
    #Cargo una matriz de forma manual. Ingreso el nro de vertices y verifico
    def newFile(self):
        t=tk.Toplevel()
        t.geometry("400x100+350+190")

        label1= tk.Label(t, text="Cantidad de vertices:")
        label1.grid(row=0)
        
        nroVertices = tk.StringVar()
        entry1= tk.Entry(t, textvariable=nroVertices)
        entry1.grid(row=0, column=1)
        
        #Verifico que sea un valor correcto
        def verificar():
            label2= tk.Label(t, text="Debe ser entero mayor que 0")
            try:
                cant = nroVertices.get()
                cant = int(cant)
                #print(cant)
                if(cant is None or cant<=0):
                    label2.grid(row=1,column=0)
                else:
                    t.destroy()
                    self._nroVertices=cant+1 #Defino la cantidad ingresada +1. Para los labels q indican el nro de filas y columnas
                    self.newFile2()
            except ValueError:
                    label2.grid(row=1,column=1)

        button1= tk.Button(t,text='Aceptar', command=verificar)
        button1.grid(row=0,column=2, padx=4, pady=4)

        label = tk.Label(t, text="Nueva ventana")
        label.pack(side="top", fill="both")

    #Cargo los valores de la matriz
    def newFile2(self):
        t=tk.Toplevel()
        self._entry={}
        
        #Cancelar: vuelvo a la primera pantalla
        def exit():
            t.destroy()
        
        def aceptar():
            self.get()
            t.destroy()

        btnCancelar = tk.Button(t, text = "Cancelar", width=7, command=exit)
        btnAceptar = tk.Button(t,text = "Aceptar", width=7,command=aceptar)

        # registra un comando para usar para la validacion
        vcmd = (self.register(self._validate), "%P")

        for r in range(0, self._nroVertices):
            for c in range(0, self._nroVertices):
                if(c!=0 and r!=0):
                    index = (r-1, c-1)
                    cell = tk.Entry(t, width=7, validate="key", validatecommand=vcmd)
                    cell.grid(row=r, column=c, stick="nsew")
                    if(c==r):
                        cell.insert(0,99999)
                    if(c<=r):
                        cell.configure(state='disabled')
                    self._entry[index]=cell
                elif(not(c==0 ^ r==0)):
                    label = tk.Label(t, text=r+c, width=7)
                    label.grid(row=r, column=c)

        btnAceptar.grid(row=self._nroVertices+1, column=self._nroVertices//2, columnspan=3)
        btnCancelar.grid(row=self._nroVertices+1, column=0, columnspan=3)

    #Valida que sea ingrese un numero de tipo float o entero
    def _validate(self, P):  

        if P.strip() == "":
            return True

        try:
            if(float(P)==P):
                print()
        except ValueError:
            self.bell()
            return False
        return True

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        matrizDist = []
        vertices = []

        for row in range(0, self._nroVertices-1):
            current_row = []
            for column in range(0, self._nroVertices-1):
                index = (row, column)
                if (column<row):
                    index = (column, row)
                    current_row.append(float((self._entry[index].get())))
                else:
                    current_row.append(float((self._entry[index].get())))
            matrizDist.append(current_row)
            vertices.append(row+1)
        
        print("Matriz distancias: ",self.__matrizDistancias)
        
        self.__matrizDistancias=matrizDist
        self.__nombreArchivo = "Matriz Nueva"
        self.calcularDatos()

    def getMatrizDistancas(self):
        return self.__matrizDistancias

    def verticesATupla(self, V):
        v = []
        for i in V:
            v.append(str(i.getValue()))
        return v

ventana = Ventana()
ventana.mainloop()