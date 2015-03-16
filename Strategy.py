import math
from model.ActionType import ActionType
from model.HockeyistType import HockeyistType
from model.Hockeyist import Hockeyist
from Constants import *
from PuckManPlay import *
from DefPlay import *
from MathFunc import *
from PlayerStates import *
from Strategy_2x2 import *
from Strategy_3x3 import *
from Strategy_6x6 import *
import traceback
import sys

def get_v(list,n=1):
    if n > len(list)+1:
        return None
    else:
        return list[len(list)-n]


class PlayerStrategy:
    def __init__(self, state, target, action, index):
        self.state = state
        self.target = target
        self.target_unit = None
        self.action = action
        self.staged = False
        self.me = None
        self.angle = None
        self.pass_power = None
        self.target_state = None
        self.teammate_index = index

class TeamStrategy:
    def __init__(self, team_size, const: WorldConstants):
        self.staged_tick = -1
        self.enemy_strategy = EnemyStrategy.COMMON
        self.team_size = team_size
        if team_size == 2:
            self.players = []
            self.players.append(PlayerStrategy(PlayerState.FREE_TAKE_PUCK,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.TAKE_PUCK,0))
            self.players.append(PlayerStrategy(PlayerState.DEFMAN_GODEF,
                                           PlayerTarget(const.def_x, const.def_y),
                                           ActionType.TAKE_PUCK,1))
        elif team_size == 3:
            self.players = []
            self.players.append(PlayerStrategy(PlayerState.FREE_TAKE_PUCK,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.TAKE_PUCK,0))
            self.players.append(PlayerStrategy(PlayerState.FREE_TAKE_PUCK,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.TAKE_PUCK,1))
            self.players.append(PlayerStrategy(PlayerState.DEFMAN_GODEF_PERMANENT,
                                           PlayerTarget(const.def_x, const.def_y),
                                           ActionType.TAKE_PUCK,2))

        else:
            self.players = []
            self.players.append(PlayerStrategy(PlayerState.FREE_TAKE_PUCK,
                                           PlayerTarget(const.def_x, const.def_y),
                                           ActionType.TAKE_PUCK,0))
            self.players.append(PlayerStrategy(PlayerState.FREE_TAKE_PUCK,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.TAKE_PUCK,1))
            self.players.append(PlayerStrategy(PlayerState.DEFMAN_GODEF_PERMANENT,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.TAKE_PUCK,2))
            self.players.append(PlayerStrategy(PlayerState.REST,
                                           PlayerTarget(const.def_x, const.def_y),
                                           ActionType.NONE,3))
            self.players.append(PlayerStrategy(PlayerState.REST,
                                           PlayerTarget(const.puck_x, const.puck_y),
                                           ActionType.NONE,4))
            self.players.append(PlayerStrategy(PlayerState.REST,
                                           PlayerTarget(const.def_x, const.def_y),
                                           ActionType.NONE,5))
        for h in const.world.hockeyists:
            if h.teammate and h.type != HockeyistType.GOALIE:
                self.players[h.teammate_index].me = h

    def find_player_in_state(self, state: PlayerState):
        for player in self.players:
            if player.state == state:
                return player
        return None

    def find_my_strategy(self, index):
        for p in self.players:
            if p.me.teammate_index == index:
                return p
        return None

    def main(self, const):
        for h in const.world.hockeyists:
            if h.teammate and h.type != HockeyistType.GOALIE:
                self.players[h.teammate_index].me = h

        if self.team_size == 2:
            strategy_2x2(const, self.players)
        elif self.team_size == 3:
            strategy_3x3(const, self.players)
        elif self.team_size == 6:
            strategy_6x6(const, self.players)




