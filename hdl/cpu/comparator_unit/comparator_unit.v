`timescale 1ns / 1ps
`include "comparator_unit.vh"

module comparator_unit (
    input i_Enable,
    input [XLEN-1:0] i_Input_A,
    input [XLEN-1:0] i_Input_B,
    input [CMP_SEL_WIDTH:0] i_Compare_Select,
    output reg o_Compare_Result
);

  always @* begin
    if (i_Enable) begin
      case (i_Compare_Select)
        CMP_SEL_EQ: o_Compare_Result = i_Input_A == i_Input_B;
        CMP_SEL_NE: o_Compare_Result = i_Input_A != i_Input_B;
        CMP_SEL_LTU: o_Compare_Result = i_Input_A < i_Input_B;  // Unsigned less
        CMP_SEL_GEU: o_Compare_Result = i_Input_A >= i_Input_B;  // Unsigned greater
        CMP_SEL_LT: o_Compare_Result = $signed(i_Input_A) < $signed(i_Input_B);  // Signed less
        CMP_SEL_GE: o_Compare_Result = $signed(i_Input_A) >= $signed(i_Input_B);  // Signed greater
        default: o_Compare_Result = 0;  // Unknown operation, default to zero
      endcase
    end else begin
      o_Compare_Result = 0;
    end
  end

endmodule
