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
    output [2:0] o_State
);

  wire w_axil_arready;
  wire w_axil_rvalid;
  wire w_axil_awready;
  wire w_axil_wready;
  wire w_axil_bvalid;
  wire [1:0] w_axil_bresp; // Unbound to anything for now, used just for testing
  wire [31:0] w_axil_rdata;

  reg [2:0] r_State = IDLE;
  wire [1:0] w_Byte_Offset = i_Addr[1:0]; // low address bits used for sub-word store placement / load selection

  reg [31:0] w_Prepared_WData;
  reg [3:0]  w_Prepared_WStrb;

  always @* begin
    w_Prepared_WData = i_Data;
    w_Prepared_WStrb = 4'b0000;
    case (i_Load_Store_Type)
      LS_TYPE_STORE_WORD: begin
        w_Prepared_WData = i_Data;
        w_Prepared_WStrb = 4'b1111;
      end
      LS_TYPE_STORE_HALF: begin
        case (w_Byte_Offset[1])
          1'b0: begin
            w_Prepared_WData = {16'b0, i_Data[15:0]};
            w_Prepared_WStrb = 4'b0011;
          end
          1'b1: begin
            w_Prepared_WData = {i_Data[15:0], 16'b0};
            w_Prepared_WStrb = 4'b1100;
          end
        endcase
      end
      LS_TYPE_STORE_BYTE: begin
        case (w_Byte_Offset)
          2'b00: begin w_Prepared_WData = {24'b0, i_Data[7:0]};         w_Prepared_WStrb = 4'b0001; end
          2'b01: begin w_Prepared_WData = {16'b0, i_Data[7:0], 8'b0};    w_Prepared_WStrb = 4'b0010; end
          2'b10: begin w_Prepared_WData = {8'b0,  i_Data[7:0], 16'b0};   w_Prepared_WStrb = 4'b0100; end
          2'b11: begin w_Prepared_WData = {i_Data[7:0], 24'b0};          w_Prepared_WStrb = 4'b1000; end
        endcase
      end
      default: ;
    endcase
  end

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
              if (i_Write_Enable) begin
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

  // Load data selection without dynamic shifting since RAM is byte-addressable.
  always @* begin
    case (i_Load_Store_Type)
      LS_TYPE_LOAD_WORD: begin
        o_Data = w_axil_rdata;
      end
      LS_TYPE_LOAD_HALF: begin
        if (w_Byte_Offset[1] == 1'b0)
          o_Data = {{16{w_axil_rdata[15]}}, w_axil_rdata[15:0]};
        else
          o_Data = {{16{w_axil_rdata[31]}}, w_axil_rdata[31:16]};
      end
      LS_TYPE_LOAD_HALF_UNSIGNED: begin
        o_Data = (w_Byte_Offset[1] == 1'b0) ? {16'b0, w_axil_rdata[15:0]} : {16'b0, w_axil_rdata[31:16]};
      end
      LS_TYPE_LOAD_BYTE: begin
        case (w_Byte_Offset)
          2'b00: o_Data = {{24{w_axil_rdata[7]}},  w_axil_rdata[7:0]};
          2'b01: o_Data = {{24{w_axil_rdata[15]}}, w_axil_rdata[15:8]};
          2'b10: o_Data = {{24{w_axil_rdata[23]}}, w_axil_rdata[23:16]};
          2'b11: o_Data = {{24{w_axil_rdata[31]}}, w_axil_rdata[31:24]};
        endcase
      end
      LS_TYPE_LOAD_BYTE_UNSIGNED: begin
        case (w_Byte_Offset)
          2'b00: o_Data = {24'b0, w_axil_rdata[7:0]};
          2'b01: o_Data = {24'b0, w_axil_rdata[15:8]};
          2'b10: o_Data = {24'b0, w_axil_rdata[23:16]};
          2'b11: o_Data = {24'b0, w_axil_rdata[31:24]};
        endcase
      end
      default: o_Data = 32'b0;
    endcase
  end


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
      .s_axil_wdata(r_State == WRITE_SUBMITTING ? w_Prepared_WData : 0),
      .s_axil_wstrb(r_State == WRITE_SUBMITTING ? w_Prepared_WStrb : 0),
      .s_axil_wready(w_axil_wready),
      .s_axil_bvalid(w_axil_bvalid),
      .s_axil_bready(r_State == WRITE_SUBMITTING),
      .s_axil_bresp(w_axil_bresp)
  );
  // verilator lint_off PINMISSING

  assign o_State = r_State;

endmodule
