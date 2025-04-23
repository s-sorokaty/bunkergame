import random
import functools
from datetime import datetime
from dataclasses import dataclass

import user_rules, exceptions



def get_random_value(min_val=0, max_val=29, excepted_values = None) -> int:
    rand_value = random.randint(min_val, max_val)
    if rand_value == 30:
        print(rand_value)
    if excepted_values:
        while rand_value in excepted_values:
            rand_value = random.randint(min_val, max_val)
        return rand_value
    else:    
        return rand_value 


@dataclass(repr=True)
class User():
    profession:int
    health:int
    bio_character:int
    additional_skills:int
    hobby:int
    spec_condition:int
    items:int

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

class GameEnigine():
    user_count:int
    users:list[User]
    is_created:bool

    def __init__(self, user_count=6):
        self.user_count = user_count
        self.users = []   
        self.is_created = False
    
    #Wrapper checking lobby created
    def lobby_created_check(func):
        def wrapper(self, *arg, **kwarg):
            if not self.is_created:
                return func(self, *arg, **kwarg)
            else:
                raise exceptions.LobbyAlreadyCreated
        return wrapper
    
    @lobby_created_check
    def _create_user(self,) -> User:
        profession = [user.profession for user in self.users]
        health = [user.health for user in self.users]
        bio_character = [user.bio_character for user in self.users]
        additional_skills = [user.additional_skills for user in self.users]
        hobby = [user.hobby for user in self.users]
        spec_condition = [user.spec_condition for user in self.users]
        items = [user.items for user in self.users]

        return User(
            get_random_value(max_val=len(user_rules.profession) - 1, excepted_values = profession),
            get_random_value(max_val=len(user_rules.health) - 1, excepted_values = health),
            get_random_value(max_val=len(user_rules.bio_character) - 1, excepted_values = bio_character),
            get_random_value(max_val=len(user_rules.additional_skills) - 1, excepted_values = additional_skills),
            get_random_value(max_val=len(user_rules.hobby) - 1, excepted_values = hobby),
            get_random_value(max_val=len(user_rules.spec_condition) - 1, excepted_values = spec_condition),
            get_random_value(max_val=len(user_rules.items) - 1, excepted_values = items),
        )
    
    
    
    @lobby_created_check
    def create_lobby(self,) -> None:
        for _ in range(self.user_count):
            user = self._create_user()
            print(user)
            self.users.append(user)
        self.is_created = True
        
        

game = GameEnigine()
game.create_lobby()

print(game.users)
