from django.test import TestCase
from django.contrib.auth.models import User
from .models import GameUser, GameEngine, GameStatusesEnum
from uuid import uuid4

class GameEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.game_engine = GameEngine.objects.create(owner_id=self.user, game_name='Test Game', user_count=6)

    def test_create_empty_game(self):
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.NOT_CREATED)

    def test_join_user(self):
        self.game_engine.join_user(self.user)
        game_user = GameUser.objects.get(account_id=self.user)
        self.assertEqual(game_user.account_id, self.user)
        self.assertTrue(game_user.is_in_game)

    def test_start_game(self):
        self.game_engine.join_user(self.user)
        self.game_engine.lobby_created()
        self.game_engine.start_game()
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.IN_PROGRESS)

    def test_end_turn(self):
        self.game_engine.join_user(self.user)
        self.game_engine.lobby_created()
        self.game_engine.start_game()
        self.game_engine.make_turn()
        self.game_engine.end_turn()
        self.assertEqual(self.game_engine.game_status, GameStatusesEnum.VOTING)

class GameUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.game_engine = GameEngine.objects.create(owner_id=self.user, game_name='Test Game', user_count=6)
        self.game_user = GameUser.objects.create(
            account_id=self.user,
            game_id=self.game_engine,
            profession=0,
            health=0,
            bio_character=0,
            additional_skills=0,
            hobby=0,
            spec_condition=0,
            items=0
        )

    def test_show_stat(self):
        self.game_user.show_stat('profession')
        self.assertTrue(self.game_user.is_profession_visible)

    def test_regenerate_user(self):
        original_game_name = self.game_user.game_name
        self.game_user.regenerate_user([])
        self.assertNotEqual(self.game_user.game_name, original_game_name)

    def test_make_vote(self):
        another_user = GameUser.objects.create(
            account_id=User.objects.create_user(username='anotheruser', password='testpass'),
            game_id=self.game_engine,
            profession=0,
            health=0,
            bio_character=0,
            additional_skills=0,
            hobby=0,
            spec_condition=0,
            items=0
        )
        self.game_user.make_vote(another_user.user_id)
        self.assertEqual(self.game_user.vote_id, another_user.user_id)