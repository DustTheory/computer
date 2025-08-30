SIM ?= verilator
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(CURDIR)/../src

VERILOG_SOURCES = $(shell find $(SRC_DIR) -name "*.v")

VERILATOR_INCLUDE_DIRS = $(shell find $(SRC_DIR) -type d)

EXTRA_ARGS += $(addprefix -I, $(VERILATOR_INCLUDE_DIRS))

TOPLEVEL = gpu

# Define the name of the Python testbench module
MODULE = test
export SIM TOPLEVEL_LANG VERILOG_SOURCES TOPLEVEL MODULE EXTRA_ARGS

# Include the cocotb makefile
include $(shell cocotb-config --makefiles)/Makefile.sim