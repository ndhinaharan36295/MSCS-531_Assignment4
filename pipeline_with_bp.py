from m5.objects import *
import m5
from m5.util import addToPath
import os

# Add configs path for workload compatibility
addToPath('../configs/')

def create_o3cpu(system):
    cpu = DerivO3CPU(
        fetchWidth=1,  # Narrow pipeline for clearer visualization
        decodeWidth=1,
        issueWidth=1,
        commitWidth=1,
        numIQEntries=8,
        numROBEntries=16,
        # a Local History Predictor
        branchPred=LocalBP(
            localPredictorSize=2048,  # Number of BHT entries
            localCtrBits=2,           # 2-bit saturating counters (default: 2)
            BTBEntries=4096
        )
    )

    # Create and connect interrupt controller
    cpu.createInterruptController()
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    return cpu

def run_simulation():
    system = System()
    system.clk_domain = SrcClockDomain(clock='1GHz')
    system.clk_domain.voltage_domain = VoltageDomain()

    # Memory system
    system.membus = SystemXBar()
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('1GB')]
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.port = system.membus.mem_side_ports

    # CPU setup
    system.cpu = create_o3cpu(system)
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

    # Workload
    binary = 'tests/test-progs/pipeline_test/bin/x86/linux/pipeline_test'
    process = Process()
    process.cmd = [binary]
    system.cpu.workload = process
    system.cpu.createThreads()
    system.workload = SEWorkload.init_compatible(binary)

    # Pipeline visualization
    os.environ['GEM5_DEBUG_FLAGS'] = 'O3PipeView,Fetch,Decode,Execute'
    os.environ['GEM5_DEBUG_FILE'] = 'O3PipeView.log'

    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Running O3CPU 5-stage pipeline")
    exit_event = m5.simulate()

    print(f"Completed @ tick {m5.curTick()}")

if __name__ == "__m5_main__":
    run_simulation()
    