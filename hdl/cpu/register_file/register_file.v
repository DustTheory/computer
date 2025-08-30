`timescale 1ns / 1ps
`include "../cpu_core_params.vh"

module register_file (
    input i_Clock,
    input [REG_ADDR_WIDTH-1:0] i_Read_Addr_1,
    input [REG_ADDR_WIDTH-1:0] i_Read_Addr_2,
    input [REG_ADDR_WIDTH-1:0] i_Write_Addr,
    input [XLEN-1:0] i_Write_Data,
    input i_Write_Enable,
    output reg [XLEN-1:0] o_Read_Data_1,
    output reg [XLEN-1:0] o_Read_Data_2
);

  reg [XLEN-1:0] registers[0:(1 << REG_ADDR_WIDTH)-1];

  assign o_Read_Data_1 = i_Read_Addr_1 != 0 ? registers[i_Read_Addr_1] : 0;
  assign o_Read_Data_2 = i_Read_Addr_2 != 0 ? registers[i_Read_Addr_2] : 0;

  always @(posedge i_Clock) begin
    if (i_Write_Enable && i_Write_Addr != 0) registers[i_Write_Addr] <= i_Write_Data;
  end

endmodule
