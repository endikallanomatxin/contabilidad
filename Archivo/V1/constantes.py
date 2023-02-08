from imports import *

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
