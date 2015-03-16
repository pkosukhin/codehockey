import traceback
import sys
from math import *
from Actions import *
from PuckManPlay import *
from DefPlay import *
from FreePlay import *
from CommonFunctions import *
from MathFunc import *
from Constants import *
from Strategy import *

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.World import World
from model.Hockeyist import Hockeyist
from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType
from model.Player import Player
from model.Unit import Unit

team_strategy = None
team_state = None

class MyStrategy:
    def __init__(self):
        self._world = None
        self._game = None
        self.team_strategy = team_strategy

    def move(self, me, world, game, move):
        global team_strategy
        global team_state
        self._world = world
        self._game = game
        self._me = me
        self._move = move
        puck_owner = get_puck_owner(world)
        if me.state != HockeyistState.RESTING:
        #try:
            const = WorldConstants(game, world, move)
            self._const = const

            #Strategy init
            if world.tick == 0:
                if team_strategy is None:
                    team_strategy = TeamStrategy((len(world.hockeyists) - 2)/2,const)
                    print('Tick:{0} ({1}) - created strategy'.format(world.tick, me.teammate_index))

            if team_strategy.staged_tick < world.tick:
                #print('\nTick:{0} ({1}) - staging strategy'.format(world.tick, me.teammate_index))
                team_strategy.main(const)
                team_strategy.staged_tick = world.tick
                curr_state = ' '.join([str(x.me.teammate_index) + ': '  + '{0}; '.format(x.state, round(x.target.x,1),round(x.target.y,1)) for x in team_strategy.players])
                curr_state_full = ' '.join([str(x.me.teammate_index) + ': '  + '{0} ({1};{2}); '.format(x.state,
                                                                                                        round(x.target.x),
                                                                                                        round(x.target.y)) for x in team_strategy.players])
                if team_state != curr_state:
                    team_state = curr_state
                    print('Tick: ' + str(world.tick) + ' States: ' + curr_state_full)
           # print('Tick {0} mystate: {1} my_index {2}'.format(world.tick,me.state,me.teammate_index))
            my_strategy = team_strategy.find_my_strategy(me.teammate_index)
            my_state = my_strategy.state
            ### DEF ###

            ### PANIC STRATEGY ON 0-0 ###
            puck_dist = hypot(world.puck.x - const.opponent_player.net_front, world.puck.y - const.rink_mid_y)
            if (const.world.puck.owner_hockeyist_id == me.id
                    and const.tick >= const.main_period_len - 50
                    and const.player.goal_count == 0
                    and const.opponent_player.goal_count == 0
                    and const.puck_owner is not None
                    and const.puck_owner.id == me.id):
                    print('PANIC!')
                    force_move(move, me, game, const.opponent_player.net_front,
                                                const.rink_mid_y,1)
                    if  me.state != HockeyistState.SWINGING and\
                        (count_enemies_around(me.x, me.y, game.stick_length + 10, const) > 0
                            or count_enemies_around(world.puck.x, world.puck.y, game.stick_length + 10, const) > 0)\
                        and abs(me.get_angle_to(const.opponent_player.net_front,
                                                const.rink_mid_y)) < game.pass_sector/2:
                        move.action = ActionType.PASS
                        move.pass_power = 1
                        move.pass_angle = me.get_angle_to(const.opponent_player.net_front, const.rink_mid_y)
                        return

                    if abs(me.get_angle_to(const.opponent_player.net_front,const.rink_mid_y))<pi/60:
                        if (count_enemies_around(me.x, me.y, game.stick_length + 10, const) == 0
                            and count_enemies_around(world.puck.x, world.puck.y, game.stick_length + 10, const) == 0):
                                move.action = ActionType.SWING

                    if (me.state == HockeyistState.SWINGING and (me.swing_ticks >= game.max_effective_swing_ticks
                        or count_enemies_around(me.x, me.y, game.stick_length*1.3, const) > 0
                        or count_enemies_around(world.puck.x, world.puck.y, game.stick_length*1.3, const) > 0)
                        and const.tick >= const.main_period_len-puck_dist/25):
                        move.action = ActionType.STRIKE
                        return
            ### END PANIC STRATEGY ON 0-0 ###
            if (const.tick >= const.main_period_len-puck_dist/25 and
                const.opponent_player.net_top +50<=
                    me.y - (const.opponent_player.net_front-me.x)*tan(me.angle)
                        <= const.opponent_player.net_top - 50)\
                and abs(me.get_angle_to_unit(world.puck)) < game.stick_sector/2:
                move.action = ActionType.STRIKE
                print('PANIC STRIKE!: {0}'.format(str(round(me.y - (const.opponent_player.net_front-me.x)*tan(me.angle)))))
                return


            if my_state == PlayerState.PUCKMAN_PANIC:
                force_move(move, me, game, const.opponent_player.net_front, const.rink_mid_y,1)
                if abs(me.get_angle_to(const.opponent_player.net_front, const.rink_mid_y))<game.pass_sector/2:
                    move.action = ActionType.PASS
                    move.pass_power = 1
                    move.pass_angle = me.get_angle_to(const.opponent_player.net_front, const.rink_mid_y)
                    return
            if my_state == PlayerState.DEFMAN_GODEF:
                #move.turn = -pi
                go_def(move, me, game, my_strategy.target.x, my_strategy.target.y, const)
            if my_state == PlayerState.DEFMAN_GODEF_PERMANENT:
                #move.turn = -pi
                stay_def(move, me, game, my_strategy.target.x, my_strategy.target.y, const)
                if me.get_angle_to_unit(world.puck) <= game.stick_sector/2 and \
                                world.puck.get_distance_to(my_strategy.target.x, my_strategy.target.y) <game.stick_length*3\
                        and const.puck_owner is None:
                    force_move(move, me, game, *pred_unit_move(world.puck, 4), slowdown=1)
                    move.action = ActionType.TAKE_PUCK
            elif my_state == PlayerState.DEFMAN_STAY:
                go_def(move, me, game, const.def_x, const.def_y, const)
            elif my_state == PlayerState.DEFMAN_DEFEND:
                go_def(move, me, game, team_strategy.players[me.teammate_index].target.x,
                                        team_strategy.players[me.teammate_index].target.y, const)
            elif my_state == PlayerState.DEFMAN_PREVENT:
                prevent(move, me, game, const)
            elif my_state == PlayerState.FREE_TAKE_PUCK:
                take_puck(move, me, game, world)
            elif my_state == PlayerState.FREE_ATTACK_DEF:
                attack_unit(move,me,game,nearest_opponent(game,world,const.opponent_player.net_front,const.rink_mid_y,False))
            elif my_state == PlayerState.DEFMAN_TAKE_PUCK:
                take_puck(move, me, game, world)
                strtake_puck(move, me, game, const, const.player)
            elif my_state == PlayerState.FREE_ATTACK_PUCK:
                attack_unit(move, me, game,world.puck)
                me_target_y =  me.y - (me.x-const.player.net_front)*tan(me.angle)
                if const.player.net_top <= me_target_y <= const.player.net_bottom\
                    and move.action == ActionType.STRIKE:
                    move.action = ActionType.TAKE_PUCK
            elif my_state == PlayerState.DEFMAN_HELP_OWNER:
                attack_unit(move, me, game,team_strategy.players[me.teammate_index].target_unit)
            elif my_state == PlayerState.PUCKMAN_GO_SIDE_POSITION:

                go_position(move, me, const,
                            team_strategy.players[me.teammate_index].target.x,
                            team_strategy.players[me.teammate_index].target.y)
                """
                cool_move(move, me, game, const,
                            team_strategy.players[me.teammate_index].target.x,
                            team_strategy.players[me.teammate_index].target.y)
                """
            elif my_state == PlayerState.PUCKMAN_GIVEPASS:
                move.action = ActionType.PASS
                move.pass_angle = me.get_angle_to(my_strategy.target.x, my_strategy.target.y)
                move.pass_power = me.get_distance_to(my_strategy.target.x, my_strategy.target.y)/const.rink_len
            elif my_state == PlayerState.PUCKMAN_GONET:
                go_position(move, me, const,
                            team_strategy.players[me.teammate_index].target.x,
                            team_strategy.players[me.teammate_index].target.y)
            elif my_state == PlayerState.PUCKMAN_TURN:
                move.speed_up = 0
                move.turn = me.get_angle_to(team_strategy.players[me.teammate_index].target.x,
                                            team_strategy.players[me.teammate_index].target.y)
            elif my_state == PlayerState.PUCKMAN_SWING:
                move.action = ActionType.SWING
                return
            elif my_state == PlayerState.PUCKMAN_STRIKE:
                move.action = ActionType.STRIKE
            elif my_state == PlayerState.PUCKMAN_PASS_STRIKE:
                move.turn = me.get_angle_to(team_strategy.players[me.teammate_index].target.x,
                            team_strategy.players[me.teammate_index].target.y)
                puck_angle = get_angle(const.puck_x,const.puck_y,team_strategy.players[me.teammate_index].target.x,
                            team_strategy.players[me.teammate_index].target.y)
                if abs(puck_angle-me.angle) <=game.pass_sector/2*me.dexterity/100*(0.75+0.25*me.stamina/game.hockeyist_max_stamina):
                    move.action = ActionType.PASS
                    move.pass_power = 1
                    move.pass_angle = puck_angle-me.angle
                    print('PASS STRIKE! ang {0} trg {1} {2}'.format(str(round((puck_angle-me.angle)/pi*180,1)),
                                                                    str(round(team_strategy.players[me.teammate_index].target.x,1)),
                                                                    str(round(team_strategy.players[me.teammate_index].target.y,1))))
            elif my_state == PlayerState.PUCKMAN_CANCEL_STRIKE:
                move.action = ActionType.CANCEL_STRIKE
                return
            elif my_state == PlayerState.GO_REST:
                if abs(me.x-const.player.net_front) < const.rink_len/2:
                    force_move(move, me, game, me.x, const.game.rink_top,1)
                else:
                    force_move(move, me, game, (const.rink_mid_x + const.player.net_front)/2, const.game.rink_top,1)
                if abs(me.x-const.player.net_front) < const.rink_len/2\
                                and abs(me.y - const.game.rink_top) <= const.game.substitution_area_height\
                        and me.remaining_cooldown_ticks == 0 and me.remaining_knockdown_ticks == 0:
                    stop_me(move, me, game)
                    if speed(me) < game.max_speed_to_allow_substitute:
                        sub_player = get_rested_player(team_strategy.players)
                        team_strategy.players[me.teammate_index].state = PlayerState.REST
                        new_state = PlayerState.DEFMAN_GODEF_PERMANENT
                        for p in team_strategy.players:
                            if p.state == PlayerState.DEFMAN_GODEF_PERMANENT:
                                new_state = PlayerState.FREE_TAKE_PUCK
                        team_strategy.players[sub_player].state = new_state
                        move.action = ActionType.SUBSTITUTE
                        print('Me index {0} sub index {1}'.format(me.teammate_index, sub_player ))
                        move.teammate_index = sub_player
                        return
            elif my_state == PlayerState.REST_FUNNY:
                move.turn = pi
                move.speed_up = -0.5

        """
        except:
            print('Something happend during main phase')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
        """

