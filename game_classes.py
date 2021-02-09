BOARD_SIZE = 6


class BoardOutException(Exception):
    pass


class ShipLivesException(Exception):
    pass


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
            if 0 <= value < BOARD_SIZE:
                return value
            else:
                raise BoardOutException()
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
        self._length = length
        self.start_point = start_point
        self.orientation = orientation
        self._lives = length

    @property
    def length(self):
        return self._length

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        if isinstance(value, int):
            raise TypeError("Ship lives must be an integer")

        if 0 < value <= self._length:
            self._lives = value
        else:
            raise ShipLivesException("Ship lives must be in the range from 0 to ship length")

    def dots(self):
        if self.orientation:
            return [Dot(_, self.start_point.y) for _ in range(self.start_point.x, self.start_point.x + self._length)]
        else:
            return [Dot(self.start_point.x, _) for _ in range(self.start_point.y, self.start_point.y + self._length)]


class Board:
    def __init__(self):
        self.board = [["" * 6] * 6]
        self.ships = [[Ship()] * 9]
        self.hid = True
        self.live_ships = 9

    def add_ship(self):
        pass

    def contour(self):
        pass

    def print_board(self):
        pass

    def out(self):
        pass

    def shot(self):
        pass


class Player:
    def __init__(self):
        self.board = Board()
        self.enemy_board = Board()

    def ask(self):
        pass

    def move(self):
        pass


class Ai(Player):
    def __init__(self):
        Player.__init__(self)
        pass

    def ask(self):
        pass


class User(Player):
    def __init__(self):
        Player.__init__(self)
        pass

    def ask(self):
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
