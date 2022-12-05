import datetime as dt
import numpy as np
import pandas as pd
import csv
import copy
import ast

CUENTAS = {}
with open('cuentas.csv', mode='r') as f:
    data = csv.reader(f,delimiter=';')
    next(data)
    CUENTAS = {int(row[0]):row[1] for row in data}


class Asiento():
    def __init__(self, concepto, debe, haber, fecha):
        self.concepto = concepto
        self.debe     = debe
        self.haber    = haber
        self.fecha    = fecha # dt.date.today()
        
    def __str__(self):
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
    
    def __repr__(self):
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
    
    def tabla(self):
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

    
    
class LibroDiario(list):
    
    def mostrar_por_dias(self):
        
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
    
    
    def tabla(self):
        
        tabla = self[0].tabla()
        tabla.insert(0,'Número de asiento', [0]*(len(self[0].debe)+len(self[0].haber)))
        for numero_de_asiento, asiento in enumerate(self):
            if asiento != self[0]:
                asiento_tabla =  asiento.tabla()
                asiento_tabla.insert(0,'Número de asiento', [numero_de_asiento]*(len(asiento.debe)+len(asiento.haber)))
                tabla = pd.concat([tabla,asiento_tabla], ignore_index=True)

        # tabla = tabla.sort_values(by=['Fecha'], ignore_index = True)
        
        return tabla


    def append(self, asiento):
        if not isinstance(asiento, Asiento):
            raise RuntimeError("Solo pueden añadirse asientos al libro diario")
        elif not(sum(asiento.debe.values()) == sum(asiento.haber.values())):
            raise RuntimeError("El asiento no es correcto")
        else:
            super().append(asiento)
    
    def save_csv(self, name):
        self.tabla().to_csv(name + '.csv', index=False)  
        pass
    
    def load_csv(self, name):
        libro_diario = LibroDiario()
        with open(name+'.csv') as csvfile:
            for row in csv.reader(csvfile):
                print(row)
        pass

    
class LibroMayor(dict):
    
    def __init__(self, libro_diario):
        
        self.libro_diario = libro_diario
        self.cuentas = []
        self.totales = {}
        
        for asiento in self.libro_diario:
            for cuenta in asiento.debe:
                if not(cuenta in self.cuentas): self.cuentas.append(cuenta)
            for cuenta in asiento.haber:
                if not(cuenta in self.cuentas): self.cuentas.append(cuenta)
        
        self.cuentas.sort()
        
        for cuenta in self.cuentas:
            d = libro_diario.tabla()
            d = d[d["Cuenta"] == cuenta]
            self[cuenta] = d
    
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

    def calcular_totales(self):
         for cuenta in self.cuentas:
            self.totales[cuenta] = self[cuenta]["Debe"].sum()-self[cuenta]["Haber"].sum()
            # La cuenta será positiva si es deudora y negativa si es acreedora.

            
# Esta información proviene del JUS/206/2009. Solo se han pasado al 100% las cuentas que no están entre paréntesis
            
SECCIONES_BALANCE = {
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
            

    
class Balance(dict):
    
    def __init__(self, libro):
        
        self["Activo"]          = copy.deepcopy(SECCIONES_BALANCE["Activo"])
        self["Patrimonio neto"] = copy.deepcopy(SECCIONES_BALANCE["Patrimonio neto"])
        self["Pasivo"]          = copy.deepcopy(SECCIONES_BALANCE["Pasivo"])
        
        self.totales = {
            "Activo":0,
            "Patrimonio neto":0,
            "Pasivo":0
        }
        
        # La clase balance es un diccionario que contiene diccionarios como sub-secciones
        # y que en el último nivel tiene una lista para cada subsección que contiene las
        # cuentas que le corresponden
        
        # (Queda un último nivel en el arbol de las secciones que he agrupado en sus
        # cuentas padres por simplicidad, queda por hacer).
        
        
        if libro is LibroDiario():
            libro = LibroMayor(libro)
            
        self.libro = libro #que debe ser de clase LibroMayor
        
        self.poner_a_cero()
        self.componer()
        
        self.calcular_totales()
        
        
    def componer(self):
        for cuenta in self.libro.totales:
            for seccion in SECCIONES_BALANCE:
                for subseccion in SECCIONES_BALANCE[seccion]:
                    for subsubseccion in SECCIONES_BALANCE[seccion][subseccion]:
                        if cuenta in SECCIONES_BALANCE[seccion][subseccion][subsubseccion]:
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
                            
    def poner_a_cero(self):
        for seccion in self:
            for subseccion in self[seccion]:
                for subsubseccion in self[seccion][subseccion]:
                    self[seccion][subseccion][subsubseccion]=0
                    
    def calcular_totales(self):
        
        self.totales["Activo"]          = 0
        self.totales["Patrimonio neto"] = 0
        self.totales["Pasivo"]          = 0
        
        for seccion in SECCIONES_BALANCE:
            for subseccion in SECCIONES_BALANCE[seccion]:
                for subsubseccion in SECCIONES_BALANCE[seccion][subseccion]:
                    if seccion == "Activo":
                        self.totales["Activo"] += self[seccion][subseccion][subsubseccion]
                    elif seccion == "Patrimonio neto":
                        self.totales["Patrimonio neto"] += self[seccion][subseccion][subsubseccion]
                    elif seccion == "Pasivo":
                        self.totales["Pasivo"] += self[seccion][subseccion][subsubseccion]
                    
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