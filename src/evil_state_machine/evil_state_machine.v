`timescale 1ns / 1ps

module evil_state_machine
  #(parameter BITS_PER_PIXEL = 3,
    parameter FRAMEBUFFER_DEPTH = 640*480)
   (
     input i_Clock,
     input i_Rx_DV,
     input [7:0] i_Rx_Byte
   );

  parameter s_op_IDLE = 8'd0;

  parameter s_OPCODE   = 3'b001;
  parameter s_OPERANDS = 3'b010;

  reg [2:0] r_State = s_OPCODE;
  reg [7:0] r_Op_Code = s_op_IDLE;

  always @(posedge i_Clock)
  begin
    case(r_State)
      s_OPCODE:
      begin
        r_Op_Code <= i_Rx_Byte;
        r_State <= s_OPERANDS;
      end
      s_OPERANDS:
      begin

        r_State <= s_OPCODE; // For now just swallow. we don't care
      end
    endcase
  end




endmodule
