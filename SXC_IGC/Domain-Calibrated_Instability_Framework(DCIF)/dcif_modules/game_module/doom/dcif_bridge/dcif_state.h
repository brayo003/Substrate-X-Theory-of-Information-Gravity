#ifndef DCIF_STATE_H
#define DCIF_STATE_H

typedef struct {
    double instability;
    double saturation;
    double resistance;
    unsigned long epoch;
} dcif_state_t;

void dcif_load_state(const char *path);
dcif_state_t *dcif_get_state(void);

#endif
