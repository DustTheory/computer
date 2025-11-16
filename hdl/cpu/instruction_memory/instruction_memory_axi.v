`timescale 1ns / 1ps
`include "cpu_core_params.vh"

module instruction_memory_axi (
    input i_Reset,
    input i_Clock,
    input i_Enable,
    input [XLEN-1:0] i_Instruction_Addr,
    output [XLEN-1:0] o_Instruction,
    output o_Instruction_Valid,

    // AXI INTERFACE
    output [31:0] s_axil_araddr,
    output s_axil_arvalid,
    input s_axil_arready,
    input [31:0] s_axil_rdata,
    input s_axil_rvalid,
    output s_axil_rready,
    output [31:0] s_axil_awaddr,
    output s_axil_awvalid,
    input s_axil_awready,
    output [31:0] s_axil_wdata,
    output [3:0] s_axil_wstrb,
    output s_axil_wvalid,
    input s_axil_wready,
    input [1:0] s_axil_bresp,  // Unbound to anything for now, used just for testing
    input s_axil_bvalid,
    output s_axil_bready
);

  localparam IDLE = 2'b00;
  localparam READ_SUBMITTING = 2'b01;
  localparam READ_AWAITING = 2'b10;
  localparam READ_SUCCESS = 2'b11;

  reg [1:0] r_State = IDLE;

  always @(posedge i_Clock, posedge i_Reset) begin
    if (i_Reset) begin
      r_State <= IDLE;
    end else if (i_Enable) begin
      case (r_State)
        IDLE: begin
          r_State <= READ_SUBMITTING;
        end
        READ_SUBMITTING: begin
          if (s_axil_arready) begin
            r_State <= READ_AWAITING;
          end
        end
        READ_AWAITING: begin
          if (s_axil_rvalid) begin
            r_State <= READ_SUCCESS;
          end
        end
        READ_SUCCESS: begin
          r_State <= IDLE;
        end
        default: begin
          r_State <= IDLE;
        end
      endcase
    end
  end

  assign o_Instruction_Valid = (r_State == READ_SUCCESS);
  assign o_Instruction = (r_State == READ_SUCCESS) ? s_axil_rdata : 0;

  assign s_axil_araddr = i_Instruction_Addr[31:0];
  assign s_axil_arvalid = (r_State == READ_SUBMITTING);
  assign s_axil_rready = (r_State == READ_AWAITING);

endmodule
