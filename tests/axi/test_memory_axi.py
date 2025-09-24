import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, FallingEdge
from cocotb.clock import Clock

from cpu.constants import (
    LS_TYPE_LOAD_WORD,
    LS_TYPE_LOAD_HALF,
    LS_TYPE_LOAD_HALF_UNSIGNED,
    LS_TYPE_LOAD_BYTE,
    LS_TYPE_LOAD_BYTE_UNSIGNED,
    LS_TYPE_STORE_WORD,
    LS_TYPE_STORE_HALF,
    LS_TYPE_STORE_BYTE,
    LS_TYPE_NONE
)

wait_ns = 1

@cocotb.test()
async def test_memory(dut):
    """Test reading memory"""

    data = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    dut.memory_axi.ram.mem[0].value = data[0]
    dut.memory_axi.ram.mem[1].value = data[1]
    dut.memory_axi.ram.mem[2].value = data[2]
    dut.memory_axi.ram.mem[3].value = data[3]

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)


    for data_index in range(2):

        dut.memory_axi.i_Addr.value = data_index*4
        dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD

        await RisingEdge(dut.memory_axi.o_Data_Valid)
        
        value = dut.memory_axi.o_Data.value.integer
        expected = data[data_index]
        assert value == expected, f"Read failed at address 0: got {value:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_load_byte_unsigned(dut):
    """Test load byte instruction"""

    data = [0xAA, 0xBB, 0xCC, 0xDD]

    dut.memory_axi.ram.mem[0].value = data[0]
    dut.memory_axi.ram.mem[1].value = data[1]
    dut.memory_axi.ram.mem[2].value = data[2]
    dut.memory_axi.ram.mem[3].value = data[3]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE_UNSIGNED

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)


    for i in range(4):
        dut.memory_axi.i_Addr.value = i*4

        await RisingEdge(dut.memory_axi.o_Data_Valid)
        
        value = dut.memory_axi.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#04x}, expected {expected:#04x}"
        
@cocotb.test()
async def test_load_byte(dut):
    """Test load byte instruction with sign extension"""

    data = [-86, 127, -128, 0]  # 0xAA, 0x7F, 0x80, 0x00

    dut.memory_axi.ram.mem[0].value = data[0]
    dut.memory_axi.ram.mem[1].value = data[1]
    dut.memory_axi.ram.mem[2].value = data[2]
    dut.memory_axi.ram.mem[3].value = data[3]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    for i in range(4):
        dut.memory_axi.i_Addr.value = i*4
        
        await RisingEdge(dut.memory_axi.o_Data_Valid)

        value = dut.memory_axi.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#010x}, expected {expected:#010x}"        

@cocotb.test()
async def test_load_half_unsigned(dut):
    """Test load half instruction"""

    data = [0xAABB, 0xCCDD]

    dut.memory_axi.ram.mem[0].value = data[0]
    dut.memory_axi.ram.mem[1].value = data[1]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF_UNSIGNED

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i*4

        await RisingEdge(dut.memory_axi.o_Data_Valid)

        value = dut.memory_axi.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*4}: got {value:#06x}, expected {expected:#06x}"

@cocotb.test()
async def test_load_half(dut):
    """Test load half instruction with sign extension"""

    data = [-21846, 32767]  # 0xAABB, 0x7FFF
    dut.memory_axi.ram.mem[0].value = data[0]
    dut.memory_axi.ram.mem[1].value = data[1]
    
    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i * 4

        await RisingEdge(dut.memory_axi.o_Data_Valid)

        value = dut.memory_axi.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*4}: got {value:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_load_word(dut):
    """Test load word instruction"""

    data = 0xAABBCCDD

    dut.memory_axi.ram.mem[0].value = 0xAABBCCDD

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD

    dut.memory_axi.i_Addr.value = 0

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    await RisingEdge(dut.memory_axi.o_Data_Valid)

    value = dut.memory_axi.o_Data.value.integer
    expected = data
    assert value == expected, f"Load word failed: got {value:#010x}, expected {expected:#010x}"


@cocotb.test()
async def test_store_byte(dut):
    """Test store byte instruction"""

    data = [0x11, 0x22, 0x33, 0x44]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_BYTE
    dut.memory_axi.i_Write_Enable.value = 1

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    for i in range(4):
        dut.memory_axi.i_Addr.value = i*4
        dut.memory_axi.i_Data.value = data[i]

        await RisingEdge(dut.memory_axi.o_Ready)

        for j in range(20):
            dut._log.info(f"{dut.memory_axi.ram.mem[j].value.integer:#04x}")

        value = dut.memory_axi.ram.mem[i].value.integer
        expected = data[i]
        assert value == expected, f"Store byte failed at address {i*4}: got {value:#04x}, expected {expected:#04x}"

@cocotb.test()
async def test_store_half(dut):
    """Test store half instruction"""

    data = [0x1122, 0x3344]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_HALF
    dut.memory_axi.i_Write_Enable.value = 1

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i * 4
        dut.memory_axi.i_Data.value = data[i]

        await RisingEdge(dut.memory_axi.o_Ready)

        value = dut.memory_axi.ram.mem[i].value.integer
        expected = data[i]
        assert value == expected, f"Store half failed at address {i*4}: got {value:#06x}, expected {expected:#06x}"


@cocotb.test()
async def test_store_word(dut):
    """Test store word instruction"""

    data = 0x11223344

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_WORD

    dut.memory_axi.i_Write_Enable.value = 1
    dut.memory_axi.i_Addr.value = 0
    dut.memory_axi.i_Data.value = data

    clock = Clock(dut.memory_axi.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.memory_axi.i_Reset.value = 1
    await ClockCycles(dut.memory_axi.i_Clock, 1)
    dut.memory_axi.i_Reset.value = 0
    await ClockCycles(dut.memory_axi.i_Clock, 1)

    await RisingEdge(dut.memory_axi.o_Ready)

    value = dut.memory_axi.ram.mem[0].value
    expected = data
    assert value == expected, f"Store word failed: got {value:#010x}, expected {expected:#010x}"

