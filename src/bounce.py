#!/usr/bin/env python

import pygame

ACCEL_LEFT  = (-1, 0)
ACCEL_RIGHT = ( 1, 0)
ACCEL_DOWN  = ( 0, 1)
ACCEL_UP    = ( 0,-1)

def accel( accel_factor, accel_dir, accel_max, accel_mult=1 ):
   i = 0
   while i < accel_mult:
      # Don't exceed X max.
      if 0 < accel_factor[0] and \
      accel_max[0] < accel_dir[0] + accel_factor[0]:
         accel_dir = (0, accel_dir[1])
      elif 0 > accel_factor[0] and \
      accel_max[0] * -1 > accel_dir[0] + accel_factor[0]:
         accel_dir = (0, accel_dir[1])

      # Don't exceed Y max.
      if 0 < accel_factor[1] and \
      accel_max[1] < accel_dir[1] + accel_factor[1]:
         accel_dir = (accel_dir[0], 0)
      elif 0 > accel_factor[1] and \
      accel_max[1] * -1 > accel_dir[1] + accel_factor[1]:
         accel_dir = (accel_dir[0], 0)

      accel_factor = \
         (accel_factor[0] + accel_dir[0], \
         accel_factor[1] + accel_dir[1])

      i += 1

   return accel_factor

def main():

   dot_coords = (5, 5)
   accel_factor = (0, 0)
   accel_rate = 1
   accel_max = (3, 5)
   radius = 2
   screen_width = 640
   screen_height = 320
   key_accel = (0, 0)
   jump_max = 30
   jump_accel = 0
   jump_rate = -8

   pygame.init()
   screen = pygame.display.set_mode( (screen_width, screen_height) )
   running = True
   clock = pygame.time.Clock()

   while running:

      # Get input state to apply below.
      for event in pygame.event.get():
         if pygame.QUIT == event.type:
            running = False
         elif pygame.KEYDOWN == event.type:
            if pygame.K_ESCAPE == event.key:
               running = False
            elif pygame.K_RIGHT == event.key:
               key_accel = (ACCEL_RIGHT[0], key_accel[1])
            elif pygame.K_LEFT == event.key:
               key_accel = (ACCEL_LEFT[0], key_accel[1])
            elif pygame.K_SPACE == event.key and 0 >= jump_accel:
               jump_accel = jump_rate
         elif pygame.KEYUP == event.type:
            if 0 == jump_accel and \
            (pygame.K_LEFT == event.key or pygame.K_RIGHT == event.key):
               # If we're not jumping, just stop.
               key_accel = (0, 0)

      # Apply input acceleration based on state grabbed above.
      accel_factor = accel( accel_factor, key_accel, accel_max, accel_mult=2 )

      if dot_coords[1] < screen_height:
         # If we're above the floor, then fall (accel according to gravity).
         accel_factor = accel( accel_factor, ACCEL_DOWN, accel_max )

      elif dot_coords[1] + accel_factor[1] + jump_accel >= screen_height:
         # Set gravity to whatever it needs to be for us to "land" on the last
         # tick.
         accel_factor = (accel_factor[0], screen_height - dot_coords[1])

      # Apply gravity drag to jump.
      if 0 > jump_accel:
         jump_accel += 1

      # Gradually slow down right/left movement.
      if 0 < accel_factor[0]:
         accel_factor = accel( accel_factor, ACCEL_LEFT, accel_max )
      elif 0 > accel_factor[0]:
         accel_factor = accel( accel_factor, ACCEL_RIGHT, accel_max )

      # Apply acceleration to coordinates.
      dot_coords = \
         (dot_coords[0] + accel_factor[0], \
         dot_coords[1] + accel_factor[1] + jump_accel)

      # Draw the current state of things.
      screen.fill( (0, 0, 0) )
      pygame.draw.circle( screen, (255, 0, 0), dot_coords, radius )
      font = pygame.font.SysFont( 'Sans', 14, False, False )
      stats = font.render( \
         '{}a_x: {}, a_y: {}, j: {}, x: {}, y: {}'.format( \
            '-' if key_accel == ACCEL_LEFT else
               '+' if key_accel == ACCEL_RIGHT else '',
            accel_factor[0], accel_factor[1], jump_accel, \
            dot_coords[0], dot_coords[1] ), True, (255, 0, 0) )
      screen.blit( stats, [10, 10] )

      pygame.display.flip()

      clock.tick( 60 )


if '__main__' == __name__:
   main()

