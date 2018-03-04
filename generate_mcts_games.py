import argparse
import numpy as np

from gencoder import get_encoder_by_name
from gboard.gstate import GState
from gagent.gagent import GAgentMCTS
from gencoder.base import GEncoder
from gutils.display import print_board, print_move


def generate_game(board_size, rounds, max_moves, temperature):
    boards = []
    moves = []

    encoder: GEncoder = get_encoder_by_name('oneplane', board_size)

    game = GState.new_game(board_size)

    bot = GAgentMCTS(rounds, temperature)

    num_moves = 0
    while not game.is_over():
        print_board(game.gboard)
        gmove = bot.select_move(game)

        if gmove.is_play:
            boards.append(encoder.encode(game))

            move_one_hot = np.zeros(encoder.num_points())
            move_one_hot[encoder.encode_point(gmove.gpoint)] = 1
            moves.append(move_one_hot)

        print_move(game.next_gplayer, gmove)
        game = game.apply_move(gmove)
        num_moves += 1

        if num_moves > max_moves:
            break

    return np.array(boards), np.array(moves)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board-size', '-b', type=int, default=9)
    parser.add_argument('--rounds', '-r', type=int, default=1000)
    parser.add_argument('--temperature', '-t', type=float, default=0.8)
    parser.add_argument('--max-moves', '-m', type=int, default=60,
    help='Max moves per game.')
    parser.add_argument('--num-games', '-n', type=int, default=10)
    parser.add_argument('--board-out')
    parser.add_argument('--move-out')
    args = parser.parse_args()
    Xs = []
    ys = []

    for i in range(args.num_games):
        print('Generating game %d/%d...' % (i + 1, args.num_games))
        X, y = generate_game(args.board_size, args.rounds, args.max_moves, args.temperature)
        Xs.append(X)
        ys.append(y)
    X = np.concatenate(Xs)
    y = np.concatenate(ys)
    np.save(args.board_out, X)
    np.save(args.move_out, y)

if __name__:
    main()