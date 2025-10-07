`timescale 1ns / 1ps

module cpu_unit_tests_harness ();

  wire [MEMORY_STATE_WIDTH:0] w_Mem_State;
  wire w_Mem_ready = w_Mem_State == IDLE;

  // verilator lint_off PINMISSING
  arithmetic_logic_unit alu (.i_Enable(1'b1));
  comparator_unit comparator_unit (.i_Enable(1'b1));
  immediate_unit immediate_unit (.i_Enable(1'b1));
  control_unit control_unit (.i_Enable(1'b1));
  register_file register_file (.i_Enable(1'b1));
  instruction_memory_axi instruction_memory_axi ();
  memory_axi memory_axi (.o_State(w_Mem_State));
  // verilator lint_on  PINMISSING
endmodule
