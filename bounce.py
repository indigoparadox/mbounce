#!/usr/bin/env python

import pygame

def main():

   dot_coords = (5, 5)
   gravity = 1
   accel_rate = 1
   accel_max = 5
   radius = 2
   screen_width = 640
   screen_height = 320
   bounce_count = 0

   pygame.init()
   screen = pygame.display.set_mode( (screen_width, screen_height) )
   running = True
   clock = pygame.time.Clock()

   while running:

      for event in pygame.event.get():
         if pygame.QUIT == event.type:
            running = False

      screen.fill( (0, 0, 0) )

      if dot_coords[1] < screen_height:
         # If we're above the floor, then fall (accel according to gravity).
         if 0 < gravity and accel_max > gravity:
            # Dot is falling.
            gravity += 2 - bounce_count
         elif 0 > gravity and accel_max > gravity:
            # Dot is moving up.
            gravity += 1
         elif 0 == gravity:
            # Dot has stopped.
            gravity = 1
         
      elif dot_coords[1] >= screen_height and gravity > 2:
         # Bounce according to current gravity.
         bounce_count += 1
         gravity = gravity * -1 - bounce_count
      elif dot_coords[1] >= screen_height and \
         gravity <= 1 and \
         gravity >= -1:

         gravity = 0
         bounce_count = 0

      dot_coords = (dot_coords[0], dot_coords[1] + gravity)

      pygame.draw.circle( screen, (255, 0, 0), dot_coords, radius )
      font = pygame.font.SysFont( 'Sans', 14, False, False )
      stats = font.render( 'g: {} x: {} y: {}'.format( \
         gravity, dot_coords[0], dot_coords[1] ), True, (255, 0, 0) )
      screen.blit( stats, [10, 10] )

      pygame.display.flip()

      clock.tick( 60 )


if '__main__' == __name__:
   main()

