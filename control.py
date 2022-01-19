class Base_Method(object):
    """ Parent class for control method """

    def __init__(self, method_config):
        self.name = method_config["name"]

    def cal_hold_time(self, **kwargs):
        raise NotImplementedError


class No_Control(Base_Method):
    def __init__(self, config):
        super(No_Control, self).__init__(config)

    def cal_hold_time(self):
        pass


class Nonlinear(Base_Method):
    def __init__(self, config, sim_config):
        super(Nonlinear, self).__init__(config)
        self.alpha = config["alpha"]
        # all the stops are the same for the current setting, so here beta
        # is simply calculated by the first stop. When you study inhomogenous
        #  corridor (i.e. stops have different parameters), you can change it to a list
        self.beta = sim_config.demand_rates[0] / sim_config.board_rates[0]
        self.H = sim_config.schd_hdw
        self.slack = config["slack"]

    def cal_hold_time(self, curr_dpt_time, last_dpt_time):
        di1, di = curr_dpt_time, last_dpt_time
        hold_time = (self.alpha+self.beta) * (self.H - (di1-di))
        hold_time = max(0.0, hold_time + self.slack)
        return hold_time
