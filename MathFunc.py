from math import *
from Actions import *
from Constants import *
from CommonFunctions import *
from copy import copy, deepcopy

class PuckState:
    def __init__(self, inside_array, swing_time_array):
        self.inside_array = inside_array
        self.swing_time_array = swing_time_array
        self.swing_time_array_x_chance = [y if x > 0 else -1 for (x,y) in zip(inside_array,swing_time_array)]
        self.hit_chance = round((sum((1 if x>0 else 0)*(1 if y >= 0 else 0)
                                      for (x,y) in zip(inside_array,swing_time_array))/3),2)
        if self.hit_chance > 0.5:
            self.max_swing = max(swing_time_array)
            self.min_swing = min(x for x in (swing_time_array) if x > -1)
        else:
            self.max_swing = -1
            self.min_swing = -1

#me - player who hold whe puck
# player  - enemy player for puck owner

def puck_angle(player, me, const, future_time = 0, use_self_speed = 1, str = 100, stamina = 2000, px=0, py=0,puck_speed=0):
    stam_mod = 0.75 + 0.25*stamina / const.game.hockeyist_max_stamina
    str_mod = str/100

    net_front = const.game.rink_right
    if px == 0:
        puck_x = const.world.puck.x
        puck_y = const.world.puck.y
    else:
        puck_x = px
        puck_y = py
    """
    if future_time>0:
        puck_speed_up = puck_speed_up * const.alpha_player**future_time
        puck_x = puck_x  + const.world.puck.speed_x * (const.alpha_player**future_time- 1)/(const.alpha_player - 1)
        puck_y = puck_y  + const.world.puck.speed_y * (const.alpha_player**future_time- 1)/(const.alpha_player - 1)
    """
    sgn_y = copysign(1,const.rink_mid_y - puck_y)
    base_goal_y = (const.net_bot - 2
                if puck_y < const.rink_mid_y else
              const.net_top + 2)
    goal_x = const.game.rink_right
    goalie_line_x = const.game.rink_right-const.goalie_radius

    Rad = const.goalie_radius + const.puck_radius #sum puck radius + goalier radius

    delta_y = ( - 1
                if puck_y < base_goal_y else
               1)
    puck_x = (puck_x if player.net_front == net_front else net_front - (puck_x-player.net_front))
    swing_time_array = []
    delta_array = []
    interval_count = 0
    zero_interval_count = 0
    dead_line = False

    while not dead_line:
        finish_puck_y = base_goal_y  + interval_count*delta_y
        base_angle = get_angle(puck_x, puck_y,goal_x, finish_puck_y)
        angle_player = base_angle if abs(base_angle) <= pi/2 \
                                        else copysign(pi- abs(base_angle),base_angle)
        target_goalier_y = finish_puck_y - const.goalie_radius*tan(angle_player) - sgn_y * Rad/cos(angle_player)
        goalie_player = get_goalie(const.world)
        if goalie_player is not None:
            start_puck_y = goalie_player.y
        else:
            start_puck_y = (player.net_top + const.goalie_radius
                            if const.puck_y <= const.rink_mid_y else
                        player.net_bottom - const.goalie_radius)
        start_puck_x = puck_x +  (start_puck_y - puck_y)/tan(base_angle)\
                        if tan(angle_player) != 0 else 0


        dead_time_goalier = trunc(abs(target_goalier_y - start_puck_y)/const.game.goalie_max_speed)
        target_puck_x = goalie_line_x  - sgn_y * Rad * sin(angle_player)
        target_puck_y_goalie_line = (goalie_line_x - puck_x)*tan(angle_player) + puck_y
        target_puck_y = target_goalier_y  + sgn_y * Rad * cos(angle_player)
        target_goalier_y_goalie_line = target_puck_y_goalie_line - Rad*sgn_y
        #print('dt puck-{0}/{1} goalie-{2}'.format(str(puck_x), str(net_front - (puck_x-player.net_front)), str(dead_time_goalier)))
        dead_time_goalier_self_line = (target_goalier_y_goalie_line - start_puck_y)*sgn_y/const.game.goalie_max_speed
        dist_puck_to_target = hypot(target_puck_x-start_puck_x,target_puck_y-start_puck_y)
        dist_puck_to_target_goalie_line = hypot(goalie_line_x - start_puck_x,target_puck_y_goalie_line-start_puck_y)
        #print('dpt {0} dptg {1}'.format(round(dist_puck_to_target,1),round(dist_puck_to_target_goalie_line,1)))
        if (target_goalier_y-start_puck_y)*sgn_y <= const.game.goalie_max_speed\
                or dist_puck_to_target <= const.goalie_radius + const.puck_radius\
                or dead_time_goalier_self_line < 0:
            dead_line = True
            continue
        dead_time_puck = 0
        min_swing_time = -1
        swing_dead_time = -1
        swing_time = -1
        dead_line = True
        """
        print('dist {0} angle {7} sx {1} sy {2} tx {3} ty {4} tgx {5} tgy {6} fy {8} dtg {9}'.format(str(round(dist_puck_to_target)),
                                         str(round(start_puck_x)),
                                         str(round(start_puck_y)),
                                         str(round(target_puck_x)),
                                         str(round(target_puck_y)),
                                         str(round(target_goalier_x)),
                                         str(round(target_goalier_y)),
                                         str(round(base_angle/pi*180,1)),
                                         str(round(finish_puck_y)),
                                         str(round(dead_time_goalier,1))))
        """
        if use_self_speed == 1:
            puck_speed_up = speed(me)*cos(angle_player)
        elif use_self_speed ==0:
            puck_speed_up = puck_speed
        elif use_self_speed ==2:
            puck_speed_up = puck_speed*cos(angle_player)
        else:
            puck_speed_up = 0
        for i in range(21):
            start_speed = abs(puck_speed_up)*dir(me) +\
                (const.game.strike_power_base_factor
                 + i*const.game.strike_power_growth_factor)*const.game.struck_puck_initial_speed_factor * stam_mod * str_mod
            dead_time_puck = ceil(travel_time(dist_puck_to_target,start_speed,const.alpha_puck))
            dead_time_puck_gloalie_line = ceil(travel_time(dist_puck_to_target_goalie_line,start_speed,const.alpha_puck))
            #print('puck dpt {0} dptg {1}'.format(round(dead_time_puck,1),round(dead_time_puck_gloalie_line,1)))
            #print('goal dgt {0} dgtg {1}'.format(round(dead_time_goalier,1),round(dead_time_puck_gloalie_line,1)))
            if dead_time_puck < dead_time_goalier and\
                dead_time_puck < dead_time_puck_gloalie_line:
                swing_time = i
                dead_line = False
                break
        if swing_time != -1:
            swing_time_array.append(swing_time)
            delta_array.append(interval_count*delta_y)
            if swing_time == 0:
                zero_interval_count +=1
            interval_count += 1
        #print('Time_puck ' + str(target_puck_x) +' - time_goal ' + str(start_puck_x))
    max_swing = max(swing_time_array) if  interval_count > 0 else -1
    #print('GGG = '+ ' '.join(str(x) for x in swing_time_array))
    return interval_count, swing_time_array, zero_interval_count, max_swing, base_goal_y
