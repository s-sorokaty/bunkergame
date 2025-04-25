from game_engine import GameEngine

game = GameEngine()

def test_game_scenarios(game:GameEngine):
    game.create_lobby()
    game.start_game()

    game.make_turn()
    game.end_turn()
    game.end_vote()

    game.make_turn()
    game.get_users_in_game()[1].make_vote(game.get_users_in_game()[3].user_id)
    game.get_users_in_game()[2].make_vote(game.get_users_in_game()[3].user_id)

    game.get_users_in_game()[3].make_vote(game.get_users_in_game()[3].user_id)
    game.get_users_in_game()[4].make_vote(game.get_users_in_game()[2].user_id)
    game.get_users_in_game()[5].make_vote(game.get_users_in_game()[2].user_id)
    game.end_turn()
    game.end_vote()

    game.make_turn()
    game.get_users_in_game()[1].make_vote(game.get_users_in_game()[3].user_id)
    game.get_users_in_game()[2].make_vote(game.get_users_in_game()[3].user_id)

    game.get_users_in_game()[3].make_vote(game.get_users_in_game()[3].user_id)
    game.get_users_in_game()[4].make_vote(game.get_users_in_game()[2].user_id)
    game.end_turn()
    game.end_vote()

    game.make_turn()
    game.get_users_in_game()[0].make_vote(game.get_users_in_game()[0].user_id)
    game.get_users_in_game()[1].make_vote(game.get_users_in_game()[0].user_id)

    game.get_users_in_game()[2].make_vote(game.get_users_in_game()[3].user_id)
    game.get_users_in_game()[3].make_vote(game.get_users_in_game()[2].user_id)
    game.end_turn()
    result = game.end_vote()
    if result:
        print(result)

test_game_scenarios(game)
print('test user ', game.get_users_in_game()[0])
game.restart_game()
test_game_scenarios(game)
print('test user ', game.get_users_in_game()[0])

print('current_turn: ', game._turn)
print('current_user_in_game: ', len(game.get_users_in_game()))
print(game.game_status)
