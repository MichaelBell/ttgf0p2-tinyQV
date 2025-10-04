import time
import sys
import rp2
import gc
import machine
from machine import UART, Pin, PWM, SPI

from ttcontrol import *

from pio_spi import PIOSPI
import flash_prog
import ecp_prog

@rp2.asm_pio(autopush=True, push_thresh=32, in_shiftdir=rp2.PIO.SHIFT_RIGHT)
def pio_capture():
    in_(pins, 8)
    
def run(query=True, stop=True):
    machine.freq(80_000_000)
    #machine.freq(96_000_000)
    #machine.freq(112_000_000)
    #machine.freq(128_000_000)

    if query:
        input("Reset? ")

    # Pull up UART RX
    Pin(GPIO_UI_IN[7], Pin.IN, pull=Pin.PULL_UP)
    
    # All other inputs no pull
    for i in range(7):
        Pin(GPIO_UI_IN[i], Pin.IN, pull=None)

    Pin(GPIO_UIO[0], Pin.IN, pull=Pin.PULL_UP)
    Pin(GPIO_UIO[1], Pin.IN, pull=None)
    Pin(GPIO_UIO[2], Pin.IN, pull=None)
    Pin(GPIO_UIO[3], Pin.IN, pull=None)
    Pin(GPIO_UIO[4], Pin.IN, pull=None)
    Pin(GPIO_UIO[5], Pin.IN, pull=None)
    Pin(GPIO_UIO[6], Pin.IN, pull=Pin.PULL_UP)
    Pin(GPIO_UIO[7], Pin.IN, pull=Pin.PULL_UP)

    clk = Pin(GPIO_PROJECT_CLK, Pin.OUT, value=0)
    rst_n = Pin(GPIO_PROJECT_RST_N, Pin.OUT, value=1)
    for i in range(2):
        clk.on()
        clk.off()
    rst_n.off()
    
    clk.on()
    time.sleep(0.001)
    clk.off()
    time.sleep(0.001)

    flash_sel = Pin(GPIO_UIO[0], Pin.OUT)
    qspi_sd0  = Pin(GPIO_UIO[1], Pin.OUT)
    qspi_sd1  = Pin(GPIO_UIO[2], Pin.OUT)
    qspi_sck  = Pin(GPIO_UIO[3], Pin.OUT)
    qspi_sd2  = Pin(GPIO_UIO[4], Pin.OUT)
    qspi_sd3  = Pin(GPIO_UIO[5], Pin.OUT)
    ram_a_sel = Pin(GPIO_UIO[6], Pin.OUT)
    ram_b_sel = Pin(GPIO_UIO[7], Pin.OUT)

    qspi_sck.off()
    flash_sel.off()
    ram_a_sel.off()
    ram_b_sel.off()
    qspi_sd0.on()
    qspi_sd1.off()
    qspi_sd2.off()
    qspi_sd3.off()

    for i in range(10):
        clk.off()
        time.sleep(0.001)
        clk.on()
        time.sleep(0.001)

    Pin(GPIO_UIO[0], Pin.IN, pull=Pin.PULL_UP)
    Pin(GPIO_UIO[1], Pin.IN, pull=None)
    Pin(GPIO_UIO[2], Pin.IN, pull=None)
    Pin(GPIO_UIO[3], Pin.IN, pull=None)
    Pin(GPIO_UIO[4], Pin.IN, pull=None)
    Pin(GPIO_UIO[5], Pin.IN, pull=None)
    Pin(GPIO_UIO[6], Pin.IN, pull=Pin.PULL_UP)
    Pin(GPIO_UIO[7], Pin.IN, pull=Pin.PULL_UP)
    
    rst_n.on()
    time.sleep(0.001)
    clk.off()

    sm = rp2.StateMachine(1, pio_capture, 80_000_000, in_base=Pin(21))
    #sm = rp2.StateMachine(1, pio_capture, 112_000_000, in_base=Pin(21))

    capture_len=1280
    buf = bytearray(capture_len)

    rx_dma = rp2.DMA()
    c = rx_dma.pack_ctrl(inc_read=False, treq_sel=5) # Read using the SM0 RX DREQ
    sm.restart()
    sm.exec("wait(%d, gpio, %d)" % (1, GPIO_UIO[3]))
    rx_dma.config(
        read=0x5020_0024,        # Read from the SM1 RX FIFO
        write=buf,
        ctrl=c,
        count=capture_len//4,
        trigger=True
    )
    sm.active(1)

    if query:
        input("Start? ")

    #uart = UART(1, baudrate=57600, tx=Pin(GPIO_UI_IN[7]), rx=Pin(GPIO_UO_OUT[0]))
    time.sleep(0.001)
    clk = PWM(Pin(GPIO_PROJECT_CLK), freq=40_000_000, duty_u16=32768)
    #clk = PWM(Pin(GPIO_PROJECT_CLK), freq=56_000_000, duty_u16=32768)
    #clk = PWM(Pin(GPIO_PROJECT_CLK), freq=32_000_000, duty_u16=32768)

    # Wait for DMA to complete
    while rx_dma.active():
        time.sleep_ms(1)
        
    sm.active(0)
    del sm

    if not stop:
        return

    if query:
        input("Stop? ")
    
    del clk
    rst_n.init(Pin.IN, pull=Pin.PULL_DOWN)
    clk = Pin(Pin.IN, pull=Pin.PULL_DOWN)

    if False:
        while True:
            data = uart.read(16)
            if data is not None:
                for d in data:
                    if d > 0 and d <= 127:
                        print(chr(d), end="")

        for i in range(len(buf)):
            print("%02x " % (buf[i],), end = "")
            if (i & 7) == 7:
                print()

    if True:
        for j in range(8):
            print("%02d: " % (j+21,), end="")
            for d in buf:
                print("-" if (d & (1 << j)) != 0 else "_", end = "")
            print()

        print("SD: ", end="")
        for d in buf:
            nibble = ((d >> 1) & 1) | ((d >> 1) & 2) | ((d >> 2) & 0x4) | ((d >> 2) & 0x8)
            print("%01x" % (nibble,), end="")
        print()

def execute(filename, tinyqv="/tinyqv.bit"):
    ecp_reset = True
    if tinyqv is None:
        # Put TinyQV into reset, which should release the QSPI
        rst_n = Pin(GPIO_PROJECT_RST_N, Pin.OUT, value=0)
        ecp_reset = False
    if filename is not None:
        flash_prog.program(filename, ecp_reset=ecp_reset)
    gc.collect()
    if tinyqv is not None:
        ecp_prog.program(tinyqv)
    gc.collect()
    run(query=False, stop=True)
