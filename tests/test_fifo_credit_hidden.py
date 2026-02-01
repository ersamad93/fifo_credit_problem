import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_fifo_fill_and_drain(dut):
    """Test filling FIFO to capacity and draining it"""
    DEPTH = 8
    DW = 16
    
    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.wr_valid.value = 0
    dut.rd_ready.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Verify initial credit count
    assert dut.credit_count.value == DEPTH, f"Expected credit_count={DEPTH}, got {dut.credit_count.value}"
    
    # Fill FIFO
    written_data = []
    for i in range(DEPTH):
        await RisingEdge(dut.clk)
        dut.wr_valid.value = 1
        data_val = random.randint(0, (1 << DW) - 1)
        dut.wr_data.value = data_val
        written_data.append(data_val)
        # Wait for write to complete if not ready
        await RisingEdge(dut.clk)
        if dut.wr_ready.value == 0:
            await RisingEdge(dut.clk)
    
    dut.wr_valid.value = 0
    await RisingEdge(dut.clk)
    
    # Try overfill (should stall)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.wr_ready.value == 0, "FIFO should not accept writes when full"
    
    # Drain FIFO
    dut.rd_ready.value = 1
    for i in range(DEPTH):
        await RisingEdge(dut.clk)
        # Wait for valid data
        if dut.rd_valid.value == 0:
            await RisingEdge(dut.clk)
    
    dut.rd_ready.value = 0
    await RisingEdge(dut.clk)
    
    # Credits should be restored
    assert dut.credit_count.value == DEPTH, f"Expected credit_count={DEPTH} after drain, got {dut.credit_count.value}"

@cocotb.test()
async def test_simultaneous_read_write(dut):
    """Test simultaneous read and write operations"""
    DEPTH = 8
    DW = 16
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.wr_valid.value = 0
    dut.rd_ready.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Fill partially
    for i in range(4):
        await RisingEdge(dut.clk)
        dut.wr_valid.value = 1
        dut.wr_data.value = i * 100
        await RisingEdge(dut.clk)
    
    dut.wr_valid.value = 0
    await RisingEdge(dut.clk)
    
    # Simultaneous read and write
    initial_credit = int(dut.credit_count.value)
    initial_fifo_count = DEPTH - initial_credit
    
    dut.wr_valid.value = 1
    dut.rd_ready.value = 1
    dut.wr_data.value = 0xABCD
    
    await RisingEdge(dut.clk)
    
    # Credit count should remain the same (write and read cancel out)
    final_credit = int(dut.credit_count.value)
    assert final_credit == initial_credit, f"Credit count should not change with simultaneous r/w: {initial_credit} -> {final_credit}"

@cocotb.test()
async def test_credit_flow_control(dut):
    """Test credit-based flow control"""
    DEPTH = 8
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.wr_valid.value = 0
    dut.rd_ready.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Initial state: credits = DEPTH, wr_ready should be 1
    assert dut.credit_count.value == DEPTH
    assert dut.wr_ready.value == 1, "Should be ready when credits available"
    assert dut.rd_valid.value == 0, "Should not be valid when FIFO empty"
    
    # Write one item - credits should decrease
    dut.wr_valid.value = 1
    dut.wr_data.value = 0x1234
    await RisingEdge(dut.clk)
    dut.wr_valid.value = 0
    
    assert dut.credit_count.value == DEPTH - 1, f"Credits should decrease after write: got {dut.credit_count.value}"
    assert dut.rd_valid.value == 1, "Should be valid after write"

# CRITICAL: Pytest wrapper function
def test_fifo_credit_hidden_runner():
    import os
    from pathlib import Path
    from cocotb_tools.runner import get_runner
    
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    sources = [
        proj_path / "sources/fifo_credit.sv",
    ]
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fifo_credit",
        always=True,
    )
    
    runner.test(
        hdl_toplevel="fifo_credit",
        test_module="test_fifo_credit_hidden"
    )
