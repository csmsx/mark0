import datetime
import Adafruit_MCP3008

'''
Access sensor readings from the MG-811 kind.

The readings are interpreted through an MC3008 ADC chip, reusing code from Adafruit.

The calibration model is very simple at this stage:
- Aimed at *rough* comparison in spite of estimation.
- Comparison to common urban air (about 350-400ppm).
- At best can say that the air has either more or less CO2 than common urban air.
- Default calibration will not return any reading for the first 60s of operations. During that time, the library "waits" for the MG-811 to heat up and get stable readings.

Although the API mainly gives a labelled comparison (MG811Result.compared_to_air()), the sensor raw reading is also available for custom comparisons (MG811Result.raw()).

References:
* https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008
* http://www.adafruit.com/datasheets/MCP3008.pdf
'''

class MG811Result:

    # About 350~400 ppm
    STD_AIR_LOW = 31
    STD_AIR_HIGH = 35

    # About 1000 ppm, standard air with a breadth
    ONE_BREADTH_AIR_LOW = 15
    ONE_BREADTH_AIR_HIGH = 18

    __dout = 0

    def __init__(self, dout):
        self.__dout = dout

    def raw(self):
        return self.__dout

    def compared_to_air(self):
        if self.__dout > self.STD_AIR_HIGH:
            return 'low'
        elif self.__dout < self.STD_AIR_LOW:
            return 'high'
        else:
            return 'normal'


class MG811:

    __clk = 0
    __dout_miso = 0
    __din_mosi = 0
    __chipselect_shutdown = 0
    __adc = None
    __in_analog_ch = None

    __start_time = None
    __calibration_time = None

    def __init__(self, dout, din=7, ch_sh=5, clk=11,
                 in_analog_ch=0, calibration_time=60):
        self.__dout_miso = dout
        self.__din_mosi = din
        self.__chipselect_shutdown = ch_sh
        self.__clk = clk
        self.__adc = Adafruit_MCP3008.MCP3008(
            clk=__clk,
            cs=__chipselect_shutdown,
            miso=__dout_miso,
            mosi=__din_mosi
        )
        self.__in_analog_ch = in_analog_ch
        self.__start_time = datetime.datetime.now()
        self.__calibration_time = datetime.timedelta(seconds=calibration_time)

    def read(self):
        '''
        Return the sensor reading if calibration time is over.
        If the sensor is still assumed calbirating, this
        method returns -1.
        '''
        now = datetime.datetime.now()
        if now - self.__start_time > self.__calibration_time:
            return self.__adc.read_adc(self.__in_analog_ch)
        else:
            return -1
