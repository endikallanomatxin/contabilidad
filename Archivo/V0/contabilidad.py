import datetime as dt
import numpy as np
import pandas as pd
import csv
import copy

from IPython.display import display


'''
CREACIÓN DEL DICCIONARIO DE CUENTAS
a partir de un .csv
'''

CUENTAS = {}
with open('cuentas.csv', mode='r') as f:
    data = csv.reader(f,delimiter=';')
    next(data)
    CUENTAS = {int(row[0]):row[1] for row in data}


'''
ASIENTOS Y LIBROS
Un libro es una lista de asientos
'''

class Asiento():
    '''Un asiento es la unidad que compone un libro'''

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

    
    
    def save_csv(self, name) -> None:
        self.tabla().to_csv(name + '.csv', index=False)  
        pass
    
    def load_csv(self, name) -> None:
        '''
        Desarrollar esta función para que parezca un libro diario creado aqui
        Para delimitar asientos se usa el número de asiento,
        primer campo en la tabla
        '''

        '''
        libro_diario = LibroDiario()
        with open(name+'.csv') as csvfile:
            last_row = csv.readlines()[-1]
            asiento_N = last_row[0]
            for asiento in range(asiento_N):

                # Crear diccionarios de debe y haber
                for row in csv.reader(csvfile):
                    # Este método es bastante poco eficiente porque pasa por
                    # todas las final para cada asiento
                    if row[0] == asiento: 
                        if row[] None

                # Añadir asiento
                self.append(Asiento())
                    
                print(row)
        pass
        '''

        '''
        Va a ser mas facil con pandas csv
        '''

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



    def append(self, asiento:Asiento) -> None:
        if not isinstance(asiento, Asiento):
            raise RuntimeError("Solo pueden añadirse asientos al libro diario")
        elif not(sum(asiento.debe.values()) == sum(asiento.haber.values())):
            raise RuntimeError("El asiento no es correcto")
        else:
            super().append(asiento)

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

    


'''
BALANCE
'''

# Esta información proviene del JUS/206/2009.
# Solo se han pasado al 100% las cuentas que no están entre paréntesis
            
BALANCE = {
    "Activo":{
        "Activo no corriente":{
            "Inmovilizado intangible":list(range(200,209+1)),
            "Inmovilizado material":list(range(210,219+1)) + [23],
            "Inversiones inmoviliarias":[220,221],
            "Inversiones de empresas del grupo y asociadas a largo plazo":[2403,2404,2423,2424,2413,2414],
            "Inversiones financieras a largo plazo":[2405,250,2425,252,253,254,2415,251,255,158,257,474],
            "Activos por impuesto diferido":[],
            "Deudores comerciales no corrientes":[]
        },
        "Activo corriente":{
            "Activos no corrientes mantenidos para la venta":list(range(580,584+1))+[599],
            "Existencias":list(range(30,36+1))+[407],
            "Deudores comerciales y otras cuentas a cobrar":list(range(430,436+1))+[433,434,44,5531,5533,460,544,4709,4700,4708,471,472,5580],
            "Inversiones en empresas del grupo y asociadas a corto plazo":[5303,5304,5323,5324,5343,5344,5313,5314,5333,5334,5353,5354,5523,5524],
            "Inversiones financieras a corto plazo":[5305,540,5325,5345,542,543,547,5315,5335,541,546,5590,5593,5355,545,548,551,5525,565,566,480,567],
            "Periodificaciones a corto plazo":[],
            "Efectivo y otros activos líquidos equivalentes":list(range(570,576+1))
        },
    },
    "Patrimonio neto":{
        "Fondos propios":{
            "Capital":[100, 101, 102, 1030, 1040],
            "Prima de emisión":[110],
            "Reservas":[112,1141,113,1140,1142,1143,1144,115,119,108,109],
            "Acciones y participaciones en patrimonio propias":[],
            "Resultados de ejercicios anteriores":[120,121],
            "Otras aportaciones de socios":[118],
            "Resultados del ejercicio":[129],
            "Dividendo a cuenta":[557],
            "Otros instrumentos de patrimonio neto":[111],
        },
        "Ajustes por cambios de valor":{
            "Activos financieros disponibles para la venta":[133],
            "Operaciones de covertura":[1340],
            "Activos no corrientes y pasivos vinculados, mantenidos para la venta":[136],
            "Diferencia de conversión":[135],
            "Otros":[137]
        },
        "Subvenciones, donaciones y legados recibidos":{
            "":[130,131,132]
        }
    },
    "Pasivo":{
        "Pasivo no corriente":{
            "Provisiones a largo plazo":list(range(140,147+1)),
            "Deudas a largo plazo":list(range(170,181+1))+[1605,1625,1615,1635,185,189,],
            "Deudas con empresas del grupo y asociadas a largo plazo":[1603,1604,1613,1614,1623,1624,1633,1634],
            "Pasivos por impuesto diferido":[479],
            "Periodificaciones a largo plazo":[181],
            "Acreedores comerciales no corrientes":[],
            "Deuda con características especiales a largo plazo":[]
        },
        "Pasivo corriente":{
            "Pasivos vinculados con activos no corrientes mantenidos para la venta":list(range(585,589+1)),
            "Provisiones a corto plazo":[499,529],
            "Deudas a corto plazo":[500,501,505,506,5105,520,527,5125,524,5595,55981034,1044,190,192,194,509,5115,5135,5145,521,522,523, 525,526,528,551,5525,5530,5532,555,5565,5566,560,561,569],
            "Deudas con empresas del grupo y asociadas a corto plazo":[5103,5104,5113,5114,5123,5124,5133,5134,5143,5144,5523,5524,5563,5564],
            "Acreedores comerciales y otras cuentas a pagar":[400,401,405,406,403,404,41,465,466,4752,4750,4751,4758,476,477,438],
            "Periodificaciones a corto plazo":[485,568],
            "Deuda con características especiales a corto plazo":[502,507]
        }
    }
}


PYG_TOTALES = {
    # 'A) OPERACIONES CONTINUADAS'
    'A.1) RESULTADO DE EXPLOTACIÓN': [1,2,3,4,5,6,7,8,9,10,11],
    'A.2) RESULTADO FINANCIERO': [12,13,14,15,16],
    'A.3) RESULTADO ANTES DE IMPUESTOS (A.1+A.2)' : [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
    'A.4) RESULTADO DEL EJERCICIO PROCEDENTE DE OPERACIONES CONTINUADAS (A.3 + impuestos)':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
    'B) OPERACIONES INTERRUMPIDAS': [18],
    'A.5) RESULTADO DEL EJERCICIO (A.4+B)':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
}

PYG_GRUPOS = {
    '1. Importe neto de la cifra de negocios.' : {
            'a) Ventas.': [700,701,702,703,704,-706,-708,-709],
            'b) Prestaciones de servicios.' : [705]
    },
    '2. Variación de existencias de productos terminados y en curso de fabricación.':[-6930, 71,7930],
    '3. Trabajos realizados por la empresa para su activo.':[73],
    '4. Aprovisionamientos.':{
        'a) Consumo de mercaderías.':[-600, 6060,6080,6090, 610],
        'b) Consumo de materias primas y otras materias consumibles.':[-601,-602,6061,6062,6081,6082,6091,6092,611,612],
        'c) Trabajos realizados por otras empresas.':[-607]	,
        'd) Deterioro de mercaderías, materias primas y otros aprovisionamientos.':[-6931,-6932,-6933,7931,7932,7933]
    },
    '5. Otros ingresos de explotación.':{
        'a) Ingresos accesorios y otros de gestión corriente.':[75],
        'b) Subvenciones de explotación incorporadas al resultado del ejercicio.':[740, 747]
    },
    '6. Gastos de personal.':{
        'a) Sueldos, salarios y asimilados.':[-640,-641,-6450],
        'b) Cargas sociales.':[-642,-643,-649],
        'c) Provisiones.':[-644,-6457,7950,7957]
    },
    '7. Otros gastos de explotación.':{
        'a) Servicios exteriores.':[-62],
        'b) Tributos.':[-631,-634,636,639],
        'c) Pérdidas, deterioro y variación de provisiones por operaciones comerciales.':[-650,-694,-695,794,7954],
        'd) Otros gastos de gestión corriente':[-651,-659],		    
    },
    '8. Amortización del inmovilizado.':[-68],
    '9. Imputación de subvenciones de inmovilizado no financiero y otras.':[746],
    '10. Excesos de provisiones.':[7951,7952,7955,7956],
    '11. Deterioro y resultado por enajenaciones del inmovilizado.':{
        'a) Deterioros y pérdidas.':[-690,-691,-692,790,791,792],
        'b) Resultados por enajenaciones y otras.':[-670,-671,-672,770,771,772]
    },
	'12. Ingresos financieros.':{
        'a) De participaciones en instrumentos de patrimonio.':{
            'a1) En empresas del grupo y asociadas.':[7600, 7601],		
            'a2) En terceros.':[7602,7603]
        },
        'b) De valores negociables y otros instrumentos financieros.':{
            'b1) De empresas del grupo y asociadas.':[7610,7611,76200,76201,76210,76211],
            'b2) De terceros.':[7612,7613,76202,76203,76212,76213,767,769]
        }
    },
    '13. Gastos financieros.':{
        'a) Por deudas con empresas del grupo y asociadas.':[-6610,-6611,-6615,-6616,-6620,-6621,-6640, -6641,-6650,-6651,-6654, -6655],
        'b) Por deudas con terceros.':[-6612,-6613,-6617,-6618,-6622,-6623,	-6624,-6642,-6643,-6652,-6653,-6656, -6657,-669],
        'c) Por actualización de provisiones':[-660]
    },
    '14. Variación de valor razonable en instrumentos financieros.':{
        'a) Valor razonable con cambios en pérdidas y ganancias.':[-6630,-6631,-6633,7630,7631,7633],
        'b) Transferencia de ajustes de valor razonable con cambios en el patrimonio neto.':[-6632,7632]
    },
    '15. Diferencias de cambio.':[-668,768],
    '16. Deterioro y resultado por enajenaciones de instrumentos financieros.':{
        'a) Deterioros y pérdidas.'	: [-696,-697,-698,-699,796,797,798,799],
        'b) Resultados por enajenaciones y otras.':[-666,-667,-673,-675,766,773,775]
    },
    '17. Impuestos sobre beneficios.':[-6300,6301,-633,638],
    '18. Resultado del ejercicio procedente de operaciones interrumpidas neto de impuestos.':[]
}

    
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

def sumar_ultimos_niveles(diccionario:dict) -> float :
    suma = 0

    if type(diccionario) is list: return diccionario.sum()
    if type(diccionario) is int: return diccionario
    if type(diccionario) is float: return diccionario
    
    for grupo in diccionario:
        if isinstance(diccionario[grupo], (int, float)):
            suma += diccionario[grupo]
        else:
            for subgrupo in diccionario[grupo]:
                if isinstance(diccionario[grupo][subgrupo], (int, float)):
                    suma += diccionario[grupo][subgrupo]
                else:
                    for subsubgrupo in diccionario[grupo][subgrupo]:
                        suma += diccionario[grupo][subgrupo][subsubgrupo]
    return suma