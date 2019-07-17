#!/usr/bin/env python

import pygame
import pdb

ACCEL_LEFT  = (-1, 0)
ACCEL_RIGHT = ( 1, 0)
ACCEL_DOWN  = ( 0, 1)
ACCEL_UP    = ( 0,-1)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 320

SPRITE_KEY_LEFT = 0
SPRITE_KEY_RIGHT = 1
SPRITE_KEY_LEFT_JUMP = 2
SPRITE_KEY_RIGHT_JUMP = 3

SPRITE_SZ_PX = 32

X = 0
Y = 1

#    1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20
MAP = [
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [-1,-1,-1,-1,-1,-1,-1,126,123,127,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0],
   [123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123,123]
]

class Mobile:

   sprite_frames_max = 30
   jump_decel_inc = 1
   jump_rate = -20
   accel_max = (3, 5)
   sprite_sz = 32

   def __init__( self, coords ):
      self.sprites = [[], [], [], []]
      self.accel_factor = (0, 0)
      self.facing = SPRITE_KEY_LEFT
      self.sprite_frames = 0
      self.sprite_key = SPRITE_KEY_LEFT
      self.jump_factor = 0
      self.sprite_frame_seq = 0
      self.coords = coords

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
      self.jump_factor = self.jump_rate

   def update_accel( self ):
      floor = self.get_floor()

      if self.coords[Y] < floor:
         # If we're above the floor, then fall (accel according to gravity).
         self.accel( ACCEL_DOWN )
      elif self.coords[Y] > floor:
         # Get back up above the floor!
         self.jump_factor = 0
         self.accel_factor = (self.accel_factor[X], 0)
         self.coords = (self.coords[0], floor)
         return

      # Apply gravity drag to jump up.
      if 0 > self.jump_factor:
         self.jump_factor += self.jump_decel_inc

      # Gradually slow down right/left movement.
      if 0 < self.accel_factor[X]:
         self.accel( ACCEL_LEFT )
      elif 0 > self.accel_factor[X]:
         self.accel( ACCEL_RIGHT )

      if self.coords[Y] + self.accel_factor[Y] + self.jump_factor >= \
      floor:
         # Set gravity to whatever it needs to be for us to "land" on the last
         # tick.
         self.jump_factor = 0
         self.accel_factor = \
            (self.accel_factor[X], floor - self.coords[Y])

   def update_coords( self ):
      # Apply acceleration to coordinates.
      self.coords = \
         (self.coords[X] + self.accel_factor[X], \
         self.coords[Y] + self.accel_factor[Y] + self.jump_factor)

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
      return 0 != self.jump_factor or 0 != self.accel_factor[Y]

   def is_moving( self ):
      return 0 != self.accel_factor[X]

   def get_floor( self ):
      # Convert blocks to pixels.
      if self.coords[1] >= 0:
         hunt_block = (self.coords[0] / self.sprite_sz, \
            (self.coords[1] / self.sprite_sz) - 1)
      else:
         hunt_block = (self.coords[0] / self.sprite_sz, 1)
      #assert( hunt_block[1] > 0 and \
      #   hunt_block[1] * self.sprite_sz < SCREEN_HEIGHT )

      # Search for the floor in this column.
      while hunt_block[1] < len( MAP ) - 1 and \
      hunt_block[1] >= 0 and \
      MAP[hunt_block[1]][hunt_block[0]] < 0:
         hunt_block = (hunt_block[0], hunt_block[1] + 1)

      floor = hunt_block[1] * self.sprite_sz
      if floor < SCREEN_HEIGHT:
         return floor
      else:
         return SCREEN_HEIGHT

   def get_sprite( self ):
      return self.sprites[self.facing][self.sprite_frame_seq]

   def set_accel_max( self, accel_max ):
      self.accel_max = accel_max

   def set_sprites( self, sprites, walk_list, dir_in, \
   colorkey=None, sprite_in_sz=0, sprite_margin=0 ):

      # Cut out the sprites.
      for xy in walk_list:
         sprite = pygame.Surface( (sprite_in_sz, sprite_in_sz) )
         sprite.blit( sprites, (0, 0), (
            sprite_margin + (sprite_in_sz * xy[X]),
            sprite_margin + (sprite_in_sz * xy[Y]),
            sprite_in_sz, sprite_in_sz) )
         if sprite_in_sz:
            sprite = pygame.transform.scale( \
               sprite, (self.sprite_sz, self.sprite_sz) )
         if colorkey:
            sprite.set_colorkey( colorkey )
         else:
            # If no color key provided, grab probable BG color.
            trans_color = sprite.get_at( (0, 0) )
            sprite.set_colorkey( trans_color )
         self.sprites[dir_in].append( sprite )

         # Make inverted copies for opposite direction.
         sprite_opposite = pygame.transform.flip( sprite, True, False )
         if SPRITE_KEY_LEFT == dir_in:
            self.sprites[SPRITE_KEY_RIGHT].append( sprite_opposite )
         elif SPRITE_KEY_RIGHT == dir_in:
            self.sprites[SPRITE_KEY_LEFT].append( sprite_opposite )
         elif SPRITE_KEY_LEFT_JUMP == dir_in:
            self.sprites[SPRITE_KEY_RIGHT_JUMP].append( sprite_opposite )
         elif SPRITE_KEY_RIGHT_JUMP == dir_in:
            self.sprites[SPRITE_KEY_LEFT_JUMP].append( sprite_opposite )

def main():

   key_accel = (0, 0)

   pygame.init()
   screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
   running = True
   clock = pygame.time.Clock()

   sprites = pygame.image.load( 'spritesheet.png' )
   sprites_sz = 23
   bgs = pygame.image.load( 'backgrounds.png' )

   bg = pygame.Surface( (231, 63) )
   bg.blit( bgs, (0, 0), (0, 0, 231, 63) )
   bg = pygame.transform.scale( bg, (1173, 320) )

   # Create player.
   player = Mobile( (5, 215) )
   player.set_sprites( \
      sprites, [(28, 0), (29, 0)], SPRITE_KEY_RIGHT,
      sprite_in_sz=23, sprite_margin=1 )
   player.set_sprites( \
      sprites, [(26, 0), (27, 0)], SPRITE_KEY_RIGHT_JUMP,
      sprite_in_sz=23, sprite_margin=1 )
   player.set_accel_max( (6, 5) )

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
      player.update_accel()
      player.update_coords()
      player.animate()
      #screen.fill( (0, 0, 0) )
      screen.blit( bg, (0, 0) )

      screen.blit( player.get_sprite(), \
         (player.coords[X], player.coords[Y] - player.sprite_sz), \
         (0, 0, SPRITE_SZ_PX, SPRITE_SZ_PX) )

      #pygame.draw.circle( screen, (255, 0, 0), dot_coords, radius )
      font = pygame.font.SysFont( 'Sans', 14, False, False )
      stats = font.render( \
         '{}a_x: {}, a_y: {}, f: {}, j: {}, x: {}, y: {}'.format( \
            '-' if key_accel == ACCEL_LEFT else
               '+' if key_accel == ACCEL_RIGHT else '',
            player.accel_factor[X], player.accel_factor[Y],
            player.sprite_frame_seq, player.jump_factor, \
            player.coords[X], player.coords[Y] ), True, (255, 0, 0) )
      screen.blit( stats, [10, 10] )

      for y in range( 0, len( MAP ) ):
         for x in range( 0, len( MAP[y] ) ):
            map_cell = MAP[y][x]
            if 0 > map_cell:
               continue
            sprite_x = 1 + ((map_cell % 30) * sprites_sz)
            sprite_y = 1 + ((map_cell / 30) * sprites_sz)
            screen.blit( sprites, \
               (SPRITE_SZ_PX * x, SPRITE_SZ_PX * y), \
               (sprite_x, sprite_y, sprites_sz, sprites_sz) )

      pygame.display.flip()

      clock.tick( 60 )

if '__main__' == __name__:
   main()

