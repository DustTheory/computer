`timescale 1ns / 1ps

module cpu_unit_tests_harness ();

  // verilator lint_off PINMISSING
  arithmetic_logic_unit alu ();
  comparator_unit comparator_unit ();
  immediate_unit immediate_unit ();
  control_unit control_unit ();
  register_file register_file ();
  memory memory ();
  instruction_memory instruction_memory ();
  // verilator lint_on  PINMISSING
endmodule
