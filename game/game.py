"""Asteroids!"""

__version__ = '0.0.1'

class Asteroids(object):

    def __init__(self):
        self.test_attr = 0
        print("Initialized")

    @classmethod
    def meth_cls(cls):
        print(cls.test_attr)

    def meth_ins(self):
        print(self.test_attr)

def main():
    game = Asteroids()
    game.test_attr = 1
    game.meth_cls()
    game.meth_ins()


if __name__ == "__main__":
    main()
