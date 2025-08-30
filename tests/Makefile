SIM ?= verilator
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(CURDIR)/../hdl/

VERILOG_SOURCES = $(shell find $(SRC_DIR) -type f -name "*.v" -o -name "*.vh")
VERILOG_SOURCES += ./harness.v
VERILATOR_INCLUDE_DIRS = $(shell find $(SRC_DIR) -type d)

EXTRA_ARGS += $(addprefix -I, $(VERILATOR_INCLUDE_DIRS))

TOPLEVEL = harness
MODULE = test_arithmetic_logic_unit,test_comparator_unit,test_immediate_unit,test_register_file

export SIM TOPLEVEL_LANG VERILOG_SOURCES TOPLEVEL MODULE EXTRA_ARGS

# Include the cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim