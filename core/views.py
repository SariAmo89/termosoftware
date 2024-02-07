from flask import request, render_template, Blueprint, redirect, url_for, flash, jsonify
from ThermoSoftware import thread
from threading import Thread
import serial
from flask_login import current_user

# Blueprint definieren
core = Blueprint('core',__name__)


# Funktion die Multi-Threading erlaubt
def start_after_app_run():
    global arduinoData
    arduinoData=serial.Serial('COM3', 115200)
    arduinoData.close()
    arduinoData.open() 
    arduinoData.timeout = 1
    
# INDEX
@core.route('/')
def index():
    # Landing Pages für verschiedene Rolen
    if current_user.is_authenticated:
        if current_user.has_role('User'):
            return redirect(url_for("users.account"))
        if current_user.has_role('Admin'):
            return redirect(url_for("users.listusers"))
        
    return redirect(url_for("users.login"))
        

# BENUTZER HILFE
@core.route('/info')
def info():
    return render_template('info.html')


# THERMOSTAT
@core.route('/thermostat', methods=['GET','POST'])
def thermostat():

    # Suche nach Arduino 
    global thread
    if thread is None:
        thread = Thread(target=start_after_app_run)
        thread.start()
    
    # Temperatur und Luftfeuchtigkeit auf None gesetzt um Fehler vorzubeugen
    temp = None
    humidity = None

    # Error Handling
    try:
        arduinoData.write(b'read_sensor_data')
        sensor_data = arduinoData.readline().decode().strip()
        try:
            temp, humidity = sensor_data.split(',')
        except ValueError:
            temp = None
            humidity = None
    except NameError:
        try:
            arduinoData.write(b'read_sensor_data')
            sensor_data = arduinoData.readline().decode().strip()
            temp, humidity = sensor_data.split(',')
        except NameError:
            pass

    return render_template('thermostat.html', temp=temp, humidity=humidity)


# HILFSROUTE FÜR TEMP/L.FEUCH. AKTUALISIERUNG
@core.route('/get_values', )
def get_values():
    arduinoData.write(b'r') # Sende Kommando zu Arduino
    sensor_data = arduinoData.readline().decode('utf-8') # Lese Daten von Arduino

    # Zerlegung der empfangenen Daten in Temperatur- und Luftfeuchtigkeitswerte
    try:
        temp, humidity = sensor_data.split(',')
        temp = float(temp)
        temp = format(temp, '.2f')
        humidity = float(humidity)
        humidity = format(humidity, '.2f')
    except ValueError:
        # Fehler beim Parsen von Daten aufgetreten dann:
        temp = None
        humidity = None

    data = {
        'temp': temp,
        'humidity': humidity
    }

    # Rückgabe des Wörterbuchs als JSON-Antwort
    return jsonify(data)


# HILFSROUTE FÜR DATEN AN ARDUINO SENDEN
@core.route('/send', methods=['POST'])
def send():
    # Ganzzahligen Wert aus Formularübermittlung abrufen
    value = int(request.form['value'])
    
    # Ganzzahligen Wert an das Arduino-Board senden
    arduinoData.write(str(value).encode())
    
    flash('Temperatur ist eingestellt', 'warning')
    return redirect(url_for("core.thermostat"))

