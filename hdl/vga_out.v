`timescale 1ns / 1ps

module vga_out #(
    parameter BITS_PER_PIXEL = 4,
    parameter FRAMEBUFFER_DEPTH = 640 * 480
) (
    input i_Clock,
    input [BITS_PER_PIXEL-1:0] i_Fb_Read_Data,
    output [31:0] o_Fb_Read_Addr,
    output [BITS_PER_PIXEL-1:0] o_RGB,
    output o_Horizontal_Sync,
    output o_Vertical_Sync
);

  reg [1:0] r_Clock_Counter = 0;

  // Horizontal timing for 640x480 @ 60Hz (approx 25MHz pixel clock)
  localparam VISIBLE_H = 640;
  localparam FRONT_PORCH_H = 16;
  localparam SYNC_PULSE_H = 96;
  localparam BACK_PORCH_H = 48;
  localparam TOTAL_H = VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H + BACK_PORCH_H;  // Should be 800

  // Vertical timing for 640x480 @ 60Hz (approx 25MHz pixel clock)
  localparam VISIBLE_V = 480;
  localparam FRONT_PORCH_V = 10;
  localparam SYNC_PULSE_V = 2;
  localparam BACK_PORCH_V = 33;
  localparam TOTAL_V = VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V + BACK_PORCH_V;  // Should be 525

  // Vertical and horizontal counter registers
  reg [15:0] r_H_Counter = 0;
  reg [15:0] r_V_Counter = 0;


  localparam [1:0] STATE_VISIBLE = 0;
  localparam [1:0] STATE_FRONT_PORCH = 1;
  localparam [1:0] STATE_SYNC = 2;
  localparam [1:0] STATE_BACK_PORCH = 3;

  reg [1:0] r_H_State;
  reg [1:0] r_V_State;

  wire w_Visible = r_H_State == STATE_VISIBLE && r_V_State == STATE_VISIBLE;

  always @* begin
    // Determine the state of the horizontal and vertical counters
    if (r_H_Counter < VISIBLE_H) r_H_State = STATE_VISIBLE;
    else if (r_H_Counter < VISIBLE_H + FRONT_PORCH_H) r_H_State = STATE_FRONT_PORCH;
    else if (r_H_Counter < VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H) r_H_State = STATE_SYNC;
    else r_H_State = STATE_BACK_PORCH;

    if (r_V_Counter < VISIBLE_V) r_V_State = STATE_VISIBLE;
    else if (r_V_Counter < VISIBLE_V + FRONT_PORCH_V) r_V_State = STATE_FRONT_PORCH;
    else if (r_V_Counter < VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V) r_V_State = STATE_SYNC;
    else r_V_State = STATE_BACK_PORCH;
  end

  always @(posedge i_Clock) begin
    r_Clock_Counter <= r_Clock_Counter + 1;
    if(r_Clock_Counter == 2'b00) // Every 4 clock cycles
    begin
      if(r_H_Counter == TOTAL_H - 1) // If we've reached the end of the horizontal line
      begin
        r_H_Counter <= 0;
        if (r_V_Counter == TOTAL_V - 1)  // If we've reached the end of the vertical frame
          r_V_Counter <= 0;
        else r_V_Counter <= r_V_Counter + 1;
      end else begin
        r_H_Counter <= r_H_Counter + 1;
      end
    end
  end

  assign o_Fb_Read_Addr = (r_V_Counter * VISIBLE_H[15:0]) + {16'd0, r_H_Counter};
  assign o_RGB = (w_Visible) ? i_Fb_Read_Data : 4'b000;
  assign o_Horizontal_Sync = ~(r_H_State == STATE_SYNC);  // Invert for active low
  assign o_Vertical_Sync = ~(r_V_State == STATE_SYNC);  // Invert for active low

endmodule
