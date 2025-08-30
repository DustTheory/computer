`timescale 1ns / 1ps
`include "immediate_unit.vh"

module immediate_unit (
    input [IMM_SEL_WIDTH:0] i_Imm_Select,
    input [XLEN-1:7] i_Instruction_No_Opcode,
    output reg [XLEN-1:0] o_Immediate
);

  // verilator lint_off WIDTH
  always @* begin
    case (i_Imm_Select)
      IMM_U_TYPE: o_Immediate = {i_Instruction_No_Opcode[31:12], 12'b0};
      IMM_J_TYPE:
      o_Immediate = $signed(
          {
            i_Instruction_No_Opcode[31],
            i_Instruction_No_Opcode[19:12],
            i_Instruction_No_Opcode[20],
            i_Instruction_No_Opcode[30:21],
            1'b0
          }
      );
      IMM_I_TYPE: o_Immediate = $signed({i_Instruction_No_Opcode[31:20]});
      IMM_S_TYPE:
      o_Immediate = $signed({i_Instruction_No_Opcode[31:25], i_Instruction_No_Opcode[11:7]});
      IMM_B_TYPE:
      o_Immediate = $signed(
          {
            i_Instruction_No_Opcode[31],
            i_Instruction_No_Opcode[7],
            i_Instruction_No_Opcode[30:25],
            i_Instruction_No_Opcode[11:8],
            1'b0
          }
      );
      IMM_UNKNOWN_TYPE: o_Immediate = 0;
      default: o_Immediate = 0;
    endcase
  end
  // verilator lint_on  WIDTH

endmodule
