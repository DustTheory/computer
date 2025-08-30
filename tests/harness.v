`timescale 1ns / 1ps

module harness #(
    parameter XLEN = 32,
    parameter REG_ADDR_WIDTH = 5
) ();

  // verilator lint_off PINMISSING
  arithmetic_logic_unit alu ();
  comparator_unit comparator_unit ();
  immediate_unit immediate_unit ();
  control_unit control_unit ();
  register_file register_file ();
  // verilator lint_on  PINMISSING
endmodule
