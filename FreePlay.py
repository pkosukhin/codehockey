from model.ActionType import *
from Actions import force_move
from CommonFunctions import *

def attack_target(self, move, game, me, x, y):
    move.action = ActionType.NONE
    if me.get_distance_to(x,y) > 120:
        force_move(move, me, game, x, y, 1)
    elif abs(me.get_angle_to(x, y)) < game.stick_sector/2:
        move.action = ActionType.STRIKE
        move.turn = me.get_angle_to(x, y)
    else:
        move.turn = me.get_angle_to(x, y)

def attack_unit(move, me, game, unit):
    if me.get_distance_to_unit(unit) > game.stick_length * 2:
        pred_move = 10
    else:
        pred_move = 0
    force_move(move, me, game, *pred_unit_move(unit, pred_move), slowdown=1)
    if (#me.get_distance_to(const.puck_owner.x, const.puck_owner.y) < game.stick_length\
            #and me.get_angle_to(const.puck_owner.x, const.puck_owner.y) <= game.stick_sector/2 or\
          me.get_distance_to_unit(unit) < game.stick_length
                and abs(me.get_angle_to_unit(unit)) <= game.stick_sector/2):
                move.action = ActionType.STRIKE

def take_puck(move, me, game, world):
    if me.get_distance_to_unit(world.puck) > game.stick_length * 2:
        pred_move = 20
    else:
        pred_move = 0
    force_move(move, me, game, *pred_unit_move(world.puck, pred_move), slowdown=1)
    if me.get_distance_to_unit(world.puck) < 53:
        move.speed_up = -1
        move.turn = me.get_angle_to(world.puck.x, world.puck.y)
    move.action = ActionType.TAKE_PUCK