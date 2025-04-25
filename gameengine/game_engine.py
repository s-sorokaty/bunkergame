from __future__ import annotations
import random
import logging
import functools
from enum import Enum
from typing import Optional
from uuid import uuid4, UUID
from collections import Counter
from dataclasses import dataclass

import user_rules, exceptions, lobby_rules

class GameStatusesEnum(Enum):
    NOT_CREATED = 0
    
    CREATED = 1
    IN_PROGRESS = 2

    TURNING = 3
    VOTING = 4

    END = 5



def get_random_value(min_val=0, max_val=29, excepted_values = None) -> int:
    rand_value = random.randint(min_val, max_val)

    if excepted_values:
        while rand_value in excepted_values:
            rand_value = random.randint(min_val, max_val)
        return rand_value
    else:    
        return rand_value 

def game_logger(action:str):
    #logging.basicConfig(level=logging.INFO)
    logging.info(f"LOGGED ACTIONS: {action}")


@dataclass(repr=True)
class User():
    user_id: UUID
    profession:int
    health:int
    bio_character:int
    additional_skills:int
    hobby:int
    spec_condition:int
    items:int
    is_in_game:bool = False
    vote_id:Optional[UUID] = None

    def __repr__(self,) -> str:
        return f"""
            Профессия: {user_rules.profession[self.profession]}
            Здоровье: {user_rules.health[self.health]}
            БИО: {user_rules.bio_character[self.bio_character]}
            ДОП навыки: {user_rules.additional_skills[self.additional_skills]}
            Хобби: {user_rules.hobby[self.hobby]}
            Особые условия: {user_rules.spec_condition[self.spec_condition]}
            Предметы: {user_rules.items[self.items]}
            """
    
    def __init__(self, game_id:UUID, users:list[User]):
        self.user_id = uuid4()
        self.profession = get_random_value(max_val=len(user_rules.profession) - 1, excepted_values = [user.profession for user in users])
        self.health = get_random_value(max_val=len(user_rules.health) - 1, excepted_values = [user.health for user in users])
        self.bio_character = get_random_value(max_val=len(user_rules.bio_character) - 1, excepted_values = [user.bio_character for user in users])
        self.additional_skills = get_random_value(max_val=len(user_rules.additional_skills) - 1, excepted_values = [user.additional_skills for user in users])
        self.hobby = get_random_value(max_val=len(user_rules.hobby) - 1, excepted_values = [user.hobby for user in users])
        self.spec_condition = get_random_value(max_val=len(user_rules.spec_condition) - 1, excepted_values = [user.spec_condition for user in users])
        self.items = get_random_value(max_val=len(user_rules.items) - 1, excepted_values = [user.items for user in users])
        self.is_in_game = True

    
    def make_vote(self, voted_user_id: UUID) -> None:
        if self.user_id == voted_user_id:
            return
        
        #TODO need to check in game users
        
        self.vote_id = voted_user_id
        game_logger(f'Player {self.user_id} voted for {voted_user_id}')

    
class GameEngine():
    _game_id:UUID = None
    _map_descriptions: int = None
    _bunker_descritions: int = None
    _user_count:int  = None
    _users:list[User]
    _turn: int
    game_status: GameStatusesEnum

    def __init__(self, user_count=6):
        self._game_id = uuid4()
        self._user_count = user_count
        self._users = []   
        self.game_status = GameStatusesEnum.NOT_CREATED

    @property
    def map_descriptions(self,):
        return self._map_descriptions

    @property
    def bunker_descritions(self,):
        return self._bunker_descritions    
    
    #Wrapper checking lobby created
    def lobby_status_check(status:GameStatusesEnum):
        def out_wrap(func:callable):
            functools.wraps(func)
            def wrapper(self, *arg, **kwarg):
                if self.game_status == status:
                    return func(self, *arg, **kwarg)
                else:
                    raise exceptions.LobbyStatusCheckMismatch(f"Current status is {self.game_status} needed {status}")
            return wrapper
        return out_wrap
    
    def __repr__(self,):
        if self._map_descriptions and self._bunker_descritions:
            return f"""
                Описание карты: {lobby_rules.map_descriptions[self._map_descriptions]}
                Описание бункера:{lobby_rules.bunker_description[self._bunker_descritions]} 
                """
        else:
            return ""
        
    def get_user_by_id(self, user_id:UUID) -> Optional[User]:
        finded_user = None
        for user in self._users:
            if user.user_id == user_id:
                finded_user = user
        return finded_user
    
    def get_users_in_game(self,) -> list[User]:
        return [user for user in self._users if user.is_in_game]
    
    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def create_lobby(self,) -> None:
        for _ in range(self._user_count):
            user = User(self._game_id, self._users)
            self._users.append(user)
            game_logger(f'User {user.user_id} CREATED')
        self._map_descriptions = get_random_value(max_val=len(lobby_rules.map_descriptions) - 1)
        self._bunker_descritions = get_random_value(max_val=len(lobby_rules.bunker_description) - 1)

        self.game_status = GameStatusesEnum.CREATED
        self._turn = 0
        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.CREATED}')
    
    @lobby_status_check(GameStatusesEnum.CREATED)
    def start_game(self,) -> None:
        self.game_status = GameStatusesEnum.IN_PROGRESS
        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.IN_PROGRESS}')

    @lobby_status_check(GameStatusesEnum.IN_PROGRESS)
    def make_turn(self,) -> None:
        self.game_status = GameStatusesEnum.TURNING
        self._turn += 1
        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.TURNING}')
    
    @lobby_status_check(GameStatusesEnum.TURNING)
    def end_turn(self,) -> None:
        self.game_status = GameStatusesEnum.VOTING
        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.VOTING}')


    @lobby_status_check(GameStatusesEnum.VOTING)
    def end_vote(self,) -> None | str:
        if self._turn > 1:
            all_votes:list[tuple[UUID, int]] = Counter([user.vote_id for user in self.get_users_in_game() if user.vote_id]).most_common()

            if len(all_votes):
                nominante_to_kick = [all_votes[0]]
                max_voted = all_votes[0][1]
                print(all_votes)

                for vote_id, vote_count in all_votes[1:]:
                    if max_voted == vote_count:
                        nominante_to_kick.append((vote_id,vote_count))
                all_voted_idx = 0
                if len(nominante_to_kick) > 1:
                    all_voted_idx = get_random_value(0, 1)
                
                self.kick_from_game_by_id(nominante_to_kick[all_voted_idx][0])

        for user in self._users:
            user.vote_id = None

        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.IN_PROGRESS}')

        if len(self.get_users_in_game()) == self._user_count/2:
            return self.game_ended()
            
        self.game_status = GameStatusesEnum.IN_PROGRESS
            
    @lobby_status_check(GameStatusesEnum.VOTING)
    def game_ended(self,) -> str:
        nn_res = 'GAME ENDED TEMPLATE'
        self.game_status = GameStatusesEnum.END
        game_logger(f'GameEngine {self._game_id} status {GameStatusesEnum.END}')
        return nn_res

    @lobby_status_check(GameStatusesEnum.END)
    def restart_game(self,):
        self.__init__(6)    

    @lobby_status_check(GameStatusesEnum.VOTING)
    def kick_from_game_by_id(self, user_id:UUID) -> None:
        for user in self._users:
            if user.user_id == user_id:
                user.is_in_game = False
                game_logger(f'GameEngine {self._game_id} player {user.user_id} kicked')

        