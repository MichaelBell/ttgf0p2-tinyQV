from machine import Pin
import tinyqv

VGA_TEST_PERI = 20
SYNC = 1 << 15
VIS = 1 << 14
ADV = 1 << 13

def set_reg_pair(addr, val):
    tinyqv.write_byte_reg(VGA_TEST_PERI, addr, val >> 8)
    tinyqv.write_byte_reg(VGA_TEST_PERI, addr+1, val & 0xff)
    
def set_horiz_timing(vis, front, sync, back, invert_sync=False):
    set_reg_pair(0, vis | VIS | (SYNC if invert_sync else 0))
    set_reg_pair(2, front | (SYNC if invert_sync else 0))
    set_reg_pair(4, sync | (0 if invert_sync else SYNC))
    set_reg_pair(6, back | ADV | (SYNC if invert_sync else 0))

def set_vert_timing(vis, front, sync, back, invert_sync=False):
    set_reg_pair(8, vis | VIS | (SYNC if invert_sync else 0))
    set_reg_pair(10, front | (SYNC if invert_sync else 0))
    set_reg_pair(12, sync | (0 if invert_sync else SYNC))
    set_reg_pair(14, back | ADV | (SYNC if invert_sync else 0))


# 640x480 CVT, works at 24MHz
#set_horiz_timing(640, 16, 64, 80, True)
#set_vert_timing(480, 3, 4, 13)

# 800x600 CVT, for 38MHz
set_horiz_timing(800, 32, 80, 112, True)
set_vert_timing(600, 3, 4, 17)

for i in range(1,8):  # Don't use out0 to preserve UART
    Pin(i, func_sel=VGA_TEST_PERI)
