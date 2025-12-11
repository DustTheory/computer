`timescale 1ns / 1ps
`include "cpu_core_params.vh"

module register_file (
    input i_Enable,
    input i_Clock,
    input [REG_ADDR_WIDTH-1:0] i_Read_Addr_1,
    input [REG_ADDR_WIDTH-1:0] i_Read_Addr_2,
    input [REG_ADDR_WIDTH-1:0] i_Write_Addr,
    input [XLEN-1:0] i_Write_Data,
    input i_Write_Enable,
    output [XLEN-1:0] o_Read_Data_1,
    output [XLEN-1:0] o_Read_Data_2
);

  reg [XLEN-1:0] Registers[0:(1 << REG_ADDR_WIDTH)-1];

  wire w_Read1_Is_Write = (i_Write_Enable && i_Write_Addr != {REG_ADDR_WIDTH{1'b0}} && i_Read_Addr_1 == i_Write_Addr);
  wire w_Read2_Is_Write = (i_Write_Enable && i_Write_Addr != {REG_ADDR_WIDTH{1'b0}} && i_Read_Addr_2 == i_Write_Addr);

  assign o_Read_Data_1 = (i_Enable && i_Read_Addr_1 != {REG_ADDR_WIDTH{1'b0}})
                           ? (w_Read1_Is_Write ? i_Write_Data : Registers[i_Read_Addr_1])
                           : {XLEN{1'b0}};
  assign o_Read_Data_2 = (i_Enable && i_Read_Addr_2 != {REG_ADDR_WIDTH{1'b0}})
                           ? (w_Read2_Is_Write ? i_Write_Data : Registers[i_Read_Addr_2])
                           : {XLEN{1'b0}};

  always @(posedge i_Clock) begin
    if (i_Enable && i_Write_Enable && i_Write_Addr != {REG_ADDR_WIDTH{1'b0}})
      Registers[i_Write_Addr] <= i_Write_Data;
    if (i_Enable && i_Write_Enable && i_Write_Addr == {REG_ADDR_WIDTH{1'b0}})
      Registers[i_Write_Addr] <= {XLEN{1'b0}};
  end

endmodule
