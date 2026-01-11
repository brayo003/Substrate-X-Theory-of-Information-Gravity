#include "dcif_state.h"

SXC_Engine global_sxc_engine = {0.0, 0.0, 0.0};

void sxc_compute_tension(SXC_Engine* engine, double signal, double time) {
    engine->signal = signal;
    engine->time = time;
    // SXC-V12: 4.80 Chi2 Calibration
    engine->t_sys = signal * 0.048; 
}
