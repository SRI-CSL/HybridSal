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

def multiplyAv(A,v):
    "multiply nxn matrix A by nx1 vector v, given as 1xn row"
    res = []
    for i in A:
        res.append(dotproduct(i,v))
    return res

def modulus(v):
    "return modulus of the vector v"
    sum = 0
    for i in range(len(v)):
        sum += v[i]*v[i]
    return(pow(sum,0.5))

def normalize(v):
    "return Av ./ |v|"
    modv = modulus(v)
    ans = list(v)
    for i in range(len(v)):
        ans[i] = v[i]/modv
    return(ans)

def Avbyv(A,v):
    "return |Av|/|v|"
    return(modulus(multiplyAv(A,v))/modulus(v))

def equal(c,d):
    return(abs(c-d) < epsilon)

def noteq(c,d):
    return(not(equal(c, d)))

def eigenvalue(A):
    "return largest eigenvalue of A, iterated method"
    #newA = exponent(A,10)
    i = 0
    lambold = 0;
    v = list(A[1])
    lamb = Avbyv(A,v)
    while noteq(lamb, lambold) and i < 100:
        v = normalize(v)
        v = multiplyAv(A,v)
        lambold = lamb
        lamb = Avbyv(A,v)
        i += 1
    print "Number of iterations %d" % i
    print "lamb %f" % lamb
    print "lambold %f" % lambold
    print normalize(v)
    print normalize(multiplyAv(A,v))
    return(lamb)

def zeros(A):
    x = list(A)
    for i in range(len(A)):
        x[i] = 0
    return x

def solve1(A,b,j,ind):
    "A[j][ind] != 0; eliminate rest"
    for i in range(len(b)):
        if not(i == j) and noteq(A[i][ind],0):
            tmp = A[i][ind]
            for k in range(len(b)):
                A[i][k] = A[i][k] - A[j][k] * tmp
            b[i] = b[i] - b[j] * tmp
    return([A,b])

def extractSoln(A,b):
    ans = list(b)
    for i in range(len(b)):
        ans[i] = None
    for i in range(len(b)):
        for j in range(len(b)):
            if equal(A[i][j], 1):
                ans[j] = b[i]
                break
    return ans

def solve(A,b):
    "Solve Ax = b"
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
            return None
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
    return(extractSoln(A,b))

def AminuslambI(A,lamb):
    "A-lamb*I"
    B = list(A)
    for i in range(len(A)):
        B[i][i] = A[i][i] - lamb
    return(solve(B,zeros(A[i])))

def eigenvector(A,lamb):
    "return vector in kernel of A-lamb*I"
    B = AminuslambI(A,lamb)
    b = list(A[0])
    for i in range(len(b)):
        b[i] = 0
    return solve(B,b)

def test1():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    #print multiplyAv(xx,[0,0,1])
    print "Test of largest eigevalue computation of:"
    print xx
    print eigenvalue(xx) 
    print "The largest eigenvalue should be 3"

def test2():
    print "Testing equation solving"
    A = [ [1,2,3], [1,3,6], [1,3,2] ]
    b = [ 6, 10, 6 ]
    ans = solve(A, b)
    print ans
    print "The solution above should be [1 1 1]"

epsilon = 1e-4
test1()
test2()

