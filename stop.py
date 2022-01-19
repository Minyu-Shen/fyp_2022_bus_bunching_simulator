import numpy as np
from collections import namedtuple


class Stop_Record(object):
    def __init__(self, demand_start_time):
        self.demand_start_time = demand_start_time
        self.Departure_Event = namedtuple(
            'departure_event', ["bus_id", "dpt_time"])
        self.reset()

    def add_arr_event(self, bus_id, arr_time):
        self.arr_events.append((bus_id, arr_time))

    def add_dpt_event(self, bus_id, dpt_time):
        dpt_event = self.Departure_Event(bus_id, dpt_time)
        # print(dpt_event)
        self.dpt_events.append(dpt_event)

    def reset(self):
        self.arr_events = []
        self.dpt_events = []
        # the id of "virtual bus" is set to be -1
        # this time is used for the first bus to determine holding time
        self.dpt_events.append(
            self.Departure_Event(-1, self.demand_start_time))


class Stop(object):
    def __init__(self, stop_id, config):
        self.stop_id = stop_id
        self._config = config

        self._loc = config.loc
        self._next_link = None
        # the (continuous) pax queue at the stop
        self._pax_queue = 0
        # store the bus into the list for future retrieval and update
        self._bus_list = []
        # storing buses that departed and check whether to hold or not
        self._outside_list = []
        self._record = Stop_Record(config.demand_start_time)

    def add_next_link(self, next_link):
        ''' Link stop and link '''
        self._next_link = next_link

    def get_stats(self):
        dpt_times = [event.dpt_time for event in self._record.dpt_events]
        dpt_times = sorted(dpt_times)
        dpt_hdws = [dpt_times[i+1] - dpt_times[i]
                    for i in range(0, len(dpt_times)-1)]
        return dpt_hdws

    def get_last_dpt_event(self):
        return self._record.dpt_events[-1]

    def enter_bus(self, bus, curr_time):
        ''' Enter one bus into the stop from the upstream link '''
        # update bus's location information
        bus.loc = self._loc
        # record arrival event for future (potential) holding action
        self._record.add_arr_event(bus.bus_id, curr_time)
        self._bus_list.append(bus)
        # return True if two buses bunched at stop
        return True if len(self._bus_list) >= 2 else False

    def operation(self, curr_time, delta_t):
        ''' stop operations during each time step'''
        self._pax_arrive(curr_time)
        self._boarding(delta_t)
        self._leaving(curr_time)
        self._holding(delta_t, curr_time)

    def _pax_arrive(self, curr_time):
        ''' randomly generate pax arrival(s) '''
        if self._config.demand_start_time <= curr_time:
            self._pax_queue += np.random.poisson(self._config.demand_rate)

    def _boarding(self, delta_t):
        ''' board the pax from queue to the bus '''
        for bus in self._bus_list:
            self._pax_queue -= self._config.board_rate*delta_t

    def _leaving(self, curr_time):
        ''' check if the bus can leave (when no pax is left)'''
        finished_buses = []
        for bus in self._bus_list:
            if self._pax_queue > 0:
                # still serving, record the "horizontal" waiting trajectory
                bus.update_traj(curr_time)
                continue
            # queue is cleared
            if self._next_link is not None:
                if bus.method is None:
                    self._next_link.enter_bus(bus, curr_time)
                else:
                    bus.set_hold_time(
                        curr_time, self._record.dpt_events[-1].dpt_time,)
                    self._outside_list.append(bus)
            else:  # finished
                bus.is_running = False
            self._record.add_dpt_event(bus.bus_id, curr_time)
            finished_buses.append(bus)

        self._bus_list = [
            bus for bus in self._bus_list if bus not in finished_buses]

    def _holding(self, delta_t, curr_time):
        finished_buses = []
        for bus in self._outside_list:
            bus.holding_time -= delta_t
            if bus.holding_time <= 0:
                finished_buses.append(bus)
                self._next_link.enter_bus(bus, curr_time)

        self._outside_list = [
            bus for bus in self._outside_list if bus not in finished_buses]

    def reset(self):
        self._bus_list = []
        self._outside_list = []
        self._pax_queue = 0
        self._record.reset()
