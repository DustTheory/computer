`timescale 1ns / 1ps

module framebuffer
  #(parameter BITS_PER_PIXEL = 3,
    parameter FRAMEBUFFER_DEPTH = 640*480)
   (
     input i_Clock,
     input [$clog2(FRAMEBUFFER_DEPTH - 1):0] i_Read_Addr,
     input i_Write_Enable,
     input [$clog2(FRAMEBUFFER_DEPTH - 1):0] i_Write_Addr,
     input [BITS_PER_PIXEL-1:0] i_Write_Data,
     output [BITS_PER_PIXEL-1:0] o_Read_Data
   );

  reg [BITS_PER_PIXEL-1:0] Frame_Buffer [0:FRAMEBUFFER_DEPTH-1];

  reg [BITS_PER_PIXEL-1:0] r_Read_Data;
  always @(posedge i_Clock)
  begin
    r_Read_Data <= Frame_Buffer[i_Read_Addr];
    if(i_Write_Enable)
    begin
      Frame_Buffer[i_Write_Addr] <= i_Write_Data;
    end
  end

  assign o_Read_Data = r_Read_Data;

endmodule
