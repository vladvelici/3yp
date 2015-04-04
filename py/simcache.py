def undirected(s):
    """Undirected score cache factory. Changes s and returns it for convenience."""
    base = type(s)
    class Undirected(base):
        def score(self, a, b):
            a = str(a)
            b = str(b)
            if b > a:
                a, b = b, a

            if not (a in self._scorecache):
                score = base.score(self,a,b)
                self._scorecache[a] = {b: score}
                return score
            elif not (b in self._scorecache[a]):
                score = base.score(self,a,b)
                self._scorecache[a][b] = score
                return score
            return self._scorecache[a][b]
    s.__class__ = Undirected
    s._scorecache = {}
    return s

def dotprod(s):
    """Dot product cache factory. Changes s and returns it for convenience."""
    base = type(s)
    class Dotprod(base):
        def _dotprod(self, a, b):
            print("the new dotprod")
            a = str(a)
            b = str(b)
            if b > a:
                a, b = b, a

            if not (a in self._dpcache):
                score = base._dotprod(self, a, b)
                self._dpcache[a] = {b: score}
                return score
            elif not (b in self._dpcache[a]):
                score = base._dotprod(self, a, b)
                self._dpcache[a][b] = score
                return score
            print("dotprod cache hit.")
            return self._dpcache[a][b]

    s.__class__ = Dotprod
    s._dpcache = {}
    return s
