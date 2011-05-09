# Generate relational abstraction of hybrid systems with
# linear dynamics in each mode

# Input:  Hybrid Sal model in XML syntax
# Output: Hybrid Sal model in XML syntax
# Output will have relational abstractions 
# of all continuous modes

# Caveat: FLOW should define ALL continuous variables.

# Algorithm for constructing relational abstraction:
# Partition variables into x;y s.t.
# d/dt (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# Then, d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
# If we fail to find eigenvector with real eigenvalues, 
# we need BOX invs and other things -- for later...

# We use eigenvalue and eigenvector computation from linearAlgebra.py
# linearAlgebra.py uses an iteration method for computing eigenvectors

# For imaginary eigenvalues:
# Suppose u' A1 = a u' + b v' and v' A1 = -b u' + a v'
# We find unknowns w1 and w2 and constant c1 and c2 s.t.
# if p1 = (u' x + w1' y + c1) and p2 = ( v' x + w2' y + c2) then
# d/dt p1 = a p1 + b p2 and d/dt p2 = -b p1 + a p2...
# for this to happen, the unknowns should satisfy the following:
# u' b1 + w1' b2 = a c1 + b c2  (Matching CONST COEFF)
# v' b1 + w2' b2 = -b c1 + a c2  (Matching CONST COEFF)
# u' A2 = a w1' + b w2'  (Matching y coeff)
# v' A2 = -b w1' + a w2'  (Matching y coeff)
# Solving this we get w1,w2, then we get c1,c2 and hence p1,p2
# If p1,p2 have the above relation, then we get the following relational abstraction:
# 3 cases: a >0, a = 0, a < 0
# if a > 0:
# p1 >= 0 and p2 >= 0 => p1' >= p1 and p2' >= 0 AND
# p1 <= 0 and p2 <= 0 => p1' <= p1 and p2' <= 0 AND
# p1 >= 0 and p2 <= 0 => p2' <= p2 and p1' >= 0 AND
# p1 <= 0 and p2 >= 0 => p2' >= p2 and p1' >= 0 


import xml.dom.minidom
import sys	# for sys.argv[0]
import linearAlgebra
import HSalExtractRelAbs
import polyrep # internal representation for expressions
import HSalXMLPP
import os.path
import shutil
import subprocess
#import polyrep2XML

equal = linearAlgebra.equal
isZero = linearAlgebra.isZero
exprs2poly = polyrep.exprs2poly
simpleDefinitionLhsVar = HSalExtractRelAbs.SimpleDefinitionLhsVar
isCont = HSalExtractRelAbs.isCont
#createNodeAnd = polyrep2XML.createNodeAnd
#createNodeInfixApp = polyrep2XML.createNodeInfixApp
#createNodeTagChild = polyrep2XML.createNodeTagChild
#createNodeTagChild2 = polyrep2XML.createNodeTagChild2
#createNodeTime = polyrep2XML.createNodeTime
#createNodePnew = polyrep2XML.createNodePnew
#createNodePold = polyrep2XML.createNodePold
#dictKey = polyrep2XML.dictKey

# ********************************************************************
# Functions for creating XML node for expressions
# ********************************************************************
def createNodeTagChildn(tag, childNodes):
    global dom
    node = dom.createElement(tag)
    for i in childNodes:
        node.appendChild(i)
    return node

def createNodeTagChild(tag, childNode):
    return createNodeTagChildn(tag, [childNode])

def createNodeTagChild2(tag, childNode, childNode2):
    return createNodeTagChildn(tag, [childNode, childNode2])

def createNodeTagChild3(tag, childNode, childNode2, childNode3):
    return createNodeTagChildn(tag, [childNode, childNode2, childNode3])

def createNodeTagChild4(tag, childNode, childNode2, childNode3, childNode4):
    return createNodeTagChildn(tag, [childNode, childNode2, childNode3, childNode4])

def createNodeTag(tag, val):
    global dom
    valNode = dom.createTextNode(val)
    return createNodeTagChild(tag, valNode)

def createNodeInfixApp(op, child1, child2):
    tupleNode = createNodeTagChild2("TUPLELITERAL", child1, child2)
    opNode = createNodeTag("NAMEEXPR", op)
    appNode = createNodeTagChild2("APPLICATION", opNode, tupleNode)
    appNode.setAttribute('INFIX', 'YES')
    return appNode

def createNodeTime(varName, rate):
    "Return varName' - varName / rate"
    rateNode = createNodeTag("NUMERAL", str(rate))
    varNode = createNodeTag("NAMEEXPR", varName)
    varPrimeNode = createNodeTagChild("NEXTOPERATOR", varNode.cloneNode(True))
    differenceNode = createNodeInfixApp('-', varPrimeNode, varNode)
    if equal(rate, 1):
        quotientNode = differenceNode
    else:
        quotientNode = createNodeInfixApp('/', differenceNode, rateNode)
    return quotientNode

def createNodeInfixAppRec(op, nodeList):
    n = len(nodeList)
    if n == 0:
        return None
    node = nodeList[0]
    for i in range(n-1):
        node = createNodeInfixApp(op, node, nodeList[i+1])
    return node

def createNodeAnd(nodeList):
    ans = createNodeInfixAppRec('AND', nodeList)
    if ans == None:
        return createNodeTag("NAMEEXPR", "TRUE")
    return ans

def createNodePlus(nodeList):
    ans = createNodeInfixAppRec('+', nodeList)
    #if ans == None:
        #return createNodeTag("NUMERAL", "0")
    return ans

def createNodeCXOne(c, x, flag):
    node1 = createNodeTag("NUMERAL", str(c))
    node2 = createNodeTag("NAMEEXPR", x)
    if flag:
        node2 = createNodeTagChild("NEXTOPERATOR", node2)
    node3 = createNodeInfixApp('*', node1, node2)
    return node3

def dictKey(varlist, value):
    "Return key given the value"
    for var,index in varlist.iteritems():
        if index == value:
            return var
    return None

def createNodeCX(c,x,flag):
    "create node for c1 x1+...+cn xn, use primes if flag"
    xindices = x.values()
    xindices.sort()
    n = len(xindices)
    cx = list()
    for i,v in enumerate(xindices):
        if not(equal(c[i], 0)):
            cx.append(createNodeCXOne(c[i], dictKey(x,v), flag))
    return createNodePlus(cx)

def createNodePaux(c,x,d,y,e,flag):
    "create node for c.x + d.y + e; with PRIME variables if flag"
    print "createNodePaux entering"
    node1 = createNodeCX(c,x,flag)
    node2 = createNodeCX(d,y,flag)
    if equal(e,0):
        node3 = None
    else:
        node3 = createNodeTag("NUMERAL", str(e))
    nodeL = [ node1, node2, node3 ]
    while None in nodeL:
        nodeL.remove(None)
    return createNodePlus(nodeL)

def createNodePnew(vec,x,A2transvec,y,const):
    return createNodePaux(vec,x,A2transvec,y,const,True)

def createNodePold(vec,x,A2transvec,y,const):
    return createNodePaux(vec,x,A2transvec,y,const,False)

def createNodeEigenInv():
    """0 <= nodePnew <= nodePold OR nodePold <= nodePnew <= 0 """
    fname = createNodeTag("IDENTIFIER", "eigenInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("xnew", "REAL")
    fparams = createNodeTagChild2("VARDECLS", vd1, vd2)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    zero = createNodeTag("NUMERAL", "0")
    fact1 = createNodeApp("<=", [ zero, "xnew" ])
    fact2 = createNodeApp("<=", [ "xnew", "xold" ])
    fact3 = createNodeApp("<=", [ "xold", "xnew" ])
    fact4 = createNodeApp("<=", [ "xnew", zero.cloneNode(True) ])
    fact12 = createNodeApp("AND", [ fact1, fact2 ])
    fact34 = createNodeApp("AND", [ fact3, fact4 ])
    fval = createNodeApp("OR", [ fact12, fact34 ])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createEigenInv(nodePnew,nodePold,lamb):
    "0 <= nodePnew <= nodePold OR nodePold <= nodePnew <= 0 if lamb < 0"
    "0 <= nodePold <= nodePnew OR nodePnew <= nodePold <= 0 if lamb > 0"
    "nodePold = nodePnew if lamb == 0"
    if lamb == 0:
        ans = createNodeInfixApp('=', nodePold, nodePnew)
    elif lamb < 0:
        ans = createNodeApp("eigenInv", [ nodePold, nodePnew ], infix=False)
    else:
        ans = createNodeApp("eigenInv", [ nodePnew, nodePold ], infix=False)
    return ans
# ********************************************************************

def simpleDefinitionRhsExpr(defn):
    "Return the RHS expression in definition def"
    rhs = defn.getElementsByTagName("RHSEXPRESSION")
    if rhs == None:
        return None
    else:
        return exprs2poly(rhs[0].childNodes)
    
def getFlow(defs):
    "Return flow of the continuous dynamics stored in definitions"
    flow = list()
    for i in defs:
        lhsvar = simpleDefinitionLhsVar(i)
        rhsexpr = simpleDefinitionRhsExpr(i)
        flow.append(lhsvar)
        flow.append(rhsexpr)
    print "printing flow"
    print flow
    return flow

def flow2var(flow):
    "extract variables from the flow"
    i = 0
    varlist = dict()
    while i < len(flow):
        varnamedot = flow[i]
        varlist[varnamedot[0:-3]] = i/2
        i += 2
    return varlist

def flow2Aibi(flowi, varlist):
    "flowi is an expression polynomial"
    n = len(varlist)
    Ai = [ 0 for i in range(n) ]
    bi = 0
    for [c,pp] in flowi:
        degree = sum(pp.values())
        if degree > 1:
            print "ERROR: Nonlinear dynamics found; can't handle"
            return None
        elif degree == 1:
            var = pp.keys()[0]
            index = varlist[var]
            Ai[index] = c
        else:
            bi = c
    return [Ai,bi]

def flow2Ab(flow):
    "get A,b matrices from the flow, if possible"
    "flow is a list of alternative variabledot, poly"
    varlist = flow2var(flow)
    n = len(varlist)
    i = 0
    A = list()
    b = list()
    while i < n:
        Aibi = flow2Aibi(flow[2*i+1], varlist)
        if Aibi == None:
            return None
        A.append(Aibi[0])
        b.append(Aibi[1])
        i += 1
    return [varlist,A,b]

def partitionAux(x, y, A, b):
    "Rearrange A,b s.t. (x;y) = (A1,A2;0,0)(x;y) + (b1;b2); DESTRUCTIVE"
    xindices = x.values()
    yindices = y.values()
    xindices.sort()
    xindices.reverse()
    yindices.sort()
    yindices.reverse()
    n = len(x)
    m = len(y)
    A2 = [ [0 for i in range(m) ] for j in range(n) ]
    b2 = [ 0 for i in range(m) ] 
    ib2 = m-1
    for i in yindices:
        del A[i]
        b2[ib2] = b[i]
        del b[i]
        ib2 -= 1
    iA2 = m-1
    for i in yindices:
        for j in range(len(A)):
            A2[j][iA2] = A[j][i]
            del A[j][i]
        iA2 -= 1
    print "A1 below should be nxn where n is %d" % n
    print A
    print "A2 below should be nxm where m is %d" % m
    print A2
    print "b1 below should be nx1 where n is %d" % n
    print b
    print "b2 below should be mx1 where m is %d" % m
    print b2
    return [A, A2, b, b2]

def partition(varlist, A, b):
    "output [x,y,A1,A2,b1,b2] s.t. (x;y) = (A1 A2; 0 0) (x;y) + (b1;b2)"
    x = dict()
    y = dict()
    index = 0
    for i in A:
        if isZero(i):
            var = dictKey(varlist, index)
            y[var] = index
        else:
            var = dictKey(varlist, index)
            x[var] = index
        index += 1
    [A1,A2,b1,b2] = partitionAux(x, y, A, b)
    return [x,y,A1,A2,b1,b2]

def multirateAbs(y, b2):
    "Return y[i]'-y[i]/b1[i] are equal for all i"
    "Return an XML SAL expression -- guard"
    m = len(b2)
    node0 = None
    nodes = list()
    yindices = y.values()
    yindices.sort()
    for i,v in enumerate(yindices):
        if equal(b2[i], 0):
            varName = dictKey(y, v)
            varNode = createNodeTag("NAMEEXPR", varName)
            varPrimeNode = createNodeTagChild("NEXTOPERATOR", varNode.cloneNode(True))
            nodes.append(createNodeInfixApp('=', varNode, varPrimeNode))
        elif node0 == None:
            node0 = createNodeTime(dictKey(y,v), b2[i])
        else:
            nodei = createNodeTime(dictKey(y,v), b2[i])
            tmp = node0.cloneNode(True)
            nodes.append(createNodeInfixApp('=', node0, nodei))
            node0 = tmp
    return createNodeAnd(nodes)

def createNodeVarType(varName, typeName):
    xold = createNodeTag("IDENTIFIER", varName)
    real = createNodeTag("TYPENAME", typeName)
    vd = createNodeTagChild2("VARDECL", xold, real)
    return vd

def createNodeApp(funName, argList, infix=True):
    """ funName(argList) """
    absNode = createNodeTag("NAMEEXPR", funName)
    argNode = createNodeTagChildn("TUPLELITERAL", [])
    for i in argList:
        if isinstance(i, basestring):
            node = createNodeTag("NAMEEXPR", i)
        else:
            node = i
        argNode.appendChild(node)
    ans = createNodeTagChild2("APPLICATION", absNode, argNode)
    if len(argList) == 2 and infix:
        ans.setAttribute('INFIX', 'YES')
    return ans

def createModNode():
    """mod(x:REAL):REAL = if x < 0 THEN -x ELSE x endif"""
    fname = createNodeTag("IDENTIFIER", "abs")
    vardecl = createNodeVarType("a", "REAL")
    fparams = createNodeTagChild("VARDECLS", vardecl)
    ftype = createNodeTag("TYPENAME", "REAL")
    a = createNodeTag("NAMEEXPR", "a")
    zero = createNodeTag("NUMERAL", "0")
    ifn = createNodeApp("<", [a, zero])		# a < 0
    thenn = createNodeApp("-", [ "a" ])		# -a
    elsen = createNodeTag("NAMEEXPR", "a")
    fval = createNodeTagChild3("CONDITIONAL", ifn, thenn, elsen)
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createNodeAbsVar(varName):
    """ |varName| """
    return createNodeApp("abs", [ varName ])

def createNodeQuadInv():
    """ if a < 0: |xnew|,|ynew| <= |xold| + |yold|
        |xnew| <= |xold| or |ynew| <= |yold|
        |xnew| <= |yold| or |ynew| <= |xold| """
    fname = createNodeTag("IDENTIFIER", "quadInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    fparams = createNodeTagChild4("VARDECLS", vd1, vd2, vd3, vd4)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    modxnew = createNodeAbsVar("xnew")
    modynew = createNodeAbsVar("ynew")
    modxold = createNodeAbsVar("xold")
    modyold = createNodeAbsVar("yold")
    xoldPlusyold = createNodeApp("+", [modxold, modyold])
    fact1 = createNodeApp("<=", [modxnew, xoldPlusyold])
    fact2 = createNodeApp("<=", [modynew, xoldPlusyold.cloneNode(True)])
    fact31 = createNodeApp("<=", [modxnew.cloneNode(True), modxold.cloneNode(True)])
    fact32 = createNodeApp("<=", [modynew.cloneNode(True), modyold.cloneNode(True)])
    fact3 = createNodeApp("OR", [ fact31, fact32 ])
    fact41 = createNodeApp("<=", [modxnew.cloneNode(True), modyold.cloneNode(True)])
    fact42 = createNodeApp("<=", [modynew.cloneNode(True), modxold.cloneNode(True)])
    fact4 = createNodeApp("OR", [ fact41, fact42 ])
    fval = createNodeAnd([fact1, fact2, fact3, fact4])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createQuadInv(nodePnew,nodePold,nodeQnew,nodeQold,a,b):
    """ if a < 0: |xnew|,|ynew| <= |xold| + |yold|
        |xnew| <= |xold| or |ynew| <= |yold|
        |xnew| <= |yold| or |ynew| <= |xold| """
    if a <= 0:
        ans=createNodeApp("quadInv", [ nodePold, nodeQold, nodePnew, nodeQnew])
    else:
        ans=createNodeApp("quadInv", [ nodePnew, nodeQnew, nodePold, nodeQold])
    return ans

def absGuardedCommandAux(varlist,A,b):
    """varlist is a dict from var to indices
    A,b are the A,b matrix defined wrt these indices
    Return an abstract GC"""
    [x,y,A1,A2,b1,b2] = partition(varlist,A,b)
    n = len(x)
    m = len(y)
    if n == 0:
        print "dx/dt is a constant for all x"
    guardAbs1 = multirateAbs(y, b2)
    A1trans = linearAlgebra.transpose(A1)
    eigen = linearAlgebra.eigen(A1trans)
    # CHECK above, tranpose added, [ l [ vectors ] l [ vectors ] ]
    print "The LEFT eigenvectors computed are:"
    print eigen
    num = len(eigen)
    i = 0
    A2trans = linearAlgebra.transpose(A2)
    nodeL = list()
    if not(guardAbs1 == None):
        nodeL.append(guardAbs1)
    while i < num:
        vectors = eigen[i+1]
        if vectors == None or len(vectors) == 0:
            continue
        lambL = eigen[i]
        i += 2
        if len(lambL) > 1:
            continue
        lamb = lambL[0]
        for vec in vectors:
            A2transvec = linearAlgebra.multiplyAv(A2trans, vec)
            for j in range(len(vec)):
                vec[j] *= lamb
            const = linearAlgebra.dotproduct(vec,b1)
            const += linearAlgebra.dotproduct(A2transvec,b2)
            nodePnew = createNodePnew(vec,x,A2transvec,y,const)
            nodePold = createNodePold(vec,x,A2transvec,y,const)
            # vec could be 0 vector and hence nodePnew could be None
            if not(nodePnew == None):
                nodeL.append(createEigenInv(nodePnew,nodePold,lamb))
            # Pick d' s.t. l d' = c' A2 or, d l = A2' c
            # Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
    i = 0
    while i < num:
        lamb = eigen[i]
        vectors = eigen[i+1]
        i += 2
        if vectors == None or len(vectors) == 0:
            continue
        if not(len(lamb) == 2):
            continue
        a = lamb[0]
        d = lamb[1]
        # add something to nodeL
        # for each vec in vectors, let u = vec
        # we want d/dt(u'x+w1'y+c1)= a*(u'x+w1'y+c1)+d*(v'x+w2'y+c2)
        # we want d/dt(v'x+w2'y+c2)= -d*(u'x+w1'y+c1)+a*(v'x+w2'y+c2)
        # first set v: v' = (u'A1 - a*u')/d
        # next find w1,w2,c1,c2 s.t.
        # u'*(A1*x+A2*y+b1)+w1'*b2 = a*(u'x+w1'y+c1)+d*(v'x+w2'y+c2)
        # i.e., u'*(A2*y+b1)+w1'*b2 = a*(w1'y+c1)+d*(w2'y+c2)
        # i.e., u' A2 = a*w1'+d*w2' and u'*b1+w1'*b2 = a*c1+d*c2
        # v'*(A1*x+A2*y+b1)+w2'*b2 = -d*(u'x+w1'y+c1)+a*(v'x+w2'y+c2)
        # i.e., v'*(A2*y+b1)+w2'*b2 = -d*(w1'y+c1)+a*(w2'y+c2)
        # i.e., v' A2 = -d w1' + a w2' and v'*b1+w2'*b2 = -d*c1+a*c2
        # find w1,w2 such that v' A2 = -d w1' + a w2' and u' A2 = a*w1'+d*w2' 
        # then find c1,c2 s.t v'*b1+w2'*b2 = -d*c1+a*c2 and u'*b1+w1'*b2 = a*c1+d*c2
        # w1,w2 satisfy v' A2 = -d w1' + a w2' and u' A2 = a*w1'+d*w2' 
        # w1,w2 satisfy (a*v'+d*u')*A2 = (a*a+d*d)*w2' 
        # w1,w2 satisfy (d*v'-a*u')*A2 = (-a*a-d*d)*w1' 
        # c1,c2 satisfy v'*b1+w2'*b2 = -d*c1+a*c2 and u'*b1+w1'*b2 = a*c1+d*c2
        # c1,c2 satisfy a*(v'*b1+w2'*b2)+d*(u'*b1+w1'*b2)=(a*a+d*d)*c2
        # c1,c2 satisfy d*(v'*b1+w2'*b2)-a*(u'*b1+w1'*b2)=(-a*a-d*d)*c1
        for vec in vectors:
            u = vec
            tmp = linearAlgebra.multiplyAv(A1trans, u)
            v = [ (tmp[j] - a*u[j])/d for j in range(n) ] # v=(u'A1 - a*u')/d
            # w2 satisfy (a*v'+d*u')*A2 = (a*a+d*d)*w2' 
            del tmp
            DD = a*a + d*d
            tmp = [ (a*v[j]+d*u[j])/DD for j in range(n) ]
            w2 = linearAlgebra.nmultiplyAv(A2trans, tmp)
            # w1 satisfy (d*v'-a*u')*A2 = (-a*a-d*d)*w1' 
            tmp = [ (-d*v[j]+a*u[j])/DD for j in range(n) ]
            w1 = linearAlgebra.nmultiplyAv(A2trans, tmp)
            # c2 satisfy a*(v'*b1+w2'*b2)+d*(u'*b1+w1'*b2)=(a*a+d*d)*c2
            # c1,c2 satisfy d*(v'*b1+w2'*b2)-a*(u'*b1+w1'*b2)=(-a*a-d*d)*c1
            tmp1 = linearAlgebra.dotproduct(v,b1)
            tmp1 += linearAlgebra.dotproduct(w2,b2)
            tmp2 = linearAlgebra.dotproduct(u,b1)
            tmp2 += linearAlgebra.dotproduct(w1,b2)
            c2 = (a*tmp1 + d*tmp2)/DD 
            c1 = (-d*tmp1 + a*tmp2)/DD
            #ux+w1y+c1 and vx+w2y+c2 are position,velocity pair.
            # 2 invariants: if a < 0: |xnew|,|ynew| <= |xold| + |yold|
            # 2 invariants: if a < 0: |xnew| <= |xold| or |ynew| <= |yold|
            # 2 invariants: if a < 0: |xnew| <= |yold| or |ynew| <= |xold|
            nodePnew = createNodePnew(u,x,w1,y,c1)
            nodePold = createNodePold(u,x,w1,y,c1)
            nodeQnew = createNodePnew(v,x,w2,y,c2)
            nodeQold = createNodePold(v,x,w2,y,c2)
            # vec could be 0 vector and hence nodePnew could be None
            if not(nodePnew == None):
                nodeL.append(createQuadInv(nodePnew,nodePold,nodeQnew,nodeQold,a,b))
    return createNodeAnd(nodeL)

# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

def makePrime(expr):
    """Replace var by var' in expr"""
    ans = expr.cloneNode(True)
    # get all NAMEEXPR nodes; if its parent is TUPLELITERAL then add prime to it
    nameexprs = ans.getElementsByTagName("NAMEEXPR")
    for i in nameexprs:
        parentNode = i.parentNode
        if parentNode.localName == 'TUPLELITERAL':
            icopy = i.cloneNode(True)
            primeVar = createNodeTagChild("NEXTOPERATOR", icopy)
            parentNode.replaceChild(oldChild=i, newChild=primeVar)
    return ans

def absAssignments(varlist):
    """For each variable in varlist, create RHSSELECTION"""
    global dom
    ans = dom.createElement("ASSIGNMENTS")
    for var,index in varlist.iteritems():
        nameexpr = createNodeTag("NAMEEXPR",var)
        nextop = createNodeTagChild("NEXTOPERATOR",nameexpr)
        ident = createNodeTag("IDENTIFIER","aZtQ")
        typename = createNodeTag("TYPENAME","REAL")
        expr = createNodeTag("NAMEEXPR","TRUE")
        setpred = createNodeTagChild3("SETPREDEXPRESSION",ident,typename,expr)
        rhssel = createNodeTagChild("RHSSELECTION",setpred)
        simpledef = createNodeTagChild2("SIMPLEDEFINITION",nextop,rhssel)
        ans.appendChild(simpledef)
    return ans

def absGuardedCommand(gc):
    "Return a new guarded command that is a rel abs of input GC"
    guard = gc.getElementsByTagName("GUARD")[0]
    assigns = gc.getElementsByTagName("ASSIGNMENTS")[0]
    defs = assigns.getElementsByTagName("SIMPLEDEFINITION")
    flow = getFlow(defs)
    [varlist,A,b] = flow2Ab(flow)
    print "A"
    print A
    print "b"
    print b
    guardExpr = HSalXMLPP.getArg(guard,1)
    guard = guardExpr.cloneNode(True)
    primeguard = makePrime(guard)
    guard = createNodeInfixApp('AND',guard,primeguard)
    absgc = absGuardedCommandAux(varlist,A,b)
    absguardnode = createNodeInfixApp('AND',guard,absgc)
    absguard = createNodeTagChild('GUARD',absguardnode)
    # absassigns = assigns.cloneNode(True)
    absassigns = absAssignments(varlist)
    return createNodeTagChild2('GUARDEDCOMMAND', absguard, absassigns)

def handleContext(ctxt):
    cbody = ctxt.getElementsByTagName("GUARDEDCOMMAND")
    for i in cbody:
        if isCont(i):
            absGC = absGuardedCommand(i)
            parentNode = i.parentNode
            if parentNode.localName == 'MULTICOMMAND':
                if not(absGC == None):
                    parentNode.appendChild(absGC)
                print "Parent is a multicommand"
            elif parentNode.localName == 'SOMECOMMANDS':
                print "Parent is SOMECOMMANDS"
                newnode = ctxt.createElement("MULTICOMMAND")
                oldChild = i.cloneNode(True)
                newnode.appendChild(oldChild)
                newnode.appendChild(absGC)
                parentNode.replaceChild(newChild=newnode, oldChild=i)
            else:
                print "Unknown parent node type"
    cbody = ctxt.getElementsByTagName("CONTEXTBODY")
    assert len(cbody) == 1
    cbody[0].insertBefore(newChild=createNodeQuadInv(),refChild=cbody[0].firstChild)
    cbody[0].insertBefore(newChild=createNodeEigenInv(),refChild=cbody[0].firstChild)
    cbody[0].insertBefore(newChild=createModNode(),refChild=cbody[0].firstChild)
    return ctxt

#def changeContextName(ctxt):
    #idnode = ctxt.getElementsByTagName("IDENTIFIER")[0]
    #for i in idnode.childNodes:
        #if i.nodeType == i.TEXT_NODE:
            #newnode = ctxt.createTextNode(i.data+"ABS")
            #idnode.replaceChild(newnode, i)
    #return ctxt

def moveIfExists(filename):
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def main():
    global dom
    filename = sys.argv[1]
    if not(os.path.isfile(filename)):
        print "File does not exist. Quitting."
        return 1
    basename,ext = os.path.splitext(filename)
    if ext == '.hxml':
        xmlfilename = filename
    elif ext == '.hsal':
        xmlfilename = basename + ".hxml"
        subprocess.call(["hybridsal2xml/hybridsal2xml", "-o", xmlfilename, filename])
        if not(os.path.isfile(xmlfilename)):
            print "hybridsal2xml failed to create XML file. Quitting."
            return 1
    else:
        print "Unknown file extension; Expecting .hsal or .hxml; Quitting"
        return 1
    dom = xml.dom.minidom.parse(xmlfilename)
    newctxt = handleContext(dom)
    absfilename = basename + ".haxml"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        print >> fp, newctxt.toxml()
    print "Created file %s containing the original+abstract model (XML)" % absfilename
    absfilename = basename + ".hasal"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the original+abstract model" % absfilename
    absXMLFile = basename + ".xml"
    moveIfExists(absXMLFile)
    with open(absXMLFile, "w") as fp:
        HSalExtractRelAbs.extractRelAbs(newctxt, fp)
    absSalFile = basename + ".sal"
    moveIfExists(absSalFile)
    with open(absSalFile, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the abstract model" % absSalFile
    return 0

if __name__ == '__main__':
    main()

