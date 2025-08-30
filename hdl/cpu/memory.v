`timescale 1ns / 1ps

module memory #(parameter XLEN = 32, parameter REG_ADDR_WIDTH = 5, parameter MEMORY_DEPTH = 1024)   (
    input i_Clock,
    input i_Write_Enable,
    input [4:0] i_Load_Store_Type,
    input [XLEN-1:0] i_Instruction_Addr,
    input [XLEN-1:0] i_Data_Addr,
    input [XLEN-1:0] i_Write_Data,
    output reg [XLEN-1:0] o_Read_Data,
    output reg [XLEN-1:0] o_Instruction
  );

  reg [XLEN-1:0] Memory_Array [0:MEMORY_DEPTH-1];

  wire [XLEN-1:0] w_Read_Data;
  wire [XLEN-1:0] w_Write_Data;

  //     parameter LS_TYPE_LOAD_WORD          = 0;
  //   parameter LS_TYPE_LOAD_HALF          = 1;
  //   parameter LS_TYPE_LOAD_HALF_UNSIGNED = 2;
  //   parameter LS_TYPE_LOAD_BYTE          = 3;
  //   parameter LS_TYPE_LOAD_BYTE_UNSIGNED = 4;
  //   parameter LS_TYPE_STORE_WORD         = 5;
  //   parameter LS_TYPE_STORE_HALF         = 6;
  //   parameter LS_TYPE_STORE_BYTE         = 7;
  //   parameter LS_TYPE_NONE               = 8;

  always @*
  begin
    case(i_Load_Store_Type)
      cpu.LS_TYPE_STORE_WORD:
        w_Write_Data = i_Write_Data;
      cpu.LS_TYPE_STORE_HALF:
        w_Write_Data = {i_Write_Data[15:0], 16'b0};
      default:
        w_Read_Data = 0;
    endcase
  end


  always @(posedge i_Clock)
  begin
    if (i_Write_Enable)
    begin
      Memory_Array[i_Data_Addr[REG_ADDR_WIDTH-1:0]] <= w_Write_Data;
    end
    w_Read_Data <= Memory_Array[i_Data_Addr[REG_ADDR_WIDTH-1:0]];


    o_Instruction <= Memory_Array[i_Instruction_Addr[REG_ADDR_WIDTH-1:0]];
  end

  always @*
  begin
    case(i_Load_Store_Type)
      cpu.LS_TYPE_LOAD_WORD:
        o_Read_Data = w_Read_Data;
      cpu.LS_TYPE_LOAD_HALF:
        o_Read_Data = $signed({w_Read_Data[15:0]});
      cpu.LS_TYPE_LOAD_HALF_UNSIGNED:
        o_Read_Data = {16'b0, w_Read_Data[15:0]};
      cpu.LS_TYPE_LOAD_BYTE:
        o_Read_Data = $signed({w_Read_Data[7:0]});
      cpu.LS_TYPE_LOAD_BYTE_UNSIGNED:
        o_Read_Data = {24'b0, w_Read_Data[7:0]};
      default:
        o_Read_Data = 0;
    endcase
  end

endmodule
