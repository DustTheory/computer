`timescale 1ns / 1ps
`include "comparator_unit.vh"

module comparator_unit (
    input [XLEN-1:0] i_Input_A,
    input [XLEN-1:0] i_Input_B,
    input [CMP_SEL_WIDTH:0] i_Compare_Select,
    output reg o_Compare_Result
);

  always @* begin
    case (i_Compare_Select)
      CMP_SEL_BEQ: o_Compare_Result = i_Input_A == i_Input_B;
      CMP_SEL_BNE: o_Compare_Result = i_Input_A != i_Input_B;
      CMP_SEL_BLTU: o_Compare_Result = i_Input_A < i_Input_B;  // Unsigned less
      CMP_SEL_BGEU: o_Compare_Result = i_Input_A >= i_Input_B;  // Unsigned greater
      CMP_SEL_BLT: o_Compare_Result = $signed(i_Input_A) < $signed(i_Input_B);  // Signed less
      CMP_SEL_BGE: o_Compare_Result = $signed(i_Input_A) >= $signed(i_Input_B);  // Signed greater
      default: o_Compare_Result = 0;  // Unknown operation, default to zero
    endcase
  end

endmodule
