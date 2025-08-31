`timescale 1ns / 1ps
`include "arithmetic_logic_unit.vh"

module arithmetic_logic_unit (
    input [XLEN-1:0] i_Input_A,
    input [XLEN-1:0] i_Input_B,
    input [ALU_SEL_WIDTH:0] i_Alu_Select,
    output reg [XLEN-1:0] o_Alu_Result
);

  always @* begin
    case (i_Alu_Select)
      ALU_SEL_ADD: o_Alu_Result = i_Input_A + i_Input_B;  // Addition
      ALU_SEL_SUB: o_Alu_Result = i_Input_A - i_Input_B;  // Subtraction
      ALU_SEL_AND: o_Alu_Result = i_Input_A & i_Input_B;  // Bitwise AND
      ALU_SEL_OR: o_Alu_Result = i_Input_A | i_Input_B;  // Bitwise OR
      ALU_SEL_XOR: o_Alu_Result = i_Input_A ^ i_Input_B;  // Bitwise XOR
      ALU_SEL_SLL: o_Alu_Result = i_Input_A << i_Input_B[REG_ADDR_WIDTH-1:0];  // Shift Left Logical
      ALU_SEL_SRL:
      o_Alu_Result = i_Input_A >> i_Input_B[REG_ADDR_WIDTH-1:0];  // Shift Right Logical
      ALU_SEL_SRA:
      o_Alu_Result = $signed(i_Input_A) >>>
          i_Input_B[REG_ADDR_WIDTH-1:0];  // Shift Right Arithmetic
      ALU_SEL_UNKNOWN: o_Alu_Result = 0;  // Unknown operation, default to zero
      default: o_Alu_Result = 0;
    endcase
  end

endmodule
