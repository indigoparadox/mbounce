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

#     1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18
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
      self.sprite_sz_px = 0

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

   def update_accel( self, level ):
      if self.coords[Y] / self.sprite_sz_px >= len( MAP[0] ) - 1:
         self.accel_factor[X] = -2

      floor = self.get_floor( level )

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

   def update_coords( self, level ):
      x = self.coords[X] + self.accel_factor[X]
      y = self.coords[Y] + self.accel_factor[Y] + self.jump_factor

      # Don't overflow off the far left or right of the level.
      if x < 0:
         x = 0
      elif x + self.sprite_sz_px > level.get_max_width():
         x = level.get_max_width() - self.sprite_sz_px

      # Don't overflow off the top or bottom of the level.
      if y < self.sprite_sz_px:
         y = self.sprite_sz_px
      elif y > level.get_height():
         y = level.get_height()

      # Apply acceleration to coordinates.
      self.coords = (x, y)

   def animate( self, level ):
      if not self.is_moving():
         return

      if 0 < self.accel_factor[X]:
         if 0 < self.coords[Y] != self.get_floor( level ):
            self.facing = SPRITE_KEY_RIGHT_JUMP
         else:
            self.facing = SPRITE_KEY_RIGHT
      if 0 > self.accel_factor[X]:
         if 0 < self.coords[Y] != self.get_floor( level ):
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

   def is_on_screen( self, screen ):
      if self.sprite_sz_px * -1 > self.coords[X] or \
      screen.vwindow[X] + screen.size[X] + self.sprite_sz_px <= self.coords[X]:
         return False
      return True

   def is_jumping_or_falling( self ):
      return 0 != self.jump_factor or 0 != self.accel_factor[Y]

   def is_moving( self ):
      return 0 != self.accel_factor[X]

   def get_floor( self, level ):
      # Convert pixels to blocks.
      if self.coords[Y] >= 0:
         hunt_block = (self.coords[X] / self.sprite_sz_px, \
            (self.coords[Y] / self.sprite_sz_px) - 1)
      else:
         hunt_block = (self.coords[X] / self.sprite_sz_px, 1)

      # Search for the floor in this column.
      while hunt_block[Y] < (level.get_height() / level.block_sz_px) - 1 and \
      hunt_block[Y] >= 0 and \
      level.is_empty_block( level.get_block( hunt_block[X], hunt_block[Y] ) ):
         hunt_block = (hunt_block[X], hunt_block[Y] + 1)

      # Don't fall through the screen bottom.
      floor = hunt_block[Y] * self.sprite_sz_px
      if floor < level.get_height():
         return floor
      else:
         return level.get_height()

   def get_sprite( self ):
      return self.sprites[self.facing][self.sprite_frame_seq]

   def set_accel_max( self, accel_max ):
      self.accel_max = accel_max

   def set_sprites( self, sprites, walk_list, dir_in, \
   colorkey=None, sprite_margin=0, sprite_sz_px=SPRITE_SZ_PX ):

      self.sprite_sz_px = sprite_sz_px

      # Cut out the sprites.
      for xy in walk_list:
         sprite = pygame.Surface( \
            (SCREEN_MULT * self.sprite_sz_px, SCREEN_MULT * self.sprite_sz_px) )
         sprite.blit( sprites, (0, 0), (
            SCREEN_MULT * (SPRITESHEET_MARGIN_PX + SPRITE_BORDER_PX + \
               (SPRITE_OUTER_SZ_PX * xy[X])),
            SCREEN_MULT * (SPRITESHEET_MARGIN_PX + SPRITE_BORDER_PX + \
               (SPRITE_OUTER_SZ_PX * xy[Y])),
            SCREEN_MULT * self.sprite_sz_px, SCREEN_MULT * self.sprite_sz_px) )
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

   def __init__( self, level_map, max_blocks_x, block_sz_px=SPRITE_SZ_PX ):

      self.block_sz_px = block_sz_px
      
      self.boundaries = (0, 0, \
         len( level_map[0] ) * self.block_sz_px, \
         len( level_map ) * self.block_sz_px)

      self.level_map = level_map
      self.max_blocks_x = max_blocks_x

   #  @param block_ceiling Grass comes at most this many blocks down from top.
   def extend_x( self, grass_odds=50, block_ceiling=5, plateau_odds_max=4 ):
      
      for y in range( 0, len( self.level_map ) ):
         # Figure out useful coords for back and to the left:
         #
         # ...xo
         # ...y.
         last_x = len( self.level_map[y] ) - 1
         x = len( self.level_map[y] )
         if y < len( self.level_map ) - 1:
            next_y = y + 1
         else:
            next_y = -1
         last_y = y - 1
   
         # Corner cases to ensure neat under-slope fills.
         if 0 < last_y and \
         BLOCK_GRASS_UP == self.level_map[last_y][x]:
            self.level_map[y].append( BLOCK_GRASS_UP_FILL )
            continue
         elif 0 < last_y and \
         BLOCK_GRASS_DOWN == self.level_map[last_y][x]:
            self.level_map[y].append( BLOCK_GRASS_DOWN_FILL )
            continue

         elif self.is_empty_block( self.level_map[y][last_x] ):
            # Last block in this row was empty.
            # Level out or keep sloping up.

            if BLOCK_GRASS == self.level_map[next_y][last_x]:
               # Last block in next row has grass, so flip a coin for a slope.
               if random.randint( 0, plateau_odds_max ) < 1 and \
               y > block_ceiling:
                  self.level_map[y].append( BLOCK_GRASS_UP )
               else:
                  self.level_map[y].append( BLOCK_EMPTY )
            elif 0 <= last_y and \
            BLOCK_GRASS_DOWN == self.level_map[last_y][last_x]:
               # Last block in the last row was a down slope.
               # Flop a coin to see if it keeps going down or levels out.
               if random.randint( 0, plateau_odds_max ) < 1:
                  self.level_map[y].append( BLOCK_GRASS_DOWN )
               else:
                  self.level_map[y].append( BLOCK_GRASS )
            else:
               self.level_map[y].append( BLOCK_EMPTY )

         elif BLOCK_GRASS_DOWN_FILL == self.level_map[y][last_x]:
            # Last block in this row was a down fill.
            # Level out or keep sloping down.

            if random.randint( 0, plateau_odds_max ) < 1 and 0 < next_y:
               self.level_map[y].append( BLOCK_GRASS_DOWN )
            else:
               self.level_map[y].append( BLOCK_GRASS )

         elif BLOCK_DIRT_FILL == self.level_map[y][last_x] or \
         BLOCK_GRASS_UP_FILL == self.level_map[y][last_x]:
            self.level_map[y].append( BLOCK_DIRT_FILL )

         elif BLOCK_GRASS == self.level_map[y][last_x]:
            # Last block in this row was grass level.
            if not self.is_empty_block( self.level_map[last_y][last_x] ):
               # Put dirt under whatever's on top of us for now.
               self.level_map[y].append( BLOCK_DIRT_FILL )
            elif random.randint( 0, plateau_odds_max ) < 1 and 0 < next_y:
               self.level_map[y].append( BLOCK_GRASS_DOWN )
            else:
               self.level_map[y].append( BLOCK_GRASS )
               if 10 > random.randint( 0, grass_odds ):
                  self.level_map[last_y][x] = 46

         elif BLOCK_GRASS_UP == self.level_map[y][last_x]:
            # Last block in this row was grass up.
            if not self.is_empty_block( self.level_map[last_y][last_x] ):
               # Put dirt under whatever's on top of us for now.
               self.level_map[y].append( BLOCK_DIRT_FILL )
            else:
               self.level_map[y].append( BLOCK_GRASS )

         else:
            self.level_map[y].append( BLOCK_EMPTY )

   def is_empty_block( self, block_id ):
      if BLOCK_EMPTY == block_id or 46 == block_id:
         return True
      return False

   def get_block( self, x, y ):
      if 0 > x or len( self.level_map[0] ) <= x or \
      0 > y or len( self.level_map ) <= y:
         return -1
      return self.level_map[y][x]

   def get_static_width( self ):
      return len( self.level_map[0] ) * self.block_sz_px

   def get_max_width( self ):
      return self.max_blocks_x * self.block_sz_px

   def get_height( self ):
      return SCREEN_HEIGHT

   def get_block_sprite_x( self, block_id ):
      return (SPRITESHEET_MARGIN_PX + \
         SPRITE_BORDER_PX + ((block_id % 30) * SPRITE_OUTER_SZ_PX))

   def get_block_sprite_y( self, block_id ):
      return (SPRITESHEET_MARGIN_PX + \
         SPRITE_BORDER_PX + ((block_id / 30) * SPRITE_OUTER_SZ_PX))

class Screen:

   def __init__( self, size, multiplier ):
      self.screen = pygame.display.set_mode( \
         (size[X] * multiplier, size[Y] * multiplier) )

      self.vwindow = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
      self.multiplier = multiplier
      self.size = size

   def blit( self, img, dest=(0, 0), dimensions=None, offscreen=0 ):

      # Skip drawing off-screen stuff.
      if offscreen * -1 > dest[X] or \
      self.size[X] + offscreen <= dest[X]:
         return

      if dimensions:
         self.screen.blit( \
            img, (dest[X] * self.multiplier, dest[Y] * self.multiplier), \
            (dimensions[X] * self.multiplier, \
            dimensions[Y] * self.multiplier, \
            dimensions[2] * self.multiplier, \
            dimensions[3] * self.multiplier) )
      else:
         self.screen.blit( \
            img, (dest[X] * self.multiplier, dest[Y] * self.multiplier) )

   def get_draw_x( self, x ):
      return x - self.vwindow[X]

   def set_vwindow_center( self, x, level ):
      left_x = x - (SCREEN_HEIGHT / 2)

      # Don't overflow off the far left or right of the level.
      if 0 >= left_x:
         left_x = 0
      if left_x + SCREEN_WIDTH > level.get_max_width():
         left_x = level.get_max_width() - SCREEN_WIDTH

      self.vwindow = (left_x, SCREEN_HEIGHT / 2, \
         SCREEN_WIDTH, SCREEN_HEIGHT)

def main():

   key_accel = (0, 0)
   left_edge = 0

   pygame.init()
   screen = Screen( (SCREEN_WIDTH, SCREEN_HEIGHT), 2 )
   running = True
   clock = pygame.time.Clock()

   level = Level( MAP, 500 )

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

      screen.set_vwindow_center( player.coords[X], level )
      while level.get_static_width() < screen.vwindow[X] + SCREEN_WIDTH and \
      level.get_static_width() < level.get_max_width():
         level.extend_x()

      bg_offset_x = -1 * \
         (player.coords[X] * SCREEN_WIDTH / level.get_max_width())
      screen.blit( bg, (bg_offset_x, 0), offscreen=bg.get_width() )

      # Draw map foreground objects.
      for y in range( 0, len( level.level_map ) ):
         for x in range( 0, len( level.level_map[y] ) ):
            map_cell = MAP[y][x]
            if 0 > map_cell:
               continue

            screen_draw_x = screen.get_draw_x( level.block_sz_px * x )
            screen_draw_y = level.block_sz_px * y

            screen.blit( sprites, \
               (screen_draw_x, screen_draw_y), \
               (level.get_block_sprite_x( map_cell ), \
               level.get_block_sprite_y( map_cell ), \
               level.block_sz_px, \
               level.block_sz_px),
               offscreen = level.block_sz_px )

      # Update and draw the mobiles.
      for mob in mobiles:
         if not mob.is_on_screen( screen ):
            continue

         mob.do_behavior()
         mob.update_accel( level )
         mob.update_coords( level )
         mob.animate( level )

         mob_draw_x = screen.get_draw_x( mob.coords[X] )
         screen.blit( mob.get_sprite(), \
            (mob_draw_x, (mob.coords[Y] - mob.sprite_sz_px)), \
            (0, 0, mob.sprite_sz_px, mob.sprite_sz_px) )

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

