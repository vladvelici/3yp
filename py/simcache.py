def precompute(s):
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

NONE = ""
DOTPROD = "dotprod"
SCORE = "score"
PRECOMPUTE = "precompute"
OPTIONS = [NONE, DOTPROD, SCORE, PRECOMPUTE]

def apply(s, cache_arg):
    """Apply the appropriate cache to s. It will change s and return it for
    convenience.

    Valid values for cache_arg are:
        - NONE: No cache at all.
        - DOTPROD: Caches the dot products in (undirected) dicts.
        - SCORE: Caches the score() method in (undirected) dicts.
        - PRECOMPUTE: Precomputes all the dot products and scores using matrix
            operations and stores them in two NxN numpy matrices.
            Very fast but uses O(2N^2) memory.
    """
    if cache_arg == NONE:
        return s
    elif cache_arg == DOTPROD:
        return dotprod(s)
    elif cache_arg == SCORE:
        return score(s)
    elif cache_arg == PRECOMPUTE:
        return precompute(s)
    raise "Invalid cache argument [%s] (for simcache.appy)" % cache_arg
