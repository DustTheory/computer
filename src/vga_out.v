`timescale 1ns / 1ps

module vga_out
  #(parameter BITS_PER_PIXEL = 3,
    parameter FRAMEBUFFER_DEPTH = 640*480)
   (
     input clk,
     input [BITS_PER_PIXEL-1:0] i_Fb_Read_Data,
     output [$clog2(FRAMEBUFFER_DEPTH - 1):0] o_Fb_Read_Addr,
     output [BITS_PER_PIXEL-1:0] o_RGB,
     output o_Horizontal_Sync,
     output o_Vertical_Sync
   );

  // Horizontal timing for 640x480 @ 60Hz (approx 25MHz pixel clock)
  parameter VISIBLE_H = 640;
  parameter FRONT_PORCH_H = 16;
  parameter SYNC_PULSE_H = 96;
  parameter BACK_PORCH_H = 48;
  parameter TOTAL_H = VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H + BACK_PORCH_H; // Should be 800

  // Vertical timing for 640x480 @ 60Hz (approx 25MHz pixel clock)
  parameter VISIBLE_V = 480;
  parameter FRONT_PORCH_V = 10;
  parameter SYNC_PULSE_V = 2;
  parameter BACK_PORCH_V = 33;
  parameter TOTAL_V = VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V + BACK_PORCH_V; // Should be 525

  // Vertical and horizontal counter registers
  reg [15:0] r_counter_h = 0;
  reg [15:0] r_counter_v = 0;

  wire w_h_visible, w_h_front_porch, w_h_sync, w_h_back_porch;
  wire w_v_visible, w_v_front_porch, w_v_sync, w_v_back_porch;

  assign w_h_visible      = r_counter_h < VISIBLE_H;
  assign w_h_front_porch  = r_counter_h >= VISIBLE_H && r_counter_h < (VISIBLE_H + FRONT_PORCH_H);
  assign w_h_sync         = r_counter_h >= (VISIBLE_H + FRONT_PORCH_H) && r_counter_h < (VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H);
  assign w_h_back_porch   = r_counter_h >= (VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H) && r_counter_h < (TOTAL_H);
  assign w_h_overflow     = (r_counter_h == TOTAL_H - 1);

  assign w_v_visible      = r_counter_v < VISIBLE_V;
  assign w_v_front_porch  = r_counter_v >= VISIBLE_V && r_counter_v < (VISIBLE_V + FRONT_PORCH_V);
  assign w_v_sync         = r_counter_v >= (VISIBLE_V + FRONT_PORCH_V) && r_counter_v < (VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V);
  assign w_v_back_porch   = r_counter_v >= (VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V) && r_counter_v < (TOTAL_V);
  assign w_v_overflow     = (r_counter_v == TOTAL_V - 1);


  wire w_visible = w_h_visible && w_v_visible;

  always @(posedge clk)
  begin
    if(w_h_overflow) // If we've reached the end of the horizontal line
    begin
      r_counter_h <= 0; // Reset horizontal counter
      if(w_v_overflow) // If we've reached the end of the vertical frame
        r_counter_v <= 0; // Reset vertical counter
      else
        r_counter_v <= r_counter_v + 1; // Increment vertical counter
    end
    else
    begin
      r_counter_h <= r_counter_h + 1; // Increment horizontal counter
    end
  end

  assign o_Fb_Read_Addr = (r_counter_v * VISIBLE_H) + r_counter_h;
  assign o_RGB = (w_visible) ? i_Fb_Read_Data :  3'b000;
  assign o_Horizontal_Sync = ~w_h_sync; // Invert for active low
  assign o_Vertical_Sync = ~w_v_sync; // Invert for active low

endmodule
