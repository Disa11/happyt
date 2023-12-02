from functools import wraps
from flask import session, redirect, Flask
from colorama import Fore, Style
import re
import serial, time
import json

def bytes_to_dict(byte_str):
    # Decodifica la cadena de bytes y convierte a str
    str_data = byte_str.decode('utf-8')

    # Elimina caracteres de escape adicionales, como '\r\n'
    str_data = str_data.strip()

    # Carga la cadena JSON en un diccionario
    data_dict = json.loads(str_data)

    return data_dict


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def is_email(mail):
    patron = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
     
    if re.match(patron, mail):
        return True
    else:
        return False
    
def tiempo_a_segundos(tiempo_str):
    horas, minutos, segundos = map(int, tiempo_str.split(':'))
    total_segundos = horas * 3600 + minutos * 60 + segundos
    return total_segundos