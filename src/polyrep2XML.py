# From internal representation of expression, generate node
# Assumes dom is set.
import xml.dom.minidom

def createNodeTagChild(tag, childNode):
    node = dom.createElement(tag)
    node.appendChild(childNode)
    return node

def createNodeTagChild2(tag, childNode, childNode2):
    print("Debug printing  child1")
    print(childNode.toxml())
    print(childNode2.toxml())
    node = createNodeTagChild(tag, childNode)
    print("Debug printing node with 1 child")
    print(node.toxml())
    node.appendChild(childNode2)
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

def createNodeInfixAppRec(op, nodeList):
    n = len(nodeList)
    if n == 0:
        return None
    node = nodeList[0]
    for i in range(n-1):
        node = createNodeInfixApp(op, node, nodeList[i+1])
    return node

def createNodeAnd(nodeList):
    return createNodeInfixAppRec('AND', nodeList)

def createNodePlus(nodeList):
    return createNodeInfixAppRec('+', nodeList)

def createNodeCXOne(c, x, flag):
    node1 = createNodeTag("NUMERAL", str(c))
    node2 = createNodeTag("NAMEEXPR", x)
    if flag:
        node2 = createNodeTagChild("NEXTOPERATOR", node2)
    node3 = createNodeInfixApp('*', node1, node2)
    return node3

def dictKey(varlist, value):
    "Return key given the value"
    for var,index in varlist.items():
        if index == value:
            return var
    return None

def createNodeCX(c,x,flag):
    "create node for c1 x1+...+cn xn, use primes if flag"
    xindices = list(x.values())
    xindices.sort()
    n = len(xindices)
    cx = list()
    for i,v in enumerate(xindices):
        if not(c[i] == 0):
            cx.append(createNodeCXOne(c[i], dictKey(x,v), flag))
    return createNodePlus(cx)

def createNodePaux(c,x,d,y,e,flag):
    "create node for c.x + d.y + e; with PRIME variables if flag"
    #print "createNodePaux entering"
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

def createEigenInv(nodePnew,nodePold,lamb):
    "0 <= nodePnew <= nodePold OR nodePold <= nodePnew <= 0 if lamb < 0"
    "0 <= nodePold <= nodePnew OR nodePnew <= nodePold <= 0 if lamb > 0"
    "nodePold = nodePnew if lamb == 0"
    if lamb == 0:
        return createNodeInfixApp('=', nodePold, nodePnew)
    if lamb < 0:
        tmp = nodePold
        nodePold = nodePnew
        nodePnew = tmp
    node0 = createNodeTag('NUMERAL', '0')
    node1 = createNodeInfixApp('<=', node0, nodePold)
    node2 = createNodeInfixApp('<=', nodePold, nodePnew)
    node = createNodeInfixApp('AND', node1, node2)
    node1 = createNodeInfixApp('<=', nodePnew, nodePold)
    node2 = createNodeInfixApp('<=', nodePold, node0)
    node0 = createNodeInfixApp('AND', node1, node2)
    node = createNodeInfixApp('OR', node, node0)
    return node
