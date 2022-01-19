from simulator import Simulator
import matplotlib.pyplot as plt
from collections import defaultdict
from sim_config import Sim_Config
from control import Nonlinear

instance_no = 100
method_config = {"name": "Nonlinear", "alpha": 0.1, "slack": 30}
sim_config = Sim_Config(method_config)

method = Nonlinear(method_config, sim_config)
simulator = Simulator(sim_config, method)

stds = []
delays = []
is_bunchings = []
for sim_r in range(instance_no):
    if sim_r % 20 == 0:
        print(f"-----{sim_r}------")
    # the time-based logic is implemented in this for-loop
    for t in range(sim_config.sim_duration):
        # when two buses bunches, the simulation of this round will terminate
        is_bunched = simulator.move_one_step()
        if is_bunched:
            is_bunchings.append(True)
            break
    is_bunchings.append(False)

    hdw_std, avg_delay = simulator.get_stats()
    stds.append(hdw_std)
    delays.append(avg_delay)

    # the time-space diagram is plotted here, for checking the rightness of the simulation logic
    # if sim_r == instance_no-1:
    #     simulator.plot_time_space()
    # reset the simulator, for next round's simulaiton if any
    simulator.reset()

std = sum(stds) / len(stds)
delay = sum(delays) / len(delays)
bunch_count = sum([1 if is_b == True else 0 for is_b in is_bunchings])
print(std, delay, bunch_count)
