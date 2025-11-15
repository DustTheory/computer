`timescale 1ns / 1ps

module instruction_engine #(
    parameter BITS_PER_PIXEL = 12,
    parameter FRAMEBUFFER_DEPTH = 640 * 480
) (
    input i_Clock,
    input i_Rx_DV,
    input [7:0] i_Rx_Byte,
    output reg o_Write_Enable,
    output reg [31:0] o_Write_Addr,
    output reg [BITS_PER_PIXEL-1:0] o_Write_Data
);

  localparam s_IDLE = 2'd0;
  localparam s_DECODE_AND_EXECUTE = 2'd1;
  localparam s_EXECUTE = 2'd2;

  localparam op_NOP = 8'b000;
  localparam op_RED = 8'b001;
  localparam op_GREEN = 8'b010;
  localparam op_BLUE = 8'b011;
  localparam op_FRAME = 8'b100;
  localparam op_STORE = 8'b101;
  localparam op_DRAW = 8'b110;
  localparam op_RESERVED = 8'b111;

  localparam s_RED = 0;
  localparam s_GREEN = 1;
  localparam s_BLUE = 2;

  reg [1:0] r_State = s_IDLE;
  reg [7:0] r_Op_Code = 0;
  reg [31:0] r_Pixel_Index = 0;
  reg [1:0] r_Which_Color = s_RED;


  reg [3:0] r_Red;
  reg [3:0] r_Green;
  reg [3:0] r_Blue;

  reg r_Next_State = 0;

  always @* begin
    if (r_State != s_IDLE) begin
      case (r_Op_Code)
        op_NOP: begin
          r_Next_State   = 1;
          o_Write_Enable = 0;
          o_Write_Addr   = 0;
          o_Write_Data   = 0;
        end
        // op_RED: begin
        //   if (r_Pixel_Index == FRAMEBUFFER_DEPTH - 1) r_Next_State = 1;
        //   else begin
        //     r_Next_State = 0;
        //   end
        //   o_Write_Enable = 1;
        //   o_Write_Addr   = r_Pixel_Index;
        //   o_Write_Data   = 12'b100;
        // end
        // op_GREEN: begin
        //   if (r_Pixel_Index == FRAMEBUFFER_DEPTH - 1) r_Next_State = 1;
        //   else begin
        //     r_Next_State = 0;
        //   end
        //   o_Write_Enable = 1;
        //   o_Write_Addr   = r_Pixel_Index;
        //   o_Write_Data   = 12'b010;
        // end
        // op_BLUE: begin
        //   if (r_Pixel_Index == FRAMEBUFFER_DEPTH - 1) r_Next_State = 1;
        //   else begin
        //     r_Next_State = 0;
        //   end
        //   o_Write_Enable = 1;
        //   o_Write_Addr   = r_Pixel_Index;
        //   o_Write_Data   = 3'b001;
        // end
        op_FRAME: begin
          if (r_Pixel_Index == FRAMEBUFFER_DEPTH - 1) r_Next_State = 1;
          else begin
            r_Next_State = 0;
          end
          o_Write_Addr   = r_Pixel_Index;
          o_Write_Data   = {r_Blue, r_Green, r_Red};
          o_Write_Enable = r_Which_Color == s_BLUE;

        end
        // op_STORE:
        // begin
        //   r_End_Of_Decode = 1;
        // end
        // op_DRAW:
        // begin
        //   r_End_Of_Decode = 1;
        // end
        default: begin
          r_Next_State   = 1;
          o_Write_Enable = 0;
          o_Write_Addr   = 0;
          o_Write_Data   = 0;
        end
      endcase
    end else begin
      o_Write_Addr   = 0;
      o_Write_Data   = 0;
      o_Write_Enable = 0;
      r_Next_State   = 0;
    end
  end


  always @(posedge i_Clock) begin
    if (i_Rx_DV) begin
      case (r_State)
        s_IDLE: begin
          r_Op_Code <= i_Rx_Byte;
          r_State <= s_DECODE_AND_EXECUTE;
          r_Which_Color <= s_RED;
          r_Pixel_Index <= 0;
        end
        s_DECODE_AND_EXECUTE: begin
          if (r_Next_State) begin
            r_Pixel_Index <= 0;
            r_State <= s_IDLE;
          end else begin
            if (r_Which_Color == s_RED) begin
              r_Red <= i_Rx_Byte;
              r_Which_Color <= r_Which_Color + 1;
            end else if (r_Which_Color == s_GREEN) begin
              r_Green <= i_Rx_Byte;
              r_Which_Color <= r_Which_Color + 1;
            end else begin
              r_Blue <= i_Rx_Byte;
              r_Pixel_Index <= r_Pixel_Index + 1;
              r_Which_Color <= s_RED;
            end
            r_State <= s_DECODE_AND_EXECUTE;
          end
        end
        default: begin
          r_State <= s_IDLE;
          r_Pixel_Index <= 0;
        end
      endcase
    end
  end

endmodule
