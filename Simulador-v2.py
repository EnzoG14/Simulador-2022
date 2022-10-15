#Simulador de Asignación de Memoria y Planificación de procesos

import pandas as pd

#Objetos
class proceso:
    def __init__(self, id, ti, ta,tamanho,):     #Constructor ej: proceso(1,0,0,5)
        self.id = id                            #id del proceso
        self.ti = ti                            #tiempo de irrupcion (tiempo que dura en el procesador)
        self.ta = ta                            #tiempo de arribo (tiempo en el que llega a la cola de nuevos)
        self.tamanho = tamanho                  #tamaño del proceso en kb
        #self.estado = estado                    #estado del proceso   | 0 = nuevo | 1 = listo | 2 = ejecutando | 3 = suspendido | 4 = terminado | 5 = bloqueado |
    def __str__(self):
        return f"{self.id} {self.ti} {self.ta} {self.tamanho}"

    def setEstado(self, estado):
        self.estado = estado

class particion:                          
    def __init__(self, id, tamanho, direccion):
        self.id = id                            
        self.tamanho = tamanho
        self.estado = "libre"
        self.proceso = None
        self.fragInterna = 0 
        self.direccion = direccion
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
        self.colaBloqueados = []                                    #Cola de procesos cuyo tamaño jamas permitirá su carga a memoria  CAMBIAR NOMBRE LOS PROCESOS BLOQUEADOS SN OTRA COSA
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
        self.memoria.append(particion(1, 75, 100000))                                                  #Particion 0 de 250 kb para procesos grandes
        self.memoria.append(particion(2, 25, 350000))                                                  #Particion 1 de 120 kb para procesos medianos
        self.memoria.append(particion(3, 10, 410000))                                                   #Particion 2 de 60 kb para procesos pequeños
    
    def setProcesos(self):                                                                                                  #Cargamos todos los procesos en una lista auxiliar y los ordenamos por tiempo de arribo y tiempo de irrupcion
        df = pd.read_csv('./procesos2.csv',index_col=0,header=0)      #Lectura de archivo csv con los procesos  #CAMBIAR RUTA Y HACERLO GENERAL
        df=df.sort_values(['tiempo de arribo','tiempo de irrupcion'])  
        df=pd.DataFrame(df)
        for i in range(len(df)):
            self.procesos.append(proceso(df.index[i],df.iat[i,0],df.iat[i,1],df.iat[i,2]))
            print (self.procesos[i])

    def cargaNuevos(self):
        for i in range(len(self.procesos)):                   
                if (self.procesos[i].ta == self.tiempoActual):
                    if (self.procesos[i].tamanho <= 250):
                        self.colaNuevos.append(self.procesos[i])
                    else:
                        self.colaBloqueados.append(self.procesos[i])

    def ordenSJF(self):
        if len(self.controlMultiprogramacion) > 0:
            aux = self.controlMultiprogramacion.pop(0)                                  #Sacamos el primer proceso de la cola de control de multiprogramacion
            self.controlMultiprogramacion.sort(key=lambda x: x.ti, reverse=False)       #Ordenamos la cola de control de multiprogramacion por tiempo de irrupcion
            self.controlMultiprogramacion.insert(0,aux)                                 #Insertamos el proceso que sacamos al principio de la cola

    def getParticion(self, proceso):
        for i in range(len(self.memoria)):
            if (self.memoria[i].proceso == proceso):
                return i

    def cargaControlMultiprogramacion(self):    #Carga de CM
        for i in range(len(self.colaNuevos)):
            if len(self.controlMultiprogramacion) < 5:
                self.controlMultiprogramacion.append(self.colaNuevos.pop(0))
        self.ordenSJF()
    
    def estadoMemoria(self):
        i=0
        for i in range(len(self.memoria)):
            if (self.memoria[i].estado == "libre"):
                i+=1
        return i

    def cargaMemoria(self): #Worst Fit
        if self.estadoMemoria() != 0:                                                    #estadoMemoria() devuelve la cantidad de particiones libres
            for i in range(len(self.controlMultiprogramacion[:3])):
                if self.controlMultiprogramacion[i].id not in [particion.proceso.id for particion in self.memoria if particion.proceso != None]:                    #Si el proceso no está en memoria
                    for j in range(len(self.memoria)):
                        if (self.controlMultiprogramacion[i].tamanho <= self.memoria[j].tamanho and self.memoria[j].estado == "libre"):
                            self.memoria[j].setParticion(self.controlMultiprogramacion[i], "ocupado", self.memoria[j].tamanho - self.controlMultiprogramacion[i].tamanho)
                            break
                                     
    def cargaProcesador(self):
        if len(self.controlMultiprogramacion) > 0:
            if (self.procesador.proceso == None and self.controlMultiprogramacion[0].id in [particion.proceso.id for particion in self.memoria if particion.proceso != None] ):    #[particion.proceso.id for particion in self.memoria  particion != Nonetype]                                                                      #Si el procesador está libre y el proceso en la primera posición de la cola de control de multiprogramacion está en memoria                                          
                self.procesador.setProcesador(self.controlMultiprogramacion[0], self.controlMultiprogramacion[0].ti, self.getParticion(self.controlMultiprogramacion[0]))       #Cargamos el proceso en el procesador

    def cargaSuspendidos(self):
        for i in range(len(self.controlMultiprogramacion)):
                if ((self.controlMultiprogramacion[i].id not in [particion.proceso.id for particion in self.memoria if particion.proceso != None]) and (self.controlMultiprogramacion[i].id not in [proceso.id for proceso in self.colaSuspendidos])):  # [proceso.id for proceso in self.colaSuspendidos]                                                                                            #Cargamos en la cola de suspendidos todos los procesos que no esten en memoria, sin tener en cuenta el orden de la CCM
                    self.colaSuspendidos.append(self.controlMultiprogramacion[i])

    def reordenarMemoria(self):
        #Tenemos que controlar que despues de ordenar todos los proceso a partir del segundo esten o en memoria o suspendidos 
        #Los primeros 3 pueden estar en memoria pero no es necesario que deban hacerlo
        #Excepto el primer proceso el resto puede estar suspendido 
        for i in range(len(self.memoria)):  
            if (self.memoria[i].proceso not in [proceso.id for proceso in self.controlMultiprogramacion[:3]])and (self.memoria[i].proceso != self.procesador.proceso):  
                #[proceso.id for particion in self.controlMultiprogramacion[:3]]   
                self.memoria[i].setParticion(None,"libre",0)                                                                                            
       #Limpiamos la cola de suspendidos exceptuando las particiones que no es necesario mover a la cola de listos

    def reordenarSuspendidos(self):
        #Tenemos que controlar que despues de ordenada y cargada la memoria los procesos que no se encuentren en la misma se encuentren suspendidos 
        """for i in range(len(self.colaSuspendidos)):
            if (self.colaSuspendidos[i].id in [particion.proceso.id for particion in self.memoria if particion.proceso != None]):
                self.colaSuspendidos.pop(i)"""                                                                                                         #Limpiamos la cola de suspendidos exceptuando las particiones que no es necesario mover a la cola de listos
        for proceso in self.colaSuspendidos:
            if (proceso.id in [particion.proceso.id for particion in self.memoria if particion.proceso != None]):
                self.colaSuspendidos.remove(proceso)

    def controlProcesador(self):                            #Actualizamos el tiempo restante del proceso que se encuentra en el procesador y controlamos si ya terminó de ejecutarse
        if (self.procesador.proceso != None):
            self.procesador.tiRestante -= 1 
            if (self.procesador.tiRestante == 0):
                for i in range(len(self.memoria)):
                    if self.memoria[i].proceso == self.procesador.proceso:
                        self.memoria[i].setParticion(None,"libre",0)                            #Eliminamos el proceso de la memoria
                self.controlMultiprogramacion.remove(self.procesador.proceso)                   #Eliminamos el proceso de la cola de control de multiprogramacion
                self.colaTerminados.append(self.procesador.proceso.id)                          #Agregamos el id del proceso a la lista de terminados
                self.procesador.setProcesador(None,-1,None)                                     #Eliminamos el proceso del procesador
            
    def printMemoria(self):
        print("Tiempo actual: ", self.tiempoActual)
        if (self.procesador.proceso == None):
            print("Estado del procesador: NULL (libre)")
        else:
            print("Estado del procesador: Proceso ", self.procesador.proceso.id, " (tiempo restante: ", self.procesador.tiRestante, ")")
        print("Tabla de Particiones")
        # Imprimir la tabla de particiones con tabulaciones para hacerla legible
        print ("| {:<15} | {:<15} | {:<15} | {:<15} | {:<15} |".format('Id Particion','Direccion','Tamaño','Id Proceso','Fragmentación Interna'))
        print ("| {:<15} | {:<15} | {:<15} | {:<15} | {:<15} |".format('0','0','100','SO','-'))
        for i in range(len(self.memoria)):
            if (self.memoria[i].proceso == None):
                print ("| {:<15} | {:<15} | {:<15} | {:<15} | {:<15} |".format(self.memoria[i].id,self.memoria[i].direccion,self.memoria[i].tamanho,'NULL','NULL'))
            else:
                print ("| {:<15} | {:<15} | {:<15} | {:<15} | {:<15} |".format(self.memoria[i].id, self.memoria[i].direccion, self.memoria[i].tamanho, self.memoria[i].proceso.id, self.memoria[i].fragInterna))
        print("Cola de listos: ", [proceso.id for proceso in self.controlMultiprogramacion])  #[proceso.id for proceso in self.controlMultiprogramacion]
        print("Cola de suspendidos: ", [proceso.id for proceso in self.colaSuspendidos])    #[proceso.id for proceso in self.colaSuspendidos]
        print("Cola de nuevos: ", [proceso.id for proceso in self.colaNuevos])             #[proceso.id for proceso in self.colaNuevos]

    def cicloPrincipal(self):
        self.setParticiones()
        self.setProcesos() 
        self.cargaNuevos()
        self.cargaControlMultiprogramacion()
        # self.limpiar()  En el primer ciclo no seria necesario
        self.cargaMemoria()
        self.cargaProcesador()
        self.cargaSuspendidos()
        self.printMemoria()
        self.tiempoActual += 1
        # while (len(self.colaTerminados)+len(self.colaBloqueados)) != (len(self.procesos)):
        for i in range(50):
            self.controlProcesador()
            self.cargaNuevos()
            self.cargaControlMultiprogramacion()
            self.reordenarMemoria() 
            self.cargaMemoria()
            self.cargaProcesador()
            self.reordenarSuspendidos()
            self.cargaSuspendidos()
            self.printMemoria()
            self.tiempoActual += 1




"""CN = 6
CS = 4 5
CM = 2 3 4 5 """
#Memoria: 1 | 2 | 3
#Procesador: 1
#Procesos: 1 2 3 4 5 6

"""
setProcesos()
self.tiempoActual = 0
While (len(self.colaTerminados) != len(self.procesos)):
    controlProcesador()
    cargaNuevos()
    cargaControlMultiprogramacion()
    limpiar()
    cargaMemoria()
    cargaProcesador()
    cargaSuspendidos()
    self.tiempoActual += 1  
    
    """



"""
OUTPUT DE EJEMPLO:
Tiempo actual: x
Estado del procesador: NULL (libre) |  PROCESO x (tiempo restante: x)
Tabla de Particiones
Id Particion| Direccion | Tamaño | Id Proceso | Fragmentación Interna
1           |           | 10     | 1          | 0
Cola de listos: 
Cola de suspendidos:
Cola de nuevos: 
"""



Memoria=memoria()
Memoria.cicloPrincipal()







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
"""        if (self.procesador.proceso == None):                                                   #Si el procesador está libre                              
            for j in range(len(self.controlMultiprogramacion)):                                      #Chequeamos en orden todos los procesos de la CCM ya que no siempre el primero va a estar cargado en memoria para ejecutarse
                    if (self.procesador.proceso == None and self.controlMultiprogramacion[j] in self.memoria):
                        self.procesador.setProcesador(self.controlMultiprogramacion[j], self.controlMultiprogramacion[j].ti, i)"""
"""     def limpiar(self):
        for i in range(len(self.memoria)):
            if (self.memoria[i].proceso not in self.controlMultiprogramacion[:3])and (self.memoria[i].proceso != self.procesador.proceso):       
                self.memoria[i].setParticion(None,"libre",0)                                        #Limpiamos la memoria exceptuando la partición del proceso que se esté ejecutando (en caso de haberlo) y las particiones que no es necesario mover a la cola de suspendidos
        
        for i in range((len(self.controlMultiprogramacion))-3):
            if (self.colaSuspendidos[i] not in self.controlMultiprogramacion[3:]):
                self.colaSuspendidos.pop(i)                                                         #Limpiamos la cola de suspendidos exceptuando las particiones que no es necesario mover a la cola de listos
"""