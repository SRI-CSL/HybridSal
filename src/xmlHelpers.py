
import linearAlgebra
equal = linearAlgebra.equal

def mystr(k):
    """return floating value k as a string; str(k) uses e notation
       use 8 decimal places"""
    for i in range(6):
        if abs(k) >= pow(10,-i):
            fmt = '{0:.' + str(i+2) + 'f}'
            return fmt.format(k)
    print 'WARNING: Very small number detected'
    return '0'

# ********************************************************************
# Functions for creating XML node for expressions
# ********************************************************************

def setDom(dom_arg):
  global dom
  dom = dom_arg

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

# unused function createNodeTime, delete it
def createNodeTime(varName, rate):
    "Return varName' - varName / rate"
    rateNode = createNodeTag("NUMERAL", mystr(rate))
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

def createNodeCXFromLinXpr(linXpr,flag):
    "create node for c1 x1+...+cn xn, use primes if flag"
    n = len(linXpr)
    cx = list()
    for ci,xi in linXpr:
        if not(equal(ci, 0)):
            cx.append(createNodeCXOne(ci, xi, flag, None))
    return createNodePlus(cx)

def createNodeCXOne(c, x, flag, inputs):
    #node1 = createNodeTag("NUMERAL", mystr(c))
    if equal(c, 1):
        node1 = None
    else:
        #node1 = createNodeTag("NUMERAL", format(c,'.4f'))
        #Increase precision
        node1 = createNodeTag("NUMERAL", mystr(c))
    node2 = createNodeTag("NAMEEXPR", x)
    if flag:
        if not(x in inputs):
            node2 = createNodeTagChild("NEXTOPERATOR", node2)
    if node1 == None:
        node3 = node2
    else:
        node3 = createNodeInfixApp('*', node1, node2)
    return node3

def dictKey(varlist, value):
    "Return key given the value"
    for var,index in varlist.iteritems():
        if index == value:
            return var
    return None

def createNodeCX(c,x,flag,inputs):
    "create node for c1 x1+...+cn xn, use primes if flag && not(xi in inputs)"
    xindices = x.values()
    xindices.sort()
    n = len(xindices)
    cx = list()
    for i,v in enumerate(xindices):
        if not(equal(c[i], 0)):
            cx.append(createNodeCXOne(c[i], dictKey(x,v), flag, inputs))
    return createNodePlus(cx)

def createNodePaux(c,x,d,y,e,flag,inputs):
    """create node for c.x + d.y + e; with PRIME variables if 
       flag && xi not in inputs"""
    print "createNodePaux entering"
    node1 = createNodeCX(c,x,flag,inputs)
    node2 = createNodeCX(d,y,flag,inputs)
    if equal(e,0):
        node3 = None
    else:
        #node3 = createNodeTag("NUMERAL", format(e,'.4f'))
        node3 = createNodeTag("NUMERAL", mystr(e))
    nodeL = [ node1, node2, node3 ]
    while None in nodeL:
        nodeL.remove(None)
    return createNodePlus(nodeL)

def createNodePnew(vec,x,A2transvec,y,const,inputs):
    return createNodePaux(vec,x,A2transvec,y,const,True,inputs)

def createNodePold(vec,x,A2transvec,y,const):
    return createNodePaux(vec,x,A2transvec,y,const,False,None)

# ********************************************************************
