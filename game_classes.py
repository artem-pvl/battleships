from random import randint

BOARD_SIZE = 6


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
        else:
            print(f"shl = {ship_lives}")
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
                dots.append(Dot(self.__start_point.x-1, self.__start_point.y))
                dots.append(Dot(self.__start_point.x+1, self.__start_point.y))
            else:
                dots.append(Dot(self.__start_point.x, self.__start_point.y-1))
                dots.append(Dot(self.__start_point.x, self.__start_point.y+1))
        return dots


class Board:
    SHIP_ST = 'ship'
    MISS_ST = 'miss'
    HIT_ST = 'hit'
    KILL_ST = 'kill'
    BLANK_ST = 'blank'
    OUT_ST = 'out of board'

    def __init__(self, board_size=BOARD_SIZE):
        self.__ship_symbol = "\033[37m█\033[0m"
        self.__miss_symbol = "\033[34m●\033[0m"
        self.__hit_symbol = "\033[33m\033[1m╳\033[0m"
        self.__kill_symbol = "\033[41m\033[30m\033[1m╳\033[0m"
        self.__blank_symbol = " \033[0m"
        self.__last_turn_symbol = "\033[7m"
        self.__last_turn = None
        self.__enum_symbol = {
            self.__miss_symbol: self.MISS_ST,
            self.__hit_symbol: self.HIT_ST,
            self.__kill_symbol: self.KILL_ST,
            }
        self.__enum_status = {
            self.MISS_ST: self.__miss_symbol,
            self.HIT_ST: self.__hit_symbol,
            self.KILL_ST: self.__kill_symbol,
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
            self.__ship_symbol: "ship",
            self.__miss_symbol: "miss",
            self.__hit_symbol: "hit",
            self.__kill_symbol: "kill",
            self.__blank_symbol: "blank",
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
                        csa = current_ship.area()
                        print([(i.x, i.y) for i in csa])
                        print(ship_dot.x, ship_dot.y)
                        if ship_dot in current_ship.area():
                            raise ShipWrongPosition
                self.ships.append(ship)
                self.alive_ships += 1
            else:
                raise BoardOutException
        else:
            raise TypeError("Ship to add must be the Ship class object")

    def append_ship(self, ship_to_append):
        if isinstance(ship_to_append, Ship):
            for ship in self.ships:
                if ship_to_append.start_point.x == ship.start_point.x:
                    if ship_to_append.start_point.y+1 == ship.start_point.y:
                        ship_to_append.length += ship.length
                        ship_to_append.orientation = False
                        self.ships.remove(ship)
                        self.append_ship(ship_to_append)
                        return
                    elif ship_to_append.start_point.y == ship.start_point.y + ship.length:
                        ship_to_append.start_point.x = ship.start_point.x
                        ship_to_append.start_point.y = ship.start_point.y
                        ship_to_append.length += ship.length
                        ship_to_append.orientation = False
                        self.ships.remove(ship)
                        self.append_ship(ship_to_append)
                        return
                elif ship_to_append.start_point.y == ship.start_point.y:
                    if ship_to_append.start_point.x + 1 == ship.start_point.x:
                        ship_to_append.length += ship.length
                        ship_to_append.orientation = True
                        self.ships.remove(ship)
                        self.append_ship(ship_to_append)
                        return
                    elif ship_to_append.start_point.x == ship.start_point.x + ship.length:
                        ship_to_append.start_point.x = ship.start_point.x
                        ship_to_append.start_point.y = ship.start_point.y
                        ship_to_append.length += ship.length
                        ship_to_append.orientation = True
                        self.ships.remove(ship)
                        self.append_ship(ship_to_append)
                        return
            self.ships.append(ship_to_append)
        else:
            raise TypeError("ship_to_append must be Ship class object")

    def print_board(self):
        rows_index = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        print(f"       {'  '.join([str(i) for i in range(1, len(self.board[0])+1)])}\n")

        temp_board = self.board.copy()
        if not self.hid:
            for ship in self.ships:
                for dot in ship.dots():
                    if temp_board[dot.x][dot.y] != self.__hit_symbol:
                        temp_board[dot.x][dot.y] = self.__ship_symbol
        for index, row in zip(rows_index, temp_board):
            print(f"   {index}   \033[34m\033[1m{'  '.join(row)}\033[37m\033[0m")

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
                for ship in self.ships:
                    if dot in ship.dots():
                        self.board[dot.x][dot.y] = self.__hit_symbol
                        ship.lives = ship.lives - 1
                        if ship.lives == 0:
                            self.alive_ships -= 1
                            self.__last_turn = dot
                            for killed_dot in ship.dots():
                                self.board[killed_dot.x][killed_dot.y] = self.__kill_symbol
                            return self.KILL_ST
                        self.__last_turn = dot
                        return self.HIT_ST
                if self.board[dot.x][dot.y] != self.__blank_symbol:
                    raise DotIsOccupiedException
                self.board[dot.x][dot.y] = self.__miss_symbol
                self.__last_turn = Dot(dot.x, dot.y)
                return self.MISS_ST
            else:
                raise BoardOutException
        else:
            raise TypeError("Dot must be Dot class object")

    def save_result(self, dot, status):
        if isinstance(dot, Dot):
            if status in self.__enum_status:
                self.board[dot.x][dot.y] = self.__enum_status[status]
                self.__last_turn = Dot(dot.x, dot.y)
                if status in (self.HIT_ST, self.KILL_ST):
                    self.append_ship(Ship(1, Dot(dot.x, dot.y), False))
                    if status == self.KILL_ST:
                        for ship in self.ships:
                            if dot in ship.dots():
                                ship.lives = 0
                                for redraw_dot in ship.dots():
                                    self.board[redraw_dot.x][redraw_dot.y] = self.__kill_symbol
                                break
            else:
                raise TypeError(f"status must be in {0}".format([i for i in self.__enum_status]))
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
        self.enemy_board.hid = False

    def ask(self):
        pass

    def save_move(self, dot, status):
        if status == "loose":
            status = "kill"
        self.enemy_board.save_result(dot, status)

    def move(self, dot):
        if isinstance(dot, Dot):
            try:
                shoot_result = self.player_board.shot(dot)
                if self.player_board.get_alive_ships_count() == 0:
                    return "loose"
            except BoardOutException:
                shoot_result = "board miss"
            except DotIsOccupiedException:
                shoot_result = "occupied"
            return shoot_result
        else:
            raise TypeError("Dot must be Dot class object")

    def print_board(self):
        print()
        print('        '+'Моё поле'.center((self.player_board.board_size-1)*2+self.player_board.board_size, ' ') +
              '        '+'Поле противника'.center((self.enemy_board.board_size-1)*2+self.enemy_board.board_size, ' '))
        print('        '+'  '.join(str(i) for i in range(1, self.player_board.board_size+1)) +
              '        '+'  '.join(str(i) for i in range(1, self.enemy_board.board_size+1)))
        for x in range(self.player_board.board_size):
            print('      '+self.CHARS[x]+' ' +
                  '  '.join(self.player_board[x, y] for y in range(self.player_board.board_size)) +
                  '      '+self.CHARS[x]+' ' +
                  '  '.join(self.enemy_board[x, y] for y in range(self.enemy_board.board_size)))

    def add_ships(self, ships):
        pass


class Ai(Player):
    def __init__(self, board_size=BOARD_SIZE):
        Player.__init__(self, board_size)

    def ask(self):
        free_dots = self.enemy_board.get_ships_edges()
        print("get_ship_edges", [(dot.x, dot.y) for dot in free_dots])
        if free_dots:
            return free_dots[randint(0, len(free_dots)-1)]
        else:
            free_dots = self.enemy_board.get_free_dots()
            print("get_free_dots", [(dot.x, dot.y) for dot in free_dots])
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

    def ask(self, reason=""):
        if reason:
            print(reason)
        turn = input("Ваш ход: ").lower()
        return self.__check_input(turn)

    def add_ships(self, ships):
        for ship in ships:
            next_ship = False
            self.print_board()
            print()
            while not next_ship:
                text = input(f"Введите начальную точку корабля размером {ship.length} палубы: ")
                start_dot = self.__check_input(text)
                ship.start_point = start_dot
                text = ""
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

    def random_board(self):
        pass

    def greet(self):
        pass

    def loop(self):
        pass

    def start(self):
        pass
