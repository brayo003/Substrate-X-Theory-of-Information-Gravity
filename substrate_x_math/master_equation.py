import numpy as np

def information_gravity_force(k, s, v_sub):
    """
    Core force law:
    F = k * s * v_sub
    """
    return k * s * v_sub
