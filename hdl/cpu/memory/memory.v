`timescale 1ns / 1ps
`include "memory.vh"

module memory #(
    parameter MEMORY_DEPTH = 1024
) (
    input i_Enable,
    input i_Clock,
    input i_Write_Enable,
    input [LS_SEL_WIDTH:0] i_Load_Store_Type,
    input [XLEN-1:0] i_Addr,
    input [XLEN-1:0] i_Data,
    output reg [XLEN-1:0] o_Data
);

  reg [7:0] Memory_Array[0:MEMORY_DEPTH-1];

  wire [XLEN-1:0] w_Read_Data = {
    Memory_Array[i_Addr+3], Memory_Array[i_Addr+2], Memory_Array[i_Addr+1], Memory_Array[i_Addr]
  };

  always @(posedge i_Clock) begin
    if (i_Enable && i_Write_Enable) begin
      // All store types write the first byte
      Memory_Array[i_Addr] <= i_Data[7:0];

      // Additional bytes for half-word and word stores
      if (i_Load_Store_Type == LS_TYPE_STORE_HALF || i_Load_Store_Type == LS_TYPE_STORE_WORD) begin
        Memory_Array[i_Addr+1] <= i_Data[15:8];
      end

      // Additional bytes for word stores
      if (i_Load_Store_Type == LS_TYPE_STORE_WORD) begin
        Memory_Array[i_Addr+2] <= i_Data[23:16];
        Memory_Array[i_Addr+3] <= i_Data[31:24];
      end
    end
  end

  // verilator lint_off WIDTH
  always @* begin
    if (i_Enable) begin
      case (i_Load_Store_Type)
        LS_TYPE_LOAD_WORD: o_Data = w_Read_Data;
        LS_TYPE_LOAD_HALF: o_Data = $signed({w_Read_Data[15:0]});
        LS_TYPE_LOAD_HALF_UNSIGNED: o_Data = {16'b0, w_Read_Data[15:0]};
        LS_TYPE_LOAD_BYTE: o_Data = $signed({w_Read_Data[7:0]});
        LS_TYPE_LOAD_BYTE_UNSIGNED: o_Data = {24'b0, w_Read_Data[7:0]};
        default: o_Data = 0;
      endcase
    end else begin
      o_Data = 0;
    end
  end
  // verilator lint_on WIDTH

endmodule
