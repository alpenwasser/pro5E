import numpy as np


def linear_function(x, b0, b1):
    return b1 * x + b0


def preamp_curve(t, amp, amp_offset, period, t_offset, duty_cycle, tau1, tau2):
    def discharge_segment(t, amp, tau):
        return amp * np.exp(-t / tau)
    def charge_segment(t, amp, tau):
        return amp * (1.0 - np.exp(-t / tau))
    t_local = (t+t_offset) % period
    t_switch = period * duty_cycle
    def preamp_curve_single():
        for t_value in t_local:
            if t_value < t_switch:
                yield charge_segment(t_value, amp, tau1) + amp_offset
            else:
                yield discharge_segment(t_value - t_switch, amp, tau2) + amp_offset
    return np.array([x for x in preamp_curve_single()])
