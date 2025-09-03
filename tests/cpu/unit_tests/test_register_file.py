import cocotb
from cocotb.triggers import Timer

wait_ns = 1


@cocotb.test()
async def test_read(dut):
    """Test reading from the register file"""
    dut._log.info("Starting read test")

    # Initialize registers with known values
    dut.register_file.Registers = [i for i in range(32)]

    # Set inputs to zero
    dut.register_file.i_Read_Addr_1.value = 0
    dut.register_file.i_Read_Addr_2.value = 0
    dut.register_file.i_Write_Addr.value = 0
    dut.register_file.i_Write_Data.value = 0
    dut.register_file.i_Write_Enable.value = 0
    dut.register_file.i_Clock.value = 0
   
    for i in range(32):
        dut.register_file.i_Read_Addr_1.value = i
        dut.register_file.i_Read_Addr_2.value = i
        await Timer(wait_ns, units='ns')
        assert dut.register_file.o_Read_Data_1.value == i, f"Read Data 1 mismatch at addr {i}: expected {i}, got {dut.register_file.o_Read_Data_1.value}"
        assert dut.register_file.o_Read_Data_2.value == i, f"Read Data 2 mismatch at addr {i}: expected {i}, got {dut.register_file.o_Read_Data_2.value}"
        dut._log.info(f"Read from addr {i}: Data 1 = {dut.register_file.o_Read_Data_1.value}, Data 2 = {dut.register_file.o_Read_Data_2.value}")


@cocotb.test()
async def test_write(dut):
    """Test writing to the register file"""
    dut._log.info("Starting write test")

    # Initialize registers with zeros
    dut.register_file.Registers = [0 for _ in range(32)]

    # Set inputs to zero
    dut.register_file.i_Read_Addr_1.value = 0
    dut.register_file.i_Read_Addr_2.value = 0
    dut.register_file.i_Write_Addr.value = 0
    dut.register_file.i_Write_Data.value = 0
    dut.register_file.i_Write_Enable.value = 0
    dut.register_file.i_Clock.value = 0

    for i in range(1, 32):
        dut.register_file.i_Write_Addr.value = i
        dut.register_file.i_Write_Data.value = i * 10
        dut.register_file.i_Write_Enable.value = 1
        # Rising edge of the clock to write data
        dut.register_file.i_Clock.value = 1
        await Timer(wait_ns, units='ns')
        dut.register_file.i_Clock.value = 0
        await Timer(wait_ns, units='ns')
        # Disable write
        dut.register_file.i_Write_Enable.value = 0

        # Read back the written value
        dut.register_file.i_Read_Addr_1.value = i
        await Timer(wait_ns, units='ns')
        assert dut.register_file.o_Read_Data_1.value == i * 10, f"Write Data mismatch at addr {i}: expected {i * 10}, got {dut.register_file.o_Read_Data_1.value}"
        dut._log.info(f"Wrote to addr {i}: Data = {dut.register_file.o_Read_Data_1.value}")


@cocotb.test()
async def test_write_zero_register(dut):
    """Test that writing to register 0 has no effect"""
    dut._log.info("Starting write zero register test")

    # Initialize registers with known values
    dut.register_file.Registers = [i for i in range(32)]

    # Set inputs to zero
    dut.register_file.i_Read_Addr_1.value = 0
    dut.register_file.i_Read_Addr_2.value = 0
    dut.register_file.i_Write_Addr.value = 0
    dut.register_file.i_Write_Data.value = 999
    dut.register_file.i_Write_Enable.value = 1
    dut.register_file.i_Clock.value = 0

    # Rising edge of the clock to attempt to write data to register 0
    dut.register_file.i_Clock.value = 1
    await Timer(wait_ns, units='ns')
    dut.register_file.i_Clock.value = 0
    await Timer(wait_ns, units='ns')

    # Disable write
    dut.register_file.i_Write_Enable.value = 0

    # Read back from register 0
    dut.register_file.i_Read_Addr_1.value = 0
    await Timer(wait_ns, units='ns')
    assert dut.register_file.o_Read_Data_1.value == 0, f"Register 0 should always read as 0, got {dut.register_file.o_Read_Data_1.value}"
    dut._log.info(f"Register 0 read value: {dut.register_file.o_Read_Data_1.value}")


@cocotb.test()
async def test_simultaneous_read_write(dut):
    """Test simultaneous read and write operations"""
    dut._log.info("Starting simultaneous read/write test")

    # Initialize registers with known values
    dut.register_file.Registers = [i for i in range(32)]

    # Set inputs to zero
    dut.register_file.i_Read_Addr_1.value = 1
    dut.register_file.i_Read_Addr_2.value = 2
    dut.register_file.i_Write_Addr.value = 3
    dut.register_file.i_Write_Data.value = 999
    dut.register_file.i_Write_Enable.value = 1
    dut.register_file.i_Clock.value = 0

    # Rising edge of the clock to write data to register 3 while reading from registers 1 and 2
    dut.register_file.i_Clock.value = 1
    await Timer(wait_ns, units='ns')
    read_data_1 = dut.register_file.o_Read_Data_1.value.integer
    read_data_2 = dut.register_file.o_Read_Data_2.value.integer
    dut.register_file.i_Clock.value = 0
    await Timer(wait_ns, units='ns')

    # Disable write
    dut.register_file.i_Write_Enable.value = 0

    # Check read values
    assert read_data_1 == 1, f"Read Data 1 mismatch: expected 1, got {read_data_1}"
    assert read_data_2 == 2, f"Read Data 2 mismatch: expected 2, got {read_data_2}"
    dut._log.info(f"Simultaneous Read: Data 1 = {read_data_1}, Data 2 = {read_data_2}")

    # Read back the written value from register 3
    dut.register_file.i_Read_Addr_1.value = 3
    await Timer(wait_ns, units='ns')
    assert dut.register_file.o_Read_Data_1.value == 999, f"Write Data mismatch at addr 3: expected 999, got {dut.register_file.o_Read_Data_1.value}"
    dut._log.info(f"Wrote to addr 3: Data = {dut.register_file.o_Read_Data_1.value}")


@cocotb.test()
async def test_no_write_when_disabled(dut):
    """Test that no write occurs when write enable is low"""
    dut._log.info("Starting no write when disabled test")

    # Initialize registers with known values
    dut.register_file.Registers = [i for i in range(32)]

    # Set inputs to zero
    dut.register_file.i_Read_Addr_1.value = 4
    dut.register_file.i_Read_Addr_2.value = 0
    dut.register_file.i_Write_Addr.value = 4
    dut.register_file.i_Write_Data.value = 888
    dut.register_file.i_Write_Enable.value = 0
    dut.register_file.i_Clock.value = 0
    await Timer(wait_ns, units='ns')
    # Rising edge of the clock to attempt to write data to register 4
    dut.register_file.i_Clock.value = 1
    await Timer(wait_ns, units='ns')
    dut.register_file.i_Clock.value = 0
    await Timer(wait_ns, units='ns')
    # Read back from register 4
    dut.register_file.i_Read_Addr_1.value = 4
    await Timer(wait_ns, units='ns')
    assert dut.register_file.o_Read_Data_1.value == 4, f"Register 4 should remain unchanged, expected 4, got {dut.register_file.o_Read_Data_1.value}"
    dut._log.info(f"Register 4 read value (should be unchanged): {dut.register_file.o_Read_Data_1.value}")

