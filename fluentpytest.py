class HauntedBus:
    """A bus model haunted by ghost passengers"""

    def __init__(self, passengers=[]):
        self.passengers = passengers

    def pick(self, name):
        self.passenger.append(name)

    def drop(self, name):
        self.passenger.remove(name)
