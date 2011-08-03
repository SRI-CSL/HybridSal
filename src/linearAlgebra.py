# Generate constraints that need to be solved
# for finding the relational abstraction

# Input: Hybrid Sal model in XML syntax
# Output: Hybrid Sal model in XML syntax
# Output will have relational abstractions 
# of all continuous modes

# Idea for relational abstraction
# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

# we need eigenvalue and eigenvector computation for square matrix
# will do that using iteration method for now until scalability
# becomes an issue

import math
import sys  # for sys.exit()
from scipy import mat
from scipy import linalg
sqrt = math.sqrt
epsilon = 1e-4

def isConjugate(a,b,ans):
    """If a+-ib occurs in ans, return True"""
    i = 0
    while i < len(ans):
        if len(ans[i]) == 2:
            r = ans[i][0]
            c = ans[i][1]
            if equal(a,r) and equal(b+c,0):
                return True
        i += 2
    return False

def insertInAns(a, vec, ans):
    """Insert [a],[vec] into ans. If a is already in ans, append there."""
    i = 0
    while i < len(ans):
        if len(ans[i]) == 1:
            lamb = ans[i][0]
            if equal(lamb, a):
                ans[i+1].append(vec)
                return ans
        i += 2
    ans.append([a])
    ans.append([ vec ])
    return ans

def eigen(A):
    """Compute eigenvalues, eigenvector of A.
       Return value la,v = list of eigenvalues,matrix of eigenvectors"""
    if len(A) == 0:
        return list()
    matA = mat(A, float)
    la,v = linalg.eig(matA)
    assert len(v.shape) == 2	# v is a 2d array
    ans = list()
    for i in range(len(la)):
        a = la[i].real
        b = la[i].imag
        if isConjugate(a,b,ans):
            continue
        if equal(b, 0):
            vec = [ v[j][i].real for j in range(v.shape[0]) ]
            ans = insertInAns(a, vec, ans)
        else:
            ans.append([a,b])
            vec1 = [ v[j][i].real for j in range(v.shape[0]) ]
            vec2 = [ v[j][i].imag for j in range(v.shape[0]) ]
            ans.append([ vec1, vec2 ])
    return ans

def dotproduct(u,v):
    """dot product of two vectors"""
    sum = 0
    n = min(len(u), len(v))
    for i in range(n):
        sum += u[i]*v[i]
    return sum

def nmultiplyAv(A,v):
    """Destructive version of multiplyAv"""
    res = []
    for i in A:
        res.append(dotproduct(i,v))
    del v
    return res

def multiplyAv(A,v):
    "multiply nxn matrix A by nx1 vector v, given as 1xn row"
    res = list(v)
    return nmultiplyAv(A,res)

def copyA(A):
    ans = list(A)
    for i in range(len(A)):
        ans[i] = list(A[i])
    return ans

def delA(A):
    del A[:]
    del A

def transpose(A):
    "Return transpose of A in a new COPY"
    if len(A) == 0:
        return list()
    ans = [ [0 for i in range(len(A))] for j in range(len(A[0])) ]
    for i in range(len(A[0])):
        for j in range(len(A)):
            ans[i][j] = A[j][i]
    return ans

def multiplyABTranspose(AB,A,B):
    "Return AB := A*B^T; return ans in AB"
    for i in range(len(A)):
        for j in range(len(B)):
            AB[i][j] = dotproduct(A[i],B[j])
    return AB

def changeOfBasis(A,B):
    "Return B*A*B^T; A,B are assumed nxn matrices"
    AB = copyA(A)
    AB = multiplyABTranspose(AB, A, B)
    ABtrans = transpose(AB)
    AB = multiplyABTranspose(AB, B, ABtrans)
    delA(ABtrans)
    return AB

def nscale(v, a):
    "destructively update v := a*v where a is a scalar, v a vector"
    for i in range(len(v)):
        v[i] = a * v[i]
    return v

def modulus(v):
    "return modulus of the vector v"
    sum = 0
    for i in range(len(v)):
        sum += v[i]*v[i]
    return(pow(sum,0.5))

def nnormalize(v):
    "DESTRUCTIVE version of normalize"
    modv = modulus(v)
    if equal(modv, 0):
        return v
    v = nscale(v,1.0/modv)
    return(v)

def normalize(v):
    "return v ./ |v|"
    ans = list(v)
    return nnormalize(ans)

def Avbyv(A,v):
    "return |Av|/|v|"
    Av = multiplyAv(A,v)
    modAv = modulus(Av)
    del Av
    return(modAv/modulus(v))

def equal(c,d,tolerance=epsilon):
    return(abs(c-d) < tolerance)

def noteq(c,d,tolerance=epsilon):
    return(not(equal(c, d, tolerance=epsilon)))

def eigenvalueLargest(A):
    "return largest eigenvalue of A, iterated method"
    v = [0 for i in range(len(A))]
    v[0] = 1
    lambold = 1;
    lamb = Avbyv(A,v)
    i = 1
    #while noteq(lamb, lambold, tolerance=epsilon) and i < 300:
    while noteq((lamb-lambold)/lamb, 0, tolerance=epsilon) and i < 300:
        v = nnormalize(v)
        v = nmultiplyAv(A,v)
        lambold = lamb
        lamb = pow(lambold,float(i)/(i+1))*pow(Avbyv(A,v),1.0/(i+1))
        i += 1
        print "lamb %f" % lamb
    print "Number of iterations %d" % i
    print "lamb %f" % lamb
    print "lambold %f" % lambold
    print v
    return([lamb, nnormalize(v)])

def zeros(v):
    x = [0 for i in range(len(v))]
    return x

def solve1(A,b,j,ind):
    """row reduction: A[i][*] -= A[j][*] * A[i][ind]
       Assumes A[j][ind] == 1; Destructively updates A,b"""
    assert equal(A[j][ind], 1)
    for i in range(len(b)):
        if not(i == j): # and noteq(A[i][ind],0):
            tmp = A[i][ind]
            for k in range(len(A[0])):
                A[i][k] = A[i][k] - A[j][k] * tmp
            b[i] = b[i] - b[j] * tmp
    return([A,b])

def unitColumn(A,i,n):
    """Check if A[*][i] is a unit vector, and if so, return index j s.t. A[j][i]==1
       Else return -1. Assuming A has n rows."""
    ans = -1
    for j in range(n):
        if equal(A[j][i], 1):
            ans = j
        elif noteq(A[j][i], 0):
            ans = -1
            break
    return ans

def dependentIndependent(A):
    """A is nxm matrix; m variables [0..m-1] are partitioned into
       dependent, independent vars. Return value [ [[0,2],[1,0]], [2] ]
       indicating var 0,1 are defined by Equation 2,0 resply, and var 2 is independent"""
    n = len(A)
    assert n > 0
    m = len(A[0])
    dep = list()
    ind = range(m)
    for i in range(m):
        j = unitColumn(A,i,n)
        if j != -1:
            dep.append([i,j])
            ind.remove(i)
    return [dep,ind]

def extractSoln(A,b):
    """A is permuted Identity nxn matrix; b is n-vector"""
    #print "Extracting solution from Ax=b where A,b are"
    #print A
    #print b
    [dep,ind] = dependentIndependent(A)
    #print "dep, independent vars from A are"
    #print dep
    #print ind
    m = len(A[0])
    assert m == len(dep) + len(ind)
    allans = list()
    for i in ind:
        ans = [0 for j in range(m)]
        ans[i] = 1
        for [j,k] in dep:
            ans[j] = b[k] - A[k][i]
        allans.append(ans)
    if len(dep) > 0:
        ans = [0 for j in range(m)]
        for [j,k] in dep:
            ans[j] = b[k]
        allans.append(ans)
    delA(dep)
    del ind
    return allans

def checkAxEqb(A,x,b):
    """Check if Ax==b.  Divide by |b| before checking equality"""
    Ax = multiplyAv(A,x)
    Ax = nminusUV(Ax,b)
    #print "checking if zero: ",
    #print Ax
    modb = modulus(b)
    if modb > 1:
        for i in range(len(Ax)):
            Ax[i] /= modb
    #print "checking if zero: ",
    #print Ax
    ans = isZero(Ax)
    del Ax
    return ans

def checkAxbSolns(A,b,ans):
    """Check Ax==b for all x in ans. If not, delete x from ans"""
    j = 0
    n = len(ans)
    for i in range(n):
        if not(checkAxEqb(A,ans[j],b)):
            print "Deleting solution index ",
            print j
            del ans[j]
        else:
            j = j + 1
    return ans

def maxColumn(A,i,n,forbidden):
    """Return j notin forbidden s.t. |A[j][i]| is max in |A[*][i]| AND A[j][i] != 0"""
    ans = 0
    ind = -1
    for j in range(n):
        if not(j in forbidden) and (abs(A[j][i]) > ans) and noteq(A[j][i], 0):
            ans = abs(A[j][i])
            ind = j
    return ind

def solve(A,b):
    "Solve Ax = b; Destructive"
    #print "Solving ",
    #print A,
    #print b 
    n = len(b)	# n is the number of constraints
    assert n == len(A)
    if n == 0:
        return list()
    m = len(A[0])
    forbidden = list()
    for i in range(m):
        ind = maxColumn(A,i,n,forbidden)
        if ind == -1:
            continue
        else:
            forbidden.append(ind)
            tmp = 1.0/A[ind][i]
            A[ind] = nscale(A[ind], tmp)
            b[ind] *= tmp
            [A,b] = solve1(A,b,ind,i)
        #print "Solving ",
        #print A,
        #print b 
    del forbidden
    ans = extractSoln(A,b)
    print "Solving returned the following...checking now...",
    print ans
    ans = checkAxbSolns(A,b,ans)
    delA(A)
    del b
    return ans

def nminusUV(u,v):
    "Destructively update u := u - v;  u,v are vectors"
    for j in range(len(u)):
        u[j] = u[j] - v[j]
    return u

def AminuslambI(A,lamb):
    "A-lamb*I; NON-DESTRUCTIVE"
    B = copyA(A)
    for i in range(len(A)):
        B[i][i] = A[i][i] - lamb
    return(B)

def isZero(vec, tolerance=epsilon):
    """Is vec a zero vector"""
    for i in vec:
        if noteq(i,0,tolerance):
            return False
    return True

def removeIfZero(ans):
    """remove lists from ans that are equal to zero"""
    n = len(ans)
    for i in range(n):
        if isZero(ans[n-i-1]):
            del ans[n-i-1]
    return ans

def eigenvector(A,lamb):
    "return vector in kernel of A-lamb*I"
    B = AminuslambI(A,lamb)
    b = zeros(A[0])
    ans = solve(B, b)
    ans = removeIfZero(ans)
    delA(B)
    del b
    return ans

def expressAnUsingAis(A, vec, n):
    """Express A^n vec as a linear combination of A^{i}vec, i < n"""
    assert n >= 1
    B = [ None for i in range(n)]
    B[0] = list(vec)
    for i in range(n-1):
        B[i+1] = multiplyAv(A, B[i])
    b = multiplyAv(A, B[n-1])
    Btrans = transpose(B)
    delA(B)
    ans = solve(Btrans,b)
    print "solve returned",
    print ans
    del b
    assert len(ans) > 0
    del ans[1:]
    return ans[0]

def nproject(v, w):
    "destructively update w := (v.w)*w"
    p = dotproduct(v, w)
    return nscale(w, p)

def projectOut(v, subspace):
    "Destructively update v := v - projection of v on subspace"
    for i in range(len(subspace)):
        w = list(subspace[i])
        w = nproject(v, w)
        v = nminusUV(v, w)
        del w
        v = nnormalize(v) 
    return v

def inSubspace(v, subspace):
    """Project out subspace from v, return result
       Return NONE if v is in Subspace spanned by subspace
       Assuming that v,subspace vectors are all normalized"""
    v = projectOut(v, subspace)
    if isZero(v,epsilon/100):	# reducing tolerance becoz of nnormalize
        del v
        ans = None
    else:
        ans = v
    return ans

def orbit(A, v):
    "Return orthonormal BASIS of subspace(v,Av,A^2v,...)"
    print "Computing ORBIT ...",
    #print v
    subspace = list()
    v = nnormalize(v)
    v = inSubspace(v, subspace)
    while not(v == None):
        subspace.append(v)
        v = multiplyAv(A, v) # v is a NEW LIST
        v = nnormalize(v)
        v = inSubspace(v, subspace)
    return subspace

def isUnitColumn(A, i, n):
    "Is the i-th column of A a vector in direction i? Assuming A is nxn matrix"
    ans = 1
    for j in range(n):
        if (not(j == i) and not(equal(A[j][i], 0))):
            ans = 0
    return ans

def nremoveRowColumn(A, i, n):
    "Remove i-th row and i-th column from A"
    del A[i]
    for j in range(n-1):
        del A[j][i] 
    return A

def newUnitVector(v, i):
    ans = zeros(v)
    ans[i] = 1
    return ans

def extendToFull(basis, n):
    "Extend the partial orthonormal basis  to a full basis"
    j = len(basis)
    i = 0
    while (j < n and i < n):
        uniti = newUnitVector(basis[0], i)
        uniti = inSubspace(uniti, basis)
        if not(uniti == None):
            basis.append(uniti)
            j += 1
        i += 1
    assert len(basis) == n
    return basis

def dictUpdate(dictionary, key, value):
    """return dictionary with dict[key] += value"""
    for k,v in dictionary.iteritems():
        if equal(key, k):
            dictionary[k] = v + value
            return dictionary
    dictionary[key] = value
    return dictionary

def zeroEigenvalue(A, eigens):
    """Find if A has 0 as an eigenvalue; remove them all.
       Return newA, neweigens.  Input eigens=nil in FIRST call.
       If 0 is an eigenvalue, then neweigens=( (0,1,[0]) )
       In the first call, len(eigens)==0; in recursive calls, len==1"""
    n = len(A)
    zeros = [0 for i in range(n)]
    tmpA = copyA(A)
    ans = solve(tmpA,zeros)
    ans = removeIfZero(ans)
    if len(ans) == 0:
        return (A, eigens)
    lamb = 0.0
    vec = ans[0]
    subspace = list()
    subspace.append( nnormalize(vec) )
    done = len(subspace)
    newbasis = extendToFull(subspace, n)
    newA = changeOfBasis(A, newbasis)
    delA(A)
    delA(newbasis)
    for i in range(done):
        newA = nremoveRowColumn(newA,0,n-i)
    if len(eigens) == 0:
        eigens.append( (lamb, done, [0.0]) )
    # do not enter 0 twice...
    return zeroEigenvalue(newA, eigens)

def neigenvalues(A, ans=None):
    """Return MODULUS of all eigenvalues of nxn matrix A; DESTROYS A/
       return value list of (lamb, m, [a0, a1, ..., a_{m-1}]) s.t.
       \exists{v} satisfies A^m v = a0 v + a1 A v + ... + a_{m-1} A^{m-1}v"""
    if ans == None:
        ans = list()
    n = len(A)
    if n == 0:
        return ans
    if n == 1:
        ans.append( (A[0][0], 1, [A[0][0]]) )
        return ans
    print "****Computing eigenvalues of matrix A with dimension %d" % n
    print A
    if len(ans) == 0:
        (A, ans) = zeroEigenvalue(A, ans)
        if len(ans) > 0:
            print "0 is an eigenvalue of A"
            n = len(A)
            print "****Computing eigenvalues of matrix A with dimension %d" % n
            print A
        else:
            print "0 is NOT an eigenvalue of A"
    for i in range(n):
        if isUnitColumn(A,i,n):
            eigenvalue = A[i][i]
            newA = nremoveRowColumn(A,i,n)
            print "NewA after removing rowcolumn %d" % i
            print newA
            ans.append((eigenvalue, 1, [eigenvalue]))
            return neigenvalues(newA, ans)
    [lamb, vec] = eigenvalueLargest(A)
    subspace = orbit(A, vec)
    done = len(subspace)
    coeffs = expressAnUsingAis(A, vec, done)
    print "Subspace found...", 
    print subspace
    newbasis = extendToFull(subspace, n)
    newA = changeOfBasis(A, newbasis)
    delA(A)
    delA(newbasis)
    for i in range(done):
        newA = nremoveRowColumn(newA,0,n-i)
    # eigens = dictUpdate(eigens, lamb, done)
    ans.append((lamb, done, coeffs))
    return neigenvalues(newA, ans)

def allEigenvectorsReal(A, lamb, ans):
    eigenvectors = eigenvector(A, lamb)
    n = len(eigenvectors)
    if n > 0:
        ans.append([lamb])
        ans.append(eigenvectors)
    return ans

def allEigenvectorsComplex(A, coeffs, ans):
    """Append u,v to ans s.t. Au = a/2*u + d*v, Av = -d*u + a/2*v,
      where a = coeff[1] and b = coeff[0] and d = sqrt(-a^2-4b)/2"""
    assert len(coeffs) == 2
    b = coeffs[0]	# coeff of I
    a = coeffs[1]	# coeff of A
    # we find u by solving A^2-aA+(a^2/2+b)I u=0
    # (A-a/2)*(A-a/2)u = -d^2*u ... A^2 - a*A + (aa/4+d^2)
    # aa/4 + -aa-4b/4 = -b !!!
    print "Solving quadratic:",
    print "a = %f" % a,
    print "b = %f, A = " % b
    print  A
    Atrans = transpose(A)
    n = len(A)
    AA = [[0 for i in range(n)] for j in range(n)]
    AA = multiplyABTranspose(AA, A, Atrans)
    for i in range(n):
        for j in range(n):
             AA[i][j] -= (a*A[i][j])
    # now AA is A^2 - a*A
    print  AA
    for i in range(n):
        AA[i][i] -= b
    print  AA
    zerovec = [0 for i in range(n)]
    uv = solve(AA, zerovec)  # CHECK here
    uv = removeIfZero(uv)
    print "Found %d solutions to the quadratic equation" % len(uv)
    print (a/2.0, sqrt(-a*a-4*b)/2.0 )
    ans.append( [a/2.0, sqrt(-a*a-4*b)/2.0] )
    ans.append(uv)
    return ans

def findNZdiagonalEntry(tmpA, indices):
    """Return index j in indices s.t. tmpA[j][j] != 0.  tmpA is nxn"""
    for i in indices:
        if noteq(tmpA[i][i], 0):
            return i
    print "ERROR: No nonzero diagonal entry found"
    return -1

def inverse(A):
    """Return inverse of A.  Do not destroy A."""
    n = len(A)
    invA = [ [0.0 for i in range(n)] for i in range(n) ]
    for i in range(n):
        invA[i][i] = 1.0
    tmpA = copyA(A)
    indices = range(n)
    for i in range(n):
        j = findNZdiagonalEntry(tmpA, indices)
        assert (j != -1)
        print "processing index %d" % j
        indices.remove(j)
        factor = tmpA[j][j]
        for k in range(n):
            tmpA[j][k] /= float(factor)
            invA[j][k] /= float(factor)
        for l in range(n):
            if l == j:
                continue
            factor = tmpA[l][j]
            for k in range(n):
                tmpA[l][k] -= (float(factor) * tmpA[j][k])
                invA[l][k] -= (float(factor) * invA[j][k])
        #print tmpA
        #print invA
    delA(tmpA)
    return invA

def complexEigenAux(A, lamb, ans):
    """Check if there is an eigenvector corr. to complex eigenvalue
       a+ib s.t. a^2+b^2=lamb^2"""
    assert lamb > 0
    # A u = a u + b v ; A v = -b u + a v ;
    # (A-aI)^2 u = -b^2 u  -->  (A^2 + (a^2+b^2)I) u = 2a A u
    # 2a is a eigenvalue and u an eigenvector of A^{-1}(A^2 + lamb.I)
    invA = inverse(A)
    Atrans = transpose(A)
    n = len(A)
    AA = [[0 for i in range(n)] for j in range(n)]
    AA = multiplyABTranspose(AA, A, Atrans)
    for i in range(n):
        AA[i][i] += lamb
    delA(Atrans)
    tmp = transpose(AA)
    AA = multiplyABTranspose(AA, invA, tmp)
    # AA is A^{-1} * (A^2 + lamb.I)
    delA(invA)
    delA(tmp)
    yy = copyA(A)
    eigens = neigenvalues(yy)
    realEigens = realEigen(eigens)
    for i in realEigens:
        ans.append( [-lamb,i] )
    del yy
    del eigens
    del realEigens
    return ans

def allEigenvectors(A, reals, complexes):
    """find all eigenvectors corresponding to eigenvalues reals and complexes"""
    ans = list()
    for i in reals:
        ans = allEigenvectorsReal(A, i, ans)
    for coeffs in complexes:
        ans = allEigenvectorsComplex(A, coeffs, ans)
    return ans

def realEigen(eigens):
    """Return all real eigenvalues of A. eigens is a list of
       (l,m,[a0,...,a_{m-1}]) s.t. ex(v):A^mv = \sum ai A^i v"""
    ans = list()
    for newlamb,multiplicity,coeffs in eigens:
        if multiplicity == 1:
            ans.append(coeffs[0])
        elif multiplicity == 2:
            assert len(coeffs) == 2
            b = coeffs[0]	# coeff of I
            a = coeffs[1]	# coeff of A
            DD = a*a+4*b
            if equal(DD, 0):
                ans.append(a/2)
            elif DD > 0:
                ans.append(a/2 + sqrt(float(DD))/2.0)
        else:
            if isRealEigen(AA, newlamb):
                ans.append(newlamb)
            elif isRealEigen(AA, -newlamb):
                ans.append(-newlamb)
    return ans

def complexEigen(A, eigens):
    """Return all complex eigenvalues of A. eigens is a list of
       (l,m,[a0,...,a_{m-1}]) s.t. ex(v):A^mv = \sum ai A^i v
       and return value is list of (a0,a1) with same meaning."""
    ans = list()
    for newlamb,multiplicity,coeffs in eigens:
        if multiplicity == 1:
            continue
        elif multiplicity == 2:
            assert len(coeffs) == 2
            b = coeffs[0]	# coeff of I
            a = coeffs[1]	# coeff of A
            DD = a*a+4*b
            if DD < 0:
                ans.append( coeffs )
        else:
            ans = complexEigenAux(A, newlamb, ans)
    return ans

def eigenOld(A):
    """Replaced by new eigen function; see above"""
    yy = copyA(A)
    eigens = neigenvalues(yy)
    reals = realEigen(eigens)
    complexes = complexEigen(A, eigens)
    eigenvectors = allEigenvectors(A, reals, complexes)
    del yy
    del eigens
    del reals
    del complexes
    return eigenvectors

def test1():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    #print multiplyAv(xx,[0,0,1])
    print "Test of largest eigevalue computation of:"
    print xx
    [lamb, v] = eigenvalueLargest(xx) 
    print "Largest eigenvalue should be 3, computed %d: eigenvector=" % lamb
    print v
    print "*************************************"

def test2():
    print "Testing equation solving"
    A = [ [1,2,3], [1,3,6], [1,3,2] ]
    b = [ 6, 10, 6 ]
    ans = solve(A, b)
    print ans
    print "The solution above should be [[1 1 1]]"
    print "*************************************"

def test3():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    print "Test of ALL eigevalue computation of:"
    print xx
    eigens = neigenvalues(xx) 
    print eigens
    print "The above dict should be [(3,1,[3]), (2,1,[2]), (1,1,[1])]"
    print "*************************************"

def test4():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    sqrt2 = pow(2,0.5)
    a = sqrt2 / 2
    basis = [ [ a, a, 0], [a, -a, 0], [0, 0, 1] ]
    xx = changeOfBasis(xx, basis)
    print "Test of ALL eigevalue computation of:"
    print xx
    eigens = neigenvalues(xx) 
    print eigens
    print "The above dict should be [(3,1,[3]), (2,1,[2]), (1,1,[1])]"
    print "*************************************"

def test5():
    xx = [ [0,1], [-1,0] ]
    eigens = neigenvalues(xx)
    print eigens
    print "The above list should be [ (1, 2, [-1,0]) ]"
    print "*************************************"

def test6():
    xx = [ [0,1], [-1,0] ]
    print "Computing all eigenvectors for [[0,1],[-1,0]]"
    eigenvectors = eigen(xx)
    delA(xx)
    print "Computed eigenvectors:",
    print eigenvectors
    print "*************************************"

def test7():
    n = 4
    xx = [ [0 for i in range(n)] for j in range(n) ]
    xx[0][1] = -5
    xx[1][0] = 5
    xx[2][2] = 3
    xx[2][3] = -4
    xx[3][2] = 4
    xx[3][3] = 3
    eigenvectors = eigen(xx)
    print eigenvectors
    print "*************************************"

def test8():
    xx = [ [1,2,3], [2,4,6], [0,0,3] ]
    sqrt2 = pow(2,0.5)
    a = sqrt2 / 2
    basis = [ [ a, a, 0], [a, -a, 0], [0, 0, 1] ]
    xx = changeOfBasis(xx, basis)
    print "Test of ALL eigevalue computation of:"
    print xx
    eigens = neigenvalues(xx) 
    print eigens
    print "The above dict should be [(3,1,[3]), (0,1,[0]), (5,1,[5])]"
    print "*************************************"

def test9():
    xx = [ [1,1], [0,1] ]
    print "Testing inverse: Inverse of:"
    print xx
    xxinv = inverse(xx)
    print "is computed to be: :"
    print xxinv
    xx = [ [1,2,3], [-1,2,6], [-2,1,-3] ]
    print "Testing inverse: Inverse of:"
    print xx
    xxinv = inverse(xx)
    print "is computed to be: :"
    print xxinv
    xx = transpose(xx)
    I = copyA(xx)
    I = multiplyABTranspose(I, xxinv, xx)
    print "Product of A and its inverse is:"
    print I
    print "*************************************"

if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test8()
    test9()
