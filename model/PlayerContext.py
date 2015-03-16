from model.World import World


class PlayerContext:
    def __init__(self, hockeyists, world: (None, World)):
        self.hockeyists = hockeyists
        self.world = world