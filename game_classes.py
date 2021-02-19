from random import randint

BOARD_SIZE = 6
SHIP_ST = 'ship'
MISS_ST = 'miss'
HIT_ST = 'hit'
KILL_ST = 'kill'
BLANK_ST = 'blank'
OUT_ST = 'out of board'
LOOSE_ST = 'loose'
OCCUPIED_ST = 'occupied'
LAST_SYM_ST = 'last'


class BoardOutException(Exception):
    def __init__(self, args="The object misses the board!"):
        Exception.__init__(self, args)


class DotIsOccupiedException(Exception):
    def __init__(self, args="The shot already made in this dot!"):
        Exception.__init__(self, args)


class ShipLivesException(Exception):
    def __init__(self, args="Ship lives must be in the range from 0 to ship length"):
        Exception.__init__(self, args)


class ShipWrongPosition(Exception):
    def __init__(self, args="Ship intersection detected!"):
        Exception.__init__(self, args)


class Dot:
    def __init__(self, x, y):
        self.x_coord = self.__test_value(x)
        self.y_coord = self.__test_value(y)

    @property
    def x(self):
        return self.x_coord

    @x.setter
    def x(self, value):
        self.x_coord = self.__test_value(value)

    @property
    def y(self):
        return self.y_coord

    @y.setter
    def y(self, value):
        self.y_coord = self.__test_value(value)

    @staticmethod
    def __test_value(value):
        if isinstance(value, int):
            return value
        else:
            raise TypeError("Coordinates must be an integer")

    def __eq__(self, other):
        if isinstance(other, Dot):
            return (self.x_coord == other.x) and (self.y_coord == other.y)
        elif isinstance(other, (tuple, list)) and len(other) == 2 and all(isinstance(_, int) for _ in other):
            return (self.x_coord == other[0]) and (self.y_coord == other[1])
        else:
            return False

    def __len__(self):
        return 1


class Ship:
    def __init__(self, length, start_point, orientation):
        self.__length = length
        self.__start_point = start_point
#       orientation: True - horizontal, False - vertical
        self.__orientation = orientation
        self.__lives = length

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, ship_length):
        if ship_length < self.__lives:
            self.__lives = ship_length
        self.__length = ship_length

    @property
    def start_point(self):
        return self.__start_point

    @start_point.setter
    def start_point(self, dot):
        self.__start_point = dot

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, ship_orientation):
        self.__orientation = ship_orientation

    @property
    def lives(self):
        return self.__lives

    @lives.setter
    def lives(self, ship_lives):
        if 0 <= ship_lives <= self.__length:
            self.__lives = ship_lives
        elif ship_lives > self.__length:
            self.__lives = self.__length
        else:
            raise ShipLivesException

    def dots(self):
        if self.__orientation:
            return [Dot(self.__start_point.x, i) for i in
                    range(self.__start_point.y, self.__start_point.y + self.__length)]
        else:
            return [Dot(i, self.__start_point.y) for i in
                    range(self.__start_point.x, self.__start_point.x + self.__length)]

    def area(self):
        area = []
        for i in range(self.__start_point.x - 1,
                       self.__start_point.x + 2 if self.__orientation
                       else self.__start_point.x + self.__length + 1):
            for j in range(self.__start_point.y - 1,
                           self.__start_point.y + self.__length + 1 if self.__orientation
                           else self.__start_point.y + 2):
                area.append(Dot(i, j))
        return area

    def get_edges(self):
        dots = []
        if self.__length == 1:
            dots.append(Dot(self.__start_point.x-1, self.__start_point.y))
            dots.append(Dot(self.__start_point.x+1, self.__start_point.y))
            dots.append(Dot(self.__start_point.x, self.__start_point.y-1))
            dots.append(Dot(self.__start_point.x, self.__start_point.y+1))
        else:
            if self.__orientation:
                dots.append(Dot(self.__start_point.x, self.__start_point.y-1))
                dots.append(Dot(self.__start_point.x, self.__start_point.y+self.__length))
            else:
                dots.append(Dot(self.__start_point.x-1, self.__start_point.y))
                dots.append(Dot(self.__start_point.x+self.__length, self.__start_point.y))
        return dots


class Board:
    def __init__(self, board_size=BOARD_SIZE):
        self.__ship_symbol = "\033[37m█\033[0m"
        self.__miss_symbol = "\033[34m●\033[0m"
        self.__hit_symbol = "\033[33m\033[1m╳\033[0m"
        self.__kill_symbol = "\033[41m\033[30m\033[1m╳\033[0m"
        self.__blank_symbol = " \033[0m"
        self.__last_turn_symbol = "\033[7m"
        self.__last_turn = None
        self.__enum_symbol = {
            self.__miss_symbol: MISS_ST,
            self.__hit_symbol: HIT_ST,
            self.__kill_symbol: KILL_ST,
            }
        self.__enum_status = {
            MISS_ST: self.__miss_symbol,
            HIT_ST: self.__hit_symbol,
            KILL_ST: self.__kill_symbol,
            }
        self.board = [[self.__blank_symbol] * board_size for _ in range(board_size)]
        self.ships = []
        self.hid = True
        self.alive_ships = 0

    @property
    def board_size(self):
        return len(self.board)

    @property
    def hid_ships(self):
        return self.hid

    @hid_ships.setter
    def hid_ships(self, value):
        self.hid = value

    def get_alive_ships_count(self):
        return self.alive_ships

    def get_last_turn(self):
        return self.__last_turn

    def get_symbols(self):
        return {
            SHIP_ST: self.__ship_symbol,
            MISS_ST: self.__miss_symbol,
            HIT_ST: self.__hit_symbol,
            KILL_ST: self.__kill_symbol,
            BLANK_ST: self.__blank_symbol,
            LAST_SYM_ST: self.__last_turn_symbol,
        }

    def get_dead_ships_area(self):
        area = []
        for ship in self.ships:
            if ship.lives == 0:
                for dot in ship.area():
                    area.append(dot)
        return area

    def get_ships_edges(self):
        edges = []
        for ship in self.ships:
            if ship.lives > 0:
                for edge in ship.get_edges():
                    if not self.out(edge):
                        if self.board[edge.x][edge.y] == self.__blank_symbol:
                            edges.append(edge)
        return edges

    def get_free_dots(self):
        dots = []
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                if ((x, y) not in self.get_dead_ships_area()) and (self.board[x][y] == self.__blank_symbol):
                    dots.append(Dot(x, y))
        return dots

    def add_ship(self, ship):
        if isinstance(ship, Ship):
            if not any(map(self.out, ship.dots())):
                for current_ship in self.ships:
                    for ship_dot in ship.dots():
                        if ship_dot in current_ship.area():
                            raise ShipWrongPosition
                self.ships.append(ship)
                self.alive_ships += 1
            else:
                raise BoardOutException
        else:
            raise TypeError("Ship to add must be the Ship class object")

    def try_ship(self, ship):
        if isinstance(ship, Ship):
            if not any(map(self.out, ship.dots())):
                for current_ship in self.ships:
                    for ship_dot in ship.dots():
                        if ship_dot in current_ship.area():
                            return False
            else:
                return False
        else:
            raise TypeError("Ship to add must be the Ship class object")
        return True

    def append_ship(self, ship_to_append):
        if isinstance(ship_to_append, Ship):
            for ship in self.ships:
                for dot in ship_to_append.dots():
                    if dot in ship.area():
                        if ship_to_append.start_point.x == ship.start_point.x:
                            if ((ship.orientation and ship.length > 1) or (ship.length == 1))\
                                or ((ship_to_append.orientation and ship_to_append.length > 1)
                                    or (ship_to_append.length == 1)):
                                if ship_to_append.start_point.y + 1 == ship.start_point.y:
                                    ship_to_append.length += ship.length
                                    ship_to_append.lives += ship.lives
                                    ship_to_append.orientation = True
                                    self.ships.remove(ship)
                                    self.append_ship(ship_to_append)
                                    return
                                elif ship_to_append.start_point.y == ship.start_point.y + ship.length:
                                    ship_to_append.start_point.y = ship.start_point.y
                                    ship_to_append.length += ship.length
                                    ship_to_append.lives += ship.lives
                                    ship_to_append.orientation = True
                                    self.ships.remove(ship)
                                    self.append_ship(ship_to_append)
                                    return
                            else:
                                ShipWrongPosition()
                        elif ship_to_append.start_point.y == ship.start_point.y:
                            if ((not ship.orientation and ship.length > 1) or (ship.length == 1)) \
                                    or ((not ship_to_append.orientation and ship_to_append.length > 1)
                                        or (ship_to_append.length == 1)):
                                if ship_to_append.start_point.x + 1 == ship.start_point.x:
                                    ship_to_append.length += ship.length
                                    ship_to_append.orientation = False
                                    self.ships.remove(ship)
                                    self.append_ship(ship_to_append)
                                    return
                                elif ship_to_append.start_point.x == ship.start_point.x + ship.length:
                                    ship_to_append.start_point.x = ship.start_point.x
                                    ship_to_append.start_point.y = ship.start_point.y
                                    ship_to_append.length += ship.length
                                    ship_to_append.orientation = False
                                    self.ships.remove(ship)
                                    self.append_ship(ship_to_append)
                                    return
            self.add_ship(ship_to_append)
        else:
            raise TypeError("ship_to_append must be Ship class object")

    def erase_ships(self):
        self.ships = []
        self.alive_ships = 0

    def __getitem__(self, item):
        if not isinstance(item, Dot):
            if all((isinstance(item, tuple), isinstance(item[0], int), isinstance(item[1], int))) and (len(item) == 2):
                item = Dot(*item)
            else:
                raise TypeError("Item must be (x,y) tuple where x and y is integer or Dot class")
        if not self.out(item):
            if self.board[item.x][item.y] != self.__blank_symbol:
                if item == self.__last_turn:
                    return self.__last_turn_symbol+self.board[item.x][item.y]
                return self.board[item.x][item.y]
            else:
                if self.hid:
                    return self.board[item.x][item.y]
                else:
                    for ship in self.ships:
                        if item in ship.dots():
                            return self.__ship_symbol
                    return self.board[item.x][item.y]
        else:
            raise KeyError

    def out(self, dot):
        if isinstance(dot, Dot):
            if (0 <= dot.x < len(self.board[0])) and (0 <= dot.y < len(self.board)):
                return False
            return True
        else:
            raise TypeError("Dot must be Dot class object")

    def shot(self, dot):
        if isinstance(dot, Dot):
            if not self.out(dot):
                if self.board[dot.x][dot.y] == self.__blank_symbol:
                    for ship in self.ships:
                        if dot in ship.dots():
                            self.__last_turn = Dot(dot.x, dot.y)
                            self.board[dot.x][dot.y] = self.__hit_symbol
                            ship.lives = ship.lives - 1
                            if ship.lives == 0:
                                self.alive_ships -= 1
                                for killed_dot in ship.dots():
                                    self.board[killed_dot.x][killed_dot.y] = self.__kill_symbol
                                return KILL_ST
                            return HIT_ST
                else:
                    raise DotIsOccupiedException
                self.board[dot.x][dot.y] = self.__miss_symbol
                self.__last_turn = Dot(dot.x, dot.y)
                return MISS_ST
            else:
                raise BoardOutException
        else:
            raise TypeError("Dot must be Dot class object")

    def save_result(self, dot, status):
        if isinstance(dot, Dot):
            if status in self.__enum_status:
                self.board[dot.x][dot.y] = self.__enum_status[status]
                self.__last_turn = Dot(dot.x, dot.y)
                if status in (HIT_ST, KILL_ST):
                    self.append_ship(Ship(1, Dot(dot.x, dot.y), False))
                    if status == KILL_ST:
                        for ship in self.ships:
                            if dot in ship.dots():
                                ship.lives = 0
                                for redraw_dot in ship.dots():
                                    self.board[redraw_dot.x][redraw_dot.y] = self.__kill_symbol
                                break
            else:
                raise TypeError("status must be in Board.__enum_status")
        else:
            raise TypeError("dot must be Dot class object")


class Player:
    CHARS = ['a', 'b', 'c', 'd',
             'e', 'f', 'g', 'h',
             'i', 'j', 'k', 'l',
             'm', 'n', 'o', 'p',
             'q', 'r', 's', 't',
             'u', 'v', 'w', 'x',
             'y', 'z']

    def __init__(self, board_size=BOARD_SIZE):
        self.player_board = Board(board_size)
        self.enemy_board = Board(board_size)
        self.player_board.hid = False
        self.enemy_board.hid = True

    def ask(self):
        pass

    def save_move(self, dot, status):
        if status == LOOSE_ST:
            self.enemy_board.save_result(dot, KILL_ST)
        else:
            self.enemy_board.save_result(dot, status)

    def move(self, dot):
        if isinstance(dot, Dot):
            try:
                shoot_result = self.player_board.shot(dot)
                if self.player_board.get_alive_ships_count() == 0:
                    return LOOSE_ST
            except BoardOutException:
                shoot_result = OUT_ST
            except DotIsOccupiedException:
                shoot_result = OCCUPIED_ST
            return shoot_result
        else:
            raise TypeError("Dot must be Dot class object")

    def print_board(self):
        print()
        print('      ' + 'Моё поле'.center((self.player_board.board_size*2-1)+4, ' ') +
              '     ' +
              'Поле противника'.center((self.enemy_board.board_size*2-1)+4, ' '))
        print('        '+' '.join(str(i) for i in range(1, self.player_board.board_size+1)) +
              '         '+' '.join(str(i) for i in range(1, self.enemy_board.board_size+1)))
        for x in range(self.player_board.board_size):
            print('      '+self.CHARS[x]+' ' +
                  ' '.join(self.player_board[x, y] for y in range(self.player_board.board_size)) + ' ' +
                  self.CHARS[x]+'     '+self.CHARS[x]+' ' +
                  ' '.join(self.enemy_board[x, y] for y in range(self.enemy_board.board_size))+' '+self.CHARS[x])
        print('        '+' '.join(str(i) for i in range(1, self.player_board.board_size+1)) +
              '         '+' '.join(str(i) for i in range(1, self.enemy_board.board_size+1)))

    def add_ships(self, ships):
        pass

    def add_ships_random(self, ships):
        for ship in ships:
            next_ship = False
            orientation = True if randint(0, 1) == 0 else False
            free_dots = self.player_board.get_free_dots()
            while not next_ship:
                if not free_dots:
                    self.player_board.erase_ships()
                    return self.add_ships_random(ships)
                ship.start_point = free_dots[randint(0, len(free_dots)-1)]
                ship.orientation = orientation
                try:
                    self.player_board.add_ship(ship)
                except (BoardOutException, ShipWrongPosition):
                    try:
                        ship.orientation = ~ship.orientation
                        self.player_board.add_ship(ship)
                    except (BoardOutException, ShipWrongPosition):
                        free_dots.remove(ship.start_point)
                    else:
                        next_ship = True
                else:
                    next_ship = True


class Ai(Player):
    def __init__(self, board_size=BOARD_SIZE):
        Player.__init__(self, board_size)

    def ask(self):
        free_dots = self.enemy_board.get_ships_edges()
        if free_dots:
            return free_dots[randint(0, len(free_dots)-1)]
        else:
            free_dots = self.enemy_board.get_free_dots()
            if free_dots:
                return free_dots[randint(0, len(free_dots)-1)]
        return None


class User(Player):
    def __init__(self, board_size=BOARD_SIZE):
        Player.__init__(self, board_size)
        pass

    def __check_input(self, turn):
        dot = [None, None]
        while None in dot:
            if len(turn) == 2:
                dot[0] = self.CHARS.index(list(turn)[0]) if list(turn)[0] in self.CHARS else None
                dot[1] = int(list(turn)[1]) - 1 if turn[1].isdigit() else None
            if None in dot:
                turn = input("Введите точку в формате RC, где: R - буква строки, C - номер колонки: ").lower()
        return Dot(*dot)

    def ask(self):
        turn = input("\nВаш ход: ").lower()
        return self.__check_input(turn)

    def add_ships(self, ships):
        self.print_board()
        for ship in ships:
            next_ship = False
            print()
            while not next_ship:
                free_dots = self.player_board.get_free_dots()
                while free_dots:
                    ship.start_point = free_dots[randint(0, len(free_dots) - 1)]
                    if not self.player_board.try_ship(ship):
                        ship.orientation = ~ship.orientation
                        if not self.player_board.try_ship(ship):
                            free_dots.remove(ship.start_point)
                        else:
                            break
                    else:
                        break
                    if not free_dots:
                        print("Похоже нет места для размещения корабля, попробуйте расставить корабли ещё раз!")
                        self.player_board.erase_ships()
                        return self.add_ships(ships)

                print(f"Осталось разместить кораблей: {len(ships) - ships.index(ship)}")
                text = input(f"Введите начальную точку корабля размером {ship.length} палубы: ")
                start_dot = self.__check_input(text)
                ship.start_point = start_dot
                text = ""
                if ship.length > 1:
                    while text not in ("h", "v", "г", "в"):
                        text = input(f"Введите ориентацию корабля (h или г - горизонтально, v или в - вертикально): ")
                    ship.orientation = True if text in ("h", "г") else False
                try:
                    self.player_board.add_ship(ship)
                except BoardOutException:
                    print("Корабль выходит за пределы игрового поля, попробуйте ввести расположение ещё раз!")
                except ShipWrongPosition:
                    print("Корабли столкнулись, попробуйте ввести расположение ещё раз!")
                else:
                    next_ship = True
                    self.print_board()


class Game:
    def __init__(self, board_size=BOARD_SIZE):
        self.user = User(board_size)
        self.ai = Ai(board_size)
        self.__turn_iter = self.__turn(1, 2)
        self.__current_player = next(self.__turn_iter)

    def get_current_player(self):
        return self.__current_player

    @classmethod
    def __turn(cls, a, b):
        while True:
            yield a
            yield b

    def greet(self):
        symbols = self.user.player_board.get_symbols()
        print("\nКонсольная игра 'Морской бой'\n")
        print("Обозначения игрового поля:")
        print(f"  {symbols[MISS_ST]}\033[0m - промах")
        print(f"  {symbols[HIT_ST]}\033[0m - подбитый корабль")
        print(f"  {symbols[KILL_ST]}\033[0m - потопленый корабль")
        print(f"  {symbols[LAST_SYM_ST]}{symbols[MISS_ST]} {symbols[HIT_ST]} {symbols[KILL_ST]}"
              f"\033[0m - обозначения последнего сделанного хода (промах, подбитый, потопленный)\n")

    def loop(self):
        win = False
        while not win:
            if self.__current_player == 1:
                current_player = self.user
                enemy_player = self.ai
            else:
                current_player = self.ai
                enemy_player = self.user

            if self.__current_player == 1:
                print("\nВаш ход!")
            else:
                print("\nХодит компьютер.")

            result = HIT_ST
            while result in (HIT_ST, KILL_ST):
                dot = current_player.ask()
                result = enemy_player.move(dot)
                while result in (OCCUPIED_ST, OUT_ST):
                    if self.__current_player == 1:
                        if result == OCCUPIED_ST:
                            print("Выстрел в эту точку уже сделан!")
                        elif result == OUT_ST:
                            print("Выстрел мимо игрового поля!")
                    dot = current_player.ask()
                    result = enemy_player.move(dot)
                current_player.save_move(dot, result)
                self.user.print_board()
                print()
                if self.__current_player == 1:
                    if result == HIT_ST:
                        print("Есть попадание, корабль противника \033[33mранен\033[0m!")
                        print("Сделайте ещё выстрел.")
                    elif result == KILL_ST:
                        print("Есть попадание, корабль противника \033[31mпотоплен\033[0m!")
                        print(f"У противника осталось кораблей: "
                              f"\033[32m{enemy_player.player_board.get_alive_ships_count()}\033[0m")
                        print("Сделайте ещё выстрел.")
                    elif result == MISS_ST:
                        print("\033[34mМимо\033[0m!")
                    elif result == LOOSE_ST:
                        print("\033[32m\033[1mПобеда\033[0m!")
                        win = True
                else:
                    if result == HIT_ST:
                        print("Есть попадание, ваш корабль \033[33mранен\033[0m!")
                        print("Компьютер ходит ещё раз.")
                    elif result == KILL_ST:
                        print("Есть попадание, ваш корабль \033[31mпотоплен\033[0m!")
                        print(f"У вас осталось кораблей: "
                              f"\033[32m{enemy_player.player_board.get_alive_ships_count()}\033[0m")
                        print("Компьютер ходит ещё раз.")
                    elif result == MISS_ST:
                        print("Компьютер \033[34mпромазал\033[0m!")
                    elif result == LOOSE_ST:
                        print("Компьютер \033[32m\033[1mпобедил\033[0m!")
                        win = True
            self.__current_player = next(self.__turn_iter)

    def start(self):
        self.greet()

        ships_user = [
            Ship(3, Dot(0, 0), True),
            Ship(2, Dot(0, 0), True),
            Ship(2, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True)
        ]

        ships_ai = [
            Ship(3, Dot(0, 0), True),
            Ship(2, Dot(0, 0), True),
            Ship(2, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True),
            Ship(1, Dot(0, 0), True)
        ]
        key = input("Хотите расставить корабли вручную? (Д, Y - да): ")
        if key.lower() in ("y", "д"):
            self.user.add_ships(ships_user)
        else:
            self.user.add_ships_random(ships_user)
            self.user.print_board()

        self.ai.add_ships_random(ships_ai)

        self.loop()
