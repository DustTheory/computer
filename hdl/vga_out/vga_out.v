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

  reg [15:0] r_Row_Buffer_0 [0:VISIBLE_H-1];
  reg [15:0] r_Row_Buffer_1 [0:VISIBLE_H-1];

  reg        r_Display_Active = 1'b0;
  reg        r_Display_Buffer = 1'b0;
  reg        r_Load_Buffer = 1'b0;
  reg [1:0]  r_Row_Count = 0;
  reg [9:0]  r_Load_Col = 0;
  reg        r_Loading = 1'b0;

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

  wire w_Pixel_Clock_Tick = (r_Clock_Counter == 3);

  wire w_Fsync_Level = (r_H_Counter == 0) && (r_V_Counter == VISIBLE_V);

  assign s_axis_tready = (r_Row_Count < 2) && !w_Fsync_Level;

  wire w_Load_Handshake = s_axis_tvalid && s_axis_tready;
  wire w_Load_Complete = w_Load_Handshake && (r_Load_Col == VISIBLE_H - 1);

  wire w_Row_Consume = w_Pixel_Clock_Tick && (r_V_Counter < VISIBLE_V) &&
                       (r_H_Counter == VISIBLE_H - 1) && r_Display_Active && (r_Row_Count > 0);

  wire w_Line_Start = w_Pixel_Clock_Tick && (r_H_Counter == TOTAL_H - 1);

  wire w_Fsync_Event = w_Pixel_Clock_Tick && (r_H_Counter == 0) && (r_V_Counter == VISIBLE_V);

  always @(posedge i_Clock or posedge i_Reset) begin
    if (i_Reset) begin
      r_Clock_Counter <= 0;
      r_H_Counter <= 0;
      r_V_Counter <= VISIBLE_V; // Start vertical counter in blanking period
      r_Display_Active <= 1'b0;
      r_Display_Buffer <= 1'b0;
      r_Load_Buffer <= 1'b0;
      r_Row_Count <= 0;
      r_Load_Col <= 0;
      r_Loading <= 1'b0;
    end else begin
      r_Clock_Counter <= r_Clock_Counter + 1;

      // AXI-Stream row loading logic
      if (w_Load_Handshake) begin
        r_Loading <= 1'b1; 
        if (r_Load_Buffer == 1'b0)
          r_Row_Buffer_0[r_Load_Col] <= s_axis_tdata;
        else
          r_Row_Buffer_1[r_Load_Col] <= s_axis_tdata;

        if (r_Load_Col == VISIBLE_H - 1) begin
          r_Load_Col <= 0;
          r_Loading <= 1'b0;
          r_Load_Buffer <= ~r_Load_Buffer;
        end else begin
          r_Load_Col <= r_Load_Col + 1;
        end
      end

      if (w_Pixel_Clock_Tick) begin // VGA pixel clock tick every 4th cycle
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

        // Start-of-line handling (after wrap) to activate display buffer
        if (w_Line_Start) begin
          if ((r_V_Counter == TOTAL_V - 1) ? 1'b1 : ((r_V_Counter + 1) < VISIBLE_V)) begin
            r_Display_Active <= (r_Row_Count > 0);
          end else begin
            r_Display_Active <= 1'b0;
          end
        end

        // End-of-visible-line consumption
        if (w_Row_Consume) begin
          r_Display_Buffer <= ~r_Display_Buffer;
          r_Display_Active <= 1'b0;
        end

        // Frame sync: reset row buffering at start of vertical back porch
        if (w_Fsync_Event) begin
          r_Display_Active <= 1'b0;
          r_Display_Buffer <= 1'b0;
          r_Load_Buffer <= 1'b0;
          r_Load_Col <= 0;
          r_Loading <= 1'b0;
        end
      end

      // Row count update (handles simultaneous load/consume)
      if (w_Fsync_Event) begin
        r_Row_Count <= 0;
      end else begin
        case ({w_Load_Complete, w_Row_Consume})
          2'b10: r_Row_Count <= r_Row_Count + 1;
          2'b01: r_Row_Count <= r_Row_Count - 1;
          default: r_Row_Count <= r_Row_Count;
        endcase
      end
    end
  end

  assign o_mm2s_fsync = w_Fsync_Level;

  wire [15:0] w_Current_Pixel = (r_H_Counter < VISIBLE_H)
    ? ((r_Display_Buffer == 1'b0) ? r_Row_Buffer_0[r_H_Counter[9:0]] : r_Row_Buffer_1[r_H_Counter[9:0]])
    : 16'h0000;
  assign o_Red = (w_Visible && r_Display_Active) ? w_Current_Pixel[15:12] : {BITS_PER_COLOR_CHANNEL{1'b0}};
  assign o_Green = (w_Visible && r_Display_Active) ? w_Current_Pixel[10:7] : {BITS_PER_COLOR_CHANNEL{1'b0}};
  assign o_Blue = (w_Visible && r_Display_Active) ? w_Current_Pixel[4:1] : {BITS_PER_COLOR_CHANNEL{1'b0}};

  assign o_Horizontal_Sync = ~(r_H_State == STATE_SYNC); 
  assign o_Vertical_Sync = ~(r_V_State == STATE_SYNC);

endmodule
