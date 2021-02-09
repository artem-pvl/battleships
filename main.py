from game_classes import Dot, Ship

if __name__ == '__main__':
    d1 = Dot(5, 1)
    d2 = Dot(1, 1)
    print(d1 == (1, 1))
    print(d1 == [1, 1])
    print(d1 == d2)

    ship1 = Ship(3, d1, False)
    ship_dots = ship1.dots()
    print(ship_dots[0].x, ship_dots[0].y)
    print(ship_dots[1].x, ship_dots[1].y)
    print(ship_dots[2].x, ship_dots[2].y)
