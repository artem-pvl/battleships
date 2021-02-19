from game_classes import Game

if __name__ == '__main__':

    loop_game = True
    while loop_game:
        game = Game()
        game.start()

        key = input("Хотите ещё одну игру? (Д, Y - да): ")
        if key.lower() not in ("y", "д"):
            loop_game = False

    print("Удачи!")
