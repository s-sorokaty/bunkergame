from __future__ import annotations
import random
import logging
from enum import Enum
from typing import Optional
from uuid import uuid4, UUID
from dataclasses import dataclass

import user_rules

def game_logger(action:str):
    #logging.basicConfig(level=logging.INFO)
    logging.info(f"LOGGED ACTIONS: {action}")


def get_random_value(min_val=0, max_val=29, excepted_values = None) -> int:
    rand_value = random.randint(min_val, max_val)

    if excepted_values:
        while rand_value in excepted_values:
            rand_value = random.randint(min_val, max_val)
        return rand_value
    else:    
        return rand_value 

class GameStatusesEnum(Enum):
    NOT_CREATED = 0
    
    CREATED = 1
    IN_PROGRESS = 2

    TURNING = 3
    VOTING = 4

    END = 5

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
        self.game_id = game_id
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
