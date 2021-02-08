from game_classes import Dot

if __name__ == '__main__':
    d1 = Dot(1, 1)
    d2 = Dot(1, 1)
    print(d1 == (1, 1))
    print(d1 == [1, 1])
    print(d1 == d2)
