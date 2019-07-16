
#include <stdint.h>

struct mbounce_xy {
   int16_t x;
   int16_t y;
};

const struct mbounce_xy g_mbounce_left    = { -1,  0 };
const struct mbounce_xy g_mbounce_right   = {  1,  0 };
const struct mbounce_xy g_mbounce_up      = {  0, -1 };
const struct mbounce_xy g_mbounce_down    = {  0,  1 };

const struct mbounce_xy g_mbounce_accel_max = { 3, 5 };

void mbounce_accel(
   struct mbounce_xy* factor,
   const struct mbounce_xy* dir,
   const struct mbounce_xy* max,
   uint8_t mult
) {
   while( mult > 0 ) {

      factor->x += dir->x;
      factor->y += dir->y;

      /* Don't exceed X max. */
      if( 
         (0 < factor->x && max->x < factor->x) ||
         (0 > factor->x && max->x * -1 > factor->x)
      ) {
         factor->x = 0;
      }

      /* Don't exceed Y max. */
      if( 
         (0 < factor->y && max->y < factor->y) ||
         (0 > factor->y && max->y * -1 > factor->y)
      ) {
         factor->y = 0;
      }

      mult--;
   }
}

void mbounce_friction(
   struct mbounce_xy* factor,
   const struct mbounce_xy* coords,
   const struct mbounce_xy* max,
   const struct mbounce_xy* ubounds,
   uint8_t jump
) {
      if( coords->y < ubounds->y ) {
         /* If we're above the floor, then fall (accel according to gravity). */
         mbounce_accel( factor, &g_mbounce_down, max, 1 );
      } else if( coords->y + factor->y + jump >= ubounds->x ) {
         /* Set gravity to whatever it needs to be for us to "land" on the last
          * tick.
          */
         factor->y = ubounds->y - coords->y;
      }

      /* Apply gravity drag to jump. */
      if( 0 > jump ) {
         jump++;
      }

      /* Gradually slow down right/left movement. */
      if( 0 < factor->x ) {
         mbounce_accel( factor, &g_mbounce_left, max, 1 );
      } else if( 0 > factor->x ) {
         mbounce_accel( factor, &g_mbounce_right, max, 1 );
      }
}

