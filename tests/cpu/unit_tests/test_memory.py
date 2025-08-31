import cocotb
from cocotb.triggers import Timer
from constants import (
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
async def test_load_byte_unsigned(dut):
    """Test load byte instruction"""

    data = [0xAA, 0xBB, 0xCC, 0xDD]

    dut.memory.Memory_Array[0].value = data[0]
    dut.memory.Memory_Array[1].value = data[1]
    dut.memory.Memory_Array[2].value = data[2]
    dut.memory.Memory_Array[3].value = data[3]

    dut.memory.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE_UNSIGNED

    for i in range(4):
        dut.memory.i_Addr.value = i
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.memory.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#04x}, expected {expected:#04x}"
        
@cocotb.test()
async def test_load_byte(dut):
    """Test load byte instruction with sign extension"""

    data = [-86, 127, -128, 0]  # 0xAA, 0x7F, 0x80, 0x00

    dut.memory.Memory_Array[0].value = data[0]
    dut.memory.Memory_Array[1].value = data[1]
    dut.memory.Memory_Array[2].value = data[2]
    dut.memory.Memory_Array[3].value = data[3]

    dut.memory.i_Load_Store_Type.value = LS_TYPE_LOAD_BYTE

    for i in range(4):
        dut.memory.i_Addr.value = i
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.memory.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load byte failed at address {i}: got {value:#010x}, expected {expected:#010x}"        

@cocotb.test()
async def test_load_half_unsigned(dut):
    """Test load half instruction"""

    data = [0xAABB, 0xCCDD]

    dut.memory.Memory_Array[0].value = data[0] & 0xFF
    dut.memory.Memory_Array[1].value = (data[0] >> 8) & 0xFF
    dut.memory.Memory_Array[2].value = data[1] & 0xFF
    dut.memory.Memory_Array[3].value = (data[1] >> 8) & 0xFF

    dut.memory.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF_UNSIGNED

    for i in range(2):
        dut.memory.i_Addr.value = i * 2
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.memory.o_Data.value.integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*2}: got {value:#06x}, expected {expected:#06x}"

@cocotb.test()
async def test_load_half(dut):
    """Test load half instruction with sign extension"""

    data = [-21846, 32767]  # 0xAABB, 0x7FFF
    dut.memory.Memory_Array[0].value = data[0] & 0xFF
    dut.memory.Memory_Array[1].value = (data[0] >> 8)
    dut.memory.Memory_Array[2].value = data[1] & 0xFF
    dut.memory.Memory_Array[3].value = (data[1] >> 8)
    
    dut.memory.i_Load_Store_Type.value = LS_TYPE_LOAD_HALF

    for i in range(2):
        dut.memory.i_Addr.value = i * 2
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.memory.o_Data.value.signed_integer
        expected = data[i]
        assert value == expected, f"Load half failed at address {i*2}: got {value:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_load_word(dut):
    """Test load word instruction"""

    data = 0xAABBCCDD

    dut.memory.Memory_Array[0].value = data & 0xFF
    dut.memory.Memory_Array[1].value = (data >> 8) & 0xFF
    dut.memory.Memory_Array[2].value = (data >> 16) & 0xFF
    dut.memory.Memory_Array[3].value = (data >> 24) & 0xFF

    dut.memory.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD
    dut.memory.i_Addr.value = 0
    dut.memory.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    dut.memory.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    value = dut.memory.o_Data.value.integer
    expected = data
    assert value == expected, f"Load word failed: got {value:#010x}, expected {expected:#010x}"


@cocotb.test()
async def test_store_byte(dut):
    """Test store byte instruction"""

    data = [0x11, 0x22, 0x33, 0x44]

    dut.memory.i_Load_Store_Type.value = LS_TYPE_STORE_BYTE
    dut.memory.i_Write_Enable.value = 1

    for i in range(4):
        dut.memory.i_Addr.value = i
        dut.memory.i_Data.value = data[i]
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.memory.Memory_Array[i].value.integer
        expected = data[i]
        assert value == expected, f"Store byte failed at address {i}: got {value:#04x}, expected {expected:#04x}"

@cocotb.test()
async def test_store_half(dut):
    """Test store half instruction"""

    data = [0x1122, 0x3344]

    dut.memory.i_Load_Store_Type.value = LS_TYPE_STORE_HALF
    dut.memory.i_Write_Enable.value = 1

    for i in range(2):
        dut.memory.i_Addr.value = i * 2
        dut.memory.i_Data.value = data[i]
        dut.memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        low_byte = dut.memory.Memory_Array[i * 2].value.integer
        high_byte = dut.memory.Memory_Array[i * 2 + 1].value.integer
        value = (high_byte << 8) | low_byte
        expected = data[i]
        assert value == expected, f"Store half failed at address {i*2}: got {value:#06x}, expected {expected:#06x}"


@cocotb.test()
async def test_store_word(dut):
    """Test store word instruction"""

    data = 0x11223344

    dut.memory.i_Load_Store_Type.value = LS_TYPE_STORE_WORD
    dut.memory.i_Write_Enable.value = 1
    dut.memory.i_Addr.value = 0
    dut.memory.i_Data.value = data
    dut.memory.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    dut.memory.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    value = (
        (dut.memory.Memory_Array[3].value.integer << 24) |
        (dut.memory.Memory_Array[2].value.integer << 16) |
        (dut.memory.Memory_Array[1].value.integer << 8) |
        dut.memory.Memory_Array[0].value.integer
    )
    expected = data
    assert value == expected, f"Store word failed: got {value:#010x}, expected {expected:#010x}"

