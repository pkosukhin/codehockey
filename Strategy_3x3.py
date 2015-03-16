from model.ActionType import ActionType
from model.HockeyistType import HockeyistType
from model.Hockeyist import Hockeyist
from Constants import *
from PuckManPlay import *
from DefPlay import *
from MathFunc import *
from PlayerStates import *
from Strategy import *

def strategy_3x3(const, players):
        for player in players:
            if player.state != PlayerState.REST:
                while not player.staged:
                    player.staged = True
                    ########################################################
                    goal_y = 0.5 * (const.player.net_bottom + const.player.net_top)
                    goal_y = (const.player.net_bottom - 2
                                if const.puck_y < goal_y else
                              const.player.net_top + 2)
                    goal_x = const.player.net_front
                    dex_mod = player.me.dexterity/100
                    base_angle = get_angle(const.puck_x,const.puck_y,goal_x,goal_y)
                    strike_solve = puck_angle(const.opponent_player,player.me,const,0,1,
                                                 player.me.strength,player.me.stamina,player.me.x,player.me.y)
                    strike_solve_pass = puck_angle(const.opponent_player,player.me,const,0,1,
                                              player.me.strength,player.me.stamina)
                    strike_dev = abs((const.opponent_player.net_front-const.puck_x)*tan(base_angle)-
                                     (const.opponent_player.net_front-const.puck_x)*tan(base_angle+pi/90))*\
                                    dex_mod
                    strike_window = strike_solve[0]
                    if strike_window is not None and strike_window>=1:
                        mid_swing = strike_solve[1][trunc((len(strike_solve[1])-1)/2)]
                        avg_swing = sum(strike_solve[1])/len(strike_solve[1])
                        max_swing = max(strike_solve[1])
                    else:
                        mid_swing = -1
                        avg_swing = -1
                        max_swing = -1

                    strike_window_pass = strike_solve_pass[0]

                    if const.puck_y < const.rink_mid_y:
                        window_bot = const.player.net_bottom
                        window_top = window_bot - 2*(strike_window-1)
                    else:
                        window_top = const.player.net_top
                        window_bot = window_top + 2*(strike_window-1)
                    finish_puck_y = const.puck_y + \
                                    (const.opponent_player.net_front -  const.puck_x)*tan(player.me.angle)
                    finish_puck_win_top = finish_puck_y - strike_dev
                    finish_puck_win_bot = finish_puck_y + strike_dev
                    #################################################################

                    if (const.player.just_scored_goal or const.player.just_missed_goal):
                        if player.state != PlayerState.REST_FUNNY:
                            if const.player.just_scored_goal:
                                print('~~~   JUST SCORED GOAL!!!   ~~~')
                            else:
                                print('~~~   MISSED GOAL :(   ~~~')
                        player.state = PlayerState.REST_FUNNY
                    if player.state == PlayerState.REST_FUNNY and \
                        not (const.player.just_scored_goal or const.player.just_missed_goal):
                        #print(str(nearest_teammate(const.game, const.world,const.def_x, const.def_y,False).id))
                        #print(player.me.id)
                        if player.me.teammate_index == 2:
                            player.state = PlayerState.DEFMAN_GODEF_PERMANENT
                            player.target = PlayerTarget(const.def_x, const.def_y)
                            player.action = ActionType.TAKE_PUCK
                        else:
                            player.state = PlayerState.FREE_TAKE_PUCK
                            player.target = PlayerTarget(const.puck_x, const.puck_y)
                            player.action = ActionType.TAKE_PUCK
                    if player.state in (PlayerState.PUCKMAN_GONET, PlayerState.PUCKMAN_SWING)\
                            and const.puck_owner is not None:
                        ########################
                        puck_owner_next = deepcopy(const.puck_owner)
                        puck_owner_next.speed_x = puck_owner_next.speed_x*0.98
                        puck_owner_next.speed_y = puck_owner_next.speed_y*0.98
                        puck_owner_next.x += puck_owner_next.speed_x
                        puck_owner_next.y += puck_owner_next.speed_y
                        puck_owner_next.angle += puck_owner_next.angular_speed

                        world_next = deepcopy(const.world)
                        world_next.puck.x += puck_owner_next.speed_x
                        world_next.puck.y += puck_owner_next.speed_y
                        ##############################

                    if (player.state in PlayerState.PUCKMAN_STATES
                                and (const.puck_owner is None
                                        or
                                     const.puck_owner is not None and const.puck_owner.id != player.me.id
                                    )
                        ):
                        if player.me.state == HockeyistState.SWINGING:
                            player.state = PlayerState.PUCKMAN_CANCEL_STRIKE
                        elif const.puck_owner is None or const.puck_owner.player_id != player.me.player_id:
                            player.state = PlayerState.FREE_TAKE_PUCK
                        else:
                            player.state = PlayerState.DEFMAN_GODEF
                            player.target = PlayerTarget(const.rink_mid_x, const.rink_mid_y)
                    elif (player.state in PlayerState.DEFMAN_STATES and const.puck_owner is  not None
                            and const.puck_owner.id == player.me.id):
                            player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                            player.target = PlayerTarget(*get_position_point(player.me, const))
                            player.stages = False
                    elif player.state in (PlayerState.DEFMAN_GODEF,
                                          PlayerState.DEFMAN_PREVENT,
                                          PlayerState.DEFMAN_TAKE_PUCK,
                                          PlayerState.DEFMAN_TAKE_PUCK,
                                          PlayerState.FREE_ATTACK_DEF,
                                          PlayerState.DEFMAN_HELP_OWNER):
                        """
                        if player.me.get_distance_to(player.target.x, player.target.y) <= const.player_radius:
                            player.state = PlayerState.DEFMAN_STAY
                        """
                        if const.puck_owner is not None and const.puck_owner.player_id != const.player.id:
                            if abs(const.puck_x - const.player.net_front) > const.rink_len/2:
                                player.state = PlayerState.DEFMAN_DEFEND
                                player.staged = False
                            else:
                                player.state = PlayerState.DEFMAN_PREVENT
                                player.target = PlayerTarget(
                                    nearest_opponent(const.game,const.world,const.player.net_front+const.sgn_x*const.rink_len/4,
                                                     const.rink_mid_y).x,
                                    nearest_opponent(const.game,const.world,const.player.net_front+const.sgn_x*const.rink_len/4,
                                                     const.rink_mid_y).y)
                        elif const.puck_owner is not None and const.puck_owner.player_id == const.player.id\
                                or abs(const.opponent_player.net_front-const.puck_x) < const.rink_len/2\
                                and speed(const.world.puck) > 14 and const.player.net_top <= const.puck_y+const.puck_y*\
                                        tan(get_angle(const.puck_x,const.puck_y,const.puck_x+const.world.puck.speed_x,const.puck_y+const.world.puck.speed_y))\
                                        <= const.player.net_bottom:
                                player.state = PlayerState.FREE_ATTACK_DEF
                        else:
                            if (abs(const.puck_x - const.player.net_front) < const.rink_len/2
                                or speed(const.world.puck) > 14 and const.world.puck.speed_x*const.sgn_x > 5):
                                player.state = PlayerState.DEFMAN_TAKE_PUCK
                            else:
                                player.state = PlayerState.DEFMAN_GODEF
                                player.target = PlayerTarget(const.rink_mid_x, const.rink_mid_y)
                    elif player.state == PlayerState.DEFMAN_DEFEND:
                        if const.puck_owner is not None and const.puck_owner.player_id != const.player.id:
                            if abs(const.puck_x - const.player.net_front) > const.rink_len/2:
                                if pred_unit_move(const.world.puck,30)[1] <= const.player.net_top:
                                    player.target = PlayerTarget(const.def_x_front,const.def_y_top)
                                elif pred_unit_move(const.world.puck,30)[1] >= const.player.net_bottom:
                                    player.target = PlayerTarget(const.def_x_front,const.def_y_bot)
                                else:
                                     player.target = PlayerTarget(const.def_x,const.def_y)
                            else:
                                player.state = PlayerState.DEFMAN_PREVENT
                                player.target = PlayerTarget(const.puck_x, const.puck_y)
                        else:
                            player.state = PlayerState.DEFMAN_GODEF
                            player.target = PlayerTarget(const.rink_mid_x, const.rink_mid_y)
                            player.staged = False
                    elif player.state in(PlayerState.FREE_TAKE_PUCK, PlayerState.FREE_ATTACK_PUCK):
                        if const.puck_owner is not None:
                            if const.puck_owner.id == player.me.id:
                                player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                                player.target = PlayerTarget(*get_position_point(player.me, const))
                            elif const.puck_owner.teammate:
                                player.state = PlayerState.DEFMAN_GODEF
                                player.target = PlayerTarget(const.rink_mid_x, const.rink_mid_y)
                            elif not const.puck_owner.teammate:
                                player.state = PlayerState.FREE_ATTACK_PUCK
                                player.target = PlayerTarget(const.puck_x, const.puck_y)
                        else:
                            player.state = PlayerState.FREE_TAKE_PUCK
                    #pre-states for turn+swing
                    elif player.state == PlayerState.PUCKMAN_PASS_STRIKE:
                        if strike_solve_pass[2] < strike_dev/8 or strike_solve_pass[2] <= 2:
                            player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                            player.staged = False
                    elif player.state in(PlayerState.PUCKMAN_GO_SIDE_POSITION,
                                         PlayerState.PUCKMAN_GONET,
                                         PlayerState.PUCKMAN_GO_MID_POSITION):
                        #print state
                        print('Tick: {5} wind-{0}, dev: {6}, mid_swing-{1}, avg-{2} max_s-{3} fin_y: {4}'.format(str(strike_window),
                                                                     str(mid_swing),
                                                                     str(round(avg_swing,1)),
                                                                     str(max_swing),
                                                                     str(round(finish_puck_y,1)),
                                                                     str(const.tick),
                                                                     str(round(strike_dev,1))))
                        target = PlayerTarget(*get_net_position(player.me, const, strike_solve))
                        turn_ticks = math.ceil(abs(player.me.get_angle_to(target.x, target.y))/const.turn_speed)

                        """
                        if False and strike_dev < strike_window:
                            shift = trunc((strike_window-strike_dev)/2)
                            max_eff_swing = max(strike_solve[1][shift:(len(strike_solve[1])-1-shift)])
                            total_to_swing =  turn_ticks + max_swing
                            print('pre-count turn_ticks: {0} swing: {1} total: {2}'.format(str(turn_ticks),
                                                                                          str(max_swing),
                                                                                          str(total_to_swing)))
                            ftr_strike_solve = puck_angle(const.opponent_player,player.me,const,total_to_swing)
                            ftr_net = get_net_position(player.me, const, ftr_strike_solve)
                            ftr_me = pred_unit_move(player.me, total_to_swing, const.alpha_player)
                            ftr_puck = pred_unit_move(const.world.puck, total_to_swing, const.alpha_player)
                            ftr_angle = get_angle(ftr_me[0],ftr_me[1],ftr_net[0], ftr_net[1])
                            ftr_strike_dev = abs((const.opponent_player.net_front-ftr_puck[0])*tan(ftr_angle)-
                                     (const.opponent_player.net_front-ftr_puck[0])*tan(ftr_angle+pi/180))
                            if ftr_strike_dev*2 < ftr_strike_solve[0] and ftr_strike_solve[0] > 0:
                                ftr_strike_window = strike_solve[0]
                                if ftr_strike_window is not None and ftr_strike_window>=1:
                                    #print('ftr_mid_swing: ' + str(trunc((len(ftr_strike_solve[1])-1)/2)))
                                    ftr_mid_swing = ftr_strike_solve[1][trunc((len(ftr_strike_solve[1])-1)/2)]
                                    ftr_avg_swing = sum(ftr_strike_solve[1])/len(ftr_strike_solve[1])
                                    ftr_max_swing = max(ftr_strike_solve[1])
                                else:
                                    ftr_mid_swing = -1
                                    ftr_avg_swing = -1
                                    ftr_max_swing = -1
                                if const.puck_y < const.rink_mid_y:
                                    ftr_window_bot = const.player.net_bottom
                                    ftr_window_top = window_bot - 2*(strike_window-1)
                                else:
                                    ftr_window_top = const.player.net_top
                                    ftr_window_bot = window_top + 2*(strike_window-1)
                                ftr_finish_puck_y = ftr_puck[1] + \
                                                (const.opponent_player.net_front -  ftr_puck[0])*tan(ftr_angle)
                                ftr_finish_puck_win_top = ftr_finish_puck_y - ftr_strike_dev
                                ftr_finish_puck_win_bot = ftr_finish_puck_y + ftr_strike_dev
                                print('predict wind-{0}, mid_swing-{1}, avg_swing-{2} max_s-{3} fin_y: {4}'.format(
                                                                         str(ftr_strike_window),
                                                                         str(ftr_mid_swing),
                                                                         str(round(ftr_avg_swing,1)),
                                                                         str(ftr_max_swing),
                                                                         str(round(ftr_finish_puck_y,1))))
                                print('predict dev: {4} f: top {0} bot {1} w: top {2} bot {3} swing: {5}'.format(
                                            str(round(ftr_finish_puck_win_top)),
                                            str(round(ftr_finish_puck_win_bot)),
                                            str(round(ftr_window_top)),
                                            str(round(ftr_window_bot)),
                                            str(round(ftr_strike_dev,1)),
                                            str(max_eff_swing))
                                        )
                        """
                        if strike_solve_pass[2] > strike_dev*1.2 and strike_solve_pass[2] > 2:
                            player.state = PlayerState.PUCKMAN_PASS_STRIKE
                            pass_target = get_net_position(player.me, const,strike_solve_pass,0)
                            player.target = PlayerTarget(pass_target[0],pass_target[1])
                            print('PASS STRIKE: dev {0} window {1}'.format(str(strike_dev),
                                                                           str(strike_solve_pass[2])))
                        elif count_enemies_around(player.me.x, player.me.y, const.player_radius*3,const) >1:
                            for h in const.world.hockeyists:
                                if h.teammate and h.type != HockeyistType.GOALIE \
                                    and h.state != HockeyistState.RESTING:
                                    if count_enemies_around(h.x, h.y, const.game.stick_length,const)==0:
                                        if abs(player.me.get_angle_to_unit(h)) < const.game.pass_sector/2*1.2*dex_mod\
                                                and player.me.get_distance_to_unit(h)  > const.game.stick_length*2\
                                                and count_enemies_around(h.x, h.y, const.player_radius*3,const) == 0:
                                            player.state = PlayerState.PUCKMAN_GIVEPASS
                                            print ('GIVE PASS!')
                                            player.target = PlayerTarget(h.x, h.y)
                                            players[h.teammate_index].state = PlayerState.FREE_TAKE_PUCK
                                            players[h.teammate_index].staged = True
                        elif player.state == PlayerState.PUCKMAN_GO_SIDE_POSITION:
                            #if check_pass
                            if strike_window > strike_dev*2:
                                player.state = PlayerState.PUCKMAN_TURN
                                player.target_state = PlayerState.PUCKMAN_GONET
                                player.target = PlayerTarget(*get_net_position(player.me, const, strike_solve))
                            elif near_point(player.me, player.target.x, player.target.y, const.game.puck_binding_range
                                                                                        +const.puck_radius*2):
                                player.state = PlayerState.PUCKMAN_TURN
                                player.target_state = PlayerState.PUCKMAN_GONET
                                player.target = PlayerTarget(*get_net_position(player.me, const, strike_solve))
                        elif player.state == PlayerState.PUCKMAN_GONET:
                            #player.target = PlayerTarget(*get_net_position(player.me, const))
                            #print(str(check_strike(player.me, const, puck_state, puck_state_next)))
                            #chk_strike = check_strike(player.me, const, puck_state, puck_state_next)
                            nearest_me = nearest_opponent(const.game, const.world,player.me.x, player.me.y,False)
                            # GIVE PASS TO FREE PLAYER
                            if strike_window >= strike_dev*2:
                                if (nearest_me is None
                                    or player.me.get_distance_to_unit(nearest_me) > const.game.stick_length*2)\
                                    and strike_dev > 5:
                                    chk_strike = 0
                                elif abs(finish_puck_y-get_net_position(player.me, const, strike_solve)[1]) > 2:
                                    player.state = PlayerState.PUCKMAN_TURN
                                    player.target_state = PlayerState.PUCKMAN_GONET
                                    player.target = PlayerTarget(*get_net_position(player.me, const, strike_solve))
                                    chk_strike = 2
                                else:
                                    chk_strike = 1
                            elif strike_window > strike_dev/4:
                                chk_strike = 0
                            else:
                                chk_strike = -1

                            if chk_strike == 1:
                                player.state = PlayerState.PUCKMAN_SWING
                                player.staged = False
                            elif chk_strike == -1:
                                player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                                player.target = PlayerTarget(*get_position_point(player.me, const))
                            else:
                                player.staged = True

                    elif player.state == PlayerState.PUCKMAN_TURN:
                        if abs(player.me.get_angle_to(player.target.x,player.target.y)) < pi/90:
                            player.state = player.target_state
                        if strike_solve_pass[2] >= strike_dev*1.2 and strike_solve_pass[2] > 2:
                            player.state = PlayerState.PUCKMAN_PASS_STRIKE
                            pass_target = get_net_position(player.me, const,strike_solve_pass,0)
                            player.target = PlayerTarget(pass_target[0],pass_target[1])
                            print('PASS STRIKE: dev {0} window {1}'.format(str(strike_dev),
                                                                           str(strike_solve_pass[2])))
                    elif player.state == PlayerState.PUCKMAN_TURN_ANGLE:
                        if player.target_angle < 0:
                            player.state = player.target_state

                    elif player.state == PlayerState.PUCKMAN_SWING:
                        #check_swing = swing_play(player.me, const, puck_state, puck_state_next)
                        #check_swing = swing_play_window(player.me, const, puck_state, puck_state_next)
                        """
                        print('Tick-{4} curr-{0}, next-{1}, c_swing-{2} swing-{3} state-{5}'.format(str(puck_state.hit_chance),
                                                                     str(puck_state_next.hit_chance),
                                                                     str(check_swing),
                                                                     str(player.me.swing_ticks),
                                                                     str(const.tick),
                                                                     str(player.me.state)))
                        """
                        p_angle = puck_angle(const.opponent_player,const.puck_owner, const)
                        """
                        print('NEW! Tick-{0} swings-{1} array-{2}'.format(str(const.tick),
                                                            str(p_angle[0]),
                                                            str(' '.join(str(x) for x in p_angle[1]))))
                        """

                        print('SWING! dev: {4} f: top {0} bot {1} w: top {2} bot {3} swing: {5}'.format(
                            str(round(finish_puck_win_top)),
                            str(round(finish_puck_win_bot)),
                            str(round(window_top)),
                            str(round(window_bot)),
                            str(round(strike_dev,1)),
                            str(player.me.swing_ticks))
                        )
                        nearest_me = nearest_opponent(const.game, const.world,player.me.x, player.me.y)
                        nearest_puck = nearest_opponent(const.game, const.world,const.puck_x, const.puck_y)
                        if  window_top + strike_dev < (finish_puck_win_top + finish_puck_win_bot)/2 < window_bot - strike_dev \
                                and (nearest_me is None
                                    or player.me.get_distance_to_unit(nearest_me) > const.game.stick_length+10
                                    or nearest_me.remaining_cooldown_ticks > 1
                                    or player.me.swing_ticks < avg_swing)\
                                and (True or nearest_puck is None
                                    or const.world.puck.get_distance_to_unit(nearest_puck) > const.game.stick_length*2+10
                                    or nearest_puck.remaining_cooldown_ticks > 1)\
                                and player.me.swing_ticks < avg_swing:
                            player.state = PlayerState.PUCKMAN_SWING
                            if player.me.swing_ticks == 0:
                                print('SWING STAT window: {0} goal: {1} bot: {2} target: {3}'.format(str(strike_solve[0]),
                                                                           str(window_top),
                                                                           str(window_bot),
                                                                           str(round(player.target.y))))
                        elif player.me.swing_ticks >= avg_swing:
                            if (nearest_me is None
                                    or player.me.get_distance_to_unit(nearest_me) > const.game.stick_length+10
                                    or nearest_me.remaining_cooldown_ticks > 1
                                    or player.me.swing_ticks < avg_swing)\
                                and (nearest_puck is None
                                    or const.world.puck.get_distance_to_unit(nearest_puck) > const.game.stick_length+10
                                    or nearest_puck.remaining_cooldown_ticks > 1) and player.me.swing_ticks < const.game.max_effective_swing_ticks:
                                player.state = PlayerState.PUCKMAN_SWING
                            else:
                                player.state = PlayerState.PUCKMAN_STRIKE
                                print(' SRKE! dev: {4} f: top {0} bot {1} w: top {2} bot {3} swing: '.format(
                                    str(round(finish_puck_win_top)),
                                    str(round(finish_puck_win_bot)),
                                    str(round(window_top)),
                                    str(round(window_bot)),
                                    str(round(strike_dev,1)),
                                    str(player.me.swing_ticks)
                                    ))
                        else:
                            if player.me.state == HockeyistState.SWINGING:
                                print('CANCEL!')
                                player.state = PlayerState.PUCKMAN_CANCEL_STRIKE
                            else:
                                player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                                player.target = PlayerTarget(*get_position_point(player.me, const))
                    elif player.state == PlayerState.PUCKMAN_STRIKE:
                        player.staged = True
                    elif player.state == PlayerState.PUCKMAN_CANCEL_STRIKE:
                        if player.me.state != HockeyistState.SWINGING:
                            player.state = PlayerState.PUCKMAN_GO_SIDE_POSITION
                            player.target = PlayerTarget(*get_position_point(player.me, const))

                    p_def = None
                    for p in players:
                        if p.state == PlayerState.DEFMAN_GODEF_PERMANENT:
                            p.target = PlayerTarget(const.def_x, const.def_y)
                            p_def = p
                    if p_def is None:
                        for p in players:
                            if p.state == PlayerState.DEFMAN_GODEF:
                                p.state = PlayerState.DEFMAN_GODEF_PERMANENT
                                p.tareget = PlayerTarget(const.def_x, const.def_y)
                                p.staged = True
                                break

            player.staged = False
