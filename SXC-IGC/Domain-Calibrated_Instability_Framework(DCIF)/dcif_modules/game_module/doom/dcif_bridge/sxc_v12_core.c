#include <math.h>

typedef struct {
    double v_limit;
    double k_sat;
    double beta;
    double gamma;
    double t_sys;
    double last_r;
} SXC_Engine;

void sxc_init(SXC_Engine *eng) {
    eng->v_limit = 108.0;
    eng->k_sat = 0.55;
    eng->beta = 0.125;
    eng->gamma = 0.045;
    eng->t_sys = 0.0;
    eng->last_r = 0.0;
}

double sxc_compute_tension(SXC_Engine *eng, double signal, double r) {
    double dr = (r - eng->last_r > 0.1) ? (r - eng->last_r) : 0.1;
    eng->last_r = r;
    
    double E = log1p(signal); // Logarithmic Flux
    double inflow = E * eng->beta;
    double outflow = eng->gamma * eng->t_sys;
    
    eng->t_sys += (inflow - outflow) * dr;
    return eng->t_sys;
}

double sxc_get_velocity_boost(SXC_Engine *eng, double v_bar, double tension) {
    double v_sub = eng->v_limit * (1.0 - exp(-eng->k_sat * tension));
    return sqrt(pow(v_bar, 2) + pow(v_sub, 2));
}
