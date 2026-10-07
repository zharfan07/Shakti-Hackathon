import cocotb
import random
import os

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from mkintegerModel import divider_model

COUNT = int(os.environ.get("COUNT", 1000))

TIMEOUT = 200


async def run_div_test(dut, A, B, opcode, funct3):
    clkedge = RisingEdge(dut.CLK)

    dut.EN_ma_start.value = 1
    dut.ma_start_opcode.value = opcode
    dut.ma_start_funct3.value = funct3
    dut.ma_start_dividend.value = A
    dut.ma_start_divisor.value = B

    await clkedge

    dut.EN_ma_start.value = 0

    #
    # Wait for divider to finish
    #
    for _ in range(TIMEOUT):

        # DUT's valid signal
        if int(dut.mav_result.value) != 0 or B == 0:
            break

        await clkedge
    else:
        raise AssertionError(
            f"Timeout waiting for divider. A={hex(A)} B={hex(B)}"
        )

    dut_result = int(dut.mav_result.value)
    model_result = divider_model(A, B, opcode, funct3)

    assert dut_result == model_result, (
        f"\nA          = {hex(A)}"
        f"\nB          = {hex(B)}"
        f"\nDUT        = {hex(dut_result)}"
        f"\nExpected   = {hex(model_result)}"
    )


@cocotb.test()
async def divider_signed_div_test(dut):

    cocotb.start_soon(Clock(dut.CLK, 10).start())

    dut.ma_set_flush_c.value = 1
    dut.EN_ma_set_flush.value = 1
    dut.RST_N.value = 0

    for _ in range(5):
        await RisingEdge(dut.CLK)

    dut.RST_N.value = 1

    opcode = 12
    funct3 = 5

    ###################################################
    # Directed Corner Cases
    ###################################################

    directed = [

        # dividend, divisor

        (0, 1),
        (1, 1),
        (2, 1),
        (5, 2),

        (0, 2),
        (2, 5),

        (0, 0),
        (1, 0),
        (0xffffffffffffffff, 0),

        (0xffffffffffffffff, 1),
        (0xffffffffffffffff, 2),
        (0xffffffffffffffff, 0xffffffffffffffff),

        (1 << 63, 1),
        ((1 << 63) - 1, 1),

        (1 << 32, 2),
        ((1 << 32) - 1, 3),

        (0x8000000000000000, 0xffffffffffffffff),
    ]

    cocotb.log.info("Running directed tests")

    for A, B in directed:
        await run_div_test(dut, A, B, opcode, funct3)

    ###################################################
    # Random Tests
    ###################################################

    cocotb.log.info(f"Running {COUNT} random tests")

    for i in range(COUNT):

        #
        # Bias toward interesting operands
        #

        if random.random() < 0.10:
            B = 0

        else:
            B = random.getrandbits(64)

        A = random.getrandbits(64)

        await run_div_test(dut, A, B, opcode, funct3)

        if (i + 1) % 100 == 0:
            cocotb.log.info(f"Completed {i+1} tests")

    cocotb.log.info("All DIV tests passed.")
