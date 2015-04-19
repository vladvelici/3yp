def precomputeSkip(s):
    base = type(s)
    class Precompute(base):
        def _dotprod(self, a, b):
            return self._dpcache[self.nid(a),self.nid(b)]
        def score(self, a, b):
            return self._scrcache[self.nid(a),self.nid(b)]
    s._dpcache = s.q.T * s.q
    j = s._dpcache.diagonal().repeat(s._dpcache.shape[0], axis=0)
    s._scrcache = j + j.transpose() - 2 * s._dpcache
    s.__class__ = Precompute
    return s

def score(s):
    """Score cache factory. Changes s and returns it for convenience."""
    base = type(s)
    class Score(base):
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
    s.__class__ = Score
    s._scorecache = {}
    return s

def dotprod(s):
    """Dot product cache factory. Changes s and returns it for convenience."""
    base = type(s)
    class Dotprod(base):
        def _dotprod(self, a, b):
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
            return self._dpcache[a][b]

    s.__class__ = Dotprod
    s._dpcache = {}
    return s
