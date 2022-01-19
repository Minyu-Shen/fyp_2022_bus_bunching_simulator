import numpy as np
from collections import defaultdict


class Link(object):
    def __init__(self, link_id, config):
        self._link_id = link_id
        self._config = config
        self._start_loc = config.start_loc
        self._mean_speed = config.mean_speed
        self._cv_speed = config.cv_speed
        self._length = config.length
        self._end_loc = self._start_loc + self._length

        self._bus_list = []

    def add_next_stop(self, next_stop):
        self._next_stop = next_stop

    def enter_bus(self, bus, curr_time):
        ''' When the bus in the stop finishes the service, enter it into the link '''
        bus.loc = self._start_loc
        bus.update_traj(curr_time)
        bus.travel_speed_this_link = max(1.0, np.random.normal(
            self._mean_speed, self._cv_speed*self._mean_speed))
        self._bus_list.append(bus)

    def forward(self, curr_time, delta_t):
        ''' Advance the bus on the link, according to its randomly-generated travel speed '''
        is_bunched = False
        sent_buses = []
        for bus in self._bus_list:
            bus.loc += bus.travel_speed_this_link * delta_t
            bus.update_traj(curr_time)
            if bus.loc >= self._end_loc:  # reach the next stop
                bus.loc = self._end_loc
                is_bunched = self._next_stop.enter_bus(bus, curr_time)
                sent_buses.append(bus)
        self._bus_list = [
            bus for bus in self._bus_list if bus not in sent_buses]
        return is_bunched

    def reset(self):
        self._bus_list = []
