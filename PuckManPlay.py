import math
from model.HockeyistState import *
from model.ActionType import *
from CommonFunctions import *
from Constants import *



def swing_play(me, const: WorldConstants, puck_state, puck_state_next):
    if me.state == HockeyistState.SWINGING or me.swing_ticks == 0:
        if me.swing_ticks < puck_state.max_swing \
                and puck_state_next.hit_chance > 0.5 \
                and me.get_distance_to_unit(nearest_opponent(const.game, const.world, me.x, me.y)) > const.game.stick_length + 10:
            return 0
        elif (me.swing_ticks < const.game.max_effective_swing_ticks
              and puck_state_next.hit_chance > 0.5
              and me.get_distance_to_unit(nearest_opponent(const.game, const.world, me.x, me.y)) > const.game.stick_length + 10):
            return 1
        elif puck_state.max_swing/2<= me.swing_ticks <=puck_state.max_swing \
                and puck_state_next.hit_chance <0.5\
                or  me.swing_ticks >= puck_state.max_swing\
                or  me.swing_ticks >= const.game.max_effective_swing_ticks\
                or puck_state.max_swing < 5 and puck_state.min_swing == 0:
            return 2
        else:
            return -1
    else:
        return None

def swing_play_window(me, const: WorldConstants, puck_state, puck_state_next):
    if me.state == HockeyistState.SWINGING or me.swing_ticks == 0:
        if me.swing_ticks < puck_state.max_swing \
                and puck_state_next.hit_chance > 0.5 \
                and me.get_distance_to_unit(nearest_opponent(const.game, const.world, me.x, me.y)) > const.game.stick_length + 10:
            return 0
        elif (me.swing_ticks < const.game.max_effective_swing_ticks
              and puck_state_next.hit_chance > 0.5
              and me.get_distance_to_unit(nearest_opponent(const.game, const.world, me.x, me.y)) > const.game.stick_length + 10):
            return 1
        elif puck_state.max_swing/2<= me.swing_ticks <=puck_state.max_swing \
                and puck_state_next.hit_chance <0.5\
                or  me.swing_ticks >= puck_state.max_swing\
                or  me.swing_ticks >= const.game.max_effective_swing_ticks\
                or puck_state.max_swing < 5 and puck_state.min_swing == 0:
            return 2
        else:
            return -1
    else:
        return None


def check_strike(me, const: WorldConstants, puck_state, puck_state_next,max_swing = 21,strike_speed = 0.5):
    if const.rink_len/7 <= abs(me.x -const.opponent_player.net_front) <=const.rink_len*3/5:
        #self.force_move(self,netX,netY,1)
        if puck_state.hit_chance > 0.5 \
                and puck_state_next.hit_chance > 0.5 \
                and puck_state.max_swing<max_swing\
                and speed(me) * cos(abs(my_angle_to_speed(me))) > strike_speed:
            return True
        else:
            return False
    else:
        return None

def check_strike_new(me, const: WorldConstants, puck_state, puck_state_next,max_swing = 21,strike_speed = 0.5):
    if const.rink_len/7 <= abs(me.x -const.opponent_player.net_front) <=const.rink_len*3/5:
        #self.force_move(self,netX,netY,1)
        if puck_state.hit_chance > 0.5 \
                and puck_state_next.hit_chance > 0.5 \
                and puck_state.max_swing<max_swing\
                and speed(me) * cos(abs(my_angle_to_speed(me))) > strike_speed:
            return True
        else:
            return False
    else:
        return None

def go_position(move, me, const, x, y):
    force_move(move, me, const.game, x, y, 1)

def get_net_position(me, const, strike_solve, ans = 1):
    netX = const.opponent_player.net_front
    """
    netY = 0.5 * (const.opponent_player.net_bottom + const.opponent_player.net_top)
    netY = (const.opponent_player.net_bottom - 2
                if me.y < netY
                else const.opponent_player.net_top + 2)
    distance_to_net = me.get_distance_to(netX,netY)
    delta_strike = sqrt(2 * distance_to_net**2 * (1-cos(const.game.strike_angle_deviation)))
    delta_pass = sqrt(2 * distance_to_net**2 * (1-cos(const.game.pass_angle_deviation)))
    net_y_strike = netY - delta_strike * (1 if me.y < netY else -1)
    net_y_pass = netY - delta_pass * (1 if me.y < netY else -1)
    """
    goal_x = const.player.net_front
    goal_y = 0.5 * (const.player.net_bottom + const.player.net_top)
    goal_y = (const.player.net_bottom
                if const.world.puck.y < goal_y else
              const.player.net_top)
    delta_y = ( - 1
                if const.world.puck.y < goal_y else
               1)
    base_y_strike = goal_y + delta_y*(strike_solve[0]-1)/2
    pass_y_strike = goal_y + strike_solve[2]/2*delta_y
    relative_y_speed = me.speed_y - me.speed_x*tan(get_angle(me.x,me.y,netX,base_y_strike))

    real_delta_predict = 0
    base_angle = get_angle(const.puck_x,const.puck_y,goal_x,goal_y)
    strike_dev = abs((const.opponent_player.net_front-const.puck_x)*tan(base_angle)-
    (const.opponent_player.net_front-const.puck_x)*tan(base_angle+pi/90))
    print('STRIKE DEV' + str(round(strike_dev,1)))
    if strike_solve[0]>1:
        predict_time = (sum(strike_solve[1])/len(strike_solve[1]) + max(strike_solve[1]))/2
        delta_predict = relative_y_speed * predict_time
        strike_dev = abs((const.opponent_player.net_front-const.puck_x)*tan(base_angle)-
                        (const.opponent_player.net_front-const.puck_x)*tan(base_angle+pi/90))
        max_delta = trunc(strike_solve[0])
        real_delta_predict = copysign(min(max_delta,abs(delta_predict)),delta_predict)
        print('-')
        print('dev {0} relyspd {1} time {2} shift {3} / max {4} =real {5} spdy {6} spdx {7} angle {8}'.format(str(round(strike_dev,1)),
                                                                 str(round(relative_y_speed,1)),
                                                                 str(round(predict_time,1)),
                                                                 str(round(delta_predict,1)),
                                                                 str(round(max_delta,1)),
                                                                 str(round(real_delta_predict,1)),
                                                                 str(round(me.speed_y,1)),
                                                                 str(round(me.speed_x,1)),
                                                                 str(round(tan(get_angle(me.x,me.y,netX,base_y_strike)),1))))
    else:
        print('WINDOW LEN LESS 1 GG')

    net_y_strike = base_y_strike - real_delta_predict
    strike_window = strike_solve[0]
    if const.puck_y < const.rink_mid_y:
                    window_bot = const.player.net_bottom
                    window_top = window_bot - (strike_window-1)
    else:
        window_top = const.player.net_top
        window_bot = window_top + (strike_window-1)
    finish_puck_y = const.puck_y + \
                    (const.opponent_player.net_front -  const.puck_x)*tan(me.angle)
    finish_puck_win_top = finish_puck_y - strike_dev
    finish_puck_win_bot = finish_puck_y + strike_dev
    print('NET STAT! base: wlen {6} top {0} bot {1} trg {2} fin: top {3} bot {4} trg {5}'.format(
        str(round(window_top)),
        str(round(window_bot)),
        str(round(base_y_strike)),
        str(round(finish_puck_win_top)),
        str(round(finish_puck_win_bot)),
        str(round(finish_puck_y,1)),
        str(round(strike_window,1))
    ))
    print('STRK STAT: zero win: {0}'.format(str(strike_solve[2])))
    """
    print('GET NET POS: w: {0} g: {1} bot: {2} target: {3} yspd:{4} pred:{5}'.format(str(strike_solve[0]),
                                                                       str(goal_y),
                                                                       str(goal_y + delta_y*(strike_solve[0]-1)),
                                                                       str(round(net_y_strike)),
                                                                       str(round(relative_y_speed,1)),
                                                                       str(round(real_delta_predict))))
                                                                       """
    if ans == 0:
        return netX, pass_y_strike
    elif ans == 1:
        return netX, net_y_strike
    else:
        return relative_y_speed, (sum(strike_solve[1])/len(strike_solve[1]) + max(strike_solve[1]))/2


def get_position_point(me,const):
    if abs(me.x-const.opponent_player.net_front) < const.rink_len*2/3:
        target_x = const.opponent_player.net_front - const.sgn_x * const.rink_len*2/5
    else:
        target_x = (me.x+const.opponent_player.net_front)/2
    diff_x = 0
    diff_y = 0
    opp_players_count = 0
    for h in const.world.hockeyists:
        if (not h.teammate
            and h.type != HockeyistType.GOALIE
            and h.state != HockeyistState.RESTING
            #and abs(h.x - const.opponent_player.net_front) >= const.rink_len/4)
            ):
            diff_y += const.rink_mid_y - h.y
            diff_x += abs(h.x-const.opponent_player.net_front)
            opp_players_count += 1

    if abs(me.x -const.player.net_front) < const.rink_len/3:
        return target_x,const.rink_mid_y + copysign(const.rink_width/2-30,diff_y)
        """
        if abs(me.y - const.rink_mid_y) > const.rink_width/4 \
            and (diff_y == 0 or diff_y/opp_players_count < const.rink_width/4):
            print('~ my way 1 ')
            return target_x,const.rink_mid_y - copysign(const.rink_width/2-30,diff_y)
        else:
            if diff_y == 0 or diff_y/opp_players_count > (const.game.rink_top-const.rink_mid_y)/2:
                print('~ my way 2')
                return target_x,const.rink_mid_y - copysign(const.rink_width/2-30,diff_y)
            else:
                print('~ my way 3')
                return target_x,const.rink_mid_y + copysign(const.rink_width/2-30,me.angle)
        """
    else:
        print('~ my way 4')
        return target_x,const.rink_mid_y + copysign(const.rink_width/2-30,diff_y)

def check_predict_strike(me,const):
    turn_time = ceil(max(abs(me.get_angle_to(const.opponent_player.net_front,const.opponent_player.net_top)),
                    abs(me.get_angle_to(const.opponent_player.net_front,const.opponent_player.net_bottom)))/const.game.hockeyist_turn_angle_factor)
    max_observe_ticks = pi/const.game.hockeyist_turn_angle_factor + const.game.max_effective_swing_ticks
    sl = const.game.stick_length
    for tick in range(max_observe_ticks):
        strike_solve = puck_angle(const.opponent_player, me, const, 0, 2, me.strength, me.stamina,
                                  me.x + cos(me.angle)*sl, me.y + sin(me.angle)*sl,speed(me)*(0.98**tick))
