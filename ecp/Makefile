TARGET = tinyqv
TOP = tt_ecp5_wrapper
PROG ?= seven

OBJS += tt_wrapper.v ../src/project.v ../src/peri*.v ../src/user_peripherals/*.v ../src/user_peripherals/*/*.v ../src/tinyQV/cpu/*.v ../src/tinyQV/peri/uart/uart_tx.v ../src/tinyQV/peri/uart/uart_rx.v

all: ${TARGET}.bit

$(TARGET).ys: $(OBJS)
	yosys -p "read -sv $(OBJS) ; synth_ecp5 -top ${TOP} -json $@" -DPURE_RTL -DSYNTH_FPGA -DNO_SCRATCH > yosys.log
	@grep Warn yosys.log || true
	@grep Error yosys.log || true
	@egrep "[0-9]+ submodules" yosys.log | head -1
	@egrep "[0-9]+   TRELLIS_FF" yosys.log | awk '{sum+=$$1;}END{printf("%9d   TRELLIS_FF*\n", sum/2);}'
	@egrep "[0-9]+   LUT" yosys.log | head -1
	@echo	

$(TARGET)_out.config: $(TARGET).ys
	./nextpnr.sh --25k --package CABGA256 --speed 6 -r --json $< --textcfg $@ --lpf tt.lpf
	@grep Warn nextpnr.log || true
	@grep Error nextpnr.log || true
	@grep "Max frequency.*clk" nextpnr.log | tail -1
	@echo

$(TARGET).bit: $(TARGET)_out.config
	ecppack --svf ${TARGET}.svf $< $@

${TARGET}.svf: ${TARGET}.bit

prog: ${TARGET}.bit
	mpremote mount . + exec "import os; os.chdir('/'); import simple_tinyqv; simple_tinyqv.execute('/remote/$(PROG).bin', '/remote/$(TARGET).bit')"

reprog:
	mpremote mount . + exec "import os; os.chdir('/'); import simple_tinyqv; simple_tinyqv.execute('/remote/$(PROG).bin', None)"

regate: #${TARGET}.bit
	mpremote mount . + exec "import os; os.chdir('/'); import simple_tinyqv; simple_tinyqv.execute(None, '/remote/$(TARGET).bit')"

reset:
	mpremote mount . + exec "import os; os.chdir('/'); import simple_tinyqv; simple_tinyqv.execute(None, None)"

clean:
	rm -f *.svf *.bit *.config *.ys *.log

.PHONY: all prog clean
