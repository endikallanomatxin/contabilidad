from imports import *
from constantes import *
from funciones import *


class Asiento():
    '''Un asiento es la unidad que compone el libro diario'''

    def __init__(self, concepto:str, debe:dict, haber:dict, \
                       fecha=dt.date.today()):
        self.concepto = concepto
        self.debe     = debe  # Diccionario de pares cuenta:int : cantidad:float
        self.haber    = haber # Diccionario de pares cuenta:int : cantidad:float
        self.fecha    = fecha

    def tabla(self) -> pd.DataFrame:
        # Esta función convierte el asiento en una Pandas DataFrame

        d = np.full([len(self.debe)+len(self.haber),6], None)
        
        for i, codigo in enumerate(self.debe):
            d[i, 0] = self.fecha
            d[i, 1] = self.concepto
            d[i, 2] = codigo
            d[i, 3] = CUENTAS[codigo]
            d[i, 4] = self.debe[codigo]
        
        for i, codigo in enumerate(self.haber):
            i_ = len(self.debe)
            d[i_+i, 0] = self.fecha
            d[i_+i, 1] = self.concepto
            d[i_+i, 2] = codigo
            d[i_+i, 3] = CUENTAS[codigo]
            d[i_+i, 5] = self.haber[codigo]
        
        tabla = pd.DataFrame(d, columns=['Fecha', 'Concepto','Cuenta', 'Nombre de cuenta', 'Debe', 'Haber'])
        
        return tabla
    

    # funciones estéticas

    def __str__(self) -> str:
        representacion = f"\n\n'{self.fecha}'\t\t{self.concepto}\n"
        representacion += "-"*64 + "\n"
        
        columna_debe = ""
        for key in self.debe:
            columna_debe += f"\t{self.debe[key]}€\t{key}\t{CUENTAS[key]}\n"
        
        columna_haber = ""
        for key in self.haber:
            columna_haber += f"\t{self.haber[key]}€\t{key}\t{CUENTAS[key]}\n"
        
        representacion += "\nDEBE\n" +columna_debe + "\nHABER\n"+columna_haber+"\n"
        
        return representacion
    
    def __repr__(self) -> str:
        representacion = f"\n\n'{self.fecha}'\t\t{self.concepto}\n"
        representacion += "-"*64 + "\n"

        columna_debe = ""
        for key in self.debe:
            columna_debe += f"\t{self.debe[key]}€\t{key}\t{CUENTAS[key]}\n"
        
        columna_haber = ""
        for key in self.haber:
            columna_haber += f"\t{self.haber[key]}€\t{key}\t{CUENTAS[key]}\n"
        
        representacion += "\nDEBE\n"+columna_debe+"\nHABER\n"+columna_haber+"\n"

        return representacion
    


class LibroDiario(list):
    '''
    Un LibroDiario es una lista de asientos
    '''
    
    def tabla(self) -> pd.DataFrame:
        '''
        Devuelve un Pandas DataFrame con todos los asientos
        '''
        tabla = self[0].tabla()
        tabla.insert(0,'Número de asiento', [0]*(len(self[0].debe)+len(self[0].haber)))
        for numero_de_asiento, asiento in enumerate(self):
            if asiento != self[0]:
                asiento_tabla =  asiento.tabla()
                asiento_tabla.insert(0,'Número de asiento', [numero_de_asiento]*(len(asiento.debe)+len(asiento.haber)))
                tabla = pd.concat([tabla,asiento_tabla], ignore_index=True)

        # tabla = tabla.sort_values(by=['Fecha'], ignore_index = True)
        
        return tabla

    
    # Funciones para almacenamiento de información en .csv

    def save_csv(self, name) -> None:
        self.tabla().to_csv(name + '.csv', index=False)  
        pass
    
    def load_csv(self, name) -> None:

        df = pd.read_csv(name+'.csv')

        asiento_N = df['Número de asiento'].iloc[-1]

        for asiento_n in range(asiento_N+1):
            asiento_tabla = df[(df['Número de asiento'] == asiento_n)]

            concepto = asiento_tabla.iloc[0]['Concepto']
            fecha = asiento_tabla.iloc[0]['Fecha']


            debe = {}
            haber = {}

            for index, row in asiento_tabla.iterrows():
                cuenta = int(row['Cuenta'])
                if pd.isna(row['Haber']):
                    # Es de debe
                    debe[cuenta] = int(row['Debe'])
                if pd.isna(row['Debe']):
                    # Es de haber
                    haber[cuenta] = int(row['Haber'])

            asiento = Asiento(concepto, debe, haber, fecha)
            self.append(asiento)

    # modificación del método .append
    def append(self, asiento:Asiento) -> None:
        if not isinstance(asiento, Asiento):
            raise RuntimeError("Solo pueden añadirse asientos al libro diario")
        elif not(sum(asiento.debe.values()) == sum(asiento.haber.values())):
            raise RuntimeError("El asiento no es correcto")
        else:
            super().append(asiento)

    # función estética
    def mostrar_por_dias(self) -> None: 
        self.fechas = []
        for asiento in self:
            if not(asiento.fecha in self.fechas): self.fechas.append(asiento.fecha)
        
        for fecha in self.fechas:
            asientos_en_fecha = [asiento for asiento in self if asiento.fecha == fecha]
            tabla = asientos_en_fecha[0].tabla()
            
            for asiento in asientos_en_fecha:
                if asiento != asientos_en_fecha[0]:
                    tabla = pd.concat([tabla, asiento.tabla()], ignore_index=True)
            print(f"Asientos a {fecha}")
            display(tabla)



class LibroMayor(dict):
    '''
    Un LibroMayor es un diccionario que se crea a partir de un LibroDiario y
    tiene la estructura:
                                cuenta:int : d:DataFrame
    '''
    
    def __init__(self, libro_diario:LibroDiario):
        
        self.libro_diario = libro_diario  # libro diario del que se generó
        self.cuentas = []  # lista con todas las cuentas que aparecen, ordenadas
        self.totales = {}  # diccionario con los pares cuenta:int : total:float
        
        # Anadir todas las cuentas de todos los asientos del libro a la lista
        # self.cuentas y ordenarlas
        for asiento in self.libro_diario:
            for cuenta in asiento.debe:
                if not(cuenta in self.cuentas): self.cuentas.append(cuenta)
            for cuenta in asiento.haber:
                if not(cuenta in self.cuentas): self.cuentas.append(cuenta)
        self.cuentas.sort()
        
        # Generar el diccionario siguiendo el formato:
        # cuenta:int : d:DataFrame
        for cuenta in self.cuentas:
            d = libro_diario.tabla()
            d = d[d["Cuenta"] == cuenta]
            self[cuenta] = d

        self.calcular_totales()


    def calcular_totales(self) -> None:
        '''Calcular el diccionario self.totales'''

        for cuenta in self.cuentas:
            self.totales[cuenta] = self[cuenta]["Debe"]\
                .sum()-self[cuenta]["Haber"].sum()
            # La cuenta será positiva si es deudora y negativa si es acreedora.
    
    def sumar_cuentas(self,lista_de_cuentas:list):
        '''función que permite sumar cuentas de una lista de cuentas
        permite valores positivos y negativos'''
        total = 0
        for cuenta in lista_de_cuentas:
            if cuenta in self.totales:
                if cuenta>0: total+=self.totales[abs(cuenta)]
                if cuenta<0: total-=self.totales[abs(cuenta)]
        return total

    def __repr__(self):
        self.calcular_totales()
        for cuenta in self:
            print(f"\n{cuenta}:\t{CUENTAS[cuenta]}")
            display(self[cuenta][["Concepto", "Debe", "Haber"]])
            if self.totales[cuenta]>0:
                print(f"cuenta deudora: {self.totales[cuenta]}")
            if self.totales[cuenta]<0:
                print(f"cuenta acreedora: {-self.totales[cuenta]}")
                
        return " "



class Balance(dict):
    '''
    Un balance es un diccionario de diccionarios y almacena las cuentas de cada
    sección.
    La información tiene estructura de árbol.
    SECCION>SUBSECCIÓN>SUBSUBSECCIÓN>total:float
    En el último nivel se encuentra el total de la cuenta
    '''

    # (Queda un último nivel en el arbol de las secciones que he agrupado en sus
    # cuentas padres por simplicidad, queda por hacer).
    
    def __init__(self, libro:LibroMayor):
        
        # Se genera replicando el diccionario ejemplo BALANCE.
        self["Activo"]          = copy.deepcopy(BALANCE["Activo"])
        self["Patrimonio neto"] = copy.deepcopy(BALANCE["Patrimonio neto"])
        self["Pasivo"]          = copy.deepcopy(BALANCE["Pasivo"])
        
        # self.totales permite acceder a los totales de las secciones principales
        self.totales = {
            "Activo":0,
            "Patrimonio neto":0,
            "Pasivo":0
        }
        
        if libro is LibroDiario():
            libro = LibroMayor(libro)
        self.libro = libro # que debe ser de clase LibroMayor
        
        self.poner_a_cero()
        self.calcular_pyg()
        self.componer()
        self.calcular_totales()

    
    def componer(self) -> None:
        for cuenta in self.libro.totales:
            for seccion in BALANCE:
                for subseccion in BALANCE[seccion]:
                    for subsubseccion in BALANCE[seccion][subseccion]:
                        if cuenta in BALANCE[seccion][subseccion][subsubseccion]:
                            if seccion == "Activo":
                                total_de_la_cuenta_a_añadir_al_balance=self.libro.totales[cuenta]
                            elif (seccion == "Patrimonio neto") or (seccion == "Pasivo"):
                                total_de_la_cuenta_a_añadir_al_balance=-self.libro.totales[cuenta]
                            else:
                                total_de_la_cuenta_a_añadir_al_balance=0
                            self[seccion][subseccion][subsubseccion]+=total_de_la_cuenta_a_añadir_al_balance
                            
    #def componer_(self):
    #    # Que vaya leyendo el balance y si en la columna de cuentas aparece, que añada al lado el valor
    #    with open('cuentas.csv', mode='r') as f:
    #        data = csv.reader(f,delimiter=';')
    #        next(data)
    #        for row in data:
    #            cuentas = ast.literal_eval(row[])
                            
    def poner_a_cero(self) -> None:
        for seccion in self:
            for subseccion in self[seccion]:
                for subsubseccion in self[seccion][subseccion]:
                    self[seccion][subseccion][subsubseccion]=0
                    
    def calcular_totales(self) -> None:
        
        self.totales["Activo"]          = 0
        self.totales["Patrimonio neto"] = 0
        self.totales["Pasivo"]          = 0
        
        for seccion in BALANCE:
            for subseccion in BALANCE[seccion]:
                for subsubseccion in BALANCE[seccion][subseccion]:
                    if seccion == "Activo":
                        self.totales["Activo"] += self[seccion][subseccion][subsubseccion]
                    elif seccion == "Patrimonio neto":
                        self.totales["Patrimonio neto"] += self[seccion][subseccion][subsubseccion]
                    elif seccion == "Pasivo":
                        self.totales["Pasivo"] += self[seccion][subseccion][subsubseccion]
    
    def calcular_pyg(self):

        # Se genera replicando el diccionario PYG_GRUPOS
        self.pyg_grupos = copy.deepcopy(PYG_GRUPOS)
        
        # Calcular los valores del diccionario pyg_grupos y sustituir las listas
        for grupo in PYG_GRUPOS:
            if type(PYG_GRUPOS[grupo]) is list:
                self.pyg_grupos[grupo] = self.libro.sumar_cuentas(PYG_GRUPOS[grupo]) # La suma correspondiente
            else:
                total_grupo = 0
                for subgrupo in PYG_GRUPOS[grupo]:
                    if type(PYG_GRUPOS[grupo][subgrupo]) is list:
                        suma = self.libro.sumar_cuentas(PYG_GRUPOS[grupo][subgrupo]) # La suma correspondiente
                        self.pyg_grupos[grupo][subgrupo] = suma
                    else:
                        for subsubgrupo in PYG_GRUPOS[grupo][subgrupo]:
                            suma = self.libro.sumar_cuentas(PYG_GRUPOS[grupo][subgrupo][subsubgrupo]) # La suma correspondiente
                            self.pyg_grupos[grupo][subgrupo][subsubgrupo] = suma

        # Calcular el diccionario pyg
        self.pyg_totales = copy.deepcopy(PYG_TOTALES)
        for total in PYG_TOTALES:
            suma = 0
            for grupo_n in PYG_TOTALES[total]:
                suma += sumar_ultimos_niveles(list(self.pyg_grupos.values())[grupo_n-1])
            self.pyg_totales[total] = suma

        # Definir la cuenta de pérdidas y ganancias
        

    def __repr__(self):
        representacion = ""
        for seccion in self:
            representacion+=f"\n{seccion}"
            for subseccion in self[seccion]:
                representacion+=f"\n\t{subseccion}"
                for subsubseccion in self[seccion][subseccion]:
                    valor = self[seccion][subseccion][subsubseccion]
                    if valor != 0: representacion+=f"\n\t\t{subsubseccion}\t{valor}"
        return representacion



class Contabilidad():

    def __init__ (self):
        self.libro_diario = LibroDiario()
        self.libro_mayor = LibroMayor(self.libro_diario)
        self.balance = Balance(self.libro_mayor)

    def actualizar_contabilidad(self):
        self.libro_mayor = LibroMayor(self.libro_diario)
        self.balance = Balance(self.libro_mayor)

    def añadir_asiento(self, concepto:str, debe:dict, haber:dict, fecha=dt.date.today()):
        self.libro_diario.append(Asiento(concepto, debe, haber, fecha))
        self.actualizar_contabilidad()