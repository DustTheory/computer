`timescale 1ns / 1ps
`include "memory.vh"

module memory_axi (
    input i_Reset,
    input i_Clock,
    input i_Write_Enable,
    input [LS_SEL_WIDTH:0] i_Load_Store_Type,
    input [XLEN-1:0] i_Addr,
    input [XLEN-1:0] i_Data,
    output reg [XLEN-1:0] o_Data,
    output reg o_Ready,  // Ready for next operation (r/w)
    output o_Data_Valid
);

  localparam IDLE = 3'b000;
  localparam READ_SUBMITTING = 3'b001;
  localparam READ_AWAITING = 3'b010;
  localparam READ_SUCCESS = 3'b011;
  localparam WRITE_SUBMITTING = 3'b100;
  localparam WRITE_AWAITING = 3'b101;
  localparam WRITE_SUCCESS = 3'b110;

  wire w_axil_arready;
  wire w_axil_rvalid;
  wire w_axil_awready;
  wire w_axil_wready;
  wire w_axil_bvalid;
  wire [31:0] w_axil_rdata;

  reg [2:0] r_State = IDLE;

  always @(posedge i_Clock) begin
    if (i_Reset) begin
      r_State <= IDLE;
    end else begin
      case (r_State)
        IDLE: begin
          case (i_Load_Store_Type)
            LS_TYPE_LOAD_WORD, LS_TYPE_LOAD_HALF, LS_TYPE_LOAD_HALF_UNSIGNED, LS_TYPE_LOAD_BYTE, LS_TYPE_LOAD_BYTE_UNSIGNED:
            begin
              r_State <= READ_SUBMITTING;
            end
            LS_TYPE_STORE_WORD, LS_TYPE_STORE_HALF, LS_TYPE_STORE_BYTE: begin
              if(i_Write_Enable) begin
                r_State <= WRITE_SUBMITTING;
              end
            end
            default: begin
              // Nothing?
            end
          endcase
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
        WRITE_SUBMITTING: begin
          if (w_axil_awready && w_axil_wready) begin
            r_State <= w_axil_bvalid ? WRITE_SUCCESS : WRITE_AWAITING;
          end
        end
        WRITE_AWAITING: begin
          if (w_axil_bvalid) begin
            r_State <= WRITE_SUCCESS;
          end
        end
        WRITE_SUCCESS: begin
          r_State <= IDLE;
        end
        default: begin
          r_State <= IDLE;
        end
      endcase
    end
  end

  // verilator lint_off WIDTH
  always @* begin
    o_Data_Valid = (r_State == READ_SUCCESS);
    o_Ready = (r_State == IDLE);

    case (i_Load_Store_Type)
      LS_TYPE_LOAD_WORD: o_Data = w_axil_rdata;
      LS_TYPE_LOAD_HALF: o_Data = $signed({w_axil_rdata[15:0]});
      LS_TYPE_LOAD_HALF_UNSIGNED: o_Data = {16'b0, w_axil_rdata[15:0]};
      LS_TYPE_LOAD_BYTE: o_Data = $signed({w_axil_rdata[7:0]});
      LS_TYPE_LOAD_BYTE_UNSIGNED: o_Data = {24'b0, w_axil_rdata[7:0]};
      default: o_Data = 0;
    endcase
  end
  // verilator lint_on WIDTH


  // verilator lint_off PINMISSING
  axil_ram ram (
      .rst(i_Reset),
      .clk(i_Clock),
      .s_axil_araddr(r_State == READ_SUBMITTING ? i_Addr[15:0] : 0),
      .s_axil_arvalid(r_State == READ_SUBMITTING),
      .s_axil_arready(w_axil_arready),
      .s_axil_rdata(w_axil_rdata),
      .s_axil_rvalid(w_axil_rvalid),
      .s_axil_rready(r_State == READ_AWAITING),
      .s_axil_awvalid(r_State == WRITE_SUBMITTING),
      .s_axil_awaddr(r_State == WRITE_SUBMITTING ? i_Addr[15:0] : 0),
      .s_axil_awready(w_axil_awready),
      .s_axil_wvalid(r_State == WRITE_SUBMITTING),
      .s_axil_wdata(r_State == WRITE_SUBMITTING ? i_Data : 0),
      .s_axil_wstrb(r_State == WRITE_SUBMITTING ? 4'b1111 : 0),
      .s_axil_wready(w_axil_wready),
      .s_axil_bvalid(w_axil_bvalid),
      .s_axil_bready(r_State == WRITE_SUBMITTING)
  );
  // verilator lint_off PINMISSING


endmodule
