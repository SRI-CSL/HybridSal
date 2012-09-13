# Converting XML to internal polynomial representation

# Internal representation for 2*x + 3*x*y^2 + 3
# [ [2 {x:1}] [3 {y:2 x:1}] [3 {}] ], monomials are dictionaries
# Currently, polynomials are not normalized; no ordering

import HSalXMLPP

valueOf = HSalXMLPP.valueOf
getNameTag = HSalXMLPP.getNameTag
appArg = HSalXMLPP.appArg

def nameExpr2poly(node):
    var = valueOf(node)
    return [ [1, dict({var: 1})] ]

def numeral2poly(node):
    numstr = valueOf(node)
    # num  = int(numstr)
    num  = float(numstr)
    if num == 0:
        return [ ]
    return [ [ num, dict() ] ]

def isConstMono(cmu):
    return len(cmu) == 2 and len(cmu[1]) == 0

def isConstant(p):
    return len(p) == 0 or (len(p) == 1 and isConstMono(p[0]))

def getConstant(p):
    if len(p) == 0:
        return 0
    else:
        return p[0][0]

def polyNeg(p):
    "Return -p; destructive"
    for i in p:
        i[0] = -i[0]
    return p

def polyAdd(p1,p2):
    "Add polynomials p1 and p2; destroy p1"
    if len(p1) == 0:
        return p2
    if len(p2) == 0:
        return p1
    for cpp2 in p2:
        for cpp1 in p1:
            if (cpp1[1] == cpp2[1]):
                cpp1[0] += cpp2[0]
                break
        else:
            p1.append(cpp2)
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

def polyDiv(p, q):
    "DESTUCTIVE Divide polynomials p by CONSTANT q; destructive"
    if isConstant(q):
        c = getConstant(q)
        for i in p:
            i[0] = float(i[0])/c
    else:
        print "Error: Can't divide by NON-CONSTANT"
    return p

def infixApp2poly(node, ignoreNext = False):
    str1 = expr2poly(appArg(node,1), ignoreNext)
    str2 = getNameTag(node, 'NAMEEXPR')
    str3 = expr2poly(appArg(node,2), ignoreNext)
    if not(str2.find('+') == -1):
        return polyAdd(str1, str3)
    elif not(str2.find('-') == -1):
        return polySub(str1, str3)
    elif not(str2.find('*') == -1):
        return polyMul(str1, str3)
    elif not(str2.find('/') == -1):
        return polyDiv(str1, str3)
    else:
        print "Error: Unidentified operator %s" % str2
        return str1

def prefixApp2poly(node, ignoreNext = False):
    str0 = getNameTag(node, 'NAMEEXPR')
    i = 1
    expr = appArg(node,i)
    str1 = expr2poly(expr, ignoreNext)
    if not(str0.find('-') == -1):
        return polyNeg(str1)
    else:
        print "Error: Unidentified operator %s" % str0
        return str1

def app2poly(node, ignoreNext=False):
    if node.getAttribute('INFIX') == 'YES':
        return infixApp2poly(node, ignoreNext)
    else:
        return prefixApp2poly(node, ignoreNext)

def nextOperator2poly(node):
    print "Error: Nextoperator not allowed on RHSExpression %s" % node.nodeValue
    return None

def setPredExpr2poly(node):
    print "Error: SetPredExpr not allowed on RHSExpression %s" % node.nodeValue
    return None

def expr2poly(node, ignoreNext = False):
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
        if ignoreNext:
            return expr2poly( HSalXMLPP.getArg(node,1), ignoreNext)
        else:
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
    return None
    #if (node.nodeType == node.TEXT_NODE):
        #print node.data

