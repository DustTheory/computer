`timescale 1ns / 1ps

module vga_unit_tests_harness ();

  wire        i_Clock;
  reg         i_Reset;

  reg  [15:0] s_axis_tdata;
  reg         s_axis_tvalid;
  wire        s_axis_tready;

  initial begin
    i_Reset = 1'b1;
    s_axis_tvalid = 1'b0;
  end


  wire       o_mm2s_fsync;
  wire [3:0] o_Red;
  wire [3:0] o_Green;
  wire [3:0] o_Blue;
  wire       o_Horizontal_Sync;
  wire       o_Vertical_Sync;

  vga_out #(
      .BITS_PER_COLOR_CHANNEL(4)
  ) vga_out (
      .i_Clock(i_Clock),
      .i_Reset(i_Reset),
      .s_axis_tdata(s_axis_tdata),
      .s_axis_tvalid(s_axis_tvalid),
      .s_axis_tready(s_axis_tready),
      .o_mm2s_fsync(o_mm2s_fsync),
      .o_Red(o_Red),
      .o_Green(o_Green),
      .o_Blue(o_Blue),
      .o_Horizontal_Sync(o_Horizontal_Sync),
      .o_Vertical_Sync(o_Vertical_Sync)
  );

endmodule
