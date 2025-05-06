import pytest
from datetime import datetime
from fibonacci import procesar_hora

def test_procesar_hora_normal():
    hora = datetime.strptime("12:23:04", "%H:%M:%S")
    min1, min2, segundos, serie = procesar_hora(hora)
    assert min1 == 2
    assert min2 == 3
    assert segundos == 4
    assert serie == [21, 13, 8, 5, 3, 2]

def test_procesar_hora_mayor_minutos():
    hora = datetime.strptime("15:49:08", "%H:%M:%S")
    min1, min2, segundos, serie = procesar_hora(hora)
    assert min1 == 4
    assert min2 == 9
    assert segundos == 8
    assert serie == [390, 241, 149, 92, 57, 35, 22, 13, 9, 4]
