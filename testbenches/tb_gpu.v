`timescale 1ns / 1ps

module tb_gpu;

  reg r_Clock = 0;
  wire [2:0] w_RGB;
  wire w_Horizontal_Sync, w_Vertical_Sync;

  // 100MHz clock: toggles every 10ns
  always #5 r_Clock = ~r_Clock;

  gpu GPU (
        .i_Clock(r_Clock),
        .o_Horizontal_Sync(w_Horizontal_Sync),
        .o_Vertical_Sync(w_Vertical_Sync),
        .o_RGB(w_RGB)
      );

  initial
  begin
    #1000 $finish;
  end

endmodule
