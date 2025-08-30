`timescale 1ns / 1ps

module comparator_unit #(parameter XLEN = 32, parameter REG_ADDR_WIDTH = 5)   (
    input [XLEN-1:0] i_Input_A,
    input [XLEN-1:0] i_Input_B,
    input [2:0] i_Compare_Select,
    output reg o_Cmp_Result
  );

  always @*
  begin
    case (i_Compare_Select)
      cpu.CMP_OP_BEQ:
        o_Cmp_Result = i_Input_A == i_Input_B;
      cpu.CMP_OP_BNE:
        o_Cmp_Result = i_Input_A != i_Input_B;
      cpu.CMP_OP_BLTU:
        o_Cmp_Result = i_Input_A < i_Input_B; // Unsigned less
      cpu.CMP_OP_BGEU:
        o_Cmp_Result = i_Input_A >= i_Input_B; // Unsigned greater
      cpu.CMP_OP_BLT:
        o_Cmp_Result = $signed(i_Input_A) < $signed(i_Input_B); // Signed less
      cpu.CMP_OP_BGE:
        o_Cmp_Result = $signed(i_Input_A) >= $signed(i_Input_B); // Signed greater
      default:
        o_Cmp_Result = 0; // Unknown operation, default to zero
    endcase
  end

endmodule
