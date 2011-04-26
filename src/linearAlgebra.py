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
    for i in range(len(v)):
        v[i] = res[i]
    del res
    return v

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
    ans = copyA(A)
    for i in range(len(A)):
        for j in range(len(A)):
            ans[i][j] = A[j][i]
    return ans

def multiplyABTranspose(AB,A,B):
    "Return AB := A*B^T; return ans in AB"
    for i in range(len(A)):
        for j in range(len(A)):
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

def equalVector(c,d):
    for i in range(len(c)):
        if not(equal(c[i], d[i])):
            return 0
    return 1

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
    x = list(v)
    for i in range(len(v)):
        x[i] = 0
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
    ind = list()
    for i in range(n):
        firstone = 1
        for j in range(n):
            if not(equal(A[i][j], 0)):
                if (firstone == 1):
                    dep.append([j,i])
                    firstone = 0
                else:
                    if not(j in ind):
                        ind.append(j)
    return [dep,ind]

def extractSoln(A,b):
    "A is permuted Identity nxn matrix; b is n-vector"
    [dep,ind] = dependentIndependent(A)
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
        if (ind1 == -1 and noteq(b(0), 0)):
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

def eigenvector(A,lamb):
    "return vector in kernel of A-lamb*I"
    B = AminuslambI(A,lamb)
    b = zeros(A[0])
    ans = solve(B, b)
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
    "Return true if v is in Subspace spanned by subspace"
    "Assuming that v,subspace vectors are all normalized"
    v = projectOut(v, subspace)
    zero = zeros(v)
    if equalVector(v, zero):
        del v
        ans = None
    else:
        ans = v
    del zero
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

def neigenvalues(A):
    "Return MODULUS of all eigenvalues of nxn matrix A; DESTROYS A"
    n = len(A)
    if n == 0:
        return list()
    if n == 1:
        ans = list()
        ans.append(A[0][0])
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
            eigens.append(eigenvalue)
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
    for i in range(done):
        eigens.append(lamb)
    return eigens

def allEigenvectors(A, eigens):
    "find all eigenvectors corresponding to eigenvalues eigens"
    i = 0
    lambold = 0
    ans = list()
    while i < len(eigens):
        lamb = eigens[i]
        if i == 0 or not(lamb == lambold):
            eigenvectors = eigenvector(A,lamb)
            if len(eigenvectors) > 0:
                ans.append(lamb)
                ans.append(eigenvectors)
            eigenvectors = eigenvector(A,-lamb)
            if len(eigenvectors) > 0:
                ans.append(-lamb)
                ans.append(eigenvectors)
        lambold = lamb
        i += 1
    return ans

epsilon = 1e-4
