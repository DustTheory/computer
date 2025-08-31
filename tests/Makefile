PYTHONPATH := $(PYTHONPATH):$(CURDIR)

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(CURDIR)/../hdl/

VERILOG_SOURCES = $(shell find $(SRC_DIR) -type f -name "*.v" -o -name "*.vh")
VERILOG_SOURCES += ./harness.v
VERILATOR_INCLUDE_DIRS = $(shell find $(SRC_DIR) -type d)

EXTRA_ARGS += $(addprefix -I, $(VERILATOR_INCLUDE_DIRS))

TOPLEVEL = harness

MODULE = "cpu.module_tests.test_arithmetic_logic_unit, \
		  cpu.module_tests.test_comparator_unit, \
		  cpu.module_tests.test_immediate_unit, \
		  cpu.module_tests.test_register_file, \
		  cpu.module_tests.test_control_unit, \
		  cpu.module_tests.test_memory, \
		  cpu.module_tests.test_instruction_memory"

export SIM TOPLEVEL_LANG VERILOG_SOURCES TOPLEVEL MODULE EXTRA_ARGS PYTHONPATH

include $(shell cocotb-config --makefiles)/Makefile.sim