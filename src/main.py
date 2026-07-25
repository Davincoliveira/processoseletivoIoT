from machine import Pin
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


def read_hx711(dout, clk):
    timeout = 100
    while dout.value() == 1:
        timeout -= 1
        if timeout <= 0:
            return 0

    value = 0
    for _ in range(24):
        clk.value(1)
        value = (value << 1) | dout.value()
        clk.value(0)

    clk.value(1)
    clk.value(0)

    if value >= 0x800000:
        value -= 0x1000000

    return value


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
    elif prev_state not in (STATE_RESTOCK_ALERT, STATE_ANOMALY):
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

print("Sistema Kanban Inicializado")

state = STATE_ANOMALY
msg_printed = False

while True:
    raw = read_hx711(dout, clk)
    update_state(raw)