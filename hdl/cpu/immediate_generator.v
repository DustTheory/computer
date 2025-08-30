`timescale 1ns / 1ps

module immediate_generator #(parameter XLEN = 32, parameter REG_ADDR_WIDTH = 5)   (
    input [2:0] i_Imm_Select,
    input [XLEN-1:7] i_Instruction_No_Opcode,
    output reg [XLEN-1:0] o_Immediate
  );

  always @*
  begin
    case (i_Imm_Select)
      cpu.IMM_U_TYPE:
        o_Immediate = $signed({i_Instruction_No_Opcode[31:12], 12'b0});
      cpu.IMM_J_TYPE:
        o_Immediate = $signed({
                                i_Instruction_No_Opcode[31],
                                i_Instruction_No_Opcode[19:12],
                                i_Instruction_No_Opcode[20],
                                i_Instruction_No_Opcode[30:21],
                                1'b0});
      cpu.IMM_I_TYPE:
        o_Immediate = $signed({i_Instruction_No_Opcode[31:20]});
      cpu.IMM_S_TYPE:
        o_Immediate = $signed({
                                i_Instruction_No_Opcode[31:25],
                                i_Instruction_No_Opcode[11:7]
                              });
      cpu.IMM_B_TYPE:
        o_Immediate = $signed({
                                i_Instruction_No_Opcode[31],
                                i_Instruction_No_Opcode[7],
                                i_Instruction_No_Opcode[30:25],
                                i_Instruction_No_Opcode[11:8],
                                1'b0
                              });

      cpu.IMM_UNKNOWN_TYPE:
        o_Immediate = 0;
    endcase
  end

endmodule
