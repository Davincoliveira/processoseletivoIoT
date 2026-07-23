from machine import Pin, enable_irq, disable_irq
import time

HX711_DOUT_PIN = 4
HX711_CLK_PIN = 5

STOCK_FULL_G = 5000
STOCK_MINIMUM_G = 150
STOCK_ANOMALY_G = 0

STATE_REGULAR = 0
STATE_RESTOCK_ALERT = 1
STATE_REFILLED = 2
STATE_ANOMALY = 3


class HX711:
    def __init__(self, clock_pin, data_pin, gain=128):
        self.clock = clock_pin
        self.data = data_pin
        self.clock.value(False)
        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1
        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        self._read_raw()

    def _wait_ready(self):
        for _ in range(100):
            if not self.data.value():
                return True
            time.sleep_ms(1)
        return False

    def _read_raw(self):
        if not self._wait_ready():
            return 0

        result = 0
        for _ in range(24):
            result = (result << 1) | self.data.value()
            self.clock.value(True)
            time.sleep_us(1)
            self.clock.value(False)
            time.sleep_us(1)

        for _ in range(self.GAIN):
            self.clock.value(True)
            time.sleep_us(1)
            self.clock.value(False)
            time.sleep_us(1)

        if result > 0x7FFFFF:
            result -= 0x1000000

        return result

    def read(self):
        return self._read_raw()

    def tare(self, times=15):
        sum_val = 0
        for _ in range(times):
            sum_val += self.read()
        self.OFFSET = sum_val / times
        return self.OFFSET

    def set_offset(self, offset):
        self.OFFSET = offset

    def get_value(self):
        return self.read() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def set_scale(self, scale):
        self.SCALE = scale


def update_state(load_g):
    global state, msg_printed

    prev_state = state

    if load_g == STOCK_ANOMALY_G:
        state = STATE_ANOMALY
    elif load_g <= STOCK_MINIMUM_G:
        state = STATE_RESTOCK_ALERT
    elif load_g >= STOCK_FULL_G and prev_state == STATE_RESTOCK_ALERT:
        state = STATE_REFILLED
    elif prev_state == STATE_REFILLED:
        state = STATE_REGULAR
    else:
        state = STATE_REGULAR

    if state != prev_state:
        msg_printed = False

    if state == STATE_ANOMALY and not msg_printed:
        print("ALERTA: Caixa ausente ou erro de calibração no sensor HX711!")
        msg_printed = True
    elif state == STATE_RESTOCK_ALERT and not msg_printed:
        print("Evento de reposição disparado! Caixa vazia detectada.")
        msg_printed = True
    elif state == STATE_REFILLED and not msg_printed:
        print("Abastecimento concluído. Caixa cheia.")
        msg_printed = True
    elif state == STATE_REGULAR:
        print("Status: Estoque Regular ({}g)".format(load_g))
        msg_printed = False


dout = Pin(HX711_DOUT_PIN, Pin.IN, pull=Pin.PULL_DOWN)
clk = Pin(HX711_CLK_PIN, Pin.OUT, value=0)

time.sleep_ms(100)

hx711 = HX711(clk, dout, gain=128)
hx711.set_offset(0)
hx711.set_scale(1)

print("Sistema Kanban Inicializado")

state = STATE_REGULAR
msg_printed = False

# while True:
#     raw = hx711.read()
#     update_state(raw)

last_load = STOCK_FULL_G

while True:
    raw = (
        hx711.read() +
        hx711.read() +
        hx711.read()
    ) // 3

    load_g = int(raw / 210)

    if load_g == 0 and last_load > STOCK_MINIMUM_G:
        time.sleep_ms(20)
        continue

    last_load = load_g

    update_state(load_g)

    time.sleep_ms(20)