#!/usr/bin/env python

import pygame

ACCEL_LEFT  = (-1, 0)
ACCEL_RIGHT = ( 1, 0)
ACCEL_DOWN  = ( 0, 1)
ACCEL_UP    = ( 0,-1)

SPRITE_KEY_LEFT = 0
SPRITE_KEY_RIGHT = 1
SPRITE_KEY_LEFT_JUMP = 2
SPRITE_KEY_RIGHT_JUMP = 3

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
   screen_width = 640
   screen_height = 320
   sprite_size = 23
   sprite_margin = 1
   sprite_xy = (28, 0)
   sprite_frames = 0
   sprite_frame_seq = 0
   sprite_key = SPRITE_KEY_LEFT
   sprite_frames_max = 30
   key_accel = (0, 0)
   jump_max = 90
   jump_accel = 0
   jump_rate = -8

   pygame.init()
   screen = pygame.display.set_mode( (screen_width, screen_height) )
   running = True
   clock = pygame.time.Clock()

   sprites = pygame.image.load( 'spritesheet.png' )
   bgs = pygame.image.load( 'backgrounds.png' )

   # Setup player sprites.
   sprite_player_r1 = pygame.Surface( (23, 23) )
   sprite_player_r1.blit( sprites, (0, 0), (
         sprite_margin + (sprite_size * 28), 0,
         sprite_size, sprite_size) )
   sprite_player_r2 = pygame.Surface( (23, 23) )
   sprite_player_r2.blit( sprites, (0, 0), (
         sprite_margin + (sprite_size * 29), 0,
         sprite_size, sprite_size) )
   sprite_player_l1 = pygame.transform.flip( sprite_player_r1, True, False )
   sprite_player_l2 = pygame.transform.flip( sprite_player_r2, True, False ) 

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

      # Advance all sprite animations.
      sprite_frames += 1
      if sprite_frames_max <= sprite_frames:
         if 0 == sprite_frame_seq:
            sprite_frame_seq = 1
         else:
            sprite_frame_seq = 0
         sprite_frames = 0

      if key_accel < 0:
         if 0 == sprite_frame_seq:
            screen.blit( sprite_player_l1, \
               (dot_coords[0], dot_coords[1] - sprite_size), \
               (0, 0, sprite_size, sprite_size) )
         else:
            screen.blit( sprite_player_l2, \
               (dot_coords[0], dot_coords[1] - sprite_size), \
               (0, 0, sprite_size, sprite_size) )
         
      else:
         if 0 == sprite_frame_seq:
            screen.blit( sprite_player_r1, \
               (dot_coords[0], dot_coords[1] - sprite_size), \
               (0, 0, sprite_size, sprite_size) )
         else:
            screen.blit( sprite_player_r2, \
               (dot_coords[0], dot_coords[1] - sprite_size), \
               (0, 0, sprite_size, sprite_size) )

      #pygame.draw.circle( screen, (255, 0, 0), dot_coords, radius )
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

