`timescale 1ns / 1ps

module instruction_engine
  #(parameter BITS_PER_PIXEL = 3,
    parameter FRAMEBUFFER_DEPTH = 640*480)
   (
     input i_Clock,
     input i_Rx_DV,
     input [7:0] i_Rx_Byte,
     output reg o_Write_Enable,
     output reg [31:0] o_Write_Addr,
     output reg [BITS_PER_PIXEL-1:0] o_Write_Data
   );

  localparam s_IDLE    = 2'd0;
  localparam s_DECODE  = 2'd1;
  localparam s_EXECUTE = 2'd2;

  localparam op_NOP = 3'b000;
  localparam op_RED = 3'b001;
  localparam op_GREEN = 3'b010;
  localparam op_BLUE = 3'b011;
  localparam op_FRAME = 3'b100;
  localparam op_STORE = 3'b101;
  localparam op_DRAW = 3'b110;
  localparam op_RESERVED = 3'b111;

  reg [1:0] r_State = s_IDLE;
  reg [2:0] r_Op_Code = 0;
  reg [31:0] r_Byte_Index = 0;

  reg r_Next_State = 0;

  always @*
  begin
    if(r_State != s_IDLE)
    begin
      case(r_Op_Code)
        op_NOP:
        begin
          r_Next_State <= 1;
          o_Write_Enable <= 0;
          o_Write_Addr <= 0;
          o_Write_Data <= 0;
        end
        op_RED:
        begin
          if(r_Byte_Index == FRAMEBUFFER_DEPTH - 1)
            r_Next_State <= 1;
          else
          begin
            r_Next_State <= 0;
          end
          o_Write_Enable <= 1;
          o_Write_Addr <= r_Byte_Index;
          o_Write_Data <= 3'b100;
        end
        op_GREEN:
        begin
          if(r_Byte_Index == FRAMEBUFFER_DEPTH - 1)
            r_Next_State <= 1;
          else
          begin
            r_Next_State <= 0;
          end
          o_Write_Enable <= 1;
          o_Write_Addr <= r_Byte_Index;
          o_Write_Data <= 3'b010;
        end
        op_BLUE:
        begin
          if(r_Byte_Index == FRAMEBUFFER_DEPTH - 1)
            r_Next_State <= 1;
          else
          begin
            r_Next_State <= 0;
          end
          o_Write_Enable <= 1;
          o_Write_Addr <= r_Byte_Index;
          o_Write_Data <= 3'b001;
        end
        // op_FRAME:
        // begin
        //   r_End_Of_Decode <= 1;
        // end
        // op_STORE:
        // begin
        //   r_End_Of_Decode <= 1;
        // end
        // op_DRAW:
        // begin
        //   r_End_Of_Decode <= 1;
        // end
        default:
        begin
          r_Next_State <= 1;
          o_Write_Enable <= 0;
          o_Write_Addr <= 0;
          o_Write_Data <= 0;
        end
      endcase
    end
    else
    begin
      o_Write_Addr <= 0;
      o_Write_Data <= 0;
      o_Write_Enable <= 0;
      r_Next_State <= 0;
    end
  end


  always @(posedge i_Clock)
  begin
    case(r_State)
      s_IDLE:
      begin
        if(i_Rx_DV)
        begin
          r_Op_Code <= i_Rx_Byte[2:0];
          r_State <= s_DECODE;
          r_Byte_Index <= 0;
        end
      end
      s_DECODE:
      begin
        if(r_Next_State)
        begin
          r_Byte_Index <= 0;
          r_State <= s_EXECUTE;
        end
        else
        begin
          r_Byte_Index <= r_Byte_Index + 1;
          r_State <= s_DECODE;
        end
      end
      s_EXECUTE:
      begin
        if(r_Next_State)
        begin
          r_Byte_Index <= 0;
          r_State <= s_IDLE;
        end
        else
        begin
          r_Byte_Index <= r_Byte_Index + 1;
          r_State <= s_EXECUTE;
        end
      end
    endcase
  end

endmodule
