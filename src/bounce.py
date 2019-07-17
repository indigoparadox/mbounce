#!/usr/bin/env python

import pygame
import pdb

ACCEL_LEFT  = (-1, 0)
ACCEL_RIGHT = ( 1, 0)
ACCEL_DOWN  = ( 0, 1)
ACCEL_UP    = ( 0,-1)

SPRITE_SIZE_PX = 23

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 320

SPRITE_KEY_LEFT = 0
SPRITE_KEY_RIGHT = 1
SPRITE_KEY_LEFT_JUMP = 2
SPRITE_KEY_RIGHT_JUMP = 3

X = 0
Y = 1

class Mobile:

   sprite_frame_seq = 0
   sprite_key = SPRITE_KEY_LEFT
   sprite_frames_max = 30
   jump_accel = 0
   jump_accel_minor = 0
   jump_accel_minor_max = 0
   gravity_accel_minor = 0
   gravity_accel_minor_max = 10
   jump_rate = -20
   coords = (5, 315)
   accel_max = (3, 5)
   accel_factor = (0, 0)
   sprite_frames = 0
   facing = SPRITE_KEY_LEFT

   def __init__( self ):
      self.sprites = [[], [], [], []]

   def accel( self, accel_dir, accel_mult=1 ) :
      i = 0
      while i < accel_mult:
         # Don't exceed X max.
         if 0 < self.accel_factor[X] and \
         self.accel_max[X] < accel_dir[X] + self.accel_factor[X]:
            accel_dir = (0, accel_dir[Y])
         elif 0 > self.accel_factor[X] and \
         self.accel_max[X] * -1 > accel_dir[X] + self.accel_factor[X]:
            accel_dir = (0, accel_dir[Y])

         # Don't exceed Y max.
         if 0 < self.accel_factor[Y] and \
         self.accel_max[Y] < accel_dir[Y] + self.accel_factor[Y]:
            accel_dir = (accel_dir[X], 0)
         elif 0 > self.accel_factor[Y] and \
         self.accel_max[Y] * -1 > accel_dir[Y] + self.accel_factor[Y]:
            accel_dir = (accel_dir[X], 0)

         self.accel_factor = \
            (self.accel_factor[X] + accel_dir[X], \
            self.accel_factor[Y] + accel_dir[Y])

         i += 1

   def jump( self ):
      self.jump_accel = self.jump_rate

   def update( self ):
      if self.coords[Y] < self.get_floor():
         # If we're above the floor, then fall (accel according to gravity).
         self.gravity_accel_minor += 1
         if self.gravity_accel_minor_max <= self.gravity_accel_minor:
            self.accel( ACCEL_DOWN )
            self.gravity_accel_minor = 0

      elif self.coords[Y] + self.accel_factor[Y] + self.jump_accel >= \
      self.get_floor():
         # Set gravity to whatever it needs to be for us to "land" on the last
         # tick.
         self.accel_factor = \
            (self.accel_factor[X], self.get_floor() - self.coords[Y])

      # Apply gravity drag to jump up.
      if 0 > self.jump_accel:
         self.jump_accel_minor += 1
         if self.jump_accel_minor_max <= self.jump_accel_minor:
            self.jump_accel += 1
            self.jump_accel_minor = 0

      # Gradually slow down right/left movement.
      if 0 < self.accel_factor[X]:
         self.accel( ACCEL_LEFT )
      elif 0 > self.accel_factor[X]:
         self.accel( ACCEL_RIGHT )

      # Apply acceleration to coordinates.
      self.coords = \
         (self.coords[X] + self.accel_factor[X], \
         self.coords[Y] + self.accel_factor[Y] + self.jump_accel)

   def animate( self ):
      if not self.is_moving():
         return

      if 0 < self.accel_factor[X]:
         if 0 < self.coords[Y] != self.get_floor():
            self.facing = SPRITE_KEY_RIGHT_JUMP
         else:
            self.facing = SPRITE_KEY_RIGHT
      if 0 > self.accel_factor[X]:
         if 0 < self.coords[Y] != self.get_floor():
            self.facing = SPRITE_KEY_LEFT_JUMP
         else:
            self.facing = SPRITE_KEY_LEFT

      # Advance all sprite animations.
      self.sprite_frames += 1
      if self.sprite_frames_max <= self.sprite_frames:
         self.sprite_frame_seq += 1
         if len( self.sprites[self.facing] ) <= self.sprite_frame_seq:
            self.sprite_frame_seq = 0
         self.sprite_frames = 0

   def is_jumping_or_falling( self ):
      return 0 != self.jump_accel or 0 != self.accel_factor[Y]

   def is_moving( self ):
      return 0 != self.accel_factor[X]

   def get_floor( self ):
      return SCREEN_HEIGHT

   def get_sprite( self ):
      return self.sprites[self.facing][self.sprite_frame_seq]

   def set_sprites( self, sprites, walk_list, dir_in, sprite_margin=0 ):

      # Cut out the sprites.
      for xy in walk_list:
         sprite = pygame.Surface( (SPRITE_SIZE_PX, SPRITE_SIZE_PX) )
         sprite.blit( sprites, (0, 0), (
            sprite_margin + (SPRITE_SIZE_PX * xy[X]),
            sprite_margin + (SPRITE_SIZE_PX * xy[Y]),
            SPRITE_SIZE_PX, SPRITE_SIZE_PX) )
         self.sprites[dir_in].append( sprite )

         # Make inverted copies for opposite direction.
         if SPRITE_KEY_LEFT == dir_in:
            self.sprites[SPRITE_KEY_RIGHT].append( \
               pygame.transform.flip( sprite, True, False ) )
         elif SPRITE_KEY_RIGHT == dir_in:
            self.sprites[SPRITE_KEY_LEFT].append( \
               pygame.transform.flip( sprite, True, False ) )
         elif SPRITE_KEY_LEFT_JUMP == dir_in:
            self.sprites[SPRITE_KEY_RIGHT_JUMP].append( \
               pygame.transform.flip( sprite, True, False ) )
         elif SPRITE_KEY_RIGHT_JUMP == dir_in:
            self.sprites[SPRITE_KEY_LEFT_JUMP].append( \
               pygame.transform.flip( sprite, True, False ) )

def main():

   key_accel = (0, 0)

   pygame.init()
   screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
   running = True
   clock = pygame.time.Clock()

   sprites = pygame.image.load( 'spritesheet.png' )
   bgs = pygame.image.load( 'backgrounds.png' )

   player = Mobile()
   player.set_sprites( \
      sprites, [(28, 0), (29, 0)], SPRITE_KEY_RIGHT, sprite_margin=1 )
   player.set_sprites( \
      sprites, [(26, 0), (27, 0)], SPRITE_KEY_RIGHT_JUMP, sprite_margin=1 )

   # Setup player sprites.

   while running:

      # Get input state to apply below.
      for event in pygame.event.get():
         if pygame.QUIT == event.type:
            running = False
         elif pygame.KEYDOWN == event.type:
            if pygame.K_ESCAPE == event.key:
               running = False
            elif pygame.K_RIGHT == event.key:
               key_accel = (ACCEL_RIGHT[X], key_accel[Y])
            elif pygame.K_LEFT == event.key:
               key_accel = (ACCEL_LEFT[X], key_accel[Y])
            elif pygame.K_SPACE == event.key and \
            not player.is_jumping_or_falling():
               player.jump()
         elif pygame.KEYUP == event.type:
            if not player.is_jumping_or_falling() and \
            (pygame.K_LEFT == event.key or pygame.K_RIGHT == event.key):
               # If we're not jumping, just stop.
               key_accel = (0, 0)

      # Apply input acceleration based on state grabbed above.
      #if 0 >= player.accel_factor[X]:
      #   pdb.set_trace()
      player.accel( key_accel, accel_mult=2 )

      # Draw the current state of things.
      player.update()
      player.animate()
      screen.fill( (0, 0, 0) )

      screen.blit( player.get_sprite(), \
         (player.coords[X], player.coords[Y] - SPRITE_SIZE_PX), \
         (0, 0, SPRITE_SIZE_PX, SPRITE_SIZE_PX) )

      #pygame.draw.circle( screen, (255, 0, 0), dot_coords, radius )
      font = pygame.font.SysFont( 'Sans', 14, False, False )
      stats = font.render( \
         '{}a_x: {}, a_y: {}, f: {}, j: {}, x: {}, y: {}'.format( \
            '-' if key_accel == ACCEL_LEFT else
               '+' if key_accel == ACCEL_RIGHT else '',
            player.accel_factor[X], player.accel_factor[Y],
            player.sprite_frame_seq, player.jump_accel, \
            player.coords[X], player.coords[Y] ), True, (255, 0, 0) )
      screen.blit( stats, [10, 10] )

      pygame.display.flip()

      clock.tick( 60 )


if '__main__' == __name__:
   main()

