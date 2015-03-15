
class Undirected:
    """Undirected cache of similarities between nodes."""

    def __init__(self, s):
        self.s = s
        self._cache = {}

    def score(self, a, b):
        a = str(a)
        b = str(b)
        if b > a:
            a, b = b, a

        if not (a in self._cache):
            score = self.s.score(a,b)
            self._cache[a] = {b: self.s.score(a,b)}
            return score
        elif not (b in self._cache[a]):
            score = self.s.score(a,b)
            self._cache[a][b] = score
            return score
        else:
            return self._cache[a][b]
