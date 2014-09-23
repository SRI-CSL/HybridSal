# Pretty Printer for VML
# Reads vmlfile.xml and outputs vmlfile.v

import xml.dom.minidom
import sys

def beautify(a):
    b = a.strip()
    if len(b) > 0 and b[0] == '\\':
        i = a.index(b)
        n = len(b)
        return a[i:i+n]
    else:
        return b

def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(beautify(i.data))

def getTag(node, tag, expected=True):
    """return first child named tag"""
    for i in node.childNodes:
        if i.nodeType == i.ELEMENT_NODE and i.tagName == tag:
            return i
    if expected:
        print >> sys.stderr, 'ERROR: Expected to find tag %s in node %s' %(tag, node.tagName)
    return None

def getNameTag(node, tag):
    nodes = node.getElementsByTagName(tag)
    if (len(nodes) < 1):
        print node.toxml()
        print >> sys.stderr, 'ERROR: Expected to find tag %s in above node' %tag
        sys.exit()
    childnode = nodes[0]
    return(valueOf(childnode))

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

def ppOp(node):
    return valueOf(node).strip()

def ppExpr(node):
    if node.tagName == 'identifier':
        return valueOf(node).strip()
    elif node.tagName == 'initidentifier':
        return valueOf(node).strip()+'__INIT'
    elif node.tagName == 'string':
        return valueOf(node).strip()
    elif node.tagName == 'number':
        return valueOf(node).strip()
    elif node.tagName == 'INITIAL':
        return 'initial()'
    elif node.tagName in ['pre','der']:
        var = getArg(node, 1)
        s1 = ppExpr(var)
        return node.tagName + '(' + s1 + ')'
    elif node.tagName == 'BAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        a2 = getArg(node, 3)
        s1 = ppOp(op)
        s2 = ppExpr(a1)
        s3 = ppExpr(a2)
        return '(' + s2 + ')' + s1 + '(' + s3 + ')'
    elif node.tagName == 'UAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        s1 = ppOp(op)
        s2 = ppExpr(a1)
        return s1 + '(' + s2 + ')'
    elif node.tagName == 'TAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        a2 = getArg(node, 3)
        a3 = getArg(node, 4)
        s1 = ppOp(op)
        s2 = ppExpr(a1)
        s3 = ppExpr(a2)
        s4 = ppExpr(a3)
        return s1 + '(' + s2 + ',' + s3 + ',' + s4 + ')'
    elif node.tagName == 'QAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        a2 = getArg(node, 3)
        a3 = getArg(node, 4)
        a4 = getArg(node, 5)
        s1 = ppOp(op)
        s2 = ppExpr(a1)
        s3 = ppExpr(a2)
        s4 = ppExpr(a3)
        s5 = ppExpr(a4)
        return s1 + '(' + s2 + ',' + s3 + ',' + s4 + ',' + s5 + ')'
    elif node.tagName == 'IF':
        c  = getArg(node, 1)
        v1 = getArg(node, 2)
        v2 = getArg(node, 3)
        s1 = ppExpr(c)
        s2 = ppExpr(v1)
        s3 = ppExpr(v2)
        return 'IF ' + s1 + ' THEN ' + s2 + ' ELSE ' + s3 
    elif node.tagName == 'set':
        ans = "{"
        n = int(node.getAttribute('cardinality'))
        first = True
        for i in range(n):
            if first:
                first = False
            else:
                ans += ',' 
            argi = getArg(node, i+1)
            ans += ppExpr(argi)
        ans += "}"
        return ans
    elif node.tagName == 'arrayselect':
        set1 = getArg(node, 1)
        index = getArg(node, 2)
        assert set1.tagName=='set', 'daexmlPP.ppExpr MISSING Code: {0}'.format(node.toprettyxml())
        setCard = int(set1.getAttribute('cardinality'))
        if setCard==1:
          return ppExpr(getArg(set1,1))
        if setCard==2:
          indexStr = ppExpr(index)
          val1 = ppExpr(getArg(set1,1))
          val2 = ppExpr(getArg(set1,2))
          return 'IF ' + indexStr + ' = 1 THEN ' + val1 + ' ELSE ' + val2 + ' ENDIF '
        print >> sys.stderr, 'daexmlPP.Warning: MISSING Code: {0}'.format(node.toprettyxml())
        return ppExpr(getArg(set1,1))
    else:
        print >> sys.stderr, 'MISSING CODE: Found {0} expression.'.format(node.tagName)
        print >> sys.stderr, 'MISSING CODE: {0}'.format(node.toprettyxml())
    return ""

def missing_code(node, names):
    for i in names:
        nodes = node.getElementsByTagName(i)
        if len(nodes) > 0:
            print >> sys.stderr, 'ERROR: MISSING CODE for tagname %s under %s' %(i, node.tagName)

def source_textPP(st, filepointer=sys.stdout, includestr=""):
    global fp 
    fp = filepointer
    eqns = st.getElementsByTagName("equations")[0]
    eqnL = eqns.getElementsByTagName("equation")
    for i in eqnL:
        print >> fp, ppEqn(i)

def ppEqn(e):
    arg1 = getArg(e, 1)
    arg2 = getArg(e, 2)
    s1 = ppExpr(arg1)
    s2 = ppExpr(arg2)
    return s1 + " = " + s2

def printUsage():
    print """
NAME: vml2verilog - pretty printer for VML 
SYNOPSIS: bin/vml2verilog <filename.xml>
DESCRIPTION: Pretty printer for VML.  Output is valid verilog. Output is printed on stdout.
CAVEAT: Prints a very small subset of VML.  Error messages arising from missing code are shown on stderr.
EXAMPLE: bin/vml2verilog examples/mux_8to1_flat_nc.xml
"""
    sys.exit()

def main():
    if len(sys.argv) != 2 or sys.argv[1][0] == '-':
        printUsage()
    dom = xml.dom.minidom.parse(sys.argv[1])
    source_textPP(dom)

if __name__ == "__main__":
    main()
