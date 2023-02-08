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