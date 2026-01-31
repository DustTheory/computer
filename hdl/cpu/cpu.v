`timescale 1ns / 1ps
`include "cpu_core_params.vh"
`include "memory.vh"

module cpu (
    input i_Reset,
    input i_Clock,
    input i_Init_Calib_Complete,
    input i_Uart_Tx_In,

    output o_Uart_Rx_Out,

    // AXI INTERFACE FOR DATA MEMORY
    output [31:0] s_data_memory_axil_araddr,
    output s_data_memory_axil_arvalid,
    input s_data_memory_axil_arready,
    input [31:0] s_data_memory_axil_rdata,
    input s_data_memory_axil_rvalid,
    output s_data_memory_axil_rready,
    output [31:0] s_data_memory_axil_awaddr,
    output s_data_memory_axil_awvalid,
    input s_data_memory_axil_awready,
    output [31:0] s_data_memory_axil_wdata,
    output [3:0] s_data_memory_axil_wstrb,
    output s_data_memory_axil_wvalid,
    input s_data_memory_axil_wready,
    input [1:0] s_data_memory_axil_bresp,
    input s_data_memory_axil_bvalid,
    output s_data_memory_axil_bready,

    // AXI INTERFACE FOR INSTRUCTION MEMORY
    output [31:0] s_instruction_memory_axil_araddr,
    output s_instruction_memory_axil_arvalid,
    input s_instruction_memory_axil_arready,
    input [31:0] s_instruction_memory_axil_rdata,
    input s_instruction_memory_axil_rvalid,
    output s_instruction_memory_axil_rready,
    output [31:0] s_instruction_memory_axil_awaddr,
    output s_instruction_memory_axil_awvalid,
    input s_instruction_memory_axil_awready,
    output [31:0] s_instruction_memory_axil_wdata,
    output [3:0] s_instruction_memory_axil_wstrb,
    output s_instruction_memory_axil_wvalid,
    input s_instruction_memory_axil_wready,
    input [1:0] s_instruction_memory_axil_bresp,
    input s_instruction_memory_axil_bvalid,
    output s_instruction_memory_axil_bready
);

  // Debug peripheral wires
  wire w_Debug_Reg_Read_Enable;
  wire [REG_ADDR_WIDTH-1:0] w_Debug_Reg_Read_Addr;

  wire w_Debug_Reg_Write_Enable;
  wire [REG_ADDR_WIDTH-1:0] w_Debug_Reg_Write_Addr;
  wire [XLEN-1:0] w_Debug_Reg_Write_Data;

  wire w_Debug_Write_PC_Enable;
  wire [XLEN-1:0] w_Debug_Write_PC_Data;

  wire w_Debug_Memory_LS_Enable;
  wire [LS_SEL_WIDTH:0] w_Debug_Memory_LS_Type;
  wire w_Debug_Memory_LS_Write_Enable;
  wire [XLEN-1:0] w_Debug_Memory_LS_Address;
  wire [XLEN-1:0] w_Debug_Memory_LS_Data;

  wire w_Debug_Reset;
  wire w_Debug_Stall;

  wire w_Instruction_Valid;

  reg [XLEN-1:0] r_PC;  // Program Counter
  wire [XLEN-1:0] w_Instruction;
  wire [XLEN-1:0] w_Immediate;
  wire [XLEN-1:0] w_PC_Next = r_PC + 4;

  wire w_Flush_Pipeline; // Flag to flush pipeline on branches
  reg r_Flushing_Pipeline; // Indicates that the pipeline is currently being flushed

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

  wire [REG_ADDR_WIDTH-1:0] w_Rs_1 = w_Debug_Reg_Read_Enable ? w_Debug_Reg_Read_Addr : w_Instruction[19:15];
  wire [REG_ADDR_WIDTH-1:0] w_Rs_2 = w_Instruction[24:20];

  // Stage2 (Memory/Wait) pipeline registers
  reg r_S2_Valid;
  reg [LS_SEL_WIDTH:0] r_S2_Load_Store_Type;
  reg r_S2_Mem_Write_Enable;
  reg [XLEN-1:0] r_S2_Alu_Result;
  reg [XLEN-1:0] r_S2_Store_Data;
  reg [REG_ADDR_WIDTH-1:0] r_S2_Rd;
  reg r_S2_Rd_Write_Enable;
  reg [REG_ADDR_WIDTH-1:0] r_S2_Wb_Src;
  reg [XLEN-1:0] r_S2_Immediate;
  reg [XLEN-1:0] r_S2_PC_Next;
  reg [XLEN-1:0] r_S2_PC_Fetch;
  reg r_S2_Compare_Result;
  reg [XLEN-1:0] r_S2_Load_Data;

  // Stage3 (Writeback) pipeline registers
  reg r_S3_Valid;
  reg [LS_SEL_WIDTH:0] r_S3_Load_Store_Type;
  reg [XLEN-1:0] r_S3_Alu_Result;
  reg [REG_ADDR_WIDTH-1:0] r_S3_Rd;
  reg r_S3_Rd_Write_Enable;
  reg [REG_ADDR_WIDTH-1:0] r_S3_Wb_Src;
  reg [XLEN-1:0] r_S3_Immediate;
  reg [XLEN-1:0] r_S3_PC_Next;
  reg [XLEN-1:0] r_S3_PC_Fetch;
  reg r_S3_Compare_Result;
  reg [XLEN-1:0] r_S3_Load_Data;
  wire w_S3_Is_Load = f_Is_Load(r_S3_Load_Store_Type);
  wire w_S3_Is_Store = f_Is_Store(r_S3_Load_Store_Type);

  reg [XLEN-1:0] w_Wb_Data;
  wire w_Wb_Enable   = r_S3_Valid && r_S3_Rd_Write_Enable && !w_S3_Is_Store && (!w_S3_Is_Load || 1'b1);


  /*----------------PIPELINE STAGE 1----------------*/

  arithmetic_logic_unit alu (
      .i_Enable(w_Instruction_Valid),
      .i_Input_A(w_Alu_Port_A),
      .i_Input_B(w_Alu_Port_B),
      .i_Alu_Select(w_Alu_Select),
      .o_Alu_Result(w_Alu_Result)
  );

  comparator_unit comparator_unit (
      .i_Enable(w_Instruction_Valid),
      .i_Input_A(w_Comp_Port_A),
      .i_Input_B(w_Comp_Port_B),
      .i_Compare_Select(w_Compare_Select),
      .o_Compare_Result(w_Compare_Result)
  );

  register_file reg_file (
      .i_Reset(w_Reset),
      .i_Enable(w_Instruction_Valid || w_Wb_Enable || w_Debug_Reg_Write_Enable || w_Debug_Reg_Read_Enable),
      .i_Clock(i_Clock),
      .i_Read_Addr_1(w_Rs_1),
      .i_Read_Addr_2(w_Rs_2),
      .i_Write_Addr(w_Debug_Reg_Write_Enable ? w_Debug_Reg_Write_Addr : r_S3_Rd),
      .i_Write_Data(w_Debug_Reg_Write_Enable ? w_Debug_Reg_Write_Data : w_Wb_Data),
      .i_Write_Enable(w_Debug_Reg_Write_Enable || w_Wb_Enable),
      .o_Read_Data_1(w_Reg_Source_1),
      .o_Read_Data_2(w_Reg_Source_2)
  );

  control_unit cu (
      .i_Enable(w_Instruction_Valid),
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
      .o_Load_Store_Type(w_Load_Store_Type),
      .o_Flush_Pipeline(w_Flush_Pipeline)
  );

  immediate_unit imm_unit (
      .i_Enable(w_Instruction_Valid),
      .i_Imm_Select(w_Imm_Select),
      .i_Instruction_No_Opcode(w_Instruction[XLEN-1:OP_CODE_WIDTH+1]),
      .o_Immediate(w_Immediate)
  );

  instruction_memory_axi instruction_memory (
      .i_Reset(w_Reset),
      .i_Clock(i_Clock),
      .i_Enable_Fetch(w_Enable_Instruction_Fetch),
      .i_Instruction_Addr(r_PC),
      .o_Instruction(w_Instruction),
      .o_Instruction_Valid(w_Instruction_Valid),
      .s_axil_araddr(s_instruction_memory_axil_araddr),
      .s_axil_arvalid(s_instruction_memory_axil_arvalid),
      .s_axil_arready(s_instruction_memory_axil_arready),
      .s_axil_rdata(s_instruction_memory_axil_rdata),
      .s_axil_rvalid(s_instruction_memory_axil_rvalid),
      .s_axil_rready(s_instruction_memory_axil_rready),
      .s_axil_awaddr(s_instruction_memory_axil_awaddr),
      .s_axil_awvalid(s_instruction_memory_axil_awvalid),
      .s_axil_awready(s_instruction_memory_axil_awready),
      .s_axil_wdata(s_instruction_memory_axil_wdata),
      .s_axil_wstrb(s_instruction_memory_axil_wstrb),
      .s_axil_wvalid(s_instruction_memory_axil_wvalid),
      .s_axil_wready(s_instruction_memory_axil_wready),
      .s_axil_bresp(s_instruction_memory_axil_bresp),
      .s_axil_bvalid(s_instruction_memory_axil_bvalid),
      .s_axil_bready(s_instruction_memory_axil_bready)
  );


  /*----------------PIPELINE STAGE 2----------------*/

  wire [MEMORY_STATE_WIDTH:0] w_Memory_State;

  function reg f_Is_Load(input [LS_SEL_WIDTH:0] v);
    begin
      case (v)
        LS_TYPE_LOAD_WORD,
        LS_TYPE_LOAD_HALF,
        LS_TYPE_LOAD_HALF_UNSIGNED,
        LS_TYPE_LOAD_BYTE,
        LS_TYPE_LOAD_BYTE_UNSIGNED:
        f_Is_Load = 1'b1;
        default: f_Is_Load = 1'b0;
      endcase
    end
  endfunction

  function reg f_Is_Store(input [LS_SEL_WIDTH:0] v);
    begin
      case (v)
        LS_TYPE_STORE_WORD, LS_TYPE_STORE_HALF, LS_TYPE_STORE_BYTE: f_Is_Store = 1'b1;
        default: f_Is_Store = 1'b0;
      endcase
    end
  endfunction

  wire w_S2_Is_Load = r_S2_Valid && f_Is_Load(r_S2_Load_Store_Type);
  wire w_S2_Is_Store = r_S2_Valid && f_Is_Store(r_S2_Load_Store_Type);

  // Memory state helper flags
  wire w_Mem_Read_Done = (w_Memory_State == READ_SUCCESS);
  wire w_Mem_Write_Done = (w_Memory_State == WRITE_SUCCESS);
  wire w_Mem_Busy = (w_Memory_State != IDLE);

  wire w_Reset = i_Reset || w_Debug_Reset;

  wire w_Enable_Instruction_Fetch = i_Init_Calib_Complete && !w_Debug_Stall && !r_Flushing_Pipeline;
  wire w_Stall_S1 = !i_Init_Calib_Complete || (r_S2_Valid && (w_S2_Is_Load || w_S2_Is_Store) && !(w_Mem_Read_Done || w_Mem_Write_Done));
  wire w_Pipeline_Flushed = !w_Instruction_Valid && !r_S2_Valid && !r_S3_Valid;

  wire [LS_SEL_WIDTH:0] w_Memory_Load_Store_type = w_Debug_Memory_LS_Enable ? w_Debug_Memory_LS_Type : r_S2_Load_Store_Type;
  wire w_Memory_Write_Enable = w_Debug_Memory_LS_Enable ? w_Debug_Memory_LS_Write_Enable : r_S2_Mem_Write_Enable;
  wire [XLEN-1:0] w_Memory_Addr = w_Debug_Memory_LS_Enable ? w_Debug_Memory_LS_Address : r_S2_Alu_Result;
  wire [XLEN-1:0] w_Memory_Data = w_Debug_Memory_LS_Enable ? w_Debug_Memory_LS_Data : r_S2_Store_Data;
  
  // Memory interface driven from S2
  memory_axi mem (
      .i_Reset(w_Reset),
      .i_Clock(i_Clock),
      .i_Enable(i_Init_Calib_Complete),
      .i_Load_Store_Type(w_Memory_Load_Store_type),
      .i_Write_Enable(w_Memory_Write_Enable),
      .i_Addr(w_Memory_Addr),
      .i_Data(w_Memory_Data),
      .o_Data(w_Dmem_Data),
      .o_State(w_Memory_State),
      .s_axil_araddr(s_data_memory_axil_araddr),
      .s_axil_arvalid(s_data_memory_axil_arvalid),
      .s_axil_arready(s_data_memory_axil_arready),
      .s_axil_rdata(s_data_memory_axil_rdata),
      .s_axil_rvalid(s_data_memory_axil_rvalid),
      .s_axil_rready(s_data_memory_axil_rready),
      .s_axil_awaddr(s_data_memory_axil_awaddr),
      .s_axil_awvalid(s_data_memory_axil_awvalid),
      .s_axil_awready(s_data_memory_axil_awready),
      .s_axil_wdata(s_data_memory_axil_wdata),
      .s_axil_wstrb(s_data_memory_axil_wstrb),
      .s_axil_wvalid(s_data_memory_axil_wvalid),
      .s_axil_wready(s_data_memory_axil_wready),
      .s_axil_bresp(s_data_memory_axil_bresp),
      .s_axil_bvalid(s_data_memory_axil_bvalid),
      .s_axil_bready(s_data_memory_axil_bready)
  );

  // Pipeline progression
  always @(posedge i_Clock) begin
    if (w_Reset) begin
      r_S2_Valid <= 1'b0;
      r_S3_Valid <= 1'b0;
      r_S2_Load_Store_Type <= LS_TYPE_NONE;
      r_S3_Load_Store_Type <= LS_TYPE_NONE;
      r_S2_Rd_Write_Enable <= 1'b0;
      r_S3_Rd_Write_Enable <= 1'b0;
      r_Flushing_Pipeline <= 1'b0;
    end else begin
      // Capture load data when ready
      if (w_Mem_Read_Done && w_S2_Is_Load) r_S2_Load_Data <= w_Dmem_Data;

      if(w_Pipeline_Flushed) begin
        if(r_Flushing_Pipeline)
          r_Flushing_Pipeline <= 1'b0;
      end else begin
        if(w_Flush_Pipeline && !w_Pipeline_Flushed)
          r_Flushing_Pipeline <= 1'b1;
      end

      if (!w_Stall_S1) begin
        // S2 -> S3
        r_S3_Valid           <= r_S2_Valid;
        r_S3_Load_Store_Type <= r_S2_Load_Store_Type;
        r_S3_Alu_Result      <= r_S2_Alu_Result;
        r_S3_Rd              <= r_S2_Rd;
        r_S3_Rd_Write_Enable <= r_S2_Rd_Write_Enable;
        r_S3_Wb_Src          <= r_S2_Wb_Src;
        r_S3_Immediate       <= r_S2_Immediate;
        r_S3_PC_Next         <= r_S2_PC_Next;
        r_S3_PC_Fetch        <= r_S2_PC_Fetch;
        r_S3_Compare_Result  <= r_S2_Compare_Result;
        if (w_Mem_Read_Done && w_S2_Is_Load) r_S3_Load_Data <= w_Dmem_Data;
        else r_S3_Load_Data <= r_S2_Load_Data;

        // Stage1 -> S2 capture (new instruction)
        r_S2_Valid            <= w_Instruction_Valid;
        r_S2_Load_Store_Type  <= w_Load_Store_Type;
        r_S2_Mem_Write_Enable <= w_Mem_Write_Enable;
        r_S2_Alu_Result       <= w_Alu_Result;
        r_S2_Store_Data       <= w_Reg_Source_2;
        r_S2_Rd               <= w_Instruction[11:7];
        r_S2_Rd_Write_Enable  <= w_Reg_Write_Enable;
        r_S2_Wb_Src           <= w_Reg_Write_Select;
        r_S2_Immediate        <= w_Immediate;
        r_S2_PC_Next          <= w_PC_Next;
        r_S2_PC_Fetch         <= r_PC;
        r_S2_Compare_Result   <= w_Compare_Result;
        if (!w_Instruction_Valid) r_S2_Load_Data <= {XLEN{1'b0}};
      end
      // else stall
    end
  end

  always @* begin
    case (r_S3_Wb_Src)
      REG_WRITE_ALU:     w_Wb_Data = r_S3_Alu_Result;
      REG_WRITE_CU:      w_Wb_Data = {31'b0, r_S3_Compare_Result};
      REG_WRITE_IMM:     w_Wb_Data = r_S3_Immediate;
      REG_WRITE_PC_NEXT: w_Wb_Data = r_S3_PC_Next;
      REG_WRITE_DMEM:    w_Wb_Data = r_S3_Load_Data;
      default:           w_Wb_Data = {XLEN{1'b0}};
    endcase
  end

  wire w_Store_Commit = w_Mem_Write_Done && w_S2_Is_Store && r_S2_Valid;
  wire w_Retire_Reg = w_Wb_Enable;
  wire w_Retire = w_Retire_Reg || w_Store_Commit;

  always @(posedge i_Clock) begin
    if (w_Reset) begin
      r_PC <= CPU_BASE_ADDR;
    end else begin
      if(w_Debug_Write_PC_Enable && w_Pipeline_Flushed) begin
        r_PC <= w_Debug_Write_PC_Data;
      end else if (!w_Stall_S1 && w_Instruction_Valid && w_Enable_Instruction_Fetch) begin
        r_PC <= w_Pc_Alu_Mux_Select ? w_Alu_Result : w_PC_Next;
      end
    end
  end

  /*----------------DEBUG PERIPHERAL----------------*/

  debug_peripheral debug_peripheral (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock),
      .i_Uart_Tx_In(i_Uart_Tx_In),

      .i_PC(r_PC),
      .i_Pipeline_Flushed(w_Pipeline_Flushed),

      .o_Uart_Rx_Out(o_Uart_Rx_Out),
      .o_Halt_Cpu(w_Debug_Stall),
      .o_Reset_Cpu(w_Debug_Reset),

      .o_Reg_Read_Enable(w_Debug_Reg_Read_Enable),
      .o_Reg_Read_Addr(w_Debug_Reg_Read_Addr),
      .i_Reg_Read_Data(w_Reg_Source_1),

      .o_Reg_Write_Enable(w_Debug_Reg_Write_Enable),
      .o_Reg_Write_Addr(w_Debug_Reg_Write_Addr),
      .o_Reg_Write_Data(w_Debug_Reg_Write_Data),

      .o_Write_PC_Enable(w_Debug_Write_PC_Enable),
      .o_Write_PC_Data(w_Debug_Write_PC_Data),

      .o_Memory_LS_Enable(w_Debug_Memory_LS_Enable),
      .o_Memory_LS_Type(w_Debug_Memory_LS_Type),
      .o_Memory_LS_Write_Enable(w_Debug_Memory_LS_Write_Enable),
      .o_Memory_LS_Address(w_Debug_Memory_LS_Address),
      .o_Memory_LS_Data(w_Debug_Memory_LS_Data),
      .i_Memory_Data_Out(w_Dmem_Data),
      .i_Memory_State(w_Memory_State) 
  );

endmodule
