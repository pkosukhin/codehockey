from MathFunc import *
from copy import copy, deepcopy
from model.Game import Game
from model.World import World
from model.Move import Move
from CommonFunctions import *

def get_puck_owner(world: World):
    h = None
    for h in world.hockeyists:
        if world.puck.owner_hockeyist_id == h.id:
            return h

class WorldConstants:
    def __init__(self, game: (None, Game), world: (None, World), move: (None, Move)):
        self.go_rest_pct = 0.7
        self.main_period_len = 6000
        self.game = game
        self.move = move
        self.world = world
        self.alpha_player = 0.98
        self.alpha_puck = 0.999
        self.tick = world.tick
        self.rink_mid_x = (game.rink_right + game.rink_left)/2
        self.rink_mid_y = (game.rink_bottom + game.rink_top)/2
        self.rink_len = game.rink_right - game.rink_left
        self.rink_width = game.rink_bottom - game.rink_top
        self.puck_radius = world.puck.radius
        self.opponent_player = world.get_opponent_player()
        self.player = world.get_my_player()
        self.net_width = self.player.net_bottom-self.player.net_top
        self.net_top = self.player.net_top
        self.net_bot = self.player.net_bottom
        self.goalie_radius = 30
        self.player_radius = 30
        self.turn_speed = game.hockeyist_turn_angle_factor
        self.sgn_x = copysign(1,self.opponent_player.net_front - self.player.net_front)
        self.puck_radius = world.puck.radius
        self.puck_x = world.puck.x
        self.puck_y = world.puck.y
        self.puck_x_range_me = abs(self.player.net_front - self.puck_x)
        self.puck_x_range_opp = abs(self.opponent_player.net_front - self.puck_x)
        self.puck_state = None
        self.puck_state_next = None
        self.def_x = self.player.net_front + copysign(self.player_radius,self.sgn_x)*2.5
        self.def_y = (self.player.net_top + self.player.net_bottom) / 2
        self.def_x_front = self.def_x + self.rink_len/4 * self.sgn_x
        self.def_y_top = (self.player.net_top + self.player.net_bottom) / 2 - self.rink_width/4
        self.def_y_bot = (self.player.net_top + self.player.net_bottom) / 2 + self.rink_width/4
        self.puck_owner = get_puck_owner(world)
