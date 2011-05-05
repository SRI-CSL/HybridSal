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

def dotproduct(u,v):
    "dot product of two vectors"
    sum = 0
    for i in range(len(u)):
        sum += u[i]*v[i]
    return sum

def nmultiplyAv(A,v):
    "Destructive version of multiplyAv"
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
    for i in range(len(v)):
        v[i] = v[i]/modv
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

def equal(c,d):
    return(abs(c-d) < epsilon)

def noteq(c,d):
    return(not(equal(c, d)))

def eigenvalueLargest(A):
    "return largest eigenvalue of A, iterated method"
    i = 0
    lambold = 0;
    v = list(A[1])
    lamb = Avbyv(A,v)
    while noteq(lamb, lambold) and i < 100:
        v = nnormalize(v)
        v = nmultiplyAv(A,v)
        lambold = lamb
        lamb = Avbyv(A,v)
        i += 1
    print "Number of iterations %d" % i
    #print "lamb %f" % lamb
    #print "lambold %f" % lambold
    return([lamb, nnormalize(v)])

def zeros(v):
    x = [0 for i in range(len(v))]
    return x

def solve1(A,b,j,ind):
    "A[j][ind] != 0; eliminate nonzero A[j][*] entries; Destructively update A,b"
    for i in range(len(b)):
        if not(i == j) and noteq(A[i][ind],0):
            tmp = A[i][ind]
            for k in range(len(b)):
                A[i][k] = A[i][k] - A[j][k] * tmp
            b[i] = b[i] - b[j] * tmp
    return([A,b])

def dependentIndependent(A):
    "Partition indices [0..n-1] into dependent, independent vars"
    n = len(A)
    dep = list()
    ind = range(n)
    for i in range(n):
        firstone = 1
        for j in range(n):
            if not(equal(A[i][j], 0)):
                if (firstone == 1):
                    dep.append([j,i])
                    ind.remove(j)
                    firstone = 0
    return [dep,ind]

def extractSoln(A,b):
    """A is permuted Identity nxn matrix; b is n-vector"""
    print "Extracting solution from Ax=b where A,b are"
    print A
    print b
    [dep,ind] = dependentIndependent(A)
    print "dep, independent vars from A are"
    print dep
    print ind
    assert len(b) == len(dep) + len(ind)
    allans = list()
    for i in range(len(ind)):
        ans = zeros(b)
        ans[ind[i]] = 1
        for [j,k] in dep:
            ans[j] = b[k] - A[k][ind[i]]
        allans.append(ans)
    if len(dep) > 0:
        ans = zeros(b)
        for [j,k] in dep:
            ans[j] = b[k]
        allans.append(ans)
    delA(dep)
    del ind
    return allans

def solve(A,b):
    "Solve Ax = b; Destructive"
    #print "Solving ",
    #print A,
    #print b 
    n = len(b)
    for j in range(n):
        ind1 = -1
        for i in range(n):
            if noteq(A[j][i], 0):
                ind1 = i
                break
        if (ind1 == -1 and noteq(b[j], 0)):
            return list()
        elif ind1 == -1:
            continue
        else:
            tmp = A[j][ind1]
            for i in range(n):
                A[j][i] /= tmp
            b[j] /= tmp
            #print "Solving ",
            #print A,
            #print b 
            [A,b] = solve1(A,b,j,ind1)
        #print "Solving ",
        #print A,
        #print b 
    ans = extractSoln(A,b)
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

def isZero(vec):
    """Is vec a zero vector"""
    for i in vec:
        if not(equal(i,0)):
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
    if isZero(v):
        del v
        ans = None
    else:
        ans = v
    return ans

def orbit(A, v):
    "Return orthonormal BASIS of subspace(v,Av,A^2v,...)"
    print "Computing ORBIT of"
    print v
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
    ans = list(v)
    for j in range(len(v)):
        if (j == i):
            ans[j] = 1
        else:
            ans[j] = 0
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

def neigenvalues(A):
    "Return MODULUS of all eigenvalues of nxn matrix A; DESTROYS A"
    n = len(A)
    if n == 0:
        return dict()
    if n == 1:
        ans = dict()
        ans[A[0][0]] = 1
        return ans
    for i in range(n):
        if isUnitColumn(A,i,n):
            eigenvalue = A[i][i]
            newA = nremoveRowColumn(A,i,n)
            print "NewA after removing rowcolumn %d" % i
            print newA
            eigens = neigenvalues(newA)
            print "eigens for newA are"
            print eigens
            eigens = dictUpdate(eigens, eigenvalue, 1)
            return eigens
    [lamb, vec] = eigenvalueLargest(A)
    subspace = orbit(A, vec)
    done = len(subspace)
    newbasis = extendToFull(subspace, n)
    newA = changeOfBasis(A, newbasis)
    delA(A)
    delA(newbasis)
    for i in range(done):
        newA = nremoveRowColumn(newA,0,n-i)
    eigens = neigenvalues(newA)
    eigens = dictUpdate(eigens, lamb, done)
    return eigens

def allEigenvectors(A, eigens):
    "find all eigenvectors corresponding to eigenvalues eigens"
    ans = list()
    for lamb,multiplicity in eigens.iteritems():
        eigenvectors = eigenvector(A,lamb)
        n = len(eigenvectors)
        if n > 0:
            ans.append(lamb)
            ans.append(eigenvectors)
        if n >= multiplicity:
            continue
        eigenvectors = eigenvector(A,-lamb)
        m = len(eigenvectors)
        if m > 0:
            ans.append(-lamb)
            ans.append(eigenvectors)
        if n + m >= multiplicity:
            continue
        print "COMPLEX eigenvectors EXIST"
    return ans

def eigen(A):
    yy = copyA(A)
    eigens = neigenvalues(yy)
    eigenvectors = allEigenvectors(A, eigens)
    return eigenvectors

epsilon = 1e-4

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
    print "The above dict should be {1:1,2:1,3:1}"
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
    print "The above dict should be {1:1, 2:1, 3:1}"
    print "*************************************"

def test5():
    xx = [ [0,1], [-1,0] ]
    eigens = neigenvalues(xx)
    print eigens
    print "The above dict should be {1:2}"
    print "*************************************"

def test6():
    xx = [ [0,1], [-1,0] ]
    yy = copyA(xx)
    eigens = neigenvalues(yy)
    eigenvectors = allEigenvectors(xx, eigens)
    delA(xx)
    print eigens
    print "The above dict should be {1:2}"
    print eigenvectors
    print "The above list should be [1, [[0,0]], -1, [[0,0]]]"
    print "*************************************"

if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
