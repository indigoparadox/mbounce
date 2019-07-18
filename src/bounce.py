#!/usr/bin/env python

import pygame
import pdb
import random

ACCEL_LEFT  = (-1, 0)
ACCEL_RIGHT = ( 1, 0)
ACCEL_DOWN  = ( 0, 1)
ACCEL_UP    = ( 0,-1)

SPRITE_KEY_LEFT = 0
SPRITE_KEY_RIGHT = 1
SPRITE_KEY_LEFT_JUMP = 2
SPRITE_KEY_RIGHT_JUMP = 3

SCREEN_MULT = 2
SPRITESHEET_MARGIN_PX = 1
SPRITE_SZ_PX = 21
SPRITE_BORDER_PX = 1
SPRITE_OUTER_SZ_PX = (2 * SPRITE_BORDER_PX) + SPRITE_SZ_PX

SCREEN_WIDTH = 16 * SPRITE_SZ_PX
SCREEN_HEIGHT = 10 * SPRITE_SZ_PX

BLOCK_EMPTY = -1
BLOCK_GRASS = 123
BLOCK_GRASS_UP = 126
BLOCK_GRASS_UP_FILL = 156
BLOCK_GRASS_DOWN = 127
BLOCK_GRASS_DOWN_FILL = 157
BLOCK_DIRT_FILL = 152

X = 0
Y = 1

BEHAVIOR_NEUTRAL = 0
BEHAVIOR_RANDOM = 1

#    1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20
MAP = [
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
   [ -1, -1, -1, -1, -1, -1, -1,126,123,127, -1, -1, -1, -1, -1, -1, -1, -1],
   [123,123,123,123,123,123,123,156,152,157,123,123,123,123,123,123,123,123]
]

class Mobile:

   sprite_frames_max = 30
   jump_decel_inc = 1
   jump_rate = -20
   accel_max = (3, 5)
   behave_timer_max = 10

   def __init__( self, coords ):
      self.sprites = [[], [], [], []]
      self.accel_factor = (0, 0)
      self.facing = SPRITE_KEY_LEFT
      self.sprite_frames = 0
      self.sprite_key = SPRITE_KEY_LEFT
      self.jump_factor = 0
      self.sprite_frame_seq = 0
      self.coords = coords
      self.behavior = BEHAVIOR_NEUTRAL
      self.behave_timer = 0

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

   def do_behavior( self ):
      self.behave_timer += 1
      if self.behave_timer < self.behave_timer_max:
         return

      self.behave_timer = 0

      # Execute this mobile's AI, if applicable.
      if BEHAVIOR_RANDOM == self.behavior:
         behave = random.randint( 0, 1000 )
         if behave < 450:
            self.accel( ACCEL_RIGHT, accel_mult=8 )
         elif behave < 900:
            self.accel( ACCEL_LEFT, accel_mult=8 )
         elif self.jump_factor == 0 and self.accel_factor[Y] == 0:
            self.jump_factor = -20

   def update_accel( self ):
      if self.coords[Y] / SPRITE_SZ_PX >= len( MAP[0] ) - 1:
         self.accel_factor[X] = -2

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
         hunt_block = (self.coords[0] / SPRITE_SZ_PX, \
            (self.coords[1] / SPRITE_SZ_PX) - 1)
      else:
         hunt_block = (self.coords[0] / SPRITE_SZ_PX, 1)

      # Search for the floor in this column.
      while hunt_block[1] < len( MAP ) - 1 and \
      hunt_block[1] >= 0 and \
      MAP[hunt_block[1]][hunt_block[0]] < 0:
         hunt_block = (hunt_block[0], hunt_block[1] + 1)

      # Don't fall through the screen bottom.
      floor = hunt_block[1] * SPRITE_SZ_PX
      if floor < (SCREEN_MULT * SCREEN_HEIGHT):
         return floor
      else:
         return (SCREEN_MULT * SCREEN_HEIGHT)

   def get_sprite( self ):
      return self.sprites[self.facing][self.sprite_frame_seq]

   def set_accel_max( self, accel_max ):
      self.accel_max = accel_max

   def set_sprites( self, sprites, walk_list, dir_in, \
   colorkey=None, sprite_margin=0 ):

      # Cut out the sprites.
      for xy in walk_list:
         sprite = pygame.Surface( \
            (SCREEN_MULT * SPRITE_SZ_PX, SCREEN_MULT * SPRITE_SZ_PX) )
         sprite.blit( sprites, (0, 0), (
            SCREEN_MULT * (SPRITESHEET_MARGIN_PX + SPRITE_BORDER_PX + \
               (SPRITE_OUTER_SZ_PX * xy[X])),
            SCREEN_MULT * (SPRITESHEET_MARGIN_PX + SPRITE_BORDER_PX + \
               (SPRITE_OUTER_SZ_PX * xy[Y])),
            SCREEN_MULT * SPRITE_SZ_PX, SCREEN_MULT * SPRITE_SZ_PX) )
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

class Level:

   def __init__( self, level_map ):
      
      self.vwindow = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
      self.boundaries = (0, 0, \
         len( level_map[0] ) * SPRITE_SZ_PX, \
         len( level_map ) * SPRITE_SZ_PX)

      self.level_map = level_map

   def extend_x( self ):
      
      for y in range( 0, len( self.level_map ) ):
         # Figure out useful coords for back and to the left:
         #
         # ...xo
         # ...y.
         last_x = len( self.level_map[y] ) - 1
         x = len( self.level_map[y] )
         if y + 1 < len( self.level_map ) - 1:
            next_y = y + 1
         else:
            next_y = -1
         last_y = y - 1

         if 0 < last_y and \
         BLOCK_GRASS_UP == self.level_map[last_y][x]:
            self.level_map[y].append( BLOCK_GRASS_UP_FILL )
            continue
         elif 0 < last_y and \
         BLOCK_GRASS_DOWN == self.level_map[last_y][x]:
            self.level_map[y].append( BLOCK_GRASS_DOWN_FILL )
            continue

         if -1 == self.level_map[y][last_x]:
            # Last block in this row was empty.
            # Level out or keep sloping up.

            if BLOCK_GRASS == self.level_map[next_y][last_x]:
               # Last block in next row has grass, so flip a coin for a slope.
               if random.randint( 1, 2 ) > 1:
                  self.level_map[y].append( BLOCK_GRASS_UP )
               else:
                  self.level_map[y].append( BLOCK_EMPTY )
            elif 0 < last_y and \
            BLOCK_GRASS_DOWN == self.level_map[last_y][last_x]:
               # Last block in the last row was a down slope.
               # Flop a coin to see if it keeps going down or levels out.
               if random.randint( 1, 2 ) > 1:
                  self.level_map[y].append( BLOCK_GRASS_DOWN )
               else:
                  self.level_map[y].append( BLOCK_GRASS )
            else:
               self.level_map[y].append( BLOCK_EMPTY )

         elif BLOCK_GRASS_DOWN_FILL == self.level_map[y][last_x]:
            # Last block in this row was a down fill.
            # Level out or keep sloping down.

            if random.randint( 1, 2 ) > 1 and 0 < next_y:
               self.level_map[y].append( BLOCK_GRASS_DOWN )
            else:
               self.level_map[y].append( BLOCK_GRASS )


         elif BLOCK_DIRT_FILL == self.level_map[y][last_x] or \
         BLOCK_GRASS_UP_FILL == self.level_map[y][last_x]:
            #if BLOCK_GRASS_UP == self.level_map[last_y][last_x]:
            #   self.level_map[y].append( BLOCK_GRASS_UP_FILL )
            #elif BLOCK_GRASS_DOWN == self.level_map[last_y][last_x]:
            #   self.level_map[y].append( BLOCK_GRASS_DOWN_FILL )
            #else:
            self.level_map[y].append( BLOCK_DIRT_FILL )

         elif BLOCK_GRASS == self.level_map[y][last_x] or \
         BLOCK_GRASS_UP == self.level_map[y][last_x]:
            # Last block in this row was grass level or up.
            if BLOCK_EMPTY != self.level_map[last_y][last_x]:
               # Put dirt under whatever's on top of us for now.
               self.level_map[y].append( BLOCK_DIRT_FILL )
            elif random.randint( 1, 2 ) > 1 and 0 < next_y:
               self.level_map[y].append( BLOCK_GRASS_DOWN )
            else:
               self.level_map[y].append( BLOCK_GRASS )

         else:
            self.level_map[y].append( BLOCK_EMPTY )

         #   if 0 < last_y and  self.level_map[last_y][last_x]:
         #   self.level_map[y].append( -1 )
         #   if 123 self.level_map[y][last_x]:
         #else:
         #   self.level_map[y].append( 123 )

   def get_draw_x( self, x ):
      return x - self.vwindow[X]

   def get_width( self ):
      return len( self.level_map[0] ) * SPRITE_SZ_PX

   def get_block_sprite_x( self, block_id ):
      return (SPRITESHEET_MARGIN_PX + \
         SPRITE_BORDER_PX + ((block_id % 30) * SPRITE_OUTER_SZ_PX))

   def get_block_sprite_y( self, block_id ):
      return (SPRITESHEET_MARGIN_PX + \
         SPRITE_BORDER_PX + ((block_id / 30) * SPRITE_OUTER_SZ_PX))

   def set_vwindow_center( self, x ):
      self.vwindow = (x - (SCREEN_WIDTH / 2), SCREEN_HEIGHT / 2, \
         SCREEN_WIDTH, SCREEN_HEIGHT)

def main():

   key_accel = (0, 0)
   left_edge = 0

   pygame.init()
   screen = pygame.display.set_mode( \
      (SCREEN_MULT * SCREEN_WIDTH, SCREEN_MULT * SCREEN_HEIGHT) )
   running = True
   clock = pygame.time.Clock()

   level = Level( MAP )

   # Load the spritesheet.
   sprites = pygame.image.load( 'spritesheet.png' )
   if 1 < SCREEN_MULT:
      sprites = pygame.transform.scale( \
         sprites, \
         ((sprites.get_width() * SCREEN_MULT), \
         (sprites.get_height() * SCREEN_MULT)) )
   trans_color = sprites.get_at( (0, 0) )
   sprites.set_colorkey( trans_color )

   # Load the background.
   bgs = pygame.image.load( 'backgrounds.png' )
   bg = pygame.Surface( (231, 63) )
   bg.blit( bgs, (0, 0), (0, 0, 231, 63) )
   bg = pygame.transform.scale( bg, \
      (SCREEN_MULT * (SCREEN_HEIGHT * bg.get_width() / bg.get_height()),
      SCREEN_MULT * SCREEN_HEIGHT) )

   # Create player.
   player = Mobile( (5, 215) )

   # Setup player sprites.
   player.set_sprites( \
      sprites, [(28, 0), (29, 0)], SPRITE_KEY_RIGHT, sprite_margin=1 )
   player.set_sprites( \
      sprites, [(26, 0), (27, 0)], SPRITE_KEY_RIGHT_JUMP, sprite_margin=1 )
   player.set_accel_max( (6, 5) )

   # Create mobiles.
   mobiles = []
   mobiles.append( player )

   mob = Mobile( (random.randint( 30, 160 ), 200) )
   mob.set_sprites( \
      sprites, [(28, 4), (29, 4)], SPRITE_KEY_RIGHT, sprite_margin=1 )
   mob.set_sprites( \
      sprites, [(26, 4), (27, 4)], SPRITE_KEY_RIGHT_JUMP, sprite_margin=1 )
   mob.set_accel_max( (6, 4) )
   mob.behavior = BEHAVIOR_RANDOM
   mobiles.append( mob )

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
      player.accel( key_accel, accel_mult=2 )

      level.set_vwindow_center( player.coords[X] )
      while level.get_width() < level.vwindow[X] + SCREEN_WIDTH:
         print level.get_width()
         print level.vwindow
         level.extend_x()

      screen.blit( bg, (SCREEN_MULT * level.get_draw_x( 0 ), 0) )

      # Draw map foreground objects.
      for y in range( 0, len( level.level_map ) ):
         for x in range( 0, len( level.level_map[y] ) ):
            map_cell = MAP[y][x]
            if 0 > map_cell:
               continue

            screen_draw_x = level.get_draw_x( SPRITE_SZ_PX * x )
            screen_draw_y = SPRITE_SZ_PX * y

            screen.blit( sprites, \
               (SCREEN_MULT * screen_draw_x,
               SCREEN_MULT * screen_draw_y), \
               (SCREEN_MULT * level.get_block_sprite_x( map_cell ), \
               SCREEN_MULT * level.get_block_sprite_y( map_cell ), \
               SCREEN_MULT * SPRITE_SZ_PX, \
               SCREEN_MULT * SPRITE_SZ_PX) )

      # Update and draw the mobiles.
      for mob in mobiles:
         mob.do_behavior()
         mob.update_accel()
         mob.update_coords()
         mob.animate()

         # Skip drawing things off-screen.
         mob_draw_x = level.get_draw_x( mob.coords[X] )
         if 0 > mob_draw_x or SCREEN_WIDTH <= mob_draw_x:
            continue

         screen.blit( mob.get_sprite(), \
            (SCREEN_MULT * mob_draw_x, \
            SCREEN_MULT * (mob.coords[Y] - SPRITE_SZ_PX)), \
            (0, 0, \
            SCREEN_MULT * SPRITE_SZ_PX, \
            SCREEN_MULT * SPRITE_SZ_PX) )

      # Show some useful system info on-screen.
      font = pygame.font.SysFont( 'Sans', 14, False, False )
      stats = font.render( \
         '{}a_x: {}, a_y: {}, f: {}, j: {}, x: {}, y: {}'.format( \
            '-' if key_accel == ACCEL_LEFT else
               '+' if key_accel == ACCEL_RIGHT else '',
            player.accel_factor[X], player.accel_factor[Y],
            player.sprite_frame_seq, player.jump_factor, \
            player.coords[X], player.coords[Y] ), True, (255, 0, 0) )
      screen.blit( stats, [10, 10] )

      pygame.display.flip()

      clock.tick( 60 )

if '__main__' == __name__:
   main()

