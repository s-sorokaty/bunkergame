from django.test import TestCase
from django.contrib.auth.models import User
from .models import GameUser, GameEngine, GameStatusesEnum
from .utils import user_rules, exceptions


class GameEngineTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.game_engine = GameEngine()
        cls.game_engine.create_game(owner_id=cls.user, game_name='Test Game', user_count=6)
        return cls


    def test_create_game(self):
        self.assertEqual(self.game_engine.game_name, 'Test Game')
        self.assertEqual(self.game_engine.user_count, 6)
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.NOT_CREATED)

    def test_join_user(self):
        self.game_engine.join_user(self.user)
        game_user = GameUser.objects.get(account_id=self.user)
        self.assertEqual(game_user.account_id, self.user)

    def test_start_game_with_only_owner(self):
        with self.assertRaises(exceptions.LobbyStatusCheckMismatch):
            self.game_engine.start_game()
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.NOT_CREATED)
    
    def __test_join_users(self):
        users = [User.objects.create_user(username=f'testuser{i}', password='password') for i in range(0,6)]
        for user in users:
            self.game_engine.join_user(user)
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.CREATED)
    
    def __test_start_game_with_users(self):
        self.game_engine.start_game()
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.TURNING)

    def __test_wrong_user_turning(self):
        with self.assertRaises(exceptions.WrongPlayerTurn):
            users = GameUser.get_user_in_game(self.game_engine.game_id)
            self.game_engine.show_stat('profession', [user for user in users if user.game_number > 1][0])

    def __test_user_show_stat(self, statname:str):
        users = GameUser.get_user_in_game(self.game_engine.game_id)
        curr_user = None
        for user in users:
            if user.game_number == self.game_engine.user_number_turn: curr_user = user
        self.game_engine.show_stat(statname, curr_user)
        self.game_engine.end_user_turn(curr_user)
        self.assertEqual(getattr(curr_user, curr_user.get_stat_dict()[statname]), True)
            
    def __test_all_users_show_stat(self,statname:str):
        for _ in range(self.game_engine.user_count):
            self.__test_user_show_stat(statname)
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.VOTING)

    def __test_end_vote(self):
        self.game_engine.end_vote()
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.TURNING)

    def test_game_run(self):
        self.__test_join_users()
        self.__test_start_game_with_users()
        self.__test_wrong_user_turning()
        self.__test_all_users_show_stat(list(GameUser.get_stat_dict().keys())[0])
        self.__test_end_vote()

    #def test_generate_ending(self):
    #    self.game_engine.join_user(self.user)
    #    self.game_engine.start_game()
    #    ending = self.game_engine.generate_ending()
    #    self.assertIsInstance(ending, str)
