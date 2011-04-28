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

import xml.dom.minidom
import sys	# for sys.argv[0]
import linearAlgebra
import HSalExtractRelAbs

# represent expression as in polyrep
def valueOf(node):
    "return text value of node"
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getNameTag(node, tag):
    nnode = node.getElementsByTagName(tag)[0]
    return(valueOf(nnode))

def nameExpr2poly(node):
    var = valueOf(node)
    return [ [1, dict({var: 1})] ]

def numeral2poly(node):
    numstr = valueOf(node)
    print numstr
    num  = int(numstr)
    if num == 0:
        return [ ]
    else:
        return [ [ int(numstr), dict() ] ]

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    #print "Error: Argument not found!"
    return None

def appArg(node,index):
    #print node.toxml()
    tuples = node.getElementsByTagName('TUPLELITERAL')[0]
    return getArg(tuples,index)

def polyNeg(p):
    "Return -p; destructive"
    for i in p:
        print i[0]
        i[0] = -i[0]
    return p

def polyAdd(p1,p2):
    "Add polynomials p1 and p2; destroy p1"
    if len(p1) == 0:
        return p2
    if len(p2) == 0:
        return p1
    p1.extend(p2)
    return p1

def polySub(p1,p2):
    return polyAdd(p1, polyNeg(p2))

def monoMul(mu, nu):
    "Multiply two monomials mu and nu; non-destructive"
    res = list(mu)
    res[1] = mu[1].copy()
    res[0] = mu[0] * nu[0]
    for (key,val) in nu[1].items():
        v1 = res[1].get(key) 
        if v1 == None:
            res[1][key] = val
        else:
            res[1][key] += val
    return res

def polyMul(p, q):
    "Multiply polynomials p and q; non-destructive"
    res = list()
    for i in p:
        for j in q:
            res.append(monoMul(i,j))
    return res

def infixApp2poly(node):
    str1 = expr2poly(appArg(node,1))
    str2 = getNameTag(node, 'NAMEEXPR')
    str3 = expr2poly(appArg(node,2))
    if not(str2.find('+') == -1):
        return polyAdd(str1, str3)
    elif not(str2.find('-') == -1):
        return polySub(str1, str3)
    elif not(str2.find('*') == -1):
        return polyMul(str1, str3)
    else:
        print "Error: Unidentified operator %s" % str2
        return str1

def prefixApp2poly(node):
    str0 = getNameTag(node, 'NAMEEXPR')
    i = 1
    expr = appArg(node,i)
    str1 = expr2poly(expr)
    if not(str0.find('-') == -1):
        return polyNeg(str1)
    else:
        print "Error: Unidentified operator %s" % str0
        return str1

def app2poly(node):
    if node.getAttribute('INFIX') == 'YES':
        return infixApp2poly(node)
    else:
        return prefixApp2poly(node)

def nextOperator2poly(node):
    print "Error: Nextoperator not allowed on RHSExpression %s" % node.nodeValue
    return None

def setPredExpr2poly(node):
    print "Error: SetPredExpr not allowed on RHSExpression %s" % node.nodeValue
    return None

def expr2poly(node):
    # print node.localName
    if (node == None) or not(node.nodeType == node.ELEMENT_NODE):
        return list()
    if node.localName == "NAMEEXPR":
        return nameExpr2poly(node)
    elif node.localName == "APPLICATION":
        return app2poly(node)
    elif node.localName == "NUMERAL":
        return numeral2poly(node)
    elif node.localName == "NEXTOPERATOR":
        return nextOperator2poly(node)
    elif node.localName == "SETPREDEXPRESSION":
        return setPredExpr2poly(node)
    else:
        print node.toxml()
        print 'Type of expr unknown? Missing code'
    return None

def exprs2poly(nodes):
    for node in nodes:
        if (node.nodeType == node.ELEMENT_NODE):
            return expr2poly(node)
        #if (node.nodeType == node.TEXT_NODE):
            #print node.data

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
        lhsvar = HSalExtractRelAbs.SimpleDefinitionLhsVar(i)
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

def equal(a,b):
    return abs(a-b) < epsilon

def dictKey(varlist, value):
    "Return key given the value"
    for var,index in varlist.iteritems():
        if index == value:
            return var
    return None

def isZero(vec):
    "Is vec a zero vector"
    for i in vec:
        if not(equal(i,0)):
            return False
    return True

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
    print "b2 below should be mx1 where n is %d" % m
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

def createNodeTagChild(tag, childNode):
    node = dom.createElement(tag)
    node.appendChild(childNode)
    return node

def createNodeTag(tag, val):
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
    varPrimeNode = createNodeTagChild("NEXTOPERATOR", varNode)
    differenceNode = createNodeInfixApp('-', varPrimeNode, varNode)
    quotientNode = createNodeInfixApp('/', differenceNode, rateNode)
    return quotientNode

def createNodeAnd(nodeList):
    n = len(nodeList)
    if n == 0:
        return None
    node = nodeList[0]
    for i in range(n-1):
        node = createNodeInfixApp('AND', node, nodeList[i+1])
    return node

def multirateAbs(y, b2):
    "Return y[i]'-y[i]/b1[i] are equal for all i"
    "Return an XML SAL expression -- guard"
    m = len(b2)
    if m <= 1:
        return None
    yindices = y.values()
    yindices.sort()
    node = [None for i in range(m)]
    for i,v in enumerate(yindices):
        node[i] = createNodeTime(dictKey(v), b2[i])
    for i in range(m-1):
        node[i] = createNodeInfixApp('=', node[0], node[i+1])
    return createNodeAnd(node)

def absGuardedCommandAux(varlist,A,b,gc):
    "varlist is a dict from var to indices"
    "A,b are the A,b matrix defined wrt these indices"
    "Return an abstract GC"
    [x,y,A1,A2,b1,b2] = partition(varlist,A,b)
    n = len(x)
    m = len(y)
    if n == 0:
        print "dx/dt is a constant for all x"
    guardAbs1 = multirateAbs(y, b2)
    A1trans = linearAlgebra.transpose(A1)
    eigen = linearAlgebra.eigen(A1)
    # [ l [ vectors ] l [ vectors ] ]
    print "The eigenvectors computed are:"
    print eigen
    n = len(eigen)
    i = 0
    A2trans = linearAlgebra.transpose(A2)
    while i < n:
        lamb = eigen[i]
        vectors = eigen[i+1]
        if vectors == None or len(vectors) == 0:
            continue
        if equal(lamb, 0):
            continue
        for vec in vectors:
            A2transvec = linearAlgebra.multiplyAv(A2trans, vec)
            for i in range(len(A2transvec)):
                A2transvec[i] /= lamb
            # Pick d' s.t. l d' = c' A2 or, d l = A2' c
            # Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
        i += 2
    return None

# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

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
    absGuardedCommandAux(varlist,A,b,gc)
    return None

def handleContext(ctxt):
    cbody = ctxt.getElementsByTagName("GUARDEDCOMMAND")
    for i in cbody:
        if HSalExtractRelAbs.isCont(i):
            absGC = absGuardedCommand(i)
            parentNode = i.parentNode
            if parentNode.localName == 'MULTICOMMAND':
                if not(absGC == None):
                    parentNode.appendChild(absGC)
                print "Parent is a multicommand"
            elif parentNode.localName == 'SOMECOMMANDS':
                print "Parent is SOMECOMMANDS"
                newnode = ctxt.createElement("MULTICOMMAND")
                newnode.appendChild(i)
                newnode.appendChild(absGC)
                parentNode.replaceChild(newChild=newnode, oldchild=i)
            else:
                print "Unknown parent node type"
    return ctxt

epsilon = 1e-4
dom = xml.dom.minidom.parse(sys.argv[1])
handleContext(dom)

