
import RPi.GPIO as GPIO
import smbus
import spidev
import lirc
import serial

from multiprocessing import Process, Manager, Value, Lock
import time
import ctypes

LOW = False
HIGH = True

MS = 0.001
US_100 = 0.0001
US = 0.000001

class Peri0:
	__ref_count = 0
    __lock = Lock()

    def __init__(self):
        with Peri0.__lock:
            if not Peri0.__ref_count:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)

            Peri0.__ref_count += 1

    def __del__(self):
        with Peri0.__lock:
            Peri0.__ref_count -= 1

            if not Peri0.__ref_count:
                GPIO.cleanup()

#################################################

class MultiTask(Process):
    def __init__(self, task, *args, **kwargs):
        """
        task : task_function
        args : tark_function arguments
        kwargs :
            oneshot=True | False
            terms=term_function
            terms=(term_function, (arg0, ..))
        """

        Process.__init__(self)
        self.is_stop = Value(ctypes.c_bool, False)
        self.task = task
        self.args = args
        self.term_func = None
        self.term_args = None

        for key, value in kwargs.items():
            if key == "oneshort":
                self.oneshort = value
            elif key == "terms":
                if type(value) == tuple:
                    self.term_func = value[0]
                    self.term_args = None if (len(value) == 1) else value[1]
                else:
                    self.term_func = value

    def run(self):
        try:
            if self.oneshort:
                self.task(*self.args)
            else:
                while not self.is_stop.value:
                    self.task(*self.args)
        finally:
            if self.term_func != None:
                self.term_func(*self.term_args)

    def stop(self):
        self.is_stop.value = True

class TempHumi(Peri0):
    CAL = 0 #-4.4

    def __init__(self):
        super().__init__()

        self.task = None
        self.delay = 0      #Minimization 220ms(internal fix 200ms)
        self.func = None
        self.args = None

        self.addr = 0x40
        self.cmd_t = 0xf3   #templature
        self.cmd_h = 0xf5   #humidity
        self.cmd_r = 0xfe   #reset

        self.temp_humi = smbus.SMBus(1)

    def __del__(self):
        super().__del__()

    def __task(self):
        ret_temp = self.measure_temp()
        ret_humi = self.measure_humi()

        self.func(ret_temp, ret_humi, *self.args)

        time.sleep(self.delay)

    def start(self, func, *args, delay = 220 * MS):
        self.func = func
        self.args = args
        self.delay = delay - 200 * MS

        self.temp_humi.write_byte(self.addr, self.cmd_r)

        if self.task == None:
            self.task = MultiTask(self.__task, oneshort=False)
            self.task.start()

    def stop(self):
        if self.task != None:
            self.task.terminate()
            self.task = None

    def measure_temp(self):
        self.temp_humi.write_byte(self.addr, self.cmd_t)
        time.sleep(100 * MS)    #Internal minimization

        data = []
        tmp = self.temp_humi.read_byte(self.addr)
        data.append(tmp)
        tmp = self.temp_humi.read_byte(self.addr)
        data.append(tmp)

        return (-46.85 + TempHumi.CAL) + 175.72 / 65536 * (data[1] | data[0] << 8)

    def measure_humi(self):
        self.temp_humi.write_byte(self.addr, self.cmd_h)
        time.sleep(100 * MS)    #Internal minimization

        data = []
        tmp = self.temp_humi.read_byte(self.addr)
        data.append(tmp)
        tmp = self.temp_humi.read_byte(self.addr)
        data.append(tmp)

        return (-6.0 + TempHumi.CAL) + 125.0 / 65536 * (data[1] | data[0] << 8)

    def measure_temp_average(self, count=5, delay = 220 * MS):
        delay = delay - 200 * MS
        sum_temp = 0

        for i in range(count):
            sum_temp += self.measure_temp()
            time.sleep(delay)

        return sum_temp / count

    def measure_humi_average(self, count=5, delay = 220 * MS):
        delay = delay - 200 * MS
        sum_humi = 0

        for i in range(count):
            sum_humi += self.measure_humi()
            time.sleep(delay)

        return sum_humi / count

#------------------------------------------------

def temphumi_read(temp, humi):
    print("temp = %.2f, humi = %.2f"%(round(temp, 2), round(humi, 2)))

def temphumi_unit_test():
    try:
        th = TempHumi()

        ret = th.measure_temp_average()
        print("current tempolature = %.2f"%ret)

        ret = th.measure_humi_average()
        print("current humidity = %.2f"%ret)

        print("wating for read(10 sec)....")
        th.start(temphumi_read)
        time.sleep(10)
        print("terminated")
        th.stop()
    finally:
        th.stop()
# http://www.uugear.com/portfolio/bluetooth-communication-between-raspberry-pi-and-arduino/

bluetoothSerial = serial.Serial("/dev/rfcomm1", baudrate=9600 )

count = None
while count == None:
    try:
        count = int(raw_input( "Please enter the number of times to blink the L$
    except:
        pass    # Ignore any errors that may occur and try again


bluetoothSerial.write(str(count))
print bluetoothSerial.readline()
