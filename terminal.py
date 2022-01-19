from bus import Bus
from copy import deepcopy


class Terminal(object):
    def __init__(self, config, method):
        self.config = config
        # counting the total bus for creating bus id
        self._total_bus_no = 0
        self._method = method
        self._schd_hdw = config.schd_hdw
        self._dspt_times = deepcopy(self.config.dspt_times)

    def dispatch(self, curr_time):
        ''' At ech time step, check if the bus can be dispatched from the terminal stop '''
        dspt_buses = []
        if self._dspt_times:
            if curr_time >= self._dspt_times[0]:
                bus = Bus(self._total_bus_no, self._method)
                self._total_bus_no += 1
                dspt_buses.append(bus)
                self._dspt_times.remove(self._dspt_times[0])
        return dspt_buses

    def reset(self):
        self._total_bus_no = 0
        self._dspt_times = deepcopy(self.config.dspt_times)
