BOARD_SIZE = 6
CHARS = ['a', 'b', 'c', 'd',
         'e', 'f', 'g', 'h',
         'i', 'j', 'k', 'l',
         'm', 'n', 'o', 'p',
         'q', 'r', 's', 't',
         'u', 'v', 'w', 'x',
         'y', 'z']
CHAR_SCALE = [i for i in CHARS[:BOARD_SIZE]]


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


class Ship:
    def __init__(self, length, start_point, orientation):
        self.length = length
        self.start_point = start_point
#       orientation: True - horizontal, False - vertical
        self.orientation = orientation
        self.lives = length

    @property
    def ship_length(self):
        return self.length

    @property
    def ship_lives(self):
        return self.lives

    @ship_lives.setter
    def ship_lives(self, value):
        if isinstance(value, int):
            raise TypeError("Ship lives must be an integer")

        if 0 < value <= self.length:
            self.lives = value
        else:
            raise ShipLivesException

    def dots(self):
        if self.orientation:
            return [Dot(i, self.start_point.y) for i in range(self.start_point.x, self.start_point.x + self.length)]
        else:
            return [Dot(self.start_point.x, i) for i in range(self.start_point.y, self.start_point.y + self.length)]

    def area(self):
        area = []
        for i in range(self.start_point.x - 1,
                       self.start_point.x + self.length + 1 if self.orientation else self.start_point.x + 1):
            for j in range(self.start_point.y - 1,
                           self.start_point.x + 1 if self.orientation else self.start_point.y + self.length + 1):
                area.append(Dot(i, j))
        return area


class Board:
    def __init__(self, board_size=BOARD_SIZE):
        self.__ship_symbol = "█"
        self.__miss_symbol = "●"
        self.__hit_symbol = "╳"
        self.__blank_symbol = " "
        self.board = [[self.__blank_symbol] * board_size for _ in range(board_size)]
        self.ships = []
        self.hid = True
        self.alive_ships = 0

    @property
    def hid_ships(self):
        return self.hid

    @hid_ships.setter
    def hid_ships(self, value):
        self.hid = value

    def get_alive_ships(self):
        return self.alive_ships

    def add_ship(self, ship):
        if isinstance(ship, Ship):
            if all(map(self.out, ship.dots())):
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
        if self.out(item):
            if self.hid or (self.board[item.x][item.y] in (self.__hit_symbol, self.__miss_symbol)):
                return self.board[item.x][item.y]
            else:
                for ship in self.ships:
                    if item in ship.dots():
                        return self.__ship_symbol
                return self.__blank_symbol
        else:
            raise KeyError

    def out(self, dot):
        if isinstance(dot, Dot):
            if (0 <= dot.x <= len(self.board[0])) and (0 <= dot.y <= len(self.board)):
                return True
            return False
        else:
            raise TypeError("Dot must be Dot class object")

    def shot(self, dot):
        if isinstance(dot, Dot):
            if self.out(dot):
                for ship in self.ships:
                    if dot in ship.dots():
                        self.board[dot.x][dot.y] = self.__hit_symbol
                        ship.lives -= 1
                        if ship.lives == 0:
                            self.alive_ships -= 1
                            return 'kill'
                        return 'hit'
                if self.board[dot.x][dot.y] != self.__blank_symbol:
                    raise DotIsOccupiedException
                self.board[dot.x][dot.y] = self.__miss_symbol
                return 'miss'
            else:
                raise BoardOutException
        else:
            raise TypeError("Dot must be Dot class object")


class Player:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_player_1 = Board(board_size)
        self.board_player_2 = Board(board_size)
        self.__current_player = 0
        self.__turn_iter = self.__turn(1, 2)

    def get_current_player(self):
        return self.__current_player

    @classmethod
    def __turn(cls, a, b):
        while True:
            yield a
            yield b

    def ask(self, reason=""):
        return Dot(0, 0)

    def move(self):
        self.__current_player = next(self.__turn_iter)
        if self.__current_player == 1:
            current_board = self.board_player_2
        else:
            current_board = self.board_player_1

        try_again = True
        while try_again:
            try:
                shoot_result = current_board.shot(self.ask())
                if shoot_result == "miss":
                    try_again = False
            except BoardOutException:
                self.ask("The shoot misses the board!")
            except DotIsOccupiedException:
                self.ask("The shot already made in this dot!")


class Ai(Player):
    def __init__(self):
        Player.__init__(self)
        pass

    def ask(self, reason=""):
        pass


class User(Player):
    def __init__(self):
        Player.__init__(self)
        pass

    def ask(self, reason=""):
        pass


class Game:
    def __init__(self):
        self.user = User()
        self.user_board = Board()
        self.ai = Ai()
        self.ai_board = Board()

    def random_board(self):
        pass

    def greet(self):
        pass

    def loop(self):
        pass

    def start(self):
        pass
