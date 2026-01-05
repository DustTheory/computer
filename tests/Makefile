PYTHONPATH := $(PYTHONPATH):$(CURDIR)

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(CURDIR)/../hdl/
INC_DIR = $(CURDIR)/../hdl_inc/

VERILOG_SOURCES = $(shell find $(SRC_DIR) -type f -name "*.v" -o -name "*.vh")
VERILATOR_INCLUDE_DIRS = $(shell find $(SRC_DIR) -type d) $(shell find $(INC_DIR) -type d)
EXTRA_ARGS += $(addprefix -I, $(VERILATOR_INCLUDE_DIRS))

CPU_UNIT_TESTS_TOPLEVEL = cpu_unit_tests_harness

CPU_UNIT_TESTS_MODULE = "cpu.unit_tests.test_arithmetic_logic_unit, \
		  cpu.unit_tests.test_comparator_unit, \
		  cpu.unit_tests.test_immediate_unit, \
		  cpu.unit_tests.test_register_file, \
		  cpu.unit_tests.test_control_unit, \
		  cpu.unit_tests.test_instruction_memory_axi, \
		  cpu.unit_tests.test_memory_axi, \
		  cpu.unit_tests.test_uart_receiver, \
		  cpu.unit_tests.test_uart_transmitter, \
		  cpu.unit_tests.test_debug_peripheral"

CPU_INTEGRATION_TESTS_TOPLEVEL = cpu_integration_tests_harness
CPU_INTEGRATION_TESTS_MODULE = "cpu.integration_tests.test_instruction_fetch, \
		cpu.integration_tests.test_lui_instruction, \
		cpu.integration_tests.test_auipc_instruction, \
		cpu.integration_tests.test_jal_instruction, \
		cpu.integration_tests.test_jalr_instruction, \
		cpu.integration_tests.test_beq_instruction, \
		cpu.integration_tests.test_bge_instruction, \
		cpu.integration_tests.test_bgeu_instruction, \
		cpu.integration_tests.test_blt_instruction, \
		cpu.integration_tests.test_bltu_instruction, \
		cpu.integration_tests.test_bne_instruction, \
		cpu.integration_tests.test_lb_instruction, \
		cpu.integration_tests.test_lh_instruction, \
		cpu.integration_tests.test_lw_instruction, \
		cpu.integration_tests.test_lbu_instruction, \
		cpu.integration_tests.test_lhu_instruction, \
		cpu.integration_tests.test_sb_instruction, \
		cpu.integration_tests.test_sh_instruction, \
		cpu.integration_tests.test_sw_instruction, \
		cpu.integration_tests.test_add_instruction, \
		cpu.integration_tests.test_sub_instruction, \
		cpu.integration_tests.test_and_instruction, \
		cpu.integration_tests.test_or_instruction, \
		cpu.integration_tests.test_xor_instruction, \
		cpu.integration_tests.test_sll_instruction, \
		cpu.integration_tests.test_srl_instruction, \
		cpu.integration_tests.test_sra_instruction, \
		cpu.integration_tests.test_slt_instruction, \
		cpu.integration_tests.test_sltu_instruction, \
		cpu.integration_tests.test_addi_instruction, \
		cpu.integration_tests.test_andi_instruction, \
		cpu.integration_tests.test_ori_instruction, \
		cpu.integration_tests.test_xori_instruction, \
		cpu.integration_tests.test_slli_instruction, \
		cpu.integration_tests.test_srli_instruction, \
		cpu.integration_tests.test_srai_instruction, \
		cpu.integration_tests.test_slti_instruction, \
		cpu.integration_tests.test_sltiu_instruction, \
		cpu.integration_tests.test_program, \
		cpu.integration_tests.test_debug_halt, \
		cpu.integration_tests.test_debug_reset, \
		cpu.integration_tests.test_debug_ping, \
		cpu.integration_tests.test_debug_read_pc"	


TEST_TYPE ?= unit  

ifeq ($(TEST_TYPE),all)
.PHONY: all
all:
	$(MAKE) clean TEST_TYPE=unit
	$(MAKE) TEST_TYPE=unit
	$(MAKE) clean TEST_TYPE=integration
	$(MAKE) TEST_TYPE=integration
else

ifeq ($(TEST_TYPE),unit)
  TOPLEVEL = $(CPU_UNIT_TESTS_TOPLEVEL)
  MODULE = $(CPU_UNIT_TESTS_MODULE)
  VERILOG_SOURCES += ./cpu/unit_tests/cpu_unit_tests_harness.v
endif

ifeq ($(TEST_TYPE),integration)
  TOPLEVEL = $(CPU_INTEGRATION_TESTS_TOPLEVEL)
  MODULE = $(CPU_INTEGRATION_TESTS_MODULE)
  VERILOG_SOURCES += ./cpu/integration_tests/cpu_integration_tests_harness.v
endif

export SIM TOPLEVEL_LANG VERILOG_SOURCES TOPLEVEL MODULE EXTRA_ARGS PYTHONPATH

include $(shell cocotb-config --makefiles)/Makefile.sim
endif
