`timescale 1ns / 1ps

module arithmetic_logic_unit #(parameter XLEN = 32, parameter REG_ADDR_WIDTH = 5)   (
    input [XLEN-1:0] i_Input_A,
    input [XLEN-1:0] i_Input_B,
    input [3:0] i_Alu_Select,
    output reg [XLEN-1:0] o_Alu_Result
  );

  always @*
  begin
    case (i_Alu_Select)
      cpu.ALU_OP_ADD:
        o_Alu_Result = i_Input_A + i_Input_B; // Addition
      cpu.ALU_OP_SUB:
        o_Alu_Result = i_Input_A - i_Input_B; // Subtraction
      cpu.ALU_OP_AND:
        o_Alu_Result = i_Input_A & i_Input_B; // Bitwise AND
      cpu.ALU_OP_OR:
        o_Alu_Result = i_Input_A | i_Input_B; // Bitwise OR
      cpu.ALU_OP_XOR:
        o_Alu_Result = i_Input_A ^ i_Input_B; // Bitwise XOR
      cpu.ALU_OP_SLL:
        o_Alu_Result = i_Input_A << i_Input_B[REG_ADDR_WIDTH-1:0]; // Shift Left Logical
      cpu.ALU_OP_SRL:
        o_Alu_Result = i_Input_A >> i_Input_B[REG_ADDR_WIDTH-1:0]; // Shift Right Logical
      cpu.ALU_OP_SRA:
        o_Alu_Result = i_Input_A >>> i_Input_B[REG_ADDR_WIDTH-1:0]; // Shift Right Arithmetic
      cpu.ALU_OP_UNKNOWN:
        o_Alu_Result = 0; // Unknown operation, default to zero
      default:
        o_Alu_Result = 0;
    endcase
  end

endmodule
