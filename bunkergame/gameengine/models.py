from __future__ import annotations

import functools
from uuid import uuid4, UUID
from django.db import models
from collections import Counter
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .utils import lobby_rules, user_rules, exceptions, nn_request
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
    game_name = models.TextField(max_length=50, default='')

    age = models.IntegerField(default=-1)
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

    is_showed_stat_at_turn = models.BooleanField(default=False)

    is_in_game = models.BooleanField(default=True)
    vote_id = models.UUIDField(editable=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_ru_dict(self,) -> dict:
        return {
            "user_id": str(self.user_id),
            "game_id": str(self.game_id),
            "game_number": self.game_number,
            "game_name": self.game_name,
            "profession": user_rules.profession[self.profession],
            "health": user_rules.health[self.health],
            "bio_character": str(self.age) + " лет, " + user_rules.bio_character[self.bio_character],
            "additional_skills": user_rules.additional_skills[self.additional_skills],
            "hobby": user_rules.hobby[self.hobby],
            "spec_condition": user_rules.spec_condition[self.spec_condition],
            "items": user_rules.items[self.items],
            "username": self.account_id.username,
            "is_in_game":self.is_in_game,
            "is_profession_visible": self.is_profession_visible,
            "is_health_visible": self.is_health_visible,
            "is_bio_character_visible": self.is_bio_character_visible,
            "is_additional_skills_visible": self.is_additional_skills_visible,
            "is_hobby_visible": self.is_hobby_visible,
            "is_spec_condition_visible": self.is_spec_condition_visible,
            "is_items_visible": self.is_items_visible
            }
    
    @staticmethod
    def get_stat_dict() -> dict:
        return {
            "profession":"is_profession_visible",
            "health":"is_health_visible",
            "bio_character":"is_bio_character_visible",
            "additional_skills":"is_additional_skills_visible",
            "hobby":"is_hobby_visible",
            "spec_condition":"is_spec_condition_visible",
            "items":"is_items_visible",
        }
    
    def as_nn_promt(self,) -> str:
        return f"""
            Имя: {self.game_name}
            Профессия: {user_rules.profession[self.profession]}
            Здоровье: {user_rules.health[self.health]}
            Биология: {str(self.age) + " лет, " + user_rules.bio_character[self.bio_character]}
            Дополнительные навыки: {user_rules.additional_skills[self.additional_skills]}
            Хобби: {user_rules.hobby[self.hobby]}
            Особые условия: {user_rules.spec_condition[self.spec_condition]}
            Вещи: {user_rules.items[self.items]}
            """   

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
        self.age = get_random_value(min_val=16, max_val=70)
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
        self.age = get_random_value(min_val=16, max_val=70)
        self.save()

    def show_stat(self, statname:str):
        if statname in list(self.get_stat_dict().keys()):
            visible_method = getattr(self, self.get_stat_dict()[statname])
            if visible_method: raise exceptions.StatAlreadyShowed
            setattr(self, self.get_stat_dict()[statname], True)
                        
            self.is_showed_stat_at_turn = True
            self.save()
        else:
            raise AttributeError(f"Stat '{statname}' does not exist")  # Обработка случая, если статистика не найдена
    
    def end_user_turn(self,):
        self.is_showed_stat_at_turn = False
        self.save()
       
    @staticmethod
    def get_user_in_game(game_id:UUID):
        return GameUser.objects.filter(game_id=game_id, is_in_game=True).all()
    
    def make_vote(self, voted_user_id: UUID) -> None:
        self.vote_id = voted_user_id
        self.save()
        game_logger(f'Player {self.user_id} voted for {voted_user_id}')
    
    def kick_from_game(self,) -> None:
        self.is_in_game = False
        self.save()


class GameEngine(models.Model):

    game_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    game_name = models.CharField(max_length=50, default='')
    map_descriptions = models.IntegerField(null=True)
    bunker_descritions = models.IntegerField(null=True)
    user_count = models.IntegerField(null=True)
    turn = models.IntegerField(default=0)
    user_number_turn = models.IntegerField(default=0)
    ending = models.CharField(max_length=50, default='Конец пока неизвестен') 

    game_status = models.IntegerField(choices=GameStatusesEnum, default=GameStatusesEnum.NOT_CREATED)

    owner_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def lobby_status_check(status:GameStatusesEnum):
        def out_wrap(func:callable):
            @functools.wraps(func)
            def wrapper(self, *arg, **kwarg):
                if self.game_status == status:
                    return func(self, *arg, **kwarg)
                else:
                    raise exceptions.LobbyStatusCheckMismatch(f"Status error {self.game_status} needed {status}")
            return wrapper
        return out_wrap
    
    def create_game(self, owner_id:User, game_name:str, user_count=4):
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
            "ending": self.ending,
            "bunker_descritions":self.get_ru_bunker_descriptions(),
            "turn":self.turn,
            "user_number_turn":self.user_number_turn,
            "all_votes": self.get_all_votes(),
        }
    
    def as_nn_promt(self,) -> str:
        return f"""
            Описание бункера: {self.map_descriptions}
            Описание карты: {self.map_descriptions}
            """   
    
    @lobby_status_check(GameStatusesEnum.TURNING)
    def set_next_game_number_turn(self, game_number:int=None) -> None:
        if game_number != None:
            self.user_number_turn = game_number
            self.save()
            return
        
        game_user = GameUser.get_user_in_game(self.game_id).order_by('game_number')
        game_user = game_user.filter(game_number__gt=self.user_number_turn)

        if game_user:
            self.user_number_turn = game_user[0].game_number
        else:
            self.user_number_turn = 0
        self.save()

    @lobby_status_check(GameStatusesEnum.TURNING)
    def show_stat(self, statname:str, game_user:GameUser) -> None:
        if game_user.is_showed_stat_at_turn: raise exceptions.StatAlreadyShowed
        if self.user_number_turn == game_user.game_number:
            game_user.show_stat(statname)
            game_logger(f'GameUser {game_user.user_id} show {statname}')
        else:
            raise exceptions.WrongPlayerTurn
        
    @lobby_status_check(GameStatusesEnum.TURNING)
    def end_user_turn(self, game_user:GameUser) -> None:
        if not game_user.is_showed_stat_at_turn: raise exceptions.StatNotShowed
        if self.user_number_turn == game_user.game_number:
            game_user.end_user_turn()
            self.set_next_game_number_turn()

            if self.user_number_turn == 0:
                self.end_turn()
    
            game_logger(f'GameUser {game_user.user_id} status end_user_turn')
        else:
            raise exceptions.WrongPlayerTurn
        
    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def join_user(self, user:User) -> None:
        existed_user = GameUser.objects.filter(game_id=self.game_id).all()
        
        if existed_user.count() < self.user_count:
            GameUser().create(self, user, \
                              get_random_value(min_val=1, max_val=existed_user.count()+1, excepted_values=[exist_user.game_number for exist_user in existed_user]), existed_user)
            game_logger(f'GameUser for User {user} CREATED')

        if existed_user.count() + 1  == self.user_count:
            self.__lobby_created()

    def remove_user(self, user:User) -> None:
        game_user = GameUser.objects.filter(account_id=user, game_id=self.game_id).first()
        game_user.kick_from_game()

        game_logger(f'GameUser for User {user} DELETED')
        if len(GameUser.objects.filter(game_id=self.game_id, is_in_game=True).all()) == 0:
            self.delete()

    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def regenerate_user(self, user:User) -> None:
        existed_user = GameUser.objects.get(account_id=user, game_id=self.game_id)
        existed_user.regenerate_user()
        game_logger(f'GameUser for User {user} REGENERATED')

    @lobby_status_check(GameStatusesEnum.NOT_CREATED)
    def __lobby_created(self) -> None:
        self.game_status = GameStatusesEnum.CREATED
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.CREATED}')


    @lobby_status_check(GameStatusesEnum.CREATED)
    def start_game(self,) -> None:
        self.game_status = GameStatusesEnum.IN_PROGRESS
        self.make_turn()
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.IN_PROGRESS}')

    @lobby_status_check(GameStatusesEnum.IN_PROGRESS)
    def make_turn(self,) -> None:
        self.game_status = GameStatusesEnum.TURNING
        self.turn += 1
        self.set_next_game_number_turn()
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.TURNING}')
    

    @lobby_status_check(GameStatusesEnum.TURNING)
    def end_turn(self,) -> None:
        self.game_status = GameStatusesEnum.VOTING
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.VOTING}')


    @lobby_status_check(GameStatusesEnum.VOTING)
    def make_vote(self, game_user:GameUser, vote_user_id:UUID):
        game_user.make_vote(vote_user_id)

    def get_all_votes(self,) -> list[tuple[str, int]]:
        return Counter([GameUser.objects.get(user_id=user.vote_id).game_name for user in GameUser.get_user_in_game(self.game_id) if user.vote_id]).most_common()

    @lobby_status_check(GameStatusesEnum.VOTING)
    def end_vote(self,) -> None | str:
        # На первом ходу нельзя исключать
        if self.turn > 1:
            all_votes:list[tuple[UUID, int]] = Counter([game_user.vote_id for game_user in GameUser.get_user_in_game(self.game_id) if game_user.vote_id]).most_common()

            if len(all_votes):
                nominante_to_kick = [all_votes[0]]
                max_voted = all_votes[0][1]

                for vote_id, vote_count in all_votes[1:]:
                    if max_voted == vote_count:
                        nominante_to_kick.append((vote_id,vote_count))
                all_voted_idx = 0
                if len(nominante_to_kick) > 1:
                    all_voted_idx = get_random_value(0, 1)
                
                print("KICKED ", nominante_to_kick[all_voted_idx][0])
                self.kick_from_game_by_id(nominante_to_kick[all_voted_idx][0])
        
        for game_user in GameUser.objects.filter(game_id=self.game_id).all():
            game_user.make_vote(None)

        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.IN_PROGRESS}')

        if len(GameUser.get_user_in_game(self.game_id)) == self.user_count/2:
            return self.game_ended()
        else:
            self.game_status = GameStatusesEnum.IN_PROGRESS
            self.save()
            self.make_turn()

    @lobby_status_check(GameStatusesEnum.VOTING)
    def game_ended(self,) -> str:
        self.game_status = GameStatusesEnum.END 
        self.ending = self.generate_ending()
        self.save()
        game_logger(f'GameEngine {self.game_id} status {GameStatusesEnum.END}')

    @lobby_status_check(GameStatusesEnum.END)
    def generate_ending(self,) -> str:
        promt = ""
        promt += self.as_nn_promt()
        for game_user in GameUser.get_user_in_game(self.game_id):
            promt += game_user.as_nn_promt()
        return nn_request.request_to_nn(promt)

    @lobby_status_check(GameStatusesEnum.VOTING)
    def kick_from_game_by_id(self, user_id:UUID) -> None:
        game_user = GameUser.objects.get(user_id=user_id)
        game_user.kick_from_game()
        game_logger(f'GameEngine {self.game_id} player {game_user.user_id} kicked')
                