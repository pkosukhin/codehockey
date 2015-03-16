from Actions import *
from MathFunc import puck_angle
from Constants import *
from model.ActionType import *


def go_def(move, me, game, x, y, const: WorldConstants):
    safe_move(move, me, game, x, y, 1)
    push_opp = 0
    for h in const.world.hockeyists:
        if not h.teammate and\
            me.get_distance_to_unit(h) <= game.stick_length and\
            abs(me.get_angle_to_unit(h)) <= game.stick_sector/2:
            push_opp = 1
    move.action = ActionType.TAKE_PUCK
    if me.get_distance_to(x, y) < me.radius*1.5:
        stop_me(move, me, game)
        move.turn = me.get_angle_to_unit(const.world.puck)
        if me.radius <= me.get_distance_to(x, y)<= me.radius*1.5:
            accelerate(move, me, game, 0.6, -1, 0)
    nearest_opp_to_me = nearest_opponent(game,const.world,me.x, me.y)
    if nearest_opp_to_me is not None and me.get_distance_to_unit(nearest_opp_to_me) <= game.stick_length\
        and abs(me.get_angle_to_unit(nearest_opp_to_me)) <= game.stick_sector/2:
            move.action = ActionType.STRIKE
    strtake_puck(move, me, game, const, const.player)


def stay_def(move, me, game, x, y, const: WorldConstants):
    safe_move(move, me, game, x, y, 1)
    push_opp = 0
    for h in const.world.hockeyists:
        if not h.teammate and\
            me.get_distance_to_unit(h) <= game.stick_length and\
            abs(me.get_angle_to_unit(h)) <= game.stick_sector/2:
            push_opp = 1
    move.action = ActionType.TAKE_PUCK
    if me.get_distance_to(x, y) < me.radius*1.5:
        stop_me(move, me, game)
        move.turn = me.get_angle_to_unit(const.world.puck)
    nearest_opp_to_me = nearest_opponent(game,const.world,me.x, me.y)
    if nearest_opp_to_me is not None and me.get_distance_to_unit(nearest_opp_to_me) <= game.stick_length\
        and abs(me.get_angle_to_unit(nearest_opp_to_me)) <= game.stick_sector/2:
        move.action = ActionType.STRIKE
    strtake_puck(move, me, game, const, const.player)

def defend_from_player(move, me, game, const):
    if me.get_distance_to_unit(const.world.puck) > game.stick_length * 2:
        pred_move = 5
    else:
        pred_move = 0
    force_move(move,me,game,pred_unit_move(const.world.puck, pred_move)[0], pred_unit_move(const.world.puck, pred_move)[1], slowdown=1)
    if me.get_distance_to(const.puck_owner.x, const.puck_owner.y) < game.stick_length\
        and abs(me.get_angle_to(const.puck_owner.x, const.puck_owner.y)) <= game.stick_sector/2:
            move.action = ActionType.STRIKE
    strtake_puck(move, me, game, const, const.player, False)

def prevent(move, me, game, const):
    puck_nearest_opp = nearest_opponent(game,const.world,const.world.puck.x, const.world.puck.y)
    if me.get_distance_to_unit(puck_nearest_opp) > game.stick_length * 2:
        pred_move = 10
    else:
        pred_move = 0
    force_move(move,me,game,pred_unit_move(const.world.puck, pred_move)[0], pred_unit_move(const.world.puck, pred_move)[1], slowdown=1)

    if me.get_distance_to_unit(puck_nearest_opp) <= game.stick_length\
        and abs(me.get_angle_to_unit(puck_nearest_opp)) <= game.stick_sector/2:
            move.action = ActionType.STRIKE
    if me.get_distance_to_unit(const.world.puck) <= game.stick_length\
        and abs(me.get_angle_to_unit(const.world.puck)) <= game.stick_sector/2:
            move.action = ActionType.STRIKE

def strtake_puck(move, me, game, const, player, check_take = True):
    if (me.get_distance_to_unit(const.world.puck) <= game.stick_length
        and abs(me.get_angle_to_unit(const.world.puck)) <= game.stick_sector/2
        and const.world.puck.owner_player_id != me.player_id):
        puck_strike_solve = puck_angle(const.player, me, const,use_self_speed=0, puck_speed = speed(const.world.puck))
        puck_strike_solve_opp = puck_angle(const.opponent_player, me, const,use_self_speed=0, puck_speed = speed(const.world.puck))
        puck_fly_angle = get_angle(const.puck_x, const.puck_y,
                               const.puck_x + const.world.puck.speed_x, const.puck_y + const.world.puck.speed_y)
        puck_target_y = const.puck_y - (const.puck_x-const.player.net_front)*tan(puck_fly_angle)
        puck_target_enemy_y = const.puck_y - (const.puck_x-const.opponent_player.net_front)*tan(puck_fly_angle)
        if (puck_strike_solve[2] >= abs(puck_target_y - puck_strike_solve[4])
                or puck_strike_solve_opp[2] >= abs(puck_target_enemy_y - puck_strike_solve_opp[4]))\
            and const.player.net_top <= puck_target_y <= const.player.net_bottom or not check_take:
                if (const.puck_x-const.player.net_front) < const.rink_len/2:
                    move.action = ActionType.STRIKE
                    print('** PUCK COMING STRIKE! CHECK = {2} ** target: {0} zero_window:{1}'.format(str(round(puck_target_y)),
                                                                             puck_strike_solve[2],
                                                                             check_take))
                else:
                    move.action = ActionType.NONE
                    print('** PUCK COMING ENEMY! SKIP! CHECK = {2} ** target: {0} zero_window:{1}'.format(str(round(puck_target_y)),
                                                                             puck_strike_solve_opp[2],
                                                                             check_take))

        else:
            move.action = ActionType.TAKE_PUCK
            print('** PUCK COMING TAKE! ** target: {0} enemy: {2} zero_window:{1}'.format(str(round(puck_target_y)),
                                                                     str(round(puck_target_enemy_y)),
                                                                     puck_strike_solve[2]))
