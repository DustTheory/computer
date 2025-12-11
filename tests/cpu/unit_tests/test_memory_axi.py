import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, FallingEdge
from cocotb.clock import Clock

from cpu.utils import (
    write_word_to_mem,
    write_half_to_mem,
    write_byte_to_mem,
)

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

    for i, w in enumerate(data):
        write_word_to_mem(dut.data_ram.mem, i * 4, w)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)


    for data_index in range(2):

        dut.memory_axi.i_Addr.value = data_index*4
        dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD

        await RisingEdge(dut.w_Mem_ready)
        
        value = dut.memory_axi.o_Data.value.integer
        expected = data[data_index]
        assert value == expected, f"Read failed at address 0: got {value:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_load_byte_unsigned(dut):
    """Test load byte instruction"""

    data = [0x11, 0x22, 0x33, 0x44]

    for i, b in enumerate(data):
        write_byte_to_mem(dut.data_ram.mem, i * 4, b)

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE_UNSIGNED

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)


    for i in range(4):
        dut.memory_axi.i_Addr.value = i * 4

        await RisingEdge(dut.w_Mem_ready)
        
        value = dut.memory_axi.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#04x}, expected {expected:#04x}"
        
@cocotb.test()
async def test_load_byte(dut):
    """Test load byte instruction with sign extension"""

    data = [-0x55, 0x7F, -0x80, 0x00]  # 0xAB, 0x7F, 0x80, 0x00 (first negative example)

    for i, v in enumerate(data):
        write_byte_to_mem(dut.data_ram.mem, i * 4, v & 0xFF)

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(4):
        dut.memory_axi.i_Addr.value = i * 4
        
        await RisingEdge(dut.w_Mem_ready)

        value = dut.memory_axi.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#010x}, expected {expected:#010x}"        

@cocotb.test()
async def test_load_half_unsigned(dut):
    """Test load half instruction"""

    data = [0xAABB, 0xCCDD]

    for i, h in enumerate(data):
        write_half_to_mem(dut.data_ram.mem, i * 4, h)

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF_UNSIGNED

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i*4

        await RisingEdge(dut.w_Mem_ready)

        value = dut.memory_axi.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*4}: got {value:#06x}, expected {expected:#06x}"

@cocotb.test()
async def test_load_half(dut):
    """Test load half instruction with sign extension"""

    data = [-21846, 32767]  # 0xAABB, 0x7FFF
    for i, h in enumerate(data):
        write_half_to_mem(dut.data_ram.mem, i * 4, h & 0xFFFF)
    
    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i * 4

        await RisingEdge(dut.w_Mem_ready)

        value = dut.memory_axi.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*4}: got {value:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_load_word(dut):
    """Test load word instruction"""

    data = 0xAABBCCDD

    write_word_to_mem(dut.data_ram.mem, 0, 0xAABBCCDD)

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD

    dut.memory_axi.i_Addr.value = 0

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await RisingEdge(dut.w_Mem_ready)

    value = dut.memory_axi.o_Data.value.integer
    expected = data
    assert value == expected, f"Load word failed: got {value:#010x}, expected {expected:#010x}"


@cocotb.test()
async def test_store_byte(dut):
    """Test store byte instruction"""

    data = [0x11, 0x7F, 0x80, 0x00]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_BYTE
    dut.memory_axi.i_Write_Enable.value = 1

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(4):
        dut.memory_axi.i_Addr.value = i * 4
        dut.memory_axi.i_Data.value = data[i] & 0xFF

        await RisingEdge(dut.w_Mem_ready)

        for j in range(8):  # trim debug noise
            pass

        value = dut.data_ram.mem[i * 4].value.integer
        expected = data[i] & 0xFF
        assert value == expected, f"Store byte failed at address {i*4}: got {value:#04x}, expected {expected:#04x}"

@cocotb.test()
async def test_store_half(dut):
    """Test store half instruction"""

    data = [0x1122, 0x3344]

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_HALF
    dut.memory_axi.i_Write_Enable.value = 1

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(2):
        dut.memory_axi.i_Addr.value = i * 4
        dut.memory_axi.i_Data.value = data[i] & 0xFFFF

        await RisingEdge(dut.w_Mem_ready)

        low  = dut.data_ram.mem[i * 4].value.integer
        high = dut.data_ram.mem[i * 4 + 1].value.integer
        value = low | (high << 8)
        expected = data[i] & 0xFFFF
        assert value == expected, f"Store half failed at base address {i*4}: got {value:#06x}, expected {expected:#06x}"


@cocotb.test()
async def test_store_word(dut):
    """Test store word instruction"""

    data = 0x11223344

    dut.memory_axi.i_Load_Store_Type.value = LS_TYPE_STORE_WORD

    dut.memory_axi.i_Write_Enable.value = 1
    dut.memory_axi.i_Addr.value = 0
    dut.memory_axi.i_Data.value = data & 0xFFFFFFFF

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await RisingEdge(dut.w_Mem_ready)

    b0 = dut.data_ram.mem[0].value.integer
    b1 = dut.data_ram.mem[1].value.integer
    b2 = dut.data_ram.mem[2].value.integer
    b3 = dut.data_ram.mem[3].value.integer
    value = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
    expected = data & 0xFFFFFFFF
    assert value == expected, f"Store word failed: got {value:#010x}, expected {expected:#010x}"

