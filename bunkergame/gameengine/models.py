from __future__ import annotations

import functools
from uuid import uuid4, UUID
from django.db import models
from collections import Counter
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest

from .utils import lobby_rules, user_rules
from .utils.helpers import game_logger, get_random_value, generate_name, ru_game_status


class GameStatusesEnum(models.IntegerChoices):
    NOT_CREATED = 0
    CREATED = 1
    IN_PROGRESS = 2
    TURNING = 3
    VOTING = 4
    END = 5

class GameUser(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    game_id = models.ForeignKey("GameEngine", on_delete=models.CASCADE)
    game_number = models.IntegerField(default=0)
    game_name = models.CharField(max_length=50, default='')
    profession = models.IntegerField()
    health = models.IntegerField()
    bio_character = models.IntegerField()
    additional_skills = models.IntegerField()
    hobby = models.IntegerField()
    spec_condition = models.IntegerField()
    items = models.IntegerField()

    is_profession_visible = models.BooleanField(default=False)
    is_health_visible = models.BooleanField(default=False)
    is_bio_character_visible = models.BooleanField(default=False)
    is_additional_skills_visible = models.BooleanField(default=False)
    is_hobby_visible = models.BooleanField(default=False)
    is_spec_condition_visible = models.BooleanField(default=False)
    is_items_visible = models.BooleanField(default=False)

    is_in_game = models.BooleanField(default=False)
    vote_id = models.UUIDField(default=uuid4, editable=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_ru_dict(self,) -> dict:
        return {
            "game_id": self.game_id,
            "game_number": self.game_number,
            "game_name": self.game_name,
            "profession": user_rules.profession[self.profession],
            "health": user_rules.health[self.health],
            "bio_character": user_rules.bio_character[self.bio_character],
            "additional_skills": user_rules.additional_skills[self.additional_skills],
            "hobby": user_rules.hobby[self.hobby],
            "spec_condition": user_rules.spec_condition[self.spec_condition],
            "items": user_rules.items[self.items],
            "username": self.account_id.username,
            "is_profession_visible": self.is_profession_visible,
            "is_health_visible": self.is_health_visible,
            "is_bio_character_visible": self.is_bio_character_visible,
            "is_additional_skills_visible": self.is_additional_skills_visible,
            "is_hobby_visible": self.is_hobby_visible,
            "is_spec_condition_visible": self.is_spec_condition_visible,
            "is_items_visible": self.is_items_visible
            }
        
    def create(self, game_id:GameEngine, user:User, game_number:int, existed_users:list[GameUser]):
        self.user_id = uuid4()
        self.game_id = game_id
        self.account_id = user
        self.game_number = game_number
        self.game_name = generate_name()
        self.profession = get_random_value(max_val=len(user_rules.profession) - 1, excepted_values = [user.profession for user in existed_users])
        self.health = get_random_value(max_val=len(user_rules.health) - 1, excepted_values = [user.health for user in existed_users])
        self.bio_character = get_random_value(max_val=len(user_rules.bio_character) - 1, excepted_values = [user.bio_character for user in existed_users])
        self.additional_skills = get_random_value(max_val=len(user_rules.additional_skills) - 1, excepted_values = [user.additional_skills for user in existed_users])
        self.hobby = get_random_value(max_val=len(user_rules.hobby) - 1, excepted_values = [user.hobby for user in existed_users])
        self.spec_condition = get_random_value(max_val=len(user_rules.spec_condition) - 1, excepted_values = [user.spec_condition for user in existed_users])
        self.items = get_random_value(max_val=len(user_rules.items) - 1, excepted_values = [user.items for user in existed_users])
        self.is_in_game = True
        self.save()
    
    def regenerate_user(self, existed_users:list[GameUser]):
        self.game_name = generate_name()
        self.profession = get_random_value(max_val=len(user_rules.profession) - 1, excepted_values = [user.profession for user in existed_users])
        self.health = get_random_value(max_val=len(user_rules.health) - 1, excepted_values = [user.health for user in existed_users])
        self.bio_character = get_random_value(max_val=len(user_rules.bio_character) - 1, excepted_values = [user.bio_character for user in existed_users])
        self.additional_skills = get_random_value(max_val=len(user_rules.additional_skills) - 1, excepted_values = [user.additional_skills for user in existed_users])
        self.hobby = get_random_value(max_val=len(user_rules.hobby) - 1, excepted_values = [user.hobby for user in existed_users])
        self.spec_condition = get_random_value(max_val=len(user_rules.spec_condition) - 1, excepted_values = [user.spec_condition for user in existed_users])
        self.items = get_random_value(max_val=len(user_rules.items) - 1, excepted_values = [user.items for user in existed_users])
        self.is_in_game = True
        self.save()

    #FIXME need to fix
    def make_vote(self, voted_user_id: UUID) -> None:
        if self.user_id == voted_user_id:
            return
        
        #TODO need to check in game users
        
        self.vote_id = voted_user_id
        game_logger(f'Player {self.user_id} voted for {voted_user_id}')


class GameEngine(models.Model):

    game_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game_name = models.CharField(max_length=50, default='')
    map_descriptions = models.IntegerField(null=True)
    bunker_descritions = models.IntegerField(null=True)
    user_count = models.IntegerField(null=True)
    turn = models.IntegerField(default=0)
    game_status = models.IntegerField(choices=GameStatusesEnum, default=GameStatusesEnum.NOT_CREATED)
    
    owner_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def lobby_status_check(status:GameStatusesEnum):
        def out_wrap(func:callable):
            functools.wraps(func)
            def wrapper(self, *arg, **kwarg):
                if self.game_status == status:
                    return func(self, *arg, **kwarg)
                else:
                    raise BadRequest(f"Current status is {self.game_status} needed {status}")
            return wrapper
        return out_wrap
    
    def create_empty_game(self, owner_id:User, game_name:str, user_count=6):
        game_id = uuid4()
        self.game_id = game_id
        self.owner_id = owner_id
        self.game_name = game_name
        self.user_count = user_count
        self.game_status = GameStatusesEnum.NOT_CREATED
        self.map_descriptions = get_random_value(max_val=len(lobby_rules.map_descriptions) - 1)
        self.bunker_descritions = get_random_value(max_val=len(lobby_rules.bunker_description) - 1)
        self.save()
        
    def get_ru_map_descriptions(self,) -> str:
        return lobby_rules.map_descriptions[self.map_descriptions]
    
    def get_ru_bunker_descriptions(self,) -> str:
        return lobby_rules.bunker_description[self.bunker_descritions]
    
    def get_game_info(self,):
        return {
            "game_id":str(self.game_id),
            "owner_id":str(self.owner_id),
            "game_name":self.game_name,
            "user_count":self.user_count,
            "game_status":ru_game_status[self.game_status],
            "map_descriptions":self.get_ru_map_descriptions(),
            "bunker_descritions":self.get_ru_bunker_descriptions(),
        }
    
    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def join_user(self, user:User) -> None:
        existed_user = GameUser.objects.filter(game_id=self.game_id).all()
        if len(existed_user) < self.user_count:
            GameUser().create(self, user, len(existed_user)+1, existed_user)
            game_logger(f'GameUser for User {user} CREATED')
        else:
            self.lobby_created()

    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def remove_user(self, user:User) -> None:
        deleted_user = GameUser.objects.filter(account_id=user, game_id=self.game_id).delete()
        print(deleted_user)
        game_logger(f'GameUser for User {user} DELETED')

    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def regenerate_user(self, user:User) -> None:
        existed_user = GameUser.objects.filter(game_id=self.game_id).all()
        for ex_user in existed_user:
            if ex_user.account_id.username == user.username:
                ex_user.regenerate_user()
                game_logger(f'GameUser for User {user} REGENERATED')

    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def lobby_created(self) -> None:
        self.game_status = GameStatusesEnum.CREATED
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.CREATED}')
    
    #FIXME need to fix
    @lobby_status_check(GameStatusesEnum.CREATED)
    def start_game(self,) -> None:
        self.game_status = GameStatusesEnum.IN_PROGRESS
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.IN_PROGRESS}')

    #FIXME need to fix
    @lobby_status_check(GameStatusesEnum.IN_PROGRESS)
    def make_turn(self,) -> None:
        self.game_status = GameStatusesEnum.TURNING
        self._turn += 1
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.TURNING}')
    
    #FIXME need to fix
    @lobby_status_check(GameStatusesEnum.TURNING)
    def end_turn(self,) -> None:
        self.game_status = GameStatusesEnum.VOTING
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.VOTING}')

    #FIXME need to fix
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

        for user in self.get_all_users():
            user.vote_id = None

        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.IN_PROGRESS}')

        if len(self.get_users_in_game()) == self._user_count/2:
            return self.game_ended()
            
        self.game_status = GameStatusesEnum.IN_PROGRESS

    #FIXME need to fix
    @lobby_status_check(GameStatusesEnum.VOTING)
    def game_ended(self,) -> str:
        nn_res = 'GAME ENDED TEMPLATE'
        self.game_status = GameStatusesEnum.END
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.END}')
        return nn_res


    #FIXME need to fix
    @lobby_status_check(GameStatusesEnum.VOTING)
    def kick_from_game_by_id(self, user_id:UUID) -> None:
        for user in self.get_all_users():
            if user.user_id == user_id:
                user.is_in_game = False
                game_logger(f'GameEngine {self.game_id} player {user.user_id} kicked')