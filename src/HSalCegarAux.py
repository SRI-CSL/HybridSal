# -----------------------------------------------------------------------------------
# Second Phase Algorithm:
# overinit = map from region (in init) to DNF;
# oversafe; overinv = same?
# for each region in Init: compute overapprox in eigen-directions; multi-directions
# we need a method to complete a DNF...
# e.g. x>0 or y>0 ---> x>0 AND y<=0 OR y>0 AND x<=0 OR x>0 AND y>0
# Then we need a method to compute an over-approx of a completed REGION
# for each overinitregion, overunsaferegion, we can check intersection
# we do this by computing time-bounds for possible intersection;
# then we can pick times in the MIDDLE...and compute Xn with EXACT unsafe...
# if it does; we can see if the corr. initial state is real/spurious and refine INIT-over
# if it doesn't; we refine unsafe-over
# refining algo: once you get a point; move it in all eigen-directions as long as it is
# spurious; get the most internal point ...we get n-factor multiplication...
# -----------------------------------------------------------------------------------

class CDS_Reach:
    def __init__(self, cds):
        self.cds = cds
        self.over_init = None
        self.over_unsafe = None
        self.unsafe = cds.safe.deep_copy()
        self.unsafe.neg()
        self.directions = None
    def set_directions(self):
        self.directions = []
        for (vec,val) in self.cds.geteigen():
            self.directions.append(vec)
        for (vec,val) in self.cds.getmulti():
            self.directions.append(vec)
        for (vec,wec,val1,val2) in self.cds.getquad():
            self.directions.append(vec)
            self.directions.append(wec)
    def get_directions(self):
        return self.directions
    def set_over_init(self):
        self.over_init = over_approx_dnf(self.cds.getinit(),self.directions)
    def set_over_unsafe(self):
        assert self.unsafe != None
        self.over_unsafe = over_approx_dnf(self.unsafe,self.directions)
    def set_all(self):
        self.set_directions()
        self.set_over_init()
        self.set_over_unsafe()
    def toStr(self):
        ans = self.cds.toStr()
        ans += '\nOverapprox of Init: '
        for (k,v) in self.over_init.items():
            ans += '{0}->{1}, '.format(k.tostr(),v.tostr())
        ans += '\nOverapprox of Unsafe:'
        for (k,v) in self.over_unsafe.items():
            ans += '{0}->{1}, '.format(k.tostr(),v.tostr())
        return ans

def over_approx_region(region, directions):
    '''given a Region, return a DNF that over-approximates it 
       in the given directions'''
    import HSalCegar
    # pass
    return HSalCegar.DNF.true()

def over_approx_dnf(dnf, directions):
    '''given a DNF, return a mapping 'over' from its regions to DNF s.t.
       over[region] = over_approx_region(region, directions)'''
    ans = {}
    for region in dnf.get_regions():
        ans[region] = over_approx_region(region, directions)
    return ans

def safety_check(cds):
    cdsr = CDS_Reach(cds)
    cdsr.set_all()
    print cdsr.toStr()

