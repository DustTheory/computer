`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "./arithmetic_logic_unit/arithmetic_logic_unit.vh"
`include "./comparator_unit/comparator_unit.vh"

module control_unit #(
    parameter XLEN = 32,
    parameter REG_ADDR_WIDTH = 5
) (
    input [6:0] i_Op_Code,
    input [2:0] i_Funct3,
    input i_Funct7_Bit_5,
    input i_Branch_Enable,
    output reg [REG_ADDR_WIDTH-1:0] o_Port_A_Select,
    output reg [REG_ADDR_WIDTH-1:0] o_Port_B_Select,
    output reg [REG_ADDR_WIDTH-1:0] o_Reg_Write_Select,
    output reg [ALU_SEL_WIDTH:0] o_Alu_Select,
    output reg [CMP_SEL_WIDTH:0] o_Cmp_Select,
    output reg [3:0] o_Imm_Select,
    output reg [4:0] o_Load_Store_Type,
    output reg o_Pc_Alu_Mux_Select,
    output reg o_Reg_Write_Enable,
    output reg o_Mem_Write_Enable
);

  localparam OP_J_TYPE = 7'b1101111;
  localparam OP_B_TYPE = 7'b1100011;
  localparam OP_S_TYPE = 7'b0100011;
  localparam OP_R_TYPE = 7'b0110011;
  localparam OP_U_TYPE_LUI = 7'b0110111;
  localparam OP_U_TYPE_AUIPC = 7'b0010111;
  localparam OP_I_TYPE_JALR = 7'b1100111;
  localparam OP_I_TYPE_LOAD = 7'b0000011;
  localparam OP_I_TYPE_ALU = 7'b0010011;
  // localparam OP_I_TYPE_SYS   = 7'b1110011; // Syscall stuff, not implemented

  localparam FUNC3_ALU_ADD_SUB = 3'b000;
  localparam FUNC3_ALU_SLL = 3'b001;
  localparam FUNC3_ALU_SLT = 3'b010;
  localparam FUNC3_ALU_SLTU = 3'b011;
  localparam FUNC3_ALU_XOR = 3'b100;
  localparam FUNC3_ALU_SRL_SRA = 3'b101;
  localparam FUNC3_ALU_OR = 3'b110;
  localparam FUNC3_ALU_AND = 3'b111;

  localparam FUNC3_LOAD_LB = 3'b000;
  localparam FUNC3_LOAD_LH = 3'b001;
  localparam FUNC3_LOAD_LW = 3'b010;
  localparam FUNC3_LOAD_LBU = 3'b100;
  localparam FUNC3_LOAD_LHU = 3'b101;

  localparam FUNC3_BRANCH_BEQ = 3'b000;
  localparam FUNC3_BRANCH_BNE = 3'b001;
  localparam FUNC3_BRANCH_BLT = 3'b100;
  localparam FUNC3_BRANCH_BGE = 3'b101;
  localparam FUNC3_BRANCH_BLTU = 3'b110;
  localparam FUNC3_BRANCH_BGEU = 3'b111;

  always @* begin
    case (i_Op_Code)
      OP_R_TYPE: begin
        o_Port_A_Select = 1'b1;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Imm_Select = cpu.IMM_UNKNOWN_TYPE;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
        case (i_Funct3)
          FUNC3_ALU_ADD_SUB: begin
            o_Alu_Select = (i_Funct7_Bit_5) ? ALU_SEL_SUB : ALU_SEL_ADD;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SLL: begin
            o_Alu_Select = ALU_SEL_SLL;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SLT: begin
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_BLT;
            o_Port_B_Select = 1'b0;
            o_Reg_Write_Select = cpu.REG_WRITE_CU;
          end
          FUNC3_ALU_SLTU: begin
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_BLTU;
            o_Port_B_Select = 1'b0;
            o_Reg_Write_Select = cpu.REG_WRITE_CU;
          end
          FUNC3_ALU_XOR: begin
            o_Alu_Select = ALU_SEL_XOR;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SRL_SRA: begin
            o_Alu_Select = (i_Funct7_Bit_5) ? ALU_SEL_SRL : ALU_SEL_SRA;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_OR: begin
            o_Alu_Select = ALU_SEL_OR;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_AND: begin
            o_Alu_Select = ALU_SEL_AND;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Port_B_Select = 1'b1;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          default: begin
            o_Port_B_Select = 1'b1;
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_NONE;
          end
        endcase
      end
      OP_U_TYPE_LUI: begin
        o_Port_A_Select = 1'b0;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Alu_Select = ALU_SEL_UNKNOWN;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_U_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_IMM;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
      end
      OP_U_TYPE_AUIPC: begin
        o_Port_A_Select = 1'b0;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Alu_Select = ALU_SEL_ADD;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_U_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_ALU;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
      end
      OP_J_TYPE: begin
        o_Port_A_Select = 1'b0;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b1;
        o_Alu_Select = ALU_SEL_ADD;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_J_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_PC_NEXT;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
      end
      OP_I_TYPE_ALU: begin
        o_Port_A_Select = 1'b1;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Imm_Select = cpu.IMM_I_TYPE;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
        case (i_Funct3)
          FUNC3_ALU_ADD_SUB: begin
            o_Alu_Select = (i_Funct7_Bit_5) ? ALU_SEL_SUB : ALU_SEL_ADD;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SLL: begin
            o_Alu_Select = ALU_SEL_SLL;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SLT: begin
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_BLT;
            o_Reg_Write_Select = cpu.REG_WRITE_CU;
          end
          FUNC3_ALU_SLTU: begin
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_BLTU;
            o_Reg_Write_Select = cpu.REG_WRITE_CU;
          end
          FUNC3_ALU_XOR: begin
            o_Alu_Select = ALU_SEL_XOR;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_SRL_SRA: begin
            o_Alu_Select = (i_Funct7_Bit_5) ? ALU_SEL_SRL : ALU_SEL_SRA;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_OR: begin
            o_Alu_Select = ALU_SEL_OR;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          FUNC3_ALU_AND: begin
            o_Alu_Select = ALU_SEL_AND;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_ALU;
          end
          default: begin
            o_Alu_Select = ALU_SEL_UNKNOWN;
            o_Cmp_Select = CMP_SEL_UNKNOWN;
            o_Reg_Write_Select = cpu.REG_WRITE_NONE;
          end
        endcase
      end
      OP_I_TYPE_JALR: begin
        o_Port_A_Select = 1'b1;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b1;
        o_Alu_Select = ALU_SEL_ADD;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_I_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_ALU;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
      end
      OP_I_TYPE_LOAD: begin
        o_Port_A_Select = 1'b1;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b1;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Alu_Select = ALU_SEL_ADD;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_I_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_DMEM;
        case (i_Funct3)
          FUNC3_LOAD_LB: o_Load_Store_Type = cpu.LS_TYPE_LOAD_BYTE;
          FUNC3_LOAD_LH: o_Load_Store_Type = cpu.LS_TYPE_LOAD_HALF;
          FUNC3_LOAD_LW: o_Load_Store_Type = cpu.LS_TYPE_LOAD_WORD;
          FUNC3_LOAD_LBU: o_Load_Store_Type = cpu.LS_TYPE_LOAD_BYTE_UNSIGNED;
          FUNC3_LOAD_LHU: o_Load_Store_Type = cpu.LS_TYPE_LOAD_HALF_UNSIGNED;
          default: o_Load_Store_Type = cpu.LS_TYPE_NONE;
        endcase
      end
      OP_S_TYPE: begin
        o_Port_A_Select = 1'b1;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b1;
        o_Reg_Write_Enable = 1'b0;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Alu_Select = ALU_SEL_ADD;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_S_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_NONE;
        case (i_Funct3)
          FUNC3_LOAD_LB: o_Load_Store_Type = cpu.LS_TYPE_STORE_BYTE;
          FUNC3_LOAD_LH: o_Load_Store_Type = cpu.LS_TYPE_STORE_HALF;
          FUNC3_LOAD_LW: o_Load_Store_Type = cpu.LS_TYPE_STORE_WORD;
          default: o_Load_Store_Type = cpu.LS_TYPE_NONE;
        endcase
      end
      OP_B_TYPE: begin
        o_Port_A_Select = 1'b0;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b0;
        o_Pc_Alu_Mux_Select = i_Branch_Enable;
        o_Alu_Select = ALU_SEL_ADD;
        o_Imm_Select = cpu.IMM_B_TYPE;
        o_Reg_Write_Select = cpu.REG_WRITE_NONE;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
        case (i_Funct3)
          FUNC3_BRANCH_BEQ: o_Cmp_Select = CMP_SEL_BEQ;
          FUNC3_BRANCH_BNE: o_Cmp_Select = CMP_SEL_BNE;
          FUNC3_BRANCH_BLT: o_Cmp_Select = CMP_SEL_BLT;
          FUNC3_BRANCH_BGE: o_Cmp_Select = CMP_SEL_BGE;
          FUNC3_BRANCH_BLTU: o_Cmp_Select = CMP_SEL_BLTU;
          FUNC3_BRANCH_BGEU: o_Cmp_Select = CMP_SEL_BGEU;
          default: o_Cmp_Select = CMP_SEL_UNKNOWN;
        endcase
      end
      default: begin
        o_Port_A_Select = 1'b0;
        o_Port_B_Select = 1'b0;
        o_Mem_Write_Enable = 1'b0;
        o_Reg_Write_Enable = 1'b0;
        o_Pc_Alu_Mux_Select = 1'b0;
        o_Alu_Select = ALU_SEL_UNKNOWN;
        o_Cmp_Select = CMP_SEL_UNKNOWN;
        o_Imm_Select = cpu.IMM_UNKNOWN_TYPE;
        o_Load_Store_Type = cpu.LS_TYPE_NONE;
        o_Reg_Write_Select = cpu.REG_WRITE_NONE;
      end
    endcase
  end

endmodule
