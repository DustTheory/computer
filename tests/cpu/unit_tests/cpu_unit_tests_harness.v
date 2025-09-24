`timescale 1ns / 1ps

module cpu_unit_tests_harness ();

  // verilator lint_off PINMISSING
  arithmetic_logic_unit alu (.i_Enable(1'b1));
  comparator_unit comparator_unit (.i_Enable(1'b1));
  immediate_unit immediate_unit (.i_Enable(1'b1));
  control_unit control_unit (.i_Enable(1'b1));
  register_file register_file (.i_Enable(1'b1));
  memory memory (.i_Enable(1'b1));
  instruction_memory_axi instruction_memory ();
  // verilator lint_on  PINMISSING
endmodule
