#include "dcif_state.h"
#include <stdio.h>

static dcif_state_t STATE = {0};

void dcif_load_state(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) return;

    fscanf(
        f,
        "{ \"instability\": %lf , \"saturation\": %lf , \"resistance\": %lf , \"epoch\": %lu }",
        &STATE.instability,
        &STATE.saturation,
        &STATE.resistance,
        &STATE.epoch
    );

    fclose(f);
}

dcif_state_t *dcif_get_state(void)
{
    return &STATE;
}
