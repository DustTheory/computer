`timescale 1ns / 1ps

module vga_out #(
    parameter BITS_PER_COLOR_CHANNEL = 4
) (
    input i_Reset,
    input i_Clock,

    // AXI-Stream Interface
    input  [15:0] s_axis_tdata,
    input         s_axis_tvalid,
    output        s_axis_tready,

    output o_mm2s_fsync,

    output [BITS_PER_COLOR_CHANNEL-1:0] o_Red,
    output [BITS_PER_COLOR_CHANNEL-1:0] o_Green,
    output [BITS_PER_COLOR_CHANNEL-1:0] o_Blue,
    output o_Horizontal_Sync,
    output o_Vertical_Sync
);

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

  // Clock divider for VGA timing (100MHz -> 25MHz)
  reg [1:0] r_Clock_Counter = 0;

  // Vertical and horizontal counter registers
  reg [15:0] r_H_Counter = 0;
  reg [15:0] r_V_Counter = 0;

  // Dual row buffers for pixel data
  reg [15:0] r_Row_Buffer_0 [0:VISIBLE_H-1];
  reg [15:0] r_Row_Buffer_1 [0:VISIBLE_H-1];

  // Buffer control signals
  reg r_Active_Buffer = 0;  // 0 = reading from buffer_0, 1 = reading from buffer_1
  reg [9:0] r_Fill_Addr = 0;  // Address for filling buffer (0 to VISIBLE_H-1)
  reg r_Blanking_Prefetch_Done = 0;

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

  always @(posedge i_Clock or posedge i_Reset) begin
    if (i_Reset) begin
      r_Clock_Counter <= 0;
      r_H_Counter <= 0;
      r_V_Counter <= VISIBLE_V; // Start vertical counter in blanking period
    end else begin
      r_Clock_Counter <= r_Clock_Counter + 1;

      if (r_Clock_Counter == 3) begin // VGA pixel clock tick every 4th cycle
        if(r_H_Counter == TOTAL_H - 1) begin // If we've reached the end of the horizontal line
          r_H_Counter <= 0;
          if (r_V_Counter == TOTAL_V - 1)  // If we've reached the end of the vertical frame
            r_V_Counter <= 0;
          else begin
            r_V_Counter <= r_V_Counter + 1;
          end
        end else begin
          r_H_Counter <= r_H_Counter + 1;
        end
      end
    end
  end

  assign s_axis_tready = !i_Reset && r_V_State == STATE_VISIBLE ? r_Fill_Addr < VISIBLE_H - 1 : !r_Blanking_Prefetch_Done;

  wire w_Frame_Sync_Position = (r_H_Counter == 0) && (r_V_Counter == VISIBLE_V);
  assign o_mm2s_fsync = w_Frame_Sync_Position;

  // Buffer filling and switching logic
  always @(posedge i_Clock or posedge i_Reset) begin
    if (i_Reset) begin
      r_Fill_Addr <= 0;
      r_Active_Buffer <= 0;
      r_Blanking_Prefetch_Done <= 0;
    end else begin
      if (s_axis_tready && s_axis_tvalid) begin
        if (r_Active_Buffer) begin
          r_Row_Buffer_0[r_Fill_Addr] <= s_axis_tdata;
        end else begin
          r_Row_Buffer_1[r_Fill_Addr] <= s_axis_tdata;
        end

        if (r_Fill_Addr < VISIBLE_H - 1) begin
          r_Fill_Addr <= r_Fill_Addr + 1;
        end else if (r_Fill_Addr == VISIBLE_H - 1) begin
          r_Fill_Addr <= VISIBLE_H;
        end
      end

      // Switch buffers and start loading new row soon as we've drawn the visible area of the line
      if (r_H_Counter == VISIBLE_H && r_V_State == STATE_VISIBLE) begin
        r_Active_Buffer <= ~r_Active_Buffer;
        r_Fill_Addr <= 0;
      end else if(r_Fill_Addr == VISIBLE_H - 1 && r_V_State != STATE_VISIBLE && !r_Blanking_Prefetch_Done) begin
        r_Active_Buffer <= ~r_Active_Buffer;
        r_Fill_Addr <= 0;
        r_Blanking_Prefetch_Done <= 1;
      end
    end
  end

  // VGA reads from opposite buffer that VDMA is filling (proper double buffering)
  wire [15:0] w_Current_Pixel = w_Visible ?
    (r_Active_Buffer ? r_Row_Buffer_1[r_H_Counter[9:0]] : r_Row_Buffer_0[r_H_Counter[9:0]]) : 16'h0000;

  assign o_Red = w_Visible ? w_Current_Pixel[15:12] : {BITS_PER_COLOR_CHANNEL{1'b0}};
  assign o_Green = w_Visible ? w_Current_Pixel[10:7] : {BITS_PER_COLOR_CHANNEL{1'b0}};
  assign o_Blue = w_Visible ? w_Current_Pixel[4:1] : {BITS_PER_COLOR_CHANNEL{1'b0}};

  assign o_Horizontal_Sync = ~(r_H_State == STATE_SYNC);  // Invert for active low
  assign o_Vertical_Sync = ~(r_V_State == STATE_SYNC);  // Invert for active low

endmodule
