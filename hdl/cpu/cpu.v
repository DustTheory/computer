`timescale 1ns / 1ps
`include "cpu_core_params.vh"

module cpu (
    input i_Reset,
    input i_Clock
);

  wire w_Instruction_Valid;
  wire w_Memory_Ready;
  wire w_Memory_Data_Valid;
  wire w_Stall = !w_Instruction_Valid || !w_Memory_Ready;

  reg [XLEN-1:0] r_PC;  // Program Counter
  wire [XLEN-1:0] w_Instruction;
  wire [XLEN-1:0] w_Immediate;
  wire [XLEN-1:0] w_PC_Next = r_PC + 4;

  // Outputs of the register file - Values at Rs1 and Rs2
  wire [XLEN-1:0] w_Reg_Source_1;
  wire [XLEN-1:0] w_Reg_Source_2;
  wire [XLEN-1:0] w_Dmem_Data;

  wire [ALU_SEL_WIDTH:0] w_Alu_Select;  // ALU opcode - comes from the control unit
  wire [CMP_SEL_WIDTH:0] w_Compare_Select;  // Comparator opcode - comes from the control unit
  wire [IMM_SEL_WIDTH:0] w_Imm_Select;  // Immediate type - comes from the control unit
  wire [LS_SEL_WIDTH:0] w_Load_Store_Type;  // Load/Store type - comes from the control unit
  wire [XLEN-1:0] w_Alu_Result;  // Result of the ALU operation
  // verilator lint_off UNOPTFLAT
  wire w_Compare_Result;  // Result of the comparison operation
  // verilator lint_on UNOPTFLAT

  wire w_Port_A_Select;  // Selects Rs1 or PC for ALU input A
  wire w_Port_B_Select;  // Selects Rs2 or Immediate for ALU input B

  // Inputs for the ALU/Comparator - based off w_Port_A_Select and w_Port_B_Select
  wire [XLEN-1:0] w_Alu_Port_A = w_Port_A_Select ? w_Reg_Source_1 : r_PC;
  wire [XLEN-1:0] w_Alu_Port_B = w_Port_B_Select ? w_Reg_Source_2 : w_Immediate;
  wire [XLEN-1:0] w_Comp_Port_A = w_Reg_Source_1;
  wire [XLEN-1:0] w_Comp_Port_B = w_Port_B_Select ? w_Immediate : w_Reg_Source_2;

  // What data to write to the register file
  wire [REG_ADDR_WIDTH-1:0] w_Reg_Write_Select;

  wire w_Pc_Alu_Mux_Select;  // Selects between ALU result or PC for next instruction address
  wire w_Reg_Write_Enable;  // Enables writing to the register file
  wire w_Mem_Write_Enable;  // Enables writing to memory (not used in this example)

  wire [REG_ADDR_WIDTH-1:0] w_Rs_1 = w_Instruction[19:15];
  wire [REG_ADDR_WIDTH-1:0] w_Rs_2 = w_Instruction[24:20];

  reg [XLEN-1:0] w_Reg_Write_data;

  always @* begin
    // if (!w_Stall) begin
      case (w_Reg_Write_Select)
        REG_WRITE_ALU: w_Reg_Write_data = w_Alu_Result;
        REG_WRITE_CU: w_Reg_Write_data = {31'b0, w_Compare_Result};
        REG_WRITE_IMM: w_Reg_Write_data = w_Immediate;
        REG_WRITE_PC_NEXT: w_Reg_Write_data = w_PC_Next;
        REG_WRITE_DMEM: w_Reg_Write_data = w_Dmem_Data;
        default: w_Reg_Write_data = 0;  // Default case
      endcase
    // end else begin
    //   w_Reg_Write_data = 0;
    // end
  end


  arithmetic_logic_unit alu (
      .i_Enable(!w_Stall),
      .i_Input_A(w_Alu_Port_A),
      .i_Input_B(w_Alu_Port_B),
      .i_Alu_Select(w_Alu_Select),
      .o_Alu_Result(w_Alu_Result)
  );

  comparator_unit comparator_unit (
      .i_Enable(!w_Stall),
      .i_Input_A(w_Comp_Port_A),
      .i_Input_B(w_Comp_Port_B),
      .i_Compare_Select(w_Compare_Select),
      .o_Compare_Result(w_Compare_Result)
  );

  register_file reg_file (
      .i_Enable(!w_Stall),
      .i_Clock(i_Clock),
      .i_Read_Addr_1(w_Rs_1),
      .i_Read_Addr_2(w_Rs_2),
      .i_Write_Addr(w_Instruction[11:7]),
      .i_Write_Data(w_Reg_Write_data),
      .i_Write_Enable(w_Reg_Write_Enable && w_Memory_Data_Valid),
      .o_Read_Data_1(w_Reg_Source_1),
      .o_Read_Data_2(w_Reg_Source_2)
  );

  control_unit cu (
      .i_Enable(!w_Stall),
      .i_Op_Code(w_Instruction[OP_CODE_WIDTH:0]),
      .i_Funct3(w_Instruction[14:12]),
      .i_Funct7_Bit_5(w_Instruction[30]),
      .i_Branch_Enable(w_Compare_Result),
      .o_Port_A_Select(w_Port_A_Select),
      .o_Port_B_Select(w_Port_B_Select),
      .o_Reg_Write_Select(w_Reg_Write_Select),
      .o_Alu_Select(w_Alu_Select),
      .o_Cmp_Select(w_Compare_Select),
      .o_Imm_Select(w_Imm_Select),
      .o_Pc_Alu_Mux_Select(w_Pc_Alu_Mux_Select),
      .o_Reg_Write_Enable(w_Reg_Write_Enable),
      .o_Mem_Write_Enable(w_Mem_Write_Enable),
      .o_Load_Store_Type(w_Load_Store_Type)
  );

  immediate_unit imm_unit (
      .i_Enable(!w_Stall),
      .i_Imm_Select(w_Imm_Select),
      .i_Instruction_No_Opcode(w_Instruction[XLEN-1:OP_CODE_WIDTH+1]),
      .o_Immediate(w_Immediate)
  );

  instruction_memory_axi instruction_memory (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock),
      .i_Instruction_Addr(r_PC),
      .o_Instruction(w_Instruction),
      .o_Instruction_Valid(w_Instruction_Valid)
  );

 memory_axi mem (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock),
      .i_Load_Store_Type(w_Load_Store_Type),
      .i_Write_Enable(w_Mem_Write_Enable),
      .i_Addr(w_Alu_Result),
      .i_Data(w_Reg_Source_2),
      .o_Data(w_Dmem_Data),
      .o_Ready(w_Memory_Ready),
      .o_Data_Valid(w_Memory_Data_Valid)
  );

  // memory #(
  //     .MEMORY_DEPTH(1024)
  // ) mem (
  //     .i_Enable(!w_Stall),
  //     .i_Clock(i_Clock),
  //     .i_Load_Store_Type(w_Load_Store_Type),
  //     .i_Write_Enable(w_Mem_Write_Enable),
  //     .i_Addr(w_Alu_Result),
  //     .i_Data(w_Reg_Source_2),
  //     .o_Data(w_Dmem_Data)
  // );

  always @(posedge i_Clock, posedge i_Reset) begin
    if (!w_Stall) begin
      if (i_Reset) begin
        r_PC <= 32'd0;
      end else begin
        r_PC <= w_Pc_Alu_Mux_Select ? w_Alu_Result : w_PC_Next;
      end
    end
  end


endmodule
