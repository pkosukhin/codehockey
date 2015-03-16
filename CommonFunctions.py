from math import *
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Unit import Unit
from model.Game import Game

def lprint(string, tick = 0, prnt = True):
    if prnt:
        if tick % 20  == 0:
            print(string)
        else:
            return
    else:
        return

def pred_unit_move(unit, pred_time,alpha = 0.999):
        (unit_x,unit_y) = (unit.x, unit.y)
        if alpha == 0.999:
            unit_x = unit.x  + unit.speed_x * (alpha**pred_time - 1)/(alpha - 1)
            unit_y = unit.y  + unit.speed_y * (alpha**pred_time - 1)/(alpha - 1)
        else:
            unit_x = unit.x  + unit.speed_x * pred_time
            unit_y = unit.y  + unit.speed_y * pred_time
        return unit_x, unit_y

def nearest_player(game: Game, world, x, y, teammate, knocked_down = True):
    nearest_player = None
    nearest_player_range = 0
    for hockeyist in world.hockeyists:
        if ((hockeyist.teammate != teammate or teammate is None)
            or hockeyist.type == HockeyistType.GOALIE
            or (hockeyist.state == HockeyistState.KNOCKED_DOWN
                and hockeyist.remaining_knockdown_ticks > game.max_effective_swing_ticks
                and knocked_down)
            or hockeyist.state == HockeyistState.RESTING):
            continue
        player_range = hypot(x - hockeyist.x, y - hockeyist.y)
        if (nearest_player is None or player_range < nearest_player_range):
            nearest_player = hockeyist
            nearest_player_range = player_range
    return nearest_player

def nearest_opponent(game, world, x, y, knocked_down = True):
    return nearest_player(game, world, x, y, False, knocked_down)

def nearest_teammate(game, world, x, y, knocked_down = True):
    return nearest_player(game, world, x, y, True, knocked_down)


def count_enemies_around(x,y,raidus,const):
    count = 0
    for h in const.world.hockeyists:
        if (not h.teammate
            and h.type != HockeyistType.GOALIE
            and h.state != HockeyistState.RESTING
            and h.get_distance_to(x,y) <= raidus):
            count +=1
    return count

def near_point(me, x, y, rad):
    #print(str(me.get_distance_to(x,y)))
    if me.get_distance_to(x,y) <= rad:
        return True
    else:
        return False

def get_angle(from_x, from_y, to_x, to_y):
        angle_to = atan2(to_y - from_y, to_x - from_x)

        while angle_to > pi:
            angle_to -= 2.0 * pi

        while angle_to < -pi:
            angle_to += 2.0 * pi
        return angle_to

def get_relative_angle(from_x, from_y, angle, to_x, to_y):
        absolute_angle_to = atan2(to_y - from_y, to_x - from_x)
        relative_angle_to = absolute_angle_to - angle

        while relative_angle_to > pi:
            relative_angle_to -= 2.0 * pi

        while relative_angle_to < -pi:
            relative_angle_to += 2.0 * pi

        return relative_angle_to

def get_goalie(world, teammate = True):
    for h in world.hockeyists:
        if h.type == HockeyistType.GOALIE:
            return h
        else:
            return None

def dist_between_point_line(x1,y1,x2,y2,x,y):
    a = y1 - y2
    b = x2 - x1
    c = y2*x1 - y1*x2
    d = abs(a*x+b*y+c)/sqrt(a*a + b*b)
    print ('dist nearest: ' + str(round(d,1)))
    return d