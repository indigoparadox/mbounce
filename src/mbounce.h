
#ifndef MBOUNCE_H
#define MBOUNCE_H

#include <stdint.h>

struct mbounce_xy {
   int16_t x;
   int16_t y;
};

#ifndef MBOUNCE_C
extern
#endif /* MBOUNCE_C */
const struct mbounce_xy g_mbounce_left
#ifdef MBOUNCE_C
= { -1,  0 }
#endif /* MBOUNCE_C */
;

#ifndef MBOUNCE_C
extern
#endif /* MBOUNCE_C */
const struct mbounce_xy g_mbounce_right
#ifdef MBOUNCE_C
= {  1,  0 }
#endif /* MBOUNCE_C */
;

#ifndef MBOUNCE_C
extern
#endif /* MBOUNCE_C */
const struct mbounce_xy g_mbounce_up
#ifdef MBOUNCE_C
= {  0, -1 }
#endif /* MBOUNCE_C */
;

#ifndef MBOUNCE_C
extern
#endif /* MBOUNCE_C */
const struct mbounce_xy g_mbounce_down
#ifdef MBOUNCE_C
= {  0,  1 }
#endif /* MBOUNCE_C */
;

#ifndef MBOUNCE_C
extern
#endif /* MBOUNCE_C */
const struct mbounce_xy g_mbounce_accel_max
#ifdef MBOUNCE_C
= { 3, 5 }
#endif /* MBOUNCE_C */
;

void mbounce_accel(
   struct mbounce_xy* factor, const struct mbounce_xy* dir,
   const struct mbounce_xy* max, uint8_t mult );

void mbounce_friction(
   struct mbounce_xy* factor, const struct mbounce_xy* coords,
   const struct mbounce_xy* max, const struct mbounce_xy* ubounds,
   uint8_t jump );

#endif /* MBOUNCE_H */

