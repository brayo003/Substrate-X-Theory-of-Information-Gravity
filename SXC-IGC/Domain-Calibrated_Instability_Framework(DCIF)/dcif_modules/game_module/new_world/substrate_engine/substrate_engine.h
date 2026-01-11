#ifndef SUBSTRATE_ENGINE_H
#define SUBSTRATE_ENGINE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double signal;      // instantaneous input
    double pressure;    // integrated system pressure
    double time;        // monotonic time reference
} SubstrateEngine;

/* Initialize engine state */
void substrate_init(SubstrateEngine *engine);

/* Step engine with external signal */
void substrate_step(SubstrateEngine *engine,
                    double signal,
                    double time_delta);

/* Read-only accessors */
double substrate_get_pressure(const SubstrateEngine *engine);
double substrate_get_signal(const SubstrateEngine *engine);

#ifdef __cplusplus
}
#endif

#endif /* SUBSTRATE_ENGINE_H */
