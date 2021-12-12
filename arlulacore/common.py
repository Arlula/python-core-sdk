class ArlulaObject:
    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')
