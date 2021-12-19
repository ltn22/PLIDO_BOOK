import random

class virtual_sensor:

    def __init__(self, start=None, variation=None, min=None, max=None):
        if start:
            self.value = start
        else:
            self.value = 0

        self.variation = variation
        self.min = min
        self.max = max

    def read_value(self):
        self.value += random.uniform(self.variation*-1, self.variation )

        if self.min and self.value < self.min: self.value = self.min
        if self.max and self.value > self.max: self.value = self.max
        
        return self.value

if __name__ == "__main__":
    import time

    temperature = virtual_sensor(start=20, variation = 0.1)
    pressure    = virtual_sensor(start=1000, variation = 1) 
    humidity    = virtual_sensor(start=30, variation = 3, min=20, max=80) 
    
    while True:
        t = temperature.read_value()
        p = pressure.read_value()
        h = humidity.read_value()

        print ("{:7.3f} {:10.3f} {:7.3f}".format(t, p, h))

        time.sleep(1)
