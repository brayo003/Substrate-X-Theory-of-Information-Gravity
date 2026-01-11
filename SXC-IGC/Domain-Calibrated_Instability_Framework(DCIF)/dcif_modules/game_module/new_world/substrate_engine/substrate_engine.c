#include "substrate_engine.h"

void substrate_init(SubstrateEngine *engine)
{
    engine->signal   = 0.0;
    engine->pressure = 0.0;
    engine->time     = 0.0;
}

void substrate_step(SubstrateEngine *engine,
                    double signal,
                    double time_delta)
{
    engine->signal = signal;
    engine->time  += time_delta;

    /* Base invariant:
       pressure accumulates proportionally to signal over time.
       No thresholds. No decay. No coefficients.
    */
    engine->pressure += signal * time_delta;
}

double substrate_get_pressure(const SubstrateEngine *engine)
{
    return engine->pressure;
}

double substrate_get_signal(const SubstrateEngine *engine)
{
    return engine->signal;
}
