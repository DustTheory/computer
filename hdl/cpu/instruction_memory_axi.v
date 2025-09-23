`timescale 1ns / 1ps
`include "../cpu_core_params.vh"

module instruction_memory_axi (
    input i_Reset,
    input i_Clock,
    input [XLEN-1:0] i_Instruction_Addr,
    output [XLEN-1:0] o_Instruction,
    output o_Instruction_Valid
);

  localparam IDLE = 2'b00;
  localparam READ_SUBMITTING = 2'b01;
  localparam READ_AWAITING = 2'b10;
  localparam READ_SUCCESS = 2'b11;

  wire w_axil_arready;
  wire w_axil_rvalid;
  wire [31:0] w_axil_rdata;

  reg [1:0] r_State = IDLE;

  always @(posedge i_Clock, posedge i_Reset) begin
    if (i_Reset) begin
      r_State <= IDLE;
    end else begin
      case (r_State)
        IDLE: begin
          r_State <= READ_SUBMITTING;
        end
        READ_SUBMITTING: begin
          if (w_axil_arready) begin
            r_State <= READ_AWAITING;
          end
        end
        READ_AWAITING: begin
          if (w_axil_rvalid) begin
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
  assign o_Instruction = (r_State == READ_SUCCESS) ? w_axil_rdata : 0;

  // verilator lint_off PINMISSING
  axil_ram ram (
      .rst(i_Reset),
      .clk(i_Clock),
      .s_axil_araddr(r_State == READ_SUBMITTING ? i_Instruction_Addr[15:0] : 0),
      .s_axil_arvalid(r_State == READ_SUBMITTING),
      .s_axil_arready(w_axil_arready),
      .s_axil_rdata(w_axil_rdata),
      .s_axil_rvalid(w_axil_rvalid),
      .s_axil_rready(r_State == READ_AWAITING)
  );
  // verilator lint_off PINMISSING


endmodule
