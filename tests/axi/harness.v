`timescale 1ns / 1ps

module stupid_harness ();

  // verilator lint_off PINMISSING
  instruction_memory_axi instruction_memory_axi ();
  // verilator lint_on  PINMISSING
endmodule
