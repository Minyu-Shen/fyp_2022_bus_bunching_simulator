from collections import namedtuple
import numpy as np
from bus import Bus
from stop import Stop
from link import Link
from terminal import Terminal
import matplotlib.pyplot as plt


class Simulator(object):
    def __init__(self, config, method):

        self.config = config
        self._delta_t = config.delta_t
        self._sim_duration = config.sim_duration
        # current simulation time
        self._curr_time = 0.0
        # total buses for stats
        self._total_bus_dict = {}
        self.method = method

        # init the terminal stop
        self._terminal = Terminal(config.terminal_config, method)
        # init stops, an array for homing all the stops
        self._stop_list = []
        for stop_id in range(self.config.seg_num):
            stop = Stop(stop_id, self.config.stop_config_dict[stop_id])
            self._stop_list.append(stop)
        # init links, an array for homing all the links
        self._link_list = []
        for link_id in range(self.config.seg_num):
            link = Link(link_id, self.config.link_config_dict[link_id])
            self._link_list.append(link)
        # connect stops and links
        for index, link in enumerate(self._link_list):
            link.add_next_stop(self._stop_list[index])
        for index, stop in enumerate(self._stop_list):
            if index != self.config.seg_num-1:
                stop.add_next_link(self._link_list[index+1])

    def move_one_step(self):
        '''
        At each time step, advance the simulation system one step
        '''
        # check if dispatch bus into the first link
        dspt_buses = self._terminal.dispatch(self._curr_time)
        for bus in dspt_buses:
            self._total_bus_dict[bus.bus_id] = bus
            self._link_list[0].enter_bus(bus, self._curr_time)
        # do the link and stop operations sequentially
        for _, (link, stop) in enumerate(zip(self._link_list, self._stop_list)):
            # operations at each stop
            stop.operation(self._curr_time, self._delta_t)

            is_bunched = link.forward(self._curr_time, self._delta_t)
            if is_bunched:
                return True

        self._curr_time += self._delta_t
        return False

    def plot_time_space(self):
        '''
        This function is used for plotting the time-space diagram
        the horizontal lines in the graph are from the parameter settings in "parameters.py". The bus trajectories used in the graph are from each bus object (see bus.py).
        '''
        # plot stops
        for stop_loc in self.config.stop_locs:
            plt.hlines(stop_loc, 0, self._sim_duration,
                       linestyles='dashed', linewidth=1.0)

        # plot the bus trajectories
        bus_list = [bus for _, bus in self._total_bus_dict.items()]
        for bus in bus_list:
            t, x = zip(*bus.record.trajectories.items())
            plt.plot(t, x, color='black')
        plt.show()

    def get_stats(self):
        agg_hdws = []
        delays = []
        for stop in self._stop_list:
            hdws = stop.get_stats()
            agg_hdws.extend(hdws)
        for _, bus in self._total_bus_dict.items():
            delays.append(bus.get_hold_delay())

        avg_delay = sum(delays) / len(delays)
        return np.std(agg_hdws), avg_delay

    def reset(self):
        self._curr_time = 0.0
        self._total_bus = 0
        self._total_bus_dict = {}
        for link, stop in zip(self._link_list, self._stop_list):
            link.reset()
            stop.reset()
        self._terminal.reset()

    # def get_mean_std(self, headways):
    #     return np.around(np.mean(headways), decimals=1), np.around(np.std(headways), decimals=1)


if __name__ == "__main__":
    pass
