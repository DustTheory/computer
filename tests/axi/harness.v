`timescale 1ns / 1ps
`include "../hdl/cpu/cpu_core_params.vh"
`include "../hdl/cpu/memory/memory.vh"

module axi_tests_harness ();

  wire [MEMORY_STATE_WIDTH:0] w_Mem_State;
  wire w_Mem_ready = w_Mem_State == IDLE;

  // verilator lint_off PINMISSING
  instruction_memory_axi instruction_memory_axi ();
  memory_axi memory_axi (.o_State(w_Mem_State));
  // verilator lint_on  PINMISSING
endmodule
