from collections import namedtuple
from itertools import accumulate


class Sim_Config(object):
    """ Configurations for simulation settings"""
    # NOTE the corridor with paramters below is "homogenous"
    # it can handle inhomegeous case with modifications and without changing the strcurture a lot

    def __init__(self, method_config):
        # simulation time step in time-based simulation logic
        self.delta_t = 1.0
        # the total simulation duration for one round (you may repeat it for many times to get the convergent result)
        self.sim_duration = int(3600*4)
        # scheduled headway at the terminal, in seconds
        self.schd_hdw = 10 * 60
        # the number of stop and links
        # terminal will dispatch bus into the first link (link_id == 0) and then first stop
        self.seg_num = 12
        # spacing between two consecutive stops
        self.inter_stop_spacing = 1000
        # all the links' upstream ends
        self.link_start_locs = [
            x*self.inter_stop_spacing for x in range(self.seg_num)]
        # link length
        self.link_lengths = [self.inter_stop_spacing] * self.seg_num
        # Assume that link travel speed is a Gaussian R.V. with mean and coefficient of variation set below
        self.mean_speeds = [30 / 3.6] * self.seg_num  # m/s
        self.cv_speeds = [0.15] * self.seg_num  # dimensionless
        # all the stops' locations
        self.stop_locs = [
            (x+1)*self.inter_stop_spacing for x in range(self.seg_num)]
        # pax arrival rate  2 pax/min = 0.0333 pax/sec
        self.demand_rates = [2.5 / 60.0] * self.seg_num
        # pax boarding rate, the unit is pax/sec
        # within each time step, "0.5" pax will board the bus
        # Note that the pax is treated as continuous variable for simplicity
        self.board_rates = [0.5] * self.seg_num
        self.method_slack = method_config["slack"]
        self.start_times = self.get_demand_start_times()

        # constructing configuration for the above parameters
        self.line_config = self._get_line_config()
        self.link_config_dict = self._get_link_config()
        self.stop_config_dict = self._get_stop_config()
        self.terminal_config = self._get_terminal_config()

    def _get_line_config(self):
        Line_Config = namedtuple(
            "line_config", ["schd_hdw"])
        # scheduled headways, 10 min = 10*60 seconds
        config = Line_Config(self.schd_hdw)
        return config

    def _get_link_config(self):
        Link_Config = namedtuple(
            "link_config", ["start_loc", "length", "mean_speed", "cv_speed"])
        # link_id -> config in "namedtuple" shape
        link_config_dict = {}
        for link in range(self.seg_num):
            start_loc = self.link_start_locs[link]
            length = self.link_lengths[link]
            mean_speed = self.mean_speeds[link]
            cv_speed = self.cv_speeds[link]
            config = Link_Config(start_loc, length, mean_speed, cv_speed)
            link_config_dict[link] = config

        return link_config_dict

    def _get_stop_config(self):
        Stop_Config = namedtuple(
            "stop_config", ["loc", "demand_rate", "board_rate", "demand_start_time"])
        # stop_id -> config in "namedtuple" shape
        stop_config_dict = {}
        seg_times = []
        for stop in range(self.seg_num):
            loc = self.stop_locs[stop]
            demand_rate = self.demand_rates[stop]
            board_rate = self.board_rates[stop]
            start_time = self.start_times[stop]
            config = Stop_Config(loc, demand_rate, board_rate, start_time)
            stop_config_dict[stop] = config

        return stop_config_dict

    def _get_terminal_config(self):
        Terminal_Config = namedtuple(
            "terminal_config", ["schd_hdw", "sim_bus_num", "dspt_times"])
        schd_hdw = self.line_config.schd_hdw
        # No. of buses needed for one simulation round
        sim_bus_num = self.sim_duration//schd_hdw + 1
        # the dispatch time for each bus (when leaving the terminal stop)
        dspt_times = [(x+1)*schd_hdw for x in range(sim_bus_num)]
        config = Terminal_Config(
            schd_hdw, sim_bus_num, dspt_times)
        return config

    def get_demand_start_times(self):
        # here we create a "virtual" bus to determine when the stops begin to make passenger arriavals
        # this bus uses mean travel time at a link and mean dwell time at a stop, plus a slack time
        seg_times = []
        for seg in range(self.seg_num):
            # "scheduled" travel time at a link
            avg_travel = self.link_lengths[seg] / self.mean_speeds[seg]
            # "scheduled" dwell time at a stop
            avg_dwell = self.demand_rates[seg] * \
                self.schd_hdw / self.board_rates[seg]
            seg_times.append(avg_travel+avg_dwell+self.method_slack)
        start_times = list(accumulate(seg_times))

        return start_times


if __name__ == "__main__":
    config = Sim_Config()
    print(config.stop_config_dict[1])
    print(config.link_config_dict[0])
    print(config.line_config)
    print(config.terminal_config)
