#ifndef DCIF_STATE_H
#define DCIF_STATE_H

typedef struct {
    double t_sys;
    double signal;
    double time;
} SXC_Engine;

extern SXC_Engine global_sxc_engine;

void sxc_compute_tension(SXC_Engine* engine, double signal, double time);

#endif
