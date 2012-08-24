import xml.dom.minidom
import xml.parsers.expat
import sys
import os.path
import daexmlPP

TRUE = [ 'true', 'True' ]
FALSE = [ 'false', 'False' ]
Shapes = [ 'box', 'cylinder', 'sphere', 'pipecylinder', 'cone', 'pipe', 'beam', 'gearwheel', 'spring' ]

def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

def helper_create_tag_val(tag, val):
    global dom
    node = dom.createElement(tag)
    node.appendChild( dom.createTextNode( val ) )
    return node 

def helper_create_app(tag, childs):
    global dom
    node = dom.createElement(tag)
    for i in childs:
        node.appendChild( i )
    return node 

def simplify1(node):
    "x * 0 is 0"
    done = True
    bapps = node.getElementsByTagName('BAPP')
    for i in bapps:
        # check if this node is already deleted somehow...
        op = getArg(i, 1)
        if op.localName == 'BINARY_OPERATOR':
            opstr = valueOf(op).strip()
            if opstr == '*' or opstr == '+':
                arg1 = getArg(i, 2)
                arg2 = getArg(i, 3)
                # in case of critical overlap 0*c*0, i could be invalid
                if arg2 == None:
                    continue
                if arg2.localName == 'number':
                    tmp = arg1
                    arg1 = arg2
                    arg2 = tmp
                if arg1 != None and arg1.localName == 'number':
                    c = float(valueOf(arg1))
                    if opstr == '*' and c == 0:
                        node = replace(i, arg1, node)
                        done = False
                        print '*0',
                    elif opstr == '*' and c == 1:
                        node = replace(i, arg2, node)
                        done = False
                        print '*1',
                    elif opstr == '+' and c == 0:
                        node = replace(i, arg2, node)
                        done = False
                        print '+0',
            elif opstr == '-':
                arg1 = getArg(i, 2)
                arg2 = getArg(i, 3)
                if arg2 != None and arg2.localName == 'number':
                    c = float(valueOf(arg2))
                    if c == 0:
                        node = replace(i, arg1, node)
                        done = False
                        print '-0',
            elif opstr == '/':
                arg1 = getArg(i, 2)
                arg2 = getArg(i, 3)
                if arg2 != None and arg2.localName == 'number':
                    c = float(valueOf(arg2))
                    if c == 1:
                        node = replace(i, arg1, node)
                        done = False
                        print '/1',
            elif opstr == '==':
                arg1 = getArg(i, 2)
                arg2 = getArg(i, 3)
                if arg1.localName != 'identifier' or arg2.localName != 'identifier':
                    continue
                v1 = valueOf(arg1).strip()
                v2 = valueOf(arg2).strip()
                if v1 in Shapes or v2 in Shapes:
                    ans = helper_create_tag_val('identifier', str(v1 == v2))
                    #ans = helper_create_tag_val('identifier', 'True')
                    node = replace(i, ans, node)
                    done = False
                    print '==',
    return done

def simplify2(node):
    "setaccess <set> arg1 arg2 arg3 </set><access> 2</access> --> arg2"
    done = True
    sas = node.getElementsByTagName('setaccess')
    for i in sas:
        # check if this node is already deleted somehow...
        set1 = getArg(i, 1)
        set2 = getArg(i, 2)
        if set1.localName == 'set' and set2.localName == 'access':
            access = valueOf(set2).strip()
            access = access.split(',')
            access = [ int(j) for j in access ]
            for j in access:
                if set1.localName == 'set':
                    set1 = getArg(set1, j)
                else:
                    set1 = None
                    break
            if set1 != None:
                node = replace(i, set1, node)
                done = False
                print 's',
    return done
 
def vector2list(v):
    "v = set n1 n2 n2 /set --> [n1 n2 n3] or None"
    nstr = v.getAttribute('cardinality')
    assert nstr != ''
    n = int(nstr)
    args = [ getArg(v, i+1) for i in range(n) ]
    if not all( i.localName == 'number' for i in args ):
        return None
    args = [ float(valueOf(i)) for i in args ]
    return args

def list2vector(l):
    "l = [n1 n2 n3] --> v = set number(n1) number(n2) number(n3) /set"
    def isNumeric(obj):
        return isinstance(obj,int) or isinstance(obj,float)
    if all( isNumeric(i) for i in l ):
        c = [ helper_create_tag_val('number', str(i)) for i in l ]
    else:
        c = l
    ans = helper_create_app('set', c )
    ans.setAttribute('cardinality', str(len(c)))
    return ans

def cross(a,b,n):
    "a = [a1 a2 a3] b = [b1 b2 b3] return cross product of a b "
    assert n == 3
    c = range(n)
    c[0] = a[1]*b[2] - a[2]*b[1]
    c[1] = a[2]*b[0] - a[0]*b[2]
    c[2] = a[0]*b[1] - a[1]*b[0]
    return c

def transpose(a,b,c):
    "a = [a1 a2 a3], b = ..., c = ..., return [a1 b1 c1], ..."
    n = len(a)
    assert len(b) == n and len(c) == n
    A = [a, b, c]
    d = [ A[i][0] for i in range(n) ]
    e = [ A[i][1] for i in range(n) ]
    f = [ A[i][2] for i in range(n) ]
    return (d,e,f)

def simplify_tapp(node,done):
    "Modelica.Math.tempInterpol1(n,table,m)"
    def table2table(set1):
        "set1 is a table...convert it to python"
        rows = int(set1.getAttribute('cardinality'))
        assert rows > 0
        cols = -1
        table = []
        for j in range(rows):
                rowi = getArg(set1, j+1)
                assert rowi.localName == 'set'
                tmp = int(rowi.getAttribute('cardinality'))
                cols = tmp if cols == -1 else cols
                assert cols == tmp
                a = vector2list(rowi)
                table.append(a)
        return (table, rows, cols)
    def compressTable(rows, cols, table, icol):
        vals = [ i[icol-1] for i in table ]
        return (min(vals), max(vals))
    def compressedTable2ite(lb, ub, var):
        then1 = helper_create_tag_val('number', str(lb))
        then2 = helper_create_tag_val('number', str(ub))
        else2 = helper_create_tag_val('number', str(lb))
        cond = helper_create_tag_val('string', "TRUE")
        ite2 = helper_create_app('IF',[cond, then2, else2])
        return helper_create_app('IF',[cond.cloneNode(True), then1, ite2])
    def table2ite(n, m, table, icol, var):
        assert n >= 1 and len(table) == n
        iteThen = helper_create_tag_val('number', str(table[0][icol-1]))
        if n == 1:
            return iteThen
        iteElse = table2ite(n-1, m, table[1:], icol, var)
        less = helper_create_tag_val('BINARY_OPERATOR', '<=')
        tmp0 = helper_create_tag_val('number', str(table[0][0]))
        cond = helper_create_app('BAPP',[less, var.cloneNode(True), tmp0])
        return helper_create_app('IF',[cond, iteThen, iteElse])
    sas = node.getElementsByTagName('TAPP')
    for i in sas:
        func = getArg(i, 1)
        set1 = getArg(i, 3)
        n = getArg(i, 2)
        m = getArg(i, 4)
        if func.localName == 'TERNARY_OPERATOR' and valueOf(func).strip() == 'Modelica.Math.tempInterpol1' and set1.localName == 'set' and m.localName == 'number':
            (table,rows,cols) = table2table(set1)
            icol = int(valueOf(m))# column that computes output 
            assert icol <= cols
            # if all values in table are same, return value
            if all([table[j][icol-1] == table[0][icol-1] for j in range(rows)]):
                ans = helper_create_tag_val('number', str(table[0][icol-1]))
                node = replace(i, ans, node)
                done = False
                print 'T',
            elif n.localName == 'number':
                u = float(valueOf(n)) # input number
                # now implement the table lookup function
                if rows <= 1:
                    y = table[0][icol-1]
                elif u <= table[0][0]:
                    j = 1
                else:
                    j = 2
                    while j < rows and u >= table[j-1][0]:
                        j = 1 + j
                    j = j - 1
                u1 = table[j-1][0]
                u2 = table[j][0]
                y1 = table[j-1][icol-1]
                y2 = table[j][icol-1]
                assert u2 > u1, "Table index must be increasing"
                y = y1 + (y2 - y1) * (u - u1) / (u2 - u1)
                ans = helper_create_tag_val('number', str(y))
                node = replace(i, ans, node)
                done = False
                print 'T',
        elif func.localName == 'TERNARY_OPERATOR' and valueOf(func).strip() == 'Modelica.Blocks.Tables.CombiTable1D.tableIpo':
            tableId = getArg(i, 2)
            col = getArg(i, 3)
            var = getArg(i, 4)
            if tableId.tagName != 'set':
                continue
            if col.tagName != 'number':
                continue
            (table, rows, cols) = table2table(tableId)
            # replace i by NEW IF-THEN_ELSE NODE
            icol = int(valueOf(col))
            assert icol <= cols
            (lb,ub) = compressTable(rows, cols, table, icol)
            newnode = compressedTable2ite(lb, ub, var)
            # newnode = table2ite(rows, cols, table, icol, var)
            node = replace(i, newnode, node)
            done = False
            print 'T',
    return (node, done)

def simplify3(node):
    "SIMPLIFY TAPP;BAPP from_nxy set1 set2 </BAPP> --> set set1 set2 set3 /set"
    # remove all QAPPs with operator PackMaterial operator
    done = True
    (node,done) = simplify_tapp(node,done)
    sas = node.getElementsByTagName('QAPP')
    for i in sas:
        func = getArg(i, 1)
        if func.localName == 'QUAD_OPERATOR' and valueOf(func).strip() == 'Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape.PackMaterial':
            ans = helper_create_tag_val('number', str(0))
            node = replace(i, ans, node)
            done = False
            print 'd',
        elif func.localName == 'QUAD_OPERATOR' and valueOf(func).strip() == 'Modelica.Blocks.Tables.CombiTable1D.tableInit':
            arg1 = getArg(i, 2)
            arg2 = getArg(i, 3)
            arg3 = getArg(i, 4)
            if not(arg1.tagName == 'string' and valueOf(arg1).strip() == 'NoName'):
                continue
            if not(arg2.tagName == 'string' and valueOf(arg2).strip() == 'NoName'):
                continue
            node = replace(i, arg3, node)
            done = False
            print 'Q',
    sas = node.getElementsByTagName('BAPP')
    for i in sas:
        # check if this node is already deleted somehow...
        func = getArg(i, 1)
        set1 = getArg(i, 2)
        set2 = getArg(i, 3)
        if func.localName == 'SPECIAL_BINARY_OPERATOR' and set1.localName == 'set' and set2.localName == 'set':
            fname =  valueOf(func).strip()
            if fname != 'Modelica.Mechanics.MultiBody.Frames.TransformationMatrices.from_nxy':
                continue
            (a,b) = (vector2list(set1), vector2list(set2))
            if a == None or b == None:
                continue
            c = cross(a,b,len(a))
            (d,e,f) = transpose(a,b,c)
            (d,e,f) = (list2vector(d),list2vector(e),list2vector(f))
            ans = list2vector([d,e,f])
            node = replace(i, ans, node)
            done = False
            print 'nxy',
    return done
 
def simplify0(node):
    done = True
    done &= simplify0ITE(node)
    done &= simplify0set(node)
    done &= simplify0bool(node)
    done &= simplify0uapp(node)
    done &= simplify0bapp(node)
    done &= simplifyITE(node)	# ASHISH: Uncomment here to revert back!
    return done

def simplify0ITE(node):
    "ITE simplification" 
    done = True
    sas = node.getElementsByTagName('IF')
    for parentnode in sas:
        changedchild = getArg(parentnode, 1)
        if changedchild.tagName == 'identifier':
            if valueOf(changedchild).strip() in TRUE: 
                ans = getArg(parentnode, 2)
                node = replace(parentnode, ans, node)
                done = False
                print 'ITE ',
            elif valueOf(changedchild).strip() in FALSE:
                ans = getArg(parentnode, 3)
                node = replace(parentnode, ans, node)
                done = False
                print 'ITE ',
    return done

def simplify0set(node):
    done = True
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        func = valueOf(getArg(parentnode, 1)).strip()
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        if (func == 'cross' or func == '*') and arg1.localName == 'set' and arg2.localName == 'set':
            a = vector2list( arg1 )
            b = vector2list( arg2 )
            if a != None and b != None:
                n = len(a)
                if func == 'cross':
                    c = cross(a, b, n)
                    ans = list2vector( c )
                else:
                    c = a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
                    ans = helper_create_tag_val('number', str(c))
                node = replace(parentnode, ans, node)
                done = False
                print 'x',
        elif (func == '/' or func == '*') and arg1.localName == 'set' and arg2.localName == 'number':
            a = vector2list(arg1)
            if a != None:
                b = float(valueOf(arg2))
                c = [ i/b for i in a ] if func == '/' else [i*b for i in a]
                ans = list2vector( c )
                node = replace(parentnode, ans, node)
                done = False
                print 's*/n',
    return done

def simplify0bool(node):
    done = True
    sas = node.getElementsByTagName('UAPP')
    for parentnode in sas:
        func = valueOf(getArg(parentnode, 1)).strip()
        if not(func == 'not'):
            continue
        arg1 = getArg(parentnode, 2)
        v1 = valueOf(arg1).strip() if arg1.tagName == 'identifier' else ''
        if v1 in FALSE:
            ans = helper_create_tag_val('identifier', 'true')
            node = replace(parentnode, ans, node)
            done = False
            print 'b',
        elif v1 in TRUE:
            ans = helper_create_tag_val('identifier', 'false')
            node = replace(parentnode, ans, node)
            done = False
            print 'b',
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        if arg1 == None or arg2 == None:
            print 'Critical Overlap Case', parentnode.toxml()
            sys.exit(1)
        func = valueOf(getArg(parentnode, 1)).strip()
        v1 = valueOf(arg1).strip() if arg1.tagName == 'identifier' else ''
        v2 = valueOf(arg2).strip() if arg2.tagName == 'identifier' else ''
        if func == 'and':
            if v1 in FALSE or v2 in TRUE:
                node = replace(parentnode, arg1, node)
                done = False
                print 'b',
            elif v2 in FALSE or v1 in TRUE:
                node = replace(parentnode, arg2, node)
                done = False
                print 'b',
        elif func == 'or':
            if v1 in TRUE or v2 in FALSE:
                node = replace(parentnode, arg1, node)
                done = False
                print 'b',
            elif v2 in TRUE or v1 in FALSE:
                node = replace(parentnode, arg2, node)
                done = False
                print 'b',
    return done

def simplify0uapp(node):
    import math
    done = True
    sas = node.getElementsByTagName('UAPP')
    for parentnode in sas:
        func = valueOf(getArg(parentnode, 1)).strip()
        arg1 = getArg(parentnode, 2)
        arg1 = valueOf(arg1).strip() if arg1.tagName == 'number' else None
        if arg1 == None:
            continue
        if func == '-':
            val = -float(arg1)
        elif func == 'sqrt':
            val = float(arg1) ** (0.5)
        elif func == 'abs':
            val = abs(float(arg1))
        elif func == 'cos':
            val = math.cos(float(arg1))
        elif func == 'sin':
            val = math.sin(float(arg1))
        elif func == 'Real':
            val = float(arg1)
        elif func == 'noEvent':
            print 'Dont know what to do with noEvent'
            val = float(arg1)
            #sys.exit()
        elif func == 'der':
            val = 0.0
        else:
            print 'WARNING: Dont know what to do with {0}'.format(func)
            continue
        ans = helper_create_tag_val('number', str(val))
        node = replace(parentnode, ans, node)
        done = False
        print func,
    return done

def my_equal(node1, node2):
    "check if two nodes are syntactically equal"
    if node1.tagName != node2.tagName:
        return False
    if node1.tagName == 'number':
        return abs(float(valueOf(node1)) - float(valueOf(node2))) < 1e-6
    if node1.tagName == 'identifier':
        return valueOf(node1).strip() == valueOf(node2).strip()
    if node1.tagName.find('OPERATO') != -1:
        return valueOf(node1).strip() == valueOf(node2).strip()
    if node1.tagName == 'BAPP':
        return my_equal(getArg(node1,1), getArg(node2,1)) and my_equal(getArg(node1,2), getArg(node2,2)) and my_equal(getArg(node1,3), getArg(node2,3))
    if node1.tagName == 'pre':
        return my_equal(getArg(node1,1), getArg(node2,1))
    return False

def simplifyITE(node):
    '''simplify 0.3*IF '''
    done = True
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        if parentnode.parentNode == None:
            # this node was removed in a previous iteration of this loop; 
            # so ignore this node
            continue
        arg0 = getArg(parentnode, 1)
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        assert arg1 != None and arg2 != None
        if not(arg1.tagName == 'number' and arg2.tagName == 'IF'):
            continue
        func = valueOf(arg0).strip()
        if func not in ['/','*','+','-']:
            continue
        iteThen = getArg(arg2,2)
        iteElse = getArg(arg2,3)
        newThen = helper_create_app('BAPP',[arg0.cloneNode(True),arg1.cloneNode(True),iteThen.cloneNode(True)])
        newElse = helper_create_app('BAPP',[arg0.cloneNode(True),arg1.cloneNode(True),iteElse.cloneNode(True)])
        arg2 = replace(iteThen, newThen, arg2)
        arg2 = replace(iteElse, newElse, arg2)
        node = replace(parentnode, arg2, node)
        done = False
    # now simplify IF( ) + IF() expression
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        arg0 = getArg(parentnode, 1)
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        assert arg1 != None and arg2 != None
        if not(arg1.tagName == 'IF' and arg2.tagName == 'IF'):
            continue
        func = valueOf(arg0).strip()
        if func not in ['/','*','+','-']:
            continue
        cond1 = getArg(arg1,1)
        then1 = getArg(arg1,2)
        else1 = getArg(arg1,3)
        cond2 = getArg(arg2,1)
        then2 = getArg(arg2,2)
        else2 = getArg(arg2,3)
        if not(my_equal(cond1, cond2)):
            continue
        newThen = helper_create_app('BAPP',[arg0.cloneNode(True),then1.cloneNode(True),then2.cloneNode(True)])
        newElse = helper_create_app('BAPP',[arg0.cloneNode(True),else1.cloneNode(True),else2.cloneNode(True)])
        arg1 = replace(then1, newThen, arg1)
        arg1 = replace(else1, newElse, arg1)
        node = replace(parentnode, arg1, node)
        done = False
    return done

def SimplifyEqnsPhase5(dom, cstate, dstate):
    "IF ( ) - c --> IF ( );  IF ( ) < c --> IF"
    done = False
    while not done:
        (done,dom) = distributeOverIf(dom, cstate, dstate)
    done = False
    while not done:
        (done,dom) = ite2boolexpr(dom, cstate, dstate)
    return dom

def distributeOverIf(dom, cstate, dstate):
    done = True
    sas = dom.getElementsByTagName('BAPP')
    for parentnode in sas:
        arg0 = getArg(parentnode, 1)
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        assert arg1 != None and arg2 != None
        if not(arg1.tagName == 'IF'):
            continue
        if arg2.tagName not in ['number','identifier']:
            continue
        func = valueOf(arg0).strip()
        if func not in ['/','*','+','-','>','<']:
            continue
        iteThen = getArg(arg1,2)
        iteElse = getArg(arg1,3)
        newThen = helper_create_app('BAPP',[arg0.cloneNode(True),iteThen.cloneNode(True),arg2.cloneNode(True)])
        newElse = helper_create_app('BAPP',[arg0.cloneNode(True),iteElse.cloneNode(True),arg2.cloneNode(True)])
        arg1 = replace(iteThen, newThen, arg1)
        arg1 = replace(iteElse, newElse, arg1)
        dom = replace(parentnode, arg1, dom)
        done = False
        break
    return (done, dom)
    # now simplify IF( ) + IF() expression

def ite2boolexpr(dom, cstate, dstate):
    "IF (IF( ),..) --> IF newconditionEXPR .."
    def ite2exprRec(ite):
        if ite.tagName != 'IF':
            return ite.cloneNode(True)
        iteCond = ite2exprRec(getArg(ite,1))
        iteThen = ite2exprRec(getArg(ite,2))
        iteElse = ite2exprRec(getArg(ite,3))
        op = helper_create_tag_val('BINARY_OPERATOR', 'and')
        newExpr1 = helper_create_app('BAPP',[op,iteCond,iteThen])
        op2 = helper_create_tag_val('UNARY_OPERATOR', 'not')
        newExpr21 = helper_create_app('UAPP',[op2,iteCond.cloneNode(True)])
        newExpr2 = helper_create_app('BAPP',[op.cloneNode(True),newExpr21,iteElse])
        op = helper_create_tag_val('BINARY_OPERATOR', 'or')
        newExpr = helper_create_app('BAPP',[op, newExpr1, newExpr2])
        return newExpr
    done = True
    sas = dom.getElementsByTagName('IF')
    for parentnode in sas:
        arg0 = getArg(parentnode, 1)
        if not(arg0.tagName == 'IF'):
            continue
        # replace arg0 by newExpr in parentnode
        newExpr = ite2exprRec(arg0)
        parentnode = replace(arg0, newExpr, parentnode)
        done = False
        break
    return (done, dom)

def simplify0bapp(node):
    '''simplify'''
    import math
    done = True
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        assert arg1 != None and arg2 != None
        if arg1.tagName == 'number' and arg2.tagName == 'number':
            arg1 = valueOf(arg1).strip()
            arg2 = valueOf(arg2).strip()
            func = valueOf(getArg(parentnode, 1)).strip()
            if func == '/':
                val = float(arg1) / float(arg2)
            elif func == '*':
                val = float(arg1) * float(arg2)
            elif func == '+':
                val = float(arg1) + float(arg2)
            elif func == '-':
                val = float(arg1) - float(arg2)  # todo: atan2/ cross
            elif func == '^':
                val = float(arg1) ** float(arg2)  # todo: atan2/ cross
            elif func == 'max' and float(arg1) > float(arg2):
                val = float(arg1)
            elif func == 'max' and float(arg1) <= float(arg2):
                val = float(arg2)
            elif func == 'min' and float(arg1) > float(arg2):
                val = float(arg2)
            elif func == 'min' and float(arg1) <= float(arg2):
                val = float(arg1)
            elif func == 'atan2':
                val = math.atan2(float(arg1),float(arg2))
            elif (func == '<' or func == '&lt;') and float(arg1) < float(arg2):
                val = 'true'
            elif (func == '<' or func == '&lt;') and float(arg1) >= float(arg2):
                val = 'false'
            elif (func == '>' or func == '&gt;') and float(arg1) > float(arg2):
                val = 'true'
            elif (func == '>' or func == '&gt;') and float(arg1) <= float(arg2):
                val = 'false'
            elif func == '>=' and float(arg1) >= float(arg2):
                val = 'true'
            elif func == '>=' and float(arg1) < float(arg2):
                val = 'false'
            elif func == '<=' and float(arg1) <= float(arg2):
                val = 'true'
            elif func == '<=' and float(arg1) > float(arg2):
                val = 'false'
            elif func == '==' and float(arg1) == float(arg2):
                val = 'true'
            elif func == '==' and not(float(arg1) == float(arg2)):
                val = 'false'
            else:
                print 'unknown op {0} over floats'.format(func)
                val = None
            if isinstance(val, float):
                tag = 'number'
            elif isinstance(val, str): # true, false
                tag = 'identifier'
            else:
                tag = None
            if tag != None:
                ans = helper_create_tag_val(tag, str(val))
                node = replace(parentnode, ans, node)
                done = False
                print func,
    return done

def replace(node, newnode, root):
    '''replace node by newnode and call simplify'''
    if node == root:	# I am the expr
        root = newnode
    else:
        parentnode = node.parentNode
        parentnode.replaceChild(newChild=newnode,oldChild=node)
        # root = simplify(parentnode, newnode, root)
    return root

def substitute(expr, mapping):
    '''replace identifiers by their mapped values in expr'''
    ids = expr.getElementsByTagName('identifier')
    for i in ids:
        varname = valueOf(i).strip()
        if mapping.has_key(varname):
            varvalue = mapping[varname]
            # print 'found', varname
            # replace i by copy of varvalue in expr tree
            valuecopy = varvalue.cloneNode(True)
            expr = replace(i, valuecopy, expr)
            # print '.',
    # print 'All constant identifiers replaced'
    return(expr)

def getMapping(varvals,root, cstate, dstate):
    def extendMapping(mapping, identifier, value):
        '''extend mapping[identifier] = value'''
        # first normalize value
        val = valueOf(value).strip()
        if mapping.has_key(val):
            value = mapping[val]
        # next normalize mapping
        for k,v in mapping.items():
            val = valueOf(v).strip()
            if val == identifier:
                mapping[k] =  value
        mapping[identifier] =  value
        return mapping
    mapping = {}
    # varvals = newknownvars.getElementsByTagName('variablevalue')
    for i in varvals:
        arg1 = getArg(i, 1)
        arg2 = getArg(i, 2)
        lhs = valueOf(arg1).strip() if arg1.localName == 'identifier' else None
        rhs = valueOf(arg2).strip() if arg2.localName == 'identifier' else None
        # ASHISH: Disable non-substitutability of c/d-state variables
        # lhs = None if lhs in dstate or lhs in cstate else lhs
        # rhs = None if rhs in dstate or rhs in cstate else rhs
        if lhs == None and rhs == None:
            continue
        identifier = lhs if lhs != None else rhs
        expr = arg2 if lhs != None else arg1
        if expr.localName == 'number' or expr.localName == 'identifier' or expr.localName == 'set':
            print '.',
            mapping = extendMapping(mapping, identifier, expr)
            root.removeChild( i )
            # i.unlink()
            print '.',
    # print 'Deleting {0} variables'.format(len(deleted))
    return (mapping, root)

def SimplifyEqnsPhase3(dom):
    '''perform substitutions in the dom; output new dom'''
    eqns = dom.getElementsByTagName('equations')[0]
    # substitute values for vars in alleqns
    # find all 'identifier nodes' in eqns...replace it by
    # expression
    done = False
    neweqns = eqns
    while not done:
        done = True
        varvals = neweqns.getElementsByTagName('equation')
        mapping = {}
        for i in varvals:
            arg1 = getArg(i, 1)
            expr = getArg(i,2)
            if expr.localName == 'identifier':
                variable = valueOf(expr).strip()
                neweqns.removeChild( i )
                mapping[variable] = arg1
                break
            # if arg1.localName != 'number':
                # continue
            if expr.localName != 'BAPP' and expr.localName != 'UAPP':
                continue
            op = valueOf(getArg(expr,1)).strip()
            if op != '+' and op != '-':
                continue
            arg21 = getArg(expr,2)
            arg22 = getArg(expr,3)
            if arg21.localName != 'identifier' and (arg22 == None or arg22.localName != 'identifier'):
                continue
            if expr.localName == 'UAPP':
                tag = 'UAPP'
                minus = helper_create_tag_val('UNARY_OPERATOR', '-')
                childs = [ minus, arg1 ]
            elif arg21.localName == 'identifier':
                variable = valueOf(arg21).strip()
                op1 = '-' if op == '+' else '+'
                tag = 'BAPP'
                minus = helper_create_tag_val('BINARY_OPERATOR', op1)
                childs = [ minus, arg1, arg22 ]
            else:
                variable = valueOf(arg22).strip()
                ans_arg1 = arg1 if op == '+' else arg21
                ans_arg2 = arg21 if op == '+' else arg1
                tag = 'BAPP'
                minus = helper_create_tag_val('BINARY_OPERATOR', '-')
                childs = [ minus, ans_arg1, ans_arg2 ]
            value = helper_create_app(tag, childs)
            neweqns.removeChild( i )
            mapping[variable] = value
            break
        if len(mapping) > 0:
            neweqns = substitute(neweqns, mapping)
            done = False
        else:
            pass
        done &= simplify3(neweqns)
        done &= simplify1(neweqns)
        done &= simplify2(neweqns)
        done &= simplify0(neweqns)
    dom = replace(eqns, neweqns, dom)
    return dom

def equation2list(eqn):
    "output a list [(a1,T),(a2,F),(a3,T)] if eqn is a1 = a2 - a3"
    def expr2list(expr, sgn, mapping):
        if expr.tagName == 'identifier':
            variable = valueOf(expr).strip()
            freq = 0 if not mapping.has_key(variable) else mapping[variable]
            mapping[variable] = freq + 1 if sgn else freq - 1
            return mapping
        elif expr.tagName == 'number':
            const = float(valueOf(expr))
            freq = 0 if not mapping.has_key('number') else mapping['number']
            mapping['number'] = freq + const if sgn else freq - const
            return mapping
        elif expr.tagName == 'BAPP' and valueOf(getArg(expr,1)).strip() == '+':
            ans1 = expr2list( getArg(expr,2), sgn, mapping)
            ans2 = expr2list( getArg(expr,3), sgn, ans1)
            return ans2
        elif expr.tagName == 'BAPP' and valueOf(getArg(expr,1)).strip() == '-':
            ans1 = expr2list( getArg(expr,2), sgn, mapping)
            ans2 = expr2list( getArg(expr,3), not(sgn), ans1)
            return ans2
        elif expr.tagName == 'UAPP' and valueOf(getArg(expr,1)).strip() == '-':
            ans2 = expr2list( getArg(expr,2), not(sgn), mapping)
            return ans2
        elif sgn:
            if not mapping.has_key('pos'):
                mapping['pos'] = []
            mapping['pos'].append(expr)
            return mapping
        else:
            if not mapping.has_key('neg'):
                mapping['neg'] = []
            mapping['neg'].append(expr)
            return mapping
        return mapping
    arg1 = getArg(eqn, 1)
    arg2 = getArg(eqn, 2)
    if arg2 == None:
        print 'ERROR: ', eqn.toprettyxml()
        sys.exit(1)
    # print 'Input eqn is {0}'.format(daexmlPP.ppEqn(eqn))
    ans1 = expr2list(arg1, True, {})
    ans2 = expr2list(arg2, False, ans1)
    #print 'Output eqn is {0} = 0'.format(daexmlPP.ppExpr(list2equation(ans2,True)))
    return ans2

def list2equation(myeqn, flag):
    "if flag then add all elements, else negate"
    def list2equationAux(ansp):
        "+(ansp)"
        if len(ansp) == 0:
            return None
        elif len(ansp) == 1:
            return ansp[0].cloneNode(True)
        else:
            ans2 = list2equationAux(ansp[1:])
            plus = helper_create_tag_val('BINARY_OPERATOR', '+')
            return helper_create_app('BAPP', [plus,ansp[0].cloneNode(True),ans2])
    anslistp = []
    anslistn = []
    if myeqn.has_key('number'):
        if myeqn['number'] != 0:
            value = myeqn['number'] if flag else 0-myeqn['number']
            anslistp.append( helper_create_tag_val('number', str(value)) )
        del myeqn['number']
    if myeqn.has_key('pos'):
        if flag:
            anslistp.extend( myeqn['pos'] )
        else:
            anslistn.extend( myeqn['pos'] )
        del myeqn['pos']
    if myeqn.has_key('neg'):
        if flag:
            anslistn.extend( myeqn['neg'] )
        else:
            anslistp.extend( myeqn['neg'] )
        del myeqn['neg']
    for (k,v) in myeqn.items():
        newv = v if flag else -v
        if newv == 1:
            anslistp.append( helper_create_tag_val('identifier', k) )
        elif newv == -1:
            anslistn.append( helper_create_tag_val('identifier', k) )
        elif newv == 0:
            pass
        else:
            nodek = helper_create_tag_val('identifier', k)
            nodev = helper_create_tag_val('number', str(newv))
            mult = helper_create_tag_val('BINARY_OPERATOR', '*')
            anslistp.append( helper_create_app('BAPP', [mult,nodev,nodek]) )
    expr1 = list2equationAux(anslistp)
    expr2 = list2equationAux(anslistn)
    if expr1 == None and expr2 == None:
        ans = helper_create_tag_val('number', '0')
    elif expr2 == None:
        ans = expr1
    elif expr1 == None:
        minus = helper_create_tag_val('UNARY_OPERATOR', '-')
        ans = helper_create_app('UAPP', [minus,expr2])
    else:
        minus = helper_create_tag_val('BINARY_OPERATOR', '-')
        ans = helper_create_app('BAPP', [minus,expr1,expr2])
    return ans

def occurs(var, myeqn):
    "Return true if var occurs in myeqn[pos] and neg; or if special identifier ooccurs in there"
    def occursNode(var, node):
        # sids = node.getElementsByTagName('sidentifier')
        # if sids != None and len(sids) > 0:
            # for sid in sids: 
                # if valueOf(sid).find(var) != -1:
                    # return True
        # if node.tagName == 'sidentifier' and valueOf(node).find(var) != -1:
            # return True
        ids = node.getElementsByTagName('identifier')
        for i in ids:
            if valueOf(i).strip() == var:
                return True
        if node.tagName == 'identifier' and valueOf(node).find(var) != -1:
            return True
        return False
    def occursL(var, nodeL):
        for i in nodeL:
            if occursNode(var, i):
                return True
        return False
    if myeqn.has_key('pos') and occursL(var, myeqn['pos']):
        return True
    if myeqn.has_key('neg') and occursL(var, myeqn['neg']):
        return True
    return False

def SimplifyEqnsPhase4(dom, cstate, dstate):
    '''x = expr or -x = expr : replace x by its value in new dom'''
    # substitute values for vars in alleqns
    # find all 'identifier nodes' in eqns...replace it by
    # expression
    done = False
    knownVars = dom.getElementsByTagName('knownVariables')[0]
    eqns = dom.getElementsByTagName('equations')[0]
    neweqns = eqns
    newknownvars = knownVars
    while not done:
        done = True
        varvals = newknownvars.getElementsByTagName('variablevalue')
        while varvals != None and len(varvals) > 0:
            done = False
            mapping = {}
            i = varvals[0]
            var = getArg(i,1)
            varname = valueOf(var).strip()
            if var.tagName != 'identifier':
                newknownvars.removeChild( i )
                i.tagName = 'equation'
                neweqns.appendChild( i )
            elif varname in cstate or varname in dstate:
                print 'knownVar {0} cannot be a state variable'.format(varname)
                print 'WARNING:potential algebraic equation; may fail later'
                newknownvars.removeChild( i )
                i.tagName = 'equation'
                neweqns.appendChild( i )
            else:
                assert varname not in cstate, 'knownVar {0} cant be in cstate'.format(varname)
                assert varname not in dstate, 'knownVar {0} cant be in dstate'.format(varname)
                val = getArg(i,2)
                mapping[varname] = val
                newknownvars.removeChild( i )
                newknownvars = substitute(newknownvars, mapping)
                neweqns = substitute(neweqns, mapping)
            varvals = newknownvars.getElementsByTagName('variablevalue')
        varvals = neweqns.getElementsByTagName('equation')
        mapping = {}
        for i in varvals:
            myeqn = equation2list(i)
            variable = None
            for (k,v) in myeqn.items():
                if k != 'pos' and k != 'neg' and k != 'number':
                    if not occurs(k, myeqn) and k not in cstate and k not in dstate:
                        variable = k
                        freq = v
                        break
            if variable != None:
                del myeqn[variable]
                value = list2equation(myeqn, True if freq==-1 else False)
                neweqns.removeChild( i )
                mapping[variable] = value
                print '{0} --> {1}'.format(variable,daexmlPP.ppExpr(value))
                break
        if len(mapping) > 0:
            neweqns = substitute(neweqns, mapping)
            done = False
        else:
            pass
        done &= simplify3(neweqns)
        done &= simplify1(neweqns)
        done &= simplify2(neweqns)
        done &= simplify0(neweqns)
    dom = replace(eqns, neweqns, dom)
    return dom

def SimplifyEqnsPhase2(dom):
    '''x = expr or -x = expr : replace x by its value in new dom'''
    eqns = dom.getElementsByTagName('equations')[0]
    # substitute values for vars in alleqns
    # find all 'identifier nodes' in eqns...replace it by
    # expression
    done = False
    neweqns = eqns
    while not done:
        done = True
        varvals = neweqns.getElementsByTagName('equation')
        mapping = {}
        for i in varvals:
            arg1 = getArg(i, 1)
            if arg1.localName == 'identifier':
                identifier = valueOf(arg1).strip()
                expr = getArg(i,2)
                neweqns.removeChild( i )
                mapping[identifier] = expr
                break
            elif arg1.localName == 'UAPP':
                op1 = valueOf(getArg(arg1, 1)).strip()
                if op1 != '-':
                    continue
                arg1 = getArg(arg1, 2)
                if arg1.localName != 'identifier':
                    continue
                identifier = valueOf(arg1).strip()
                expr = getArg(i,2)
                minus = helper_create_tag_val('UNARY_OPERATOR', '-')
                newexpr = helper_create_app('UAPP', [minus,expr])
                neweqns.removeChild( i )
                mapping[identifier] = newexpr
                break
        if len(mapping) > 0:
            neweqns = substitute(neweqns, mapping)
            done = False
        else:
            pass
        done &= simplify3(neweqns)
        done &= simplify1(neweqns)
        done &= simplify2(neweqns)
        done &= simplify0(neweqns)
    dom = replace(eqns, neweqns, dom)
    return dom

def simplifyPreDer(varval, eqn, cstate, dstate):
    "find value for der(v) for all v in cstate; keep just ONE definition"
    def replacederx(node, var, val):
        "replace der(var) by val in node"
        ders = node.getElementsByTagName('der')
        done = True
        if ders == None:
            return done
        for i in ders:
            arg1 = getArg(i, 1)
            name = valueOf(arg1) if arg1.tagName == 'identifier' else None
            if name != None and name.strip() == var:
                node = replace(i, val.cloneNode(True), node)
                done = False
        return done	
    varvals = varval.getElementsByTagName('variablevalue')
    eqns = eqn.getElementsByTagName('equation')
    done = True
    eqns.extend(varvals)
    for i in eqns:
        arg1 = getArg(i, 1)
        arg2 = getArg(i, 2)
        # print 'Equation {0}={1}'.format(daexmlPP.ppExpr(arg1),daexmlPP.ppExpr(arg2))
        lhs = getArg(arg1,1) if arg1.tagName == 'der' else None
        rhs = getArg(arg2,1) if arg2.tagName == 'der' else None
        lhs = valueOf(lhs).strip() if lhs != None and lhs.tagName == 'identifier' else None
        rhs = valueOf(rhs).strip() if rhs != None and rhs.tagName == 'identifier' else None
        # ASHISH: Disable non-substitutability of c/d-state variables
        # lhs = None if lhs in dstate or lhs in cstate else lhs
        # rhs = None if rhs in dstate or rhs in cstate else rhs
        if lhs == None and rhs == None:
            continue
        identifier = lhs if lhs != None else rhs
        expr = arg2 if lhs != None else arg1
        # check if expr has any pre or der symbol in it
        pres = expr.getElementsByTagName('pre')
        ders = expr.getElementsByTagName('der')
        #if(pres != None and len(pres) > 0) or (ders != None and len(ders) > 0):
        if (ders != None and len(ders) > 0):
            print 'Warning: der({0}) defined in terms of der'.format(identifier)
            continue
        # replace der(identifier) by expr everywhere, but NOT in i.
        print '%',
        # print 'Equation {0}={1}'.format(daexmlPP.ppExpr(arg1),daexmlPP.ppExpr(arg2))
        # print 'der({0})-->{1}'.format(identifier,daexmlPP.ppExpr(expr))
        # for j in varvals:
            # done &= replacederx(j, identifier, expr)
        for j in eqns:
            if j != i:
                done &= replacederx(j, identifier, expr)
    return done

def ppdebug(dom, msg):
    print '--------------------------------------------------------------------------'
    print msg
    knownVars = dom.getElementsByTagName('knownVariables')[0]
    varvals = knownVars.getElementsByTagName('variablevalue')
    print 'printing {0} variable values...'.format(len(varvals))
    for i in varvals:
        print daexmlPP.ppEqn(i)
    print 'printing {0} equations......'.format(len(dom.getElementsByTagName('equation')))
    daexmlPP.source_textPP(dom)
    print '--------------------------------------------------------------------------'

def SimplifyEqnsPPDaeXML(dom, cstate, dstate, filepointer=sys.stdout):
    '''perform substitutions in the dom; output new dom'''
    knownVars = dom.getElementsByTagName('knownVariables')[0]
    eqns = dom.getElementsByTagName('equations')[0]
    alleqns = eqns.getElementsByTagName('equation')
    # substitute values for vars in alleqns
    # find all 'identifier nodes' in eqns...replace it by
    # expression
    done = False
    newknownvars = knownVars
    neweqns = eqns
    ppdebug(dom, 'Simplification Phase 0.0 over...printing {0} equations...')
    while not done:
        done = True
        varvals = newknownvars.getElementsByTagName('variablevalue')
        (mapping,newknownvars) = getMapping(varvals, newknownvars, cstate, dstate)
        # print 'Now we have {0} variables'.format(len(varvals))
        if len(mapping) == 0:
            varvals = neweqns.getElementsByTagName('equation')
            (mapping,neweqns) = getMapping(varvals, neweqns, cstate, dstate)
        if len(mapping) > 0:
            newknownvars = substitute(newknownvars, mapping)
            neweqns = substitute(neweqns, mapping)
            done = False
        else:
            pass
        ppdebug(dom, 'Simplification Phase 0.1 over...printing equations...')
        done &= simplify3(newknownvars)
        done &= simplify3(neweqns)	# simplify special tapp,bapp,etc.
        #ppdebug(dom, 'Simplification Phase 0.2 over...printing equations...')
        done &= simplify1(newknownvars)
        done &= simplify1(neweqns)	# simplify arithmetic
        #ppdebug(dom, 'Simplification Phase 0.3 over...printing equations...')
        done &= simplify2(newknownvars)
        done &= simplify2(neweqns)	# setaccess
        #ppdebug(dom, 'Simplification Phase 0.4 over...printing equations...')
        done &= simplify0(newknownvars)
        done &= simplify0(neweqns)	# ite,set,uapp,bapp,bool
        #ppdebug(dom, 'Simplification Phase 0.5 over...printing equations...')
        done &= simplifyPreDer(newknownvars, neweqns, cstate, dstate)
        ppdebug(dom, 'Simplification Phase 0.6 over...printing equations...')
    dom = replace(knownVars, newknownvars, dom)
    dom = replace(eqns, neweqns, dom)
    return dom
'''
    mapping = {}
    for i in varvals:
        identifier = valueOf(getArg(i,1)).strip()
        expr = getArg(i,2)
        newexpr = substitute(expr, mapping)
        tmpdict = { identifier: newexpr }
        for (k,v) in mapping.items():
            mapping[k] = substitute(v, tmpdict)
        print 'Adding {0} = {1}'.format(identifier,newexpr)
        mapping[identifier] = newexpr
    # Now mapping is a substitution
    eqns = dom.getElementsByTagName('equations')[0]
    alleqns = eqns.getElementsByTagName('equation')
    for i in alleqns:
        expr1 = getArg(i,1)
        expr2 = getArg(i,2)
        newexpr1 = substitute(expr1, mapping)
        newexpr2 = substitute(expr2, mapping)
        i.replaceChild(newChild=newexpr1,oldChild=expr1)
        i.replaceChild(newChild=newexpr2,oldChild=expr2)
'''

def moveIfExists(filename):
    import shutil
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def create_output_file(filename, z):
    basename,ext = os.path.splitext(filename)
    if ext != '.daexml':
        print 'ERROR: Unknown file extension; expecting .daexml ... Quitting'
        return 1
    xmlfilename = basename + ".dae_flat_xml"
    moveIfExists(xmlfilename)
    with open(xmlfilename, "w") as fp:
        z.writexml(fp, indent=' ', addindent=' ', newl='\n')
        # print >> fp, z.toprettyxml()
    print "Created file %s containing XML representation" % xmlfilename

def simplifydaexml(dom1, filename):
    global dom
    dom = dom1
    tmp = dom.getElementsByTagName('continuousState')[0]
    tmp2 = tmp.getElementsByTagName('identifier')
    cstate = [ valueOf(i).strip() for i in tmp2 ]
    tmp = dom.getElementsByTagName('discreteState')[0]
    tmp2 = tmp.getElementsByTagName('identifier')
    dstate = [ valueOf(i).strip() for i in tmp2 ]
    dom = SimplifyEqnsPPDaeXML(dom, cstate, dstate)
    print 'Simplification Phase 1 over...printing equations...'
    daexmlPP.source_textPP(dom)
    # dom = SimplifyEqnsPhase2(dom)
    # dom = SimplifyEqnsPhase3(dom)
    dom = SimplifyEqnsPhase4(dom, cstate, dstate)
    print 'Simplification Phase 2 over...printing equations...'
    daexmlPP.source_textPP(dom)
    dom = SimplifyEqnsPhase5(dom, cstate, dstate)
    print 'Simplification Phase 3 over...printing equations...'
    daexmlPP.source_textPP(dom)
    # create_output_file(filename, dom) # do not create .dae_flat_xml file
    return dom

if __name__ == "__main__":
    #xmlparser = xml.parsers.expat.ParserCreate()
    dom = xml.dom.minidom.parse(sys.argv[1])
    simplifydaexml(dom, sys.argv[1])
    #xmlparser.StartElementHandler = start_element
    #xmlparser.ElementDeclHandler = elmtdeclhandle
    #xmlparser.AttlistDeclHandler = attlistdeclhandler
    #fp = open(sys.argv[1])
    #dom = xmlparser.ParseFile(fp)
