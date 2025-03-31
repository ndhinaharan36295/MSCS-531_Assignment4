from m5.objects import *
import m5
from m5.util import addToPath
import os

# Add configs path for workload compatibility
addToPath('../configs/')

def create_superscalar_cpu(system):
    cpu = DerivO3CPU(
        # Superscalar widths (4-wide pipeline)
        fetchWidth=4,       # Fetch up to 4 instructions per cycle
        decodeWidth=4,      # Decode up to 4 instructions per cycle
        renameWidth=4,      # Rename up to 4 instructions per cycle
        issueWidth=4,       # Issue up to 4 instructions per cycle
        commitWidth=4,      # Commit up to 4 instructions per cycle

        # Larger structures to prevent bottlenecks
        numIQEntries=32,    # Increased instruction queue entries
        numROBEntries=64,   # Increased reorder buffer entries
        numPhysIntRegs=256, # More physical registers for renaming
        numPhysFloatRegs=256,

        # Branch predictor (improved for superscalar)
        branchPred=TournamentBP(
            localPredictorSize=2048,
            localCtrBits=2,
            globalPredictorSize=8192,
            choicePredictorSize=8192,
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

    # Memory system (improved for superscalar)
    system.membus = SystemXBar()
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]  # Increased memory
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR4_2400_16x4()  # Faster DDR4 memory
    system.mem_ctrl.port = system.membus.mem_side_ports

    # CPU setup
    system.cpu = create_superscalar_cpu(system)
    system.cpu.icache_port = system.membus.cpu_side_ports
    system.cpu.dcache_port = system.membus.cpu_side_ports

    # Workload
    binary = 'tests/test-progs/pipeline_test/bin/x86/linux/pipeline_test'
    process = Process()
    process.cmd = [binary]
    system.cpu.workload = process
    system.cpu.createThreads()
    system.workload = SEWorkload.init_compatible(binary)

    # Pipeline visualization (now tracks superscalar execution)
    os.environ['GEM5_DEBUG_FLAGS'] = 'O3PipeView,Fetch,Decode,Rename,IEW,Commit'
    os.environ['GEM5_DEBUG_FILE'] = 'SuperscalarPipeView.log'

    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Running 4-wide Superscalar O3CPU")
    exit_event = m5.simulate()

    print(f"Simulation completed @ tick {m5.curTick()}")

if __name__ == "__m5_main__":
    run_simulation()
    