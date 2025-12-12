`timescale 1ns / 1ps

module cpu_unit_tests_harness ();

  wire i_Reset;
  wire i_Clock;

  wire [MEMORY_STATE_WIDTH:0] w_Mem_State;
  wire w_Mem_ready = w_Mem_State == IDLE;

  wire [31:0] s_data_memory_axil_araddr;
  wire s_data_memory_axil_arvalid;
  wire s_data_memory_axil_arready;
  wire [31:0] s_data_memory_axil_rdata;
  wire s_data_memory_axil_rvalid;
  wire s_data_memory_axil_rready;
  wire [31:0] s_data_memory_axil_awaddr;
  wire s_data_memory_axil_awvalid;
  wire s_data_memory_axil_awready;
  wire [31:0] s_data_memory_axil_wdata;
  wire [3:0] s_data_memory_axil_wstrb;
  wire s_data_memory_axil_wvalid;
  wire s_data_memory_axil_wready;
  wire [1:0] s_data_memory_axil_bresp;
  wire s_data_memory_axil_bvalid;
  wire s_data_memory_axil_bready;

  wire [31:0] s_instruction_memory_axil_araddr;
  wire s_instruction_memory_axil_arvalid;
  wire s_instruction_memory_axil_arready;
  wire [31:0] s_instruction_memory_axil_rdata;
  wire s_instruction_memory_axil_rvalid;
  wire s_instruction_memory_axil_rready;

  // verilator lint_off PINMISSING
  arithmetic_logic_unit alu (.i_Enable(1'b1));
  comparator_unit comparator_unit (.i_Enable(1'b1));
  immediate_unit immediate_unit (.i_Enable(1'b1));
  control_unit control_unit (.i_Enable(1'b1));
  register_file register_file (.i_Enable(1'b1));
  instruction_memory_axi instruction_memory_axi (
      .i_Clock(i_Clock),
      .i_Reset(i_Reset),
      .i_Enable(1'b1),
      .s_axil_araddr(s_instruction_memory_axil_araddr),
      .s_axil_arvalid(s_instruction_memory_axil_arvalid),
      .s_axil_arready(s_instruction_memory_axil_arready),
      .s_axil_rdata(s_instruction_memory_axil_rdata),
      .s_axil_rvalid(s_instruction_memory_axil_rvalid),
      .s_axil_rready(s_instruction_memory_axil_rready)
  );
  memory_axi memory_axi (
      .i_Clock(i_Clock),
      .i_Reset(i_Reset),
      .i_Enable(1'b1),
      .o_State(w_Mem_State),
      .s_axil_araddr(s_data_memory_axil_araddr),
      .s_axil_arvalid(s_data_memory_axil_arvalid),
      .s_axil_arready(s_data_memory_axil_arready),
      .s_axil_rdata(s_data_memory_axil_rdata),
      .s_axil_rvalid(s_data_memory_axil_rvalid),
      .s_axil_rready(s_data_memory_axil_rready),
      .s_axil_awaddr(s_data_memory_axil_awaddr),
      .s_axil_awvalid(s_data_memory_axil_awvalid),
      .s_axil_awready(s_data_memory_axil_awready),
      .s_axil_wdata(s_data_memory_axil_wdata),
      .s_axil_wstrb(s_data_memory_axil_wstrb),
      .s_axil_wvalid(s_data_memory_axil_wvalid),
      .s_axil_wready(s_data_memory_axil_wready),
      .s_axil_bresp(s_data_memory_axil_bresp),
      .s_axil_bvalid(s_data_memory_axil_bvalid),
      .s_axil_bready(s_data_memory_axil_bready)
  );
  // verilator lint_on  PINMISSING

  // verilator lint_off PINMISSING
  axil_ram data_ram (
      .clk           (i_Clock),
      .rst           (i_Reset),
      .s_axil_araddr (s_data_memory_axil_araddr[15:0]),
      .s_axil_arvalid(s_data_memory_axil_arvalid),
      .s_axil_arready(s_data_memory_axil_arready),
      .s_axil_rdata  (s_data_memory_axil_rdata),
      .s_axil_rvalid (s_data_memory_axil_rvalid),
      .s_axil_rready (s_data_memory_axil_rready),
      .s_axil_awvalid(s_data_memory_axil_awvalid),
      .s_axil_awaddr (s_data_memory_axil_awaddr[15:0]),
      .s_axil_awready(s_data_memory_axil_awready),
      .s_axil_wvalid (s_data_memory_axil_wvalid),
      .s_axil_wdata  (s_data_memory_axil_wdata),
      .s_axil_wstrb  (s_data_memory_axil_wstrb),
      .s_axil_wready (s_data_memory_axil_wready),
      .s_axil_bvalid (s_data_memory_axil_bvalid),
      .s_axil_bready (s_data_memory_axil_bready),
      .s_axil_bresp  (s_data_memory_axil_bresp)
  );
  // verilator lint_off PINMISSING

  // verilator lint_off PINMISSING
  axil_ram instruction_ram (
      .clk           (i_Clock),
      .rst           (i_Reset),
      .s_axil_araddr (s_instruction_memory_axil_araddr[15:0]),
      .s_axil_arvalid(s_instruction_memory_axil_arvalid),
      .s_axil_arready(s_instruction_memory_axil_arready),
      .s_axil_rdata  (s_instruction_memory_axil_rdata),
      .s_axil_rvalid (s_instruction_memory_axil_rvalid),
      .s_axil_rready (s_instruction_memory_axil_rready)
  );
  // verilator lint_off PINMISSING

  uart_receiver uart_receiver (.i_Clock(i_Clock));

  debug_peripheral debug_peripheral (
      .i_Reset(i_Reset),
      .i_Clock(i_Clock)
  );

endmodule
