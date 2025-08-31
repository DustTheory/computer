`timescale 1ns / 1ps
`include "../cpu_core_params.vh"

module instruction_memory #(
    parameter MEMORY_DEPTH = 1024
) (
    input i_Clock,
    input [XLEN-1:0] i_Instruction_Addr,
    output reg [XLEN-1:0] o_Instruction
);

  reg [XLEN-1:0] Memory_Array[0:MEMORY_DEPTH-1];

  always @(i_Clock) begin
    o_Instruction = Memory_Array[i_Instruction_Addr>>2];
  end

endmodule
