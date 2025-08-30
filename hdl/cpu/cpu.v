`timescale 1ns / 1ps
`include "cpu_core_params.vh"

module cpu #(
    parameter XLEN = 32,
    parameter REG_ADDR_WIDTH = 5
) (
    input i_Reset,
    input i_Clock,
    input [XLEN-1:0] i_Instruction,
    output [XLEN-1:0] o_Instruction_Addr
);

  // Load/Store types
  parameter LS_TYPE_LOAD_WORD = 0;
  parameter LS_TYPE_LOAD_HALF = 1;
  parameter LS_TYPE_LOAD_HALF_UNSIGNED = 2;
  parameter LS_TYPE_LOAD_BYTE = 3;
  parameter LS_TYPE_LOAD_BYTE_UNSIGNED = 4;
  parameter LS_TYPE_STORE_WORD = 5;
  parameter LS_TYPE_STORE_HALF = 6;
  parameter LS_TYPE_STORE_BYTE = 7;
  parameter LS_TYPE_NONE = 8;

  reg [XLEN-1:0] r_PC;  // Program Counter
  wire [XLEN-1:0] w_Immediate;
  wire [XLEN-1:0] w_PC_Next = r_PC + 4;

  // Outputs of the register file - Values at Rs1 and Rs2
  wire [XLEN-1:0] w_Reg_Source_1;
  wire [XLEN-1:0] w_Reg_Source_2;
  wire [XLEN-1:0] w_Dmem_Data;

  wire [ALU_SEL_WIDTH:0] w_Alu_Select;  // ALU opcode - comes from the control unit
  wire [CMP_SEL_WIDTH:0] w_Compare_Select;  // Comparator opcode - comes from the control unit
  wire [2:0] w_Imm_Select;  // Immediate type - comes from the control unit
  wire [4:0] w_Load_Store_Type;  // Load/Store type - comes from the control unit
  wire [XLEN-1:0] w_Alu_Result;  // Result of the ALU operation
  wire [XLEN-1:0] w_Compare_Result;  // Result of the comparison operation

  wire w_Port_A_Select;  // Selects Rs1 or PC for ALU input A
  wire w_Port_B_Select;  // Selects Rs2 or Immediate for ALU input B

  // Inputs for the ALU/Comparator - based off w_Port_A_Select and w_Port_B_Select
  wire w_Alu_Port_A = w_Port_A_Select ? w_Reg_Source_1 : r_PC;
  wire w_Alu_Port_B = w_Port_B_Select ? w_Reg_Source_2 : w_Immediate;
  wire w_Comp_Port_A = w_Reg_Source_1;
  wire w_Comp_Port_B = w_Port_B_Select ? w_Immediate : w_Reg_Source_2;

  // What data to write to the register file
  wire [REG_ADDR_WIDTH-1:0] w_Reg_Write_Select;

  wire w_Pc_Alu_Mux_Select;  // Selects between ALU result or PC for next instruction address
  wire w_Reg_Write_Enable;  // Enables writing to the register file
  wire w_Mem_Write_Enable;  // Enables writing to memory (not used in this example)

  reg [XLEN-1:0] w_Reg_Write_data;

  always @* begin
    case (w_Reg_Write_Select)
      REG_WRITE_ALU: w_Reg_Write_data = w_Alu_Result;
      REG_WRITE_CU: w_Reg_Write_data = w_Compare_Result;
      REG_WRITE_IMM: w_Reg_Write_data = w_Immediate;
      REG_WRITE_PC_NEXT: w_Reg_Write_data = w_PC_Next;
      REG_WRITE_DMEM: w_Reg_Write_data = w_Dmem_Data;
      default: w_Reg_Write_data = 0;  // Default case
    endcase
  end


  arithmetic_logic_unit alu (
      .i_Input_A(w_Reg_Source_1),
      .i_Input_B(w_Reg_Source_2),
      .i_Alu_Select(w_Alu_Select),
      .o_Alu_Result(w_Alu_Result)
  );

  comparator_unit comparator_unit (
      .i_Input_A(w_Comp_Port_A),
      .i_Input_B(w_Comp_Port_B),
      .i_Compare_Select(w_Compare_Select),
      .o_Compare_Result(w_Compare_Result)
  );

  register_file #(
      .XLEN(XLEN),
      .REG_ADDR_WIDTH(REG_ADDR_WIDTH)
  ) reg_file (
      .i_Clock(i_Clock),
      .i_Read_Addr_1(w_Reg_Source_1),
      .i_Read_Addr_2(w_Reg_Source_2),
      .i_Write_Addr(i_Instruction[11:7]),
      .i_Write_Data(w_Reg_Write_data),
      .i_Write_Enable(w_Reg_Write_Enable),
      .o_Read_Data_1(i_Instruction[19:15]),  // Rs1
      .o_Read_Data_2(i_Instruction[24:20])  // Rs2
  );

  control_unit #(
      .XLEN(XLEN),
      .REG_ADDR_WIDTH(REG_ADDR_WIDTH)
  ) cu (
      .i_Op_Code(i_Instruction[6:0]),
      .i_Funct3(i_Instruction[14:12]),
      .i_Funct7_Bit_5(i_Instruction[30]),
      .i_Branch_Enable(w_Compare_Result),
      .o_Port_A_Select(w_Port_A_Select),
      .o_Port_B_Select(w_Port_B_Select),
      .o_Reg_Write_Select(w_Reg_Write_Select),
      .o_Alu_Select(w_Alu_Select),
      .o_Cmp_Select(w_Compare_Select),
      .o_Imm_Select(w_Imm_Select),
      .o_Pc_Alu_Mux_Select(),
      .o_Reg_Write_Enable(w_Reg_Write_Enable),
      .o_Mem_Write_Enable(w_Mem_Write_Enable),
      .o_Load_Store_Type(w_Load_Store_Type)
  );

  memory #(
      .XLEN(XLEN),
      .REG_ADDR_WIDTH(REG_ADDR_WIDTH),
      .MEMORY_DEPTH(1024)
  ) mem (
      .i_Clock(i_Clock),
      .i_Load_Store_Type(w_Load_Store_Type),
      .i_Instruction_Addr(r_PC),
      .i_Data_Addr(w_Alu_Result),
      .i_Write_Data(w_Reg_Source_2),
      .i_Write_Enable(w_Mem_Write_Enable),
      .o_Read_Data(w_Dmem_Data),
      .o_Instruction(o_Instruction_Addr)
  );

  always @(posedge i_Clock, posedge i_Reset) begin
    if (i_Reset) begin
      r_PC <= 32'd0;
    end else begin
      r_PC <= w_Pc_Alu_Mux_Select ? w_Alu_Result : w_PC_Next;
    end
  end




endmodule
