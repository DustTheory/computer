`timescale 1ns / 1ps

module framebuffer #(
    parameter BITS_PER_PIXEL = 4,
    parameter FRAMEBUFFER_DEPTH = 640 * 480
) (
    input i_Clock,
    input [31:0] i_Read_Addr,
    input i_Write_Enable,
    input [31:0] i_Write_Addr,
    input [BITS_PER_PIXEL-1:0] i_Write_Data,
    output reg [BITS_PER_PIXEL-1:0] o_Read_Data
);

  localparam FRAMEBUFFER_CUTOFF = 640 * 300;

  (* ram_style = "block" *) reg [BITS_PER_PIXEL-1:0] Frame_Buffer[0:FRAMEBUFFER_CUTOFF-1];

  always @(posedge i_Clock) begin
    if (i_Write_Enable && i_Write_Addr < FRAMEBUFFER_CUTOFF)
      Frame_Buffer[i_Write_Addr] <= i_Write_Data;

    o_Read_Data <= i_Read_Addr < FRAMEBUFFER_CUTOFF ? Frame_Buffer[i_Read_Addr] : 0;
  end

endmodule
