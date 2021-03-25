import requests
import json
import pandas

elTypes = ['Temperature', 'Light', 'Voltage', 'Current', 'PH', 'Oxygen',
           'PhotoGate', 'Pulse', 'Force', 'Sound', 'Humidity', 'Pressure',
           'Motion', 'Magtnetic', 'Conductivity', 'GSR', 'CO2', 'Barometer',
           'Rotary', 'Acceleration', 'Spirometer', 'SoilMoisture',
           'Turbidity', 'UVB', 'EKG', 'Colorimeter', 'DropCounter',
           'FlowRate', 'ForcePlate', 'BloodPressure', 'Salinity', 'UVA',
           'SurfaceTemp', 'WideRangeTemp', 'InfraredThermometer',
           'Respiration', 'HandDynamometer', 'Calcium', 'Chloride',
           'Ammonium', 'Nitrate', 'Anemometer', 'GPS', 'Gyroscope',
           'DewPoint', 'Charge', 'Tonic', 'Phasic']


class Edulogger:
    def __init__(self, logger, eventNames=[], port=2000):
        self.port = port
        self.logger = logger
        if isinstance(eventNames, str):
            self.eventNames = [eventNames]
        else:
            self.eventNames = eventNames
        self.template = "http://localhost:{port}/NeuLogAPI?GetSensorValue:[{logger}],[1]"
        self.data = pandas.DataFrame(columns=['time', str(self.logger)] + self.eventNames)

    def getValue(self, timeout=400):
        req = self.template.format(**self.__dict__)
        resp = requests.get(req)
        parsed = json.loads(str(resp))
        if 'GetSensorValue' in parsed:
            return parsed['GetSensorValue']

    def poll(self, t, timeout=400):
        self.data = self.data.append({
            'time': t,
            self.logger: self.getValue()
        })

    def mark(self, t, eventName):
        if eventName not in self.eventNames:
            raise ValueError("Event name {} not recognised, event names must be "
                             "specified when initialising Edulogger object.")
        self.data = self.data.append({
            'time': t,
            eventName: True
        }, ignore_index=True)



