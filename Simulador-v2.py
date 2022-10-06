#Simulador de Asignación de Memoria y Planificación de procesos


import pandas as pd

#Objetos
class proceso:
    def __init__(self, id, ti, ta,tamanho):     #Constructor ej: proceso(1,0,0,5)
        self.id = id                            #id del proceso
        self.ti = ti                            #tiempo de irrupcion (tiempo que dura en el procesador)
        self.ta = ta                            #tiempo de arribo (tiempo en el que llega a la cola de nuevos)
        self.tamanho = tamanho                  #tamaño del proceso en kb
    def __str__(self):
        return f"{self.id} {self.ti} {self.ta} {self.tamanho}"


class particion:                          
    def __init__(self, id, tamanho):
        self.id = id                            
        self.tamanho = tamanho
        self.estado = "libre"
        self.proceso = None
        self.fragInterna = 0 
    def __str__(self): 
        return f"Particion: {self.id} Tamaño: {self.tamanho} Estado: {self.estado} Proceso: {self.proceso} Fragmentación interna: {self.fragInterna}"
    
    def setParticion(self, proceso, estado, fragInterna):
        self.proceso = proceso
        self.estado = estado
        self.fragInterna = fragInterna

class procesador:
    def __init__(self):
        self.particion = None
        self.proceso = None
        self.tiRestante = -1
    def __str__(self):
        return f"Particion: {self.particion} Proceso: {self.proceso} Tiempo de irrupcion: {self.tiRestante}"
    
    def setProcesador(self, proceso, tiRestante, particion):
        self.proceso = proceso
        self.tiRestante = tiRestante 
        self.particion = particion


class memoria:
    def __init__(self):
        self.memoria = []                                           #Lista de particiones
        self.procesos = []                                          #Lista de todos los procesos 
        self.colaNuevos = []                                        #Cola de nuevos
        self.colaListos = []                                        #Cola de listos
        self.colaSuspendidos = []                                   #Cola de suspendidos
        self.controlMultiprogramacion = []                          #Cola de control de multiprogramacion (maximo 5 procesos)
        self.colaTerminados = []                                    #Lista de procesos terminados
        self.tiempoActual = 0
        self.procesador = procesador()
        self.sumaTiempoIrrupcion = 0
    def __str__(self):
        return f"Memoria: {self.memoria}"

    def setParticiones(self): 
        self.memoria.append(particion(0, 250))                  #Particion 0 de 250 kb para procesos grandes
        self.memoria.append(particion(1, 120))                  #Particion 1 de 120 kb para procesos medianos
        self.memoria.append(particion(2, 60))                   #Particion 2 de 60 kb para procesos pequeños
    
    def setProcesos(self):                                      #Cargamos todos los procesos en una lista auxiliar y los ordenamos por tiempo de arribo y tiempo de irrupcion
        df = pd.read_csv('C:/Users/Asus/Desktop/Programacion/pitón/Simulador-2022/procesos2.csv',index_col=0,header=0)      #Lectura de archivo csv con los procesos  #CAMBIAR RUTA Y HACERLO GENERAL
        df=df.sort_values(['tiempo de arribo','tiempo de irrupcion'])  
        df=pd.DataFrame(df)
        for i in range(len(df)):
            self.procesos.append(proceso(df.index[i],df.iat[i,0],df.iat[i,1],df.iat[i,2]))
            print (self.procesos[i])

    def controlTiempo(self):
        
        pass

    def cargaNuevos(self):
        for i in range(len(self.procesos)):                   
                if self.procesos[i].ta == self.tiempoActual:
                    self.colaNuevos.append(self.procesos[i])

    def ordenSJF(self):
        self.controlMultiprogramacion.sort(key=lambda x: x.ti, reverse=False)       #Ordenamos la cola de control de multiprogramacion por tiempo de irrupcion                
        #self.colaListos.sort(key=lambda x: x.ti, reverse=False)                    #Ordenamos la cola de listos por tiempo de irrupcion
        #self.colaSuspendidos.sort(key=lambda x: x.ti, reverse=False)               #Ordenamos la cola de suspendidos por tiempo de irrupcion

    def cargaControlMultiprogramacion(self):
        #Carga de CM
        for i in range(len(self.colaNuevos)):
            if self.procesador.proceso != None:
                TotCM = 4
            else:
                TotCM = 5
            if len(self.controlMultiprogramacion) < TotCM:
                self.controlMultiprogramacion.append(self.colaNuevos[0])
                self.colaNuevos.pop(0)
            self.ordenSJF()    
            
        self.cargaMemoria()
        self.cargaProcesador()
        self.cargaSuspendidos()
    
    def cargaMemoria(self): #wor fi
        for j in range(len(self.controlMultiprogramacion)):
            for i in range(len(self.memoria)):
                if (self.memoria[i].estado == "libre") and (self.memoria[i].tamanho >= self.controlMultiprogramacion[j].tamanho):   #Buscamos una partición libre donde entre el proceso
                    fragInt =  self.memoria[i].tamanho - self.controlMultiprogramacion[j].tamanho           #Calculamos la fragmentación interna       
                    self.memoria[i].setParticion(self.controlMultiprogramacion[j],"ocupada",fragInt)     #Cargamos el proceso en la partición
                                          
    def cargaProcesador(self):
        for i in range(len(self.memoria)):
            if (self.controlMultiprogramacion[0].id in self.memoria[i].id and self.procesador.proceso == None ):
                self.procesador.setProcesador(self.controlMultiprogramacion[0], self.controlMultiprogramacion[0].ti, i)
                self.controlMultiprogramacion.pop(0)

    def cargaSuspendidos(self):
        if (len(self.controlMultiprogramacion) > 2):
            for i in range((len(self.controlMultiprogramacion))-2):
                    self.colaSuspendidos.append(self.controlMultiprogramacion[i+2])

    def limpiar(self):
        for i in range(len(self.memoria)):
            if self.memoria[i].proceso != self.procesador.proceso:
               self.memoria[i].setParticion(None,"libre",0)     #Limpiamos la memoria exceptuando la partición del proceso que se esté ejecutando (en caso de haberlo)
        self.colaSuspendidos.clear()                            #Limpiamos la cola de suspendidos

    def controlProcesador(self):                            #Controla si el proceso que se encuentra en el procesador ya terminó de ejecutarse
        if (self.procesador.tiRestante == 0):
            for i in range(len(self.memoria)):
                if self.memoria[i].proceso == self.procesador.proceso:
                    self.memoria[i].setParticion(None,"libre",0)    #Eliminamos el proceso de la memoria
            self.colaTerminados.append(self.procesador.proceso.id)  #Agregamos el id del proceso a la lista de terminados
            self.procesador.setProcesador(None,-1,None)             #Eliminamos el proceso del procesador
        

"""CN = 6
CS = 4 5
CM = 2 3 4 5 """
                                                # FALTA VER COMO CONTROLAMOS EL TIEMPO !
#Memoria: 1 | 2 | 3
#Procesador: 1
#Procesos: 1 2 3 4 5 6

"""controlProcesador()
cargaNuevos()
cargaControlMultiprogramacion()
limpiar()
cargaMemoria()
cargaProcesador()
cargaSuspendidos()"""







memoria=memoria()
memoria.setParticiones()
memoria.setProcesos()







        #     Funciones del control multiprogramacion
        #     Para agregar nuevos procesos a la cola de listos tiene que controlar que la sumatoria de la cola de listos + la cola de suspension 
        #     y un proceso mas en caso de estar ejecutando uno sea menor igual a 5.
        #     Poder mover un proceso de la cola de listos a la cola de suspension 
        #     Poder mover un proceso de la cola de suspension a la cola de listos
        #     Poder mover un proceso de listo a ejecucion
        #     Poder terminar un proceso luego de finalizada su ejecucion       


        
        # while (self.procesador.proceso == None) and ():
        #     if (self.controlMultiprogramacion[0] in self.colaListos):                            #Si el proceso a ejecutar está en la cola de listos:
        #         self.procesador.proceso == self.controlMultiprogramacion[0]
        #         self.colaListos.pop(0)                                                              #Cargamos el proceso al procesador y lo eliminamos de la cola de listos
        #     else:
        #         if (self.controlMultiprogramacion[0] in self.colaSuspendidos):                   #Si el proceso a ejecutar está en la cola de suspendidos:
        #             self.colaListos.append(self.colaSuspendidos[0])
        #             self.colaSuspendidos.pop(0)                                                     #Cargamos el proceso a la cola de listos y lo eliminamos de la cola de suspendidos
        #         else:
        #             self.colaSuspendidos.append(self.controlMultiprogramacion[0])                #Si el proceso a ejecutar NO está en la cola de suspendidos los cargamos en ella

        
        # if (len(self.controlMultiprogramacion) > 1):                                            #Cargamos / Actualizamos la cola de listos hasta tener máximo 2 procesos listos y 1 proceso ejecutandose
        #     for i in range(len(self.self.colaListos)):
        #         self.colaListos.pop(0)                                                              #Vaciamos la cola de Listos
        #     for i in range(len(self.controlMultiprogramacion)):
        #         if (i < 2):
        #             self.colaListos.append(self.controlMultiprogramacion[i+1])                      #Cargamos, en caso de que existan, el segundo y tercer proceso de menor tiempo de irrupción en la cola de listos

        # if (len(self.controlMultiprogramacion) > 3):                                            #Cargamos / Actualizamos la cola de suspendidos hasta tener máximo 2 procesos suspendidos, 2 procesos listos y 1 proceso ejecutandose
        #     for i in range(len(self.colaSuspendidos)):
        #         self.colaSuspendidos.pop(0)                                                         #Vaciamos la cola de Suspendidos
        #     for i in range(len(self.controlMultiprogramacion)):
        #             self.colaSuspendidos.append(self.controlMultiprogramacion[i+3])                 #Cargamos, en caso de que existan, el cuarto y quinto proceso de menor tiempo de irrupción en la cola de suspendidos
