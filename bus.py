from collections import defaultdict, namedtuple

from sklearn.neighbors import NearestCentroid


class Travel_Record(object):
    "Recording traveling information"

    def __init__(self):
        # for ploting the trajectory and check the rightness
        self.trajectories = defaultdict(float)
        self.hold_delay = 0.0


class Bus(object):
    """Recording the bus's status"""

    def __init__(self, bus_id, method):
        # an integer indicating the bus id
        self.bus_id = bus_id
        # record the bus's current location
        self.loc = 0.0
        self.is_running = True
        # updated when entering the link
        self.seg_id = None
        # when bus enters a link, generate the link travel speed and assign it to this property
        self.travel_speed_this_link = None
        # when bus departs a stop, generate a holding time for it to stay still
        self.method = method
        self.holding_time = None
        self.record = Travel_Record()

        self.Control_Event = namedtuple(
            "control_event", ["bus_id", "stop_id", "action"])

    def update_traj(self, t):
        self.record.trajectories[t] = self.loc

    def set_hold_time(self, curr_time, last_dpt_time):
        hold_time = self.method.cal_hold_time(curr_time, last_dpt_time)
        self.holding_time = hold_time
        self.record.hold_delay += hold_time
        return hold_time

    def get_hold_delay(self):
        return self.record.hold_delay


if __name__ == "__main__":
    pass
