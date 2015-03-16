from math import *
from model.Unit import Unit
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from CommonFunctions import *

def dir(me: Unit):
    return 1 if abs(me.get_angle_to(me.x + me.speed_x, me.y + me.speed_y)) <= pi/2 else -1


def travel_time(start_dist, start_speed, alpha):
    underlog = min(start_dist*(alpha-1)/(start_speed*alpha)+1,1)
    return log(underlog,alpha) if 0<underlog < 1 else 0

def my_angle_to_speed(me: Unit):
    return me.get_angle_to(me.x + me.speed_x, me.y + me.speed_y)

def speed(me: Unit):
        return hypot(me.speed_x,me.speed_y)

def stop_me(move, me, game):
    if speed(me) <= game.hockeyist_speed_down_factor/10:
        move.speed_up = 0
    elif speed(me) <= game.hockeyist_speed_down_factor * 2:
        move.speed_up = -dir(me) * speed(me) / (2 * game.hockeyist_speed_down_factor)
    else:
        move.speed_up = -dir(me)

def accelerate(move, me, game, action, fwd, force_stop = 0):
    if action == 0:
        if fwd == 0:
            move.speed_up = 0
        else:
            if speed(me) <= game.hockeyist_speed_down_factor/10:
                move.speed_up = 0
            elif speed(me) <= game.hockeyist_speed_down_factor * 3:
                move.speed_up = -dir(me) * speed(me) / (3 * game.hockeyist_speed_down_factor)
            else:
                move.speed_up = -dir(me)
    else:
        if fwd != dir(me) and speed(me) >= game.hockeyist_speed_down_factor/10 and force_stop == 1:
            move.speed_up = -dir(me)
        else:
            move.speed_up = fwd * action

def safe_move(move, me, game, x, y, slowdown):
    if slowdown == 0:
        move.speed_up = 1
        move.turn = me.get_angle_to(x, y)
    if me.get_distance_to(x,y) < me.radius:
        stop_me(move,me,game)
    elif abs(me.get_angle_to(x,y)) > pi*3/4:
        if me.get_distance_to(x,y) < me.radius*6:
            accelerate(move, me, game, 0.5, -1, 0)
            move.turn = -copysign(pi-abs(me.get_angle_to(x,y)),me.get_angle_to(x,y))
        else:
            accelerate(move, me, game, 0.5, -1, 0)
            if me.get_distance_to(x,y) > me.radius *1.5:
                move.turn = me.get_angle_to(x, y)
            else:
                move.turn = copysign(pi,me.get_angle_to(x, y)) - abs(me.get_angle_to(x, y))
    elif abs(me.get_angle_to(x,y)) > pi/4 and me.get_distance_to(x,y) > me.radius*0.8:
        accelerate(move, me, game, 0.4, 1, 0)
        move.turn = me.get_angle_to(x, y)
    elif (abs(me.get_angle_to(x, y)) > pi/1000 and me.get_distance_to(x,y) > me.radius*0.8):
        move.turn = me.get_angle_to(x, y)
        accelerate(move, me, game, 1, 0, 0)
    elif (me.get_distance_to(x,y) * cos(me.get_angle_to(x,y))/(speed(me)+ game.hockeyist_speed_up_factor)
              >= (speed(me)/game.hockeyist_speed_down_factor + 1)
        and me.get_distance_to(x,y) > me.radius*0.8):
        accelerate(move, me, game, 1, 1)
        move.turn = me.get_angle_to(x, y)
    else:
        move.speed_up = 0
        move.turn = me.get_angle_to(x, y)

def force_move(move, me, game, x, y, slowdown):
    if slowdown == 0:
        move.speed_up = 1
        move.turn = me.get_angle_to(x, y)
    elif abs(me.get_angle_to(x,y)) > pi/2 and me.get_distance_to(x,y):
        accelerate(move, me, game,  1, -1, 0)
        move.turn = me.get_angle_to(x, y)
    elif abs(me.get_angle_to(x,y)) > pi/4 and me.get_distance_to(x,y):
        accelerate(move, me, game,  1, 1, 0)
        move.turn = me.get_angle_to(x, y)
    else:
        accelerate(move, me, game,  1, 1)
        move.turn = me.get_angle_to(x, y)

def cool_move(move, me, game, const, x, y):
    R = game.stick_length*3
    """
    for p in const.world.hockeyists:
        if not p.teammate and p.state != HockeyistState.RESTING and p.type != HockeyistType.GOALIE:
    """
    p = nearest_opponent(game,const.world,me.x,me.y)
    dist = me.get_distance_to_unit(p)
    dist_opp_to_line = dist_between_point_line(me.x,me.y,x,y,p.x,p.y)
    if dist_opp_to_line < R and dist > R:
        abs_angle = get_angle(me.x,me.y,p.x,p.y)
        angle_between = abs_angle-me.angle
        opp_angle = pi/4-2*abs_angle-me.get_angle_to(x,y)
        trg_point_x = p.x + R*cos(opp_angle)
        trg_point_y = p.y + R*sin(opp_angle)
        force_move(move,me,game,trg_point_x,trg_point_y,1)
    else:
        force_move(move,me,game,x,y,1)

def check_pass(me, player, game):
    return abs(me.get_angle_to_unit(player)) < game.stick_sector/2

def get_rested_player(players):
    max_rest = 0
    max_rst_str = 0
    rested_player = None
    for p in players:
        if p.me.state == HockeyistState.RESTING:
            if p.me.stamina > max_rest+100\
                    or p.me.stamina > max_rest and (p.me.strength-max_rst_str)<5\
                    or p.me.stamina > max_rest-100 and p.me.strength-max_rst_str>=5:
                max_rest = p.me.stamina
                max_rst_str = p.me.strength
                rested_player = p.me.teammate_index
    return rested_player

