# NOTES:
# 2013/08/22: State variables can NOT be eliminated now
# 2013/08/22: Fixed /flag bug in SimplifyEqnsPhase4
# 2013/08/23: Added SimplifyAC (x + c) - d ==> x + (c-d)
# 2014/02/24: Important bug fixed in getMapping
# 2014/04/01: ... substitute: var->expr if var in expr IGNORE!

# 2014/08/26: WRITING dom = arrayselect2if(dom) --
 
import xml.dom.minidom
import xml.parsers.expat
import sys
import os.path
import daexmlPP
#from pympler.asizeof import asizeof

# -------------------------------------------------------------------
# Usage: From within python code
# -------------------------------------------------------------------
# simplifydaexml(dom1, filename, library = None, ctxt = None)
# Returns: XML parse of .daexml4 simplified daexml file
# Creates daexml1,2,3,4 intermediate daeXML files.
# -------------------------------------------------------------------

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

# -------------------------------------------------------------------
# Simplification routines for expressions.
# -------------------------------------------------------------------
def simplifyPredicate(node):
    "-x <= c ==> x >= -c"
    done = True
    bapps = node.getElementsByTagName('BAPP')
    predops = ['<', '>', '<=', '>=', '&gt;', '&lt;', 'gt', 'lt']
    negate_op = {'<':'>','>':'<','<=':'>=','>=':'<=','gt':'lt','lt':'gt','&gt;':'&lt;','&lt;':'&gt;'}
    for i in bapps:
        op = getArg(i, 1)
        opstr = valueOf(op).strip()
        if not opstr in predops:
            continue
        arg1 = getArg(i, 2)
        arg2 = getArg(i, 3)
        if arg1.localName != 'number' and arg2.localName != 'number':
            continue
        if arg1.localName == 'UAPP':
            if valueOf(getArg(arg1,1)).strip() != '-':
                continue
            num = float(valueOf(arg2))
            nnum = helper_create_tag_val('number',str(-num))
            narg1 = getArg(arg1, 2).cloneNode(True)
            negop = helper_create_tag_val('BINARY_OPERATOR',negate_op[opstr])
            newnode = helper_create_app('BAPP',[negop, narg1, nnum])
            node = replace(i, newnode, node)
            print '-<',
        elif arg2.localName == 'UAPP':
            if valueOf(getArg(arg2,1)).strip() != '-':
                continue
            num = float(valueOf(arg1))
            nnum = helper_create_tag_val('number',str(-num))
            narg1 = getArg(arg2, 2).cloneNode(True)
            negop = helper_create_tag_val('BINARY_OPERATOR',opstr)
            newnode = helper_create_app('BAPP',[negop, narg1, nnum])
            node = replace(i, newnode, node)
            print '-<',
        else:
            continue
    return done

def simplifyAC(node):
    "(x+c)-d ==> x+(c-d); (x*c)*d ==> x*(c*d); etc."
    def isXopC(node):
        if node.localName != 'BAPP':
            return None
        op = getArg(node, 1)
        opstr = valueOf(op).strip()
        if not opstr in arithops:
            return None
        arg1 = getArg(node, 2)
        arg2 = getArg(node, 3)
        if arg1 == None or arg2 == None:
            return None
        if arg1.localName != 'number' and arg2.localName != 'number':
            return None
        if opstr in ['+','*']:
            if arg2.localName == 'number':
                return (opstr, arg1, float(valueOf(arg2)))
            else:
                return (opstr, arg2, float(valueOf(arg1)))
        elif opstr == '-':
            if arg2.localName == 'number':
                return ('+', arg1, -float(valueOf(arg2)))
            else:
                return ('-', arg2, float(valueOf(arg1)))
        else:
            if arg2.localName == 'number':
                den = float(valueOf(arg2))
                if den != 0:
                    return ('*', arg1, 1.0/den)
                else:
                    # This can happen if division is GUARDED by if.
                    # In which case outcome does not matter.
                    # THis happens in no_controls_dae.xml example.
                    # print node.toxml()
                    return ('*', arg1, 0.0)
            else:
                return ('/', arg2, float(valueOf(arg1)))
    done = True
    bapps = node.getElementsByTagName('BAPP')
    arithops = ['+', '-', '*', '/']
    for i in bapps:
        opArgNum = isXopC(i)
        if opArgNum == None:
            continue
        (op, arg1, num1) = opArgNum
        opArgNum1 = isXopC(arg1)
        if opArgNum1 == None:
            continue
        (op1, arg11, num11) = opArgNum1
        #print 'debug: input:', i.toxml(), opArgNum, opArgNum1
        #ans = None
        if op == '+' and op1 == '+':
            num = helper_create_tag_val('number', str(num1+num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '+')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,newarg,num])
            node = replace(i, ans, node)
            print '++',
            done = False
        if op == '*' and op1 == '*':
            num = helper_create_tag_val('number', str(num1 * num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '*')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,newarg,num])
            node = replace(i, ans, node)
            print '**',
            done = False
        elif op == '+' and op1 == '-':  # (num11-x) + num1
            num = helper_create_tag_val('number', str(num11 + num1))
            newop = helper_create_tag_val('BINARY_OPERATOR', '-')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,num,newarg])
            node = replace(i, ans, node)
            print '+-',
            done = False
        elif op == '-' and op1 == '+':  # num1 - (num11+x) 
            num = helper_create_tag_val('number', str(num1 - num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '-')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,num,newarg])
            node = replace(i, ans, node)
            print '-+',
            done = False
        elif op == '-' and op1 == '-':  # num1 - (num11 - x)
            num = helper_create_tag_val('number', str(num1 - num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '+')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[ newop, num, newarg])
            node = replace(i, ans, node)
            print '--',
            done = False
        elif op == '*' and op1 == '/':  # num1 * (num11 / arg11)
            num = helper_create_tag_val('number', str(num1 * num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '/')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,num,newarg])
            node = replace(i, ans, node)
            print '*/',
            done = False
        elif op == '/' and op1 == '*':  # num1 / (num11 * arg11)
            num = helper_create_tag_val('number', str(num1 / num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '/')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,num,newarg])
            node = replace(i, ans, node)
            print '/*',
            done = False
        elif op == '/' and op1 == '/':  # num1 / (num11 / arg11)
            num = helper_create_tag_val('number', str(num1 / num11))
            newop = helper_create_tag_val('BINARY_OPERATOR', '*')
            newarg = arg11.cloneNode(True)
            ans = helper_create_app('BAPP',[newop,num,newarg])
            node = replace(i, ans, node)
            print '//',
            done = False
        #if ans:
            # print 'debug: output:', ans.toxml()
    simplifyPredicate(node)
    return done 

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
                if arg1.localName not in ['identifier','string'] or arg2.localName not in ['identifier','string']:
                    continue
                v1 = valueOf(arg1).strip()
                v2 = valueOf(arg2).strip()
                if v1 in Shapes or v2 in Shapes:
                    ans = helper_create_tag_val('string', str(v1 == v2))
                    #ans = helper_create_tag_val('identifier', 'True')
                    node = replace(i, ans, node)
                    done = False
                    print '==',
    done = done and simplifyAC(node)
    return done

def simplify2_arrayselect(node):
    "<arrayselect> id1 id2 </arrayselect> --> id if id2 is a number"
    done = True
    sas = node.getElementsByTagName('arrayselect')
    for i in sas:
        # check if this node is already deleted somehow...
        set1 = getArg(i, 1)
        set2 = getArg(i, 2)
        if set1.localName == 'identifier' and set2.localName == 'number':
            access0 = valueOf(set1).strip()
            access1 = valueOf(set2).strip()
	    answer = access0 + '[' + access1 + ']'
            ans = helper_create_tag_val('identifier', answer)
            node = replace(i, ans, node)
            done = False
            print 's',
        elif set1.localName == 'set' and set2.localName == 'number':
            # ASHISH: NEW CODE ADDED; 04/04/2014
            access = int(valueOf(set2).strip())
            set1 = getArg(set1, access)
            if set1 != None:
                node = replace(i, set1, node)
                done = False
                print 's',
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
    done2 = simplify2_arrayselect( node )
    return done and done2
 
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
        return isinstance(obj, (int, float))
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

def handle_table(table,rows,cols,icol,n):
    def compressTableNew(rows, cols, table, icol):
        def collapse_monotone_range(table,rows,icol,startingrow,op):
            i = startingrow
            while i < rows and op(table[i][icol-1], table[i-1][icol-1]):
                i = i + 1
            return i
        def next_monotone_range(table,rows,icol,startingrow):
            i = collapse_monotone_range(table,rows,icol,startingrow,lambda x,y: x >= y)
            if i == startingrow:
                i = collapse_monotone_range(table,rows,icol,startingrow,lambda x,y: x <= y)
            return i
        newtable = [ (table[0][0],table[0][icol-1]) ]
        i = next_monotone_range(table,rows,icol,1)
        newtable.append( (table[i-1][0], table[i-1][icol-1]) )
        if i < rows:
            i = next_monotone_range(table,rows,icol,i+1)
            newtable.append( (table[i-1][0], table[i-1][icol-1]) )
        if i < rows:
            print 'WARNING: Table more than 2-monotonic; approximated'
        return newtable
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

    if all([table[j][icol-1] == table[0][icol-1] for j in range(rows)]):
        return helper_create_tag_val('number', str(table[0][icol-1]))
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
        newnode = helper_create_tag_val('number', str(y))
    elif rows <= 3:
        newnode = table2ite(rows, cols, table, icol, n)
    else: # rows > 3 rows <= 3:
        tableNew = compressTableNew(rows, cols, table, icol)
        newnode = table2ite(len(tableNew), 2, tableNew, 2, n)
    return newnode

def interpolate(x1,y1, x2,y2, x):
    '''return (y2-y1)/(x2-x1) * (x-x1) + y1'''
    return (y2-y1)/(x2-x1) * (x-x1) + y1

def handle_table2D(table, rows, cols, u1, u2):
    '''u1,u2 two inputs: table is rowsxcols matrix'''
    assert rows >= 2 and cols >= 2, 'ERROR: 2D table has fewer than 2 rows/cols'
    if rows == 2:
        newtable = [ [table[0][i], table[1][i]] for i in range(1,cols) ]
        return handle_table(newtable, cols-1, 2, 2, u2)
    elif cols == 2:
        newtable = [ [table[i][0], table[i][1]] for i in range(1,rows) ]
        return handle_table(newtable, rows-1, 2, 2, u1)
    elif u1.localName == 'number':
        n1 = float(valueOf(u1))
        j = 2
        while j < rows and table[j][0] < n1:
            j = j + 1
        # interpolate using j and j-1
        newtable = [ [table[0][i], interpolate( table[j-1][0], table[j-1][i], table[j][0], table[j][i], n1 ) ] for i in range(1,cols) ]
        return handle_table(newtable, cols-1, 2, 2, u2)
    elif u2.localName == 'number':
        n2 = float(valueOf(u2))
        j = 2
        while j < cols and table[0][j] < n2:
            j = j + 1
        # interpolate using j-1 and j
        newtable = [ [table[i][0], interpolate( table[0][j-1],table[i][j-1], table[0][j],table[i][j], n2 ) ] for i in range(1, rows) ]
        return handle_table(newtable, rows-1, 2, 2, u1)
    else:
        return helper_create_tag_val('number', str(table[int(rows)/2][int(cols)/2]))

def simplify_tapp(node,done):
    "Modelica.Math.tempInterpol1(input_number,table,icol) and Modelica.Blocks.Tables.CombiTable1D.tableIpo(table,icol,variable) are rewritten by the LIBRARY now into mytable, which is handled here"
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
                #assert a != None, 'SERIOUS ERROR: Table row does not simplify to a constant {0}'.format(rowi.toprettyxml())
                if a == None:
                    return (None,0,0)
                table.append(a)
        return (table, rows, cols)
    sas = node.getElementsByTagName('TAPP')
    for i in sas:
        func = getArg(i, 1)
        set1 = getArg(i, 3)	# table
        n = getArg(i, 2)	# input number; column 0 value
        m = getArg(i, 4)	# icol; column that has the answer.
        fname = valueOf(func).strip()
        if fname == 'mytable':
            if not(set1.localName == 'set' and m.localName == 'number'):
                continue
            #print 'ERROR: Unable to handle 1D table {0} {1}'.format(set1.toxml(),m.toxml())
            (table,rows,cols) = table2table(set1)
            if table == None:
                continue
            icol = int(valueOf(m))# column that computes output 
            assert icol <= cols
            # if all values in table are same, return value
            newnode = handle_table(table,rows,cols,icol,n)
            node = replace(i, newnode, node)
            done = False
            print 'T',
        elif fname == 'mytable2':
            if not(m.localName == 'set'):
                continue
            (table,rows,cols) = table2table(m)
            if table == None:
                continue
            newnode = handle_table2D(table,rows,cols,n,set1)
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
        fname = valueOf(func).strip()
        if fname == 'Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape.PackMaterial':
            ans = helper_create_tag_val('number', str(0))
            node = replace(i, ans, node)
            done = False
            print 'd',
        elif fname == 'Modelica.Blocks.Tables.CombiTable1D.tableInit':
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
        fname =  valueOf(func).strip()
        if fname == 'Modelica.Mechanics.MultiBody.Frames.TransformationMatrices.from_nxy' and set1.localName == 'set' and set2.localName == 'set':
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
        # THIS IS UNSOUND CODE....
        elif fname in ['min', 'max']:
            arg1, arg2 = set1, set2
            if arg2 != None and arg2.localName == 'number':
                c = float(valueOf(arg2))
                node = replace(i, arg2, node)
                done = False
                print 'Mx',
            elif arg1 != None and arg1.localName == 'number':
                c = float(valueOf(arg1))
                node = replace(i, arg1, node)
                done = False
                print 'Mx',
        # END OF UNSOUND CODE....
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
        # if changedchild.tagName == 'identifier':
        if changedchild.tagName == 'string':
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
        # UNSOUND code: begin
        '''
        else:
            then_xml = getArg(parentnode, 2)
            else_xml = getArg(parentnode, 3)
            if then_xml.tagName == 'number' and else_xml.tagName == 'number':
              ans = (float(valueOf(then_xml)) + float(valueOf(else_xml)))/2.0
              ans_xml = helper_create_tag_val('number', str(ans))
              node = replace(parentnode, ans_xml, node)
              done = False
              print 'ITEx ',
            elif then_xml.tagName in ['number', 'identifier']:
              node = replace(parentnode, then_xml, node)
              done = False
              print 'ITExx ',
            elif else_xml.tagName in ['number', 'identifier']:
              node = replace(parentnode, else_xml, node)
              done = False
              print 'ITExx ',
        '''
        # UNSOUND code: end
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
        # v1 = valueOf(arg1).strip() if arg1.tagName == 'identifier' else ''
        v1 = valueOf(arg1).strip() if arg1.tagName == 'string' else ''
        if v1 in FALSE:
            ans = helper_create_tag_val('string', 'true')
            node = replace(parentnode, ans, node)
            done = False
            print 'b',
        elif v1 in TRUE:
            ans = helper_create_tag_val('string', 'false')
            node = replace(parentnode, ans, node)
            done = False
            print 'b',
    sas = node.getElementsByTagName('BAPP')
    for parentnode in sas:
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        if arg1 == None or arg2 == None:
            print 'Critical Overlap Case', parentnode.toxml()
            assert False, 'critical overlap case'
            sys.exit(1)
        func = valueOf(getArg(parentnode, 1)).strip()
        v1 = valueOf(arg1).strip() if arg1.tagName == 'string' else ''
        v2 = valueOf(arg2).strip() if arg2.tagName == 'string' else ''
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
        elif func == 'log':
            val = math.log(float(arg1))
        elif func == 'exp':
            val = math.exp(float(arg1))
        elif func == 'Real' or func == 'real':
            val = float(arg1)
        elif func == 'sign':
            val = float(arg1)
            val = 1 if val >= 0 else -1
        elif func == 'noEvent':
            #print 'Dont know what to do with noEvent'
            val = float(arg1)
            #sys.exit()
        elif func == 'der':
            val = 0.0
        else:
            print 'WARNING: Dont know what to do with {0}'.format(func)
            assert False, 'WARNING: node = {0}'.format(node.toxml())
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
    if node1.tagName == 'identifier' or node1.tagName == 'string':
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Subroutines for going from .daexml3 -> .daexml4
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# More simplification routines
# -------------------------------------------------------------------
def simplify0bapp(node):
    '''simplify'''
    import math
    done = True
    sas = node.getElementsByTagName('BAPP')
    #print 'Number of BAPPS is', len(sas)
    for parentnode in sas:
        arg1 = getArg(parentnode, 2)
        arg2 = getArg(parentnode, 3)
        assert arg1 != None and arg2 != None
        if arg1.tagName == 'number' and arg2.tagName == 'number':
            arg1 = valueOf(arg1).strip()
            arg2 = valueOf(arg2).strip()
            func = valueOf(getArg(parentnode, 1)).strip()
            if func == '/' and abs(float(arg2)) < 1e-9:
                #print 'WARNING: Division by very small constant'
                print '~0',
                if abs(float(arg1)) < 1e-9:
                  val = 1
                else:
                  val = 1e10
            elif func == '/':
                val = float(arg1) / float(arg2)
            elif func == '*':
                val = float(arg1) * float(arg2)
            elif func == '+':
                val = float(arg1) + float(arg2)
            elif func == '-':
                val = float(arg1) - float(arg2)  # todo: atan2/ cross
            elif func == '^' or func == 'power':
                if abs(float(arg1)) < 1e-8:	# ASHISH: 1e-5 check
                    val = 0.0
                else:
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
            elif (func in ['<', '&lt;', 'lt']) and float(arg1) < float(arg2):
                val = 'true'
            elif (func in ['<', '&lt;', 'lt']) and float(arg1) >= float(arg2):
                val = 'false'
            elif (func in ['>', '&gt;', 'gt']) and float(arg1) > float(arg2):
                val = 'true'
            elif (func in ['>', '&gt;', 'gt']) and float(arg1) <= float(arg2):
                val = 'false'
            elif func in ['>=','geq'] and float(arg1) >= float(arg2):
                val = 'true'
            elif func in ['>=','geq'] and float(arg1) < float(arg2):
                val = 'false'
            elif func in ['<=','leq'] and float(arg1) <= float(arg2):
                val = 'true'
            elif func in ['<=','leq'] and float(arg1) > float(arg2):
                val = 'false'
            elif func == '==' and float(arg1) == float(arg2):
                val = 'true'
            elif func == '==' and not(float(arg1) == float(arg2)):
                val = 'false'
            elif func == 'smooth':
                val = float(arg2)
            else:
                print 'unknown op {0} over floats'.format(func)
                val = None
            if isinstance(val, (float,int)):
                tag = 'number'
            elif isinstance(val, (str,unicode)): # true, false
                # tag = 'identifier'
                tag = 'string'
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Apply mapping to the DOMs.
# -------------------------------------------------------------------
def has_variable(expr, var):
  '''does variable name var occur in expr'''
  if expr.tagName == 'identifier':
    ids = [ expr ]
  else:
    ids = expr.getElementsByTagName('identifier')
  for i in ids:
    varname = valueOf(i).strip()
    if var == varname:
      return True
  return False

def substitute(expr, mapping):
    '''replace identifiers by their mapped values in expr'''
    for (k,v) in mapping.items():
      if has_variable(v,k):
        print 'WARNING: mapping fails occur check. Ignoring.'
        del mapping[k]
    if len(mapping) == 0:
      return expr
    if expr.tagName == 'identifier':
        ids = [ expr ]
    else:
        ids = expr.getElementsByTagName('identifier')
    for i in ids:
        varname = valueOf(i).strip()
        if mapping.has_key(varname):
            varvalue = mapping[varname]
            # print 'found', varname
            # replace i by copy of varvalue in expr tree
            valuecopy = varvalue.cloneNode(True)
            expr = replace(i, valuecopy, expr)
    # print 'All constant identifiers replaced'
    return(expr)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Generate var->val mapping from variablevalue or equation XMLs
# -------------------------------------------------------------------
def getMapping(varvals,root, cstate, dstate, options):
    '''return var=val where val.tagName should be in options'''
    def extendMapping(mapping, identifier, value):
        '''extend mapping[identifier] = value'''
        # first normalize value
        if value.tagName == 'identifier':
            val = valueOf(value).strip() 
            if mapping.has_key(val):
                value = mapping[val]
        # next normalize mapping
        for k,v in mapping.items():
            if v.tagName == 'identifier':
                val = valueOf(v).strip()
                if val == identifier:
                    mapping[k] =  value
        mapping[identifier] =  value
        return mapping
    mapping = {}
    # varvals = newknownvars.getElementsByTagName('variablevalue')
    for i in varvals:
        # If trackPreserve=='1' then continue
        if i.getAttribute('trackPreserve')=='1':
            continue
        arg1 = getArg(i, 1)
        arg2 = getArg(i, 2)
        lhs = valueOf(arg1).strip() if arg1.localName == 'identifier' else None
        rhs = valueOf(arg2).strip() if arg2.localName == 'identifier' else None
        # ASHISH: RE-Enable non-substitutability of c/d-state variables
        lhs = None if lhs in dstate or lhs in cstate else lhs
        rhs = None if rhs in dstate or rhs in cstate else rhs
        if lhs == None and rhs == None:
            continue
        identifier = lhs if lhs != None else rhs
        expr = arg2 if lhs != None else arg1
        # Condition below was ADDED
        # if mapping has_key identifier then do nothing!!!
        if mapping.has_key(identifier):
            continue
        # Condition below was ADDED: x -> sth+der(y) DISABLED
        if len(expr.getElementsByTagName('der')) > 0:
            continue
        if expr.localName in options:
            # ['number', 'identifier', 'set', 'string']
            # assert len(expr.getElementsByTagName('cn'))==0, 'ERR {0}={1}'.format(identifier, expr.toxml())
            print '.',
            mapping = extendMapping(mapping, identifier, expr)
            root.removeChild( i )
            # i.unlink()
            # print '.',
    # print 'Deleting {0} variables'.format(len(deleted))
    return (mapping, root)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Convert eqn to list so that it is easy to solve for a variable
# -------------------------------------------------------------------
def equation2list(eqn):
    "output a list [(a1,T),(a2,F),(a3,T)] if eqn is a1 = a2 - a3"
    def update_var_val(mapping, var, val):
        if val != 0:
            mapping[var] = val
        else:
            if mapping.has_key(var):
                del mapping[var]
        return mapping
    def expr2list(expr, sgn, mapping):
        if expr.tagName == 'identifier':
            variable = valueOf(expr).strip()
            freq = 0 if not mapping.has_key(variable) else mapping[variable]
            value = freq + 1 if sgn else freq - 1
            return update_var_val(mapping, variable, value)
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
        elif expr.tagName == 'BAPP' and valueOf(getArg(expr,1)).strip() == '*' and getArg(expr,2).tagName == 'number' and getArg(expr,3).tagName == 'identifier':
            variable = valueOf(getArg(expr,3)).strip()
            freq = 0 if not mapping.has_key(variable) else mapping[variable]
            freq1 = float(valueOf(getArg(expr,2))) 
            value = freq + freq1 if sgn else freq - freq1
            return update_var_val(mapping, variable, value)
        elif expr.tagName == 'BAPP' and valueOf(getArg(expr,1)).strip() == '*' and getArg(expr,3).tagName == 'number' and getArg(expr,2).tagName == 'identifier':
            variable = valueOf(getArg(expr,2)).strip()
            freq = 0 if not mapping.has_key(variable) else mapping[variable]
            freq1 = float(valueOf(getArg(expr,3))) 
            value = freq + freq1 if sgn else freq - freq1
            return update_var_val(mapping, variable, value)
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
    assert arg2 != None, 'ERROR: equation {0} has 1 arg?'.format(eqn.toprettyxml())
    # print 'Input eqn is {0}'.format(daexmlPP.ppEqn(eqn))
    ans1 = expr2list(arg1, True, {})
    ans2 = expr2list(arg2, False, ans1)
    # print 'Output eqn is {0} = 0'.format(daexmlPP.ppExpr(list2equation(ans2,True)))
    return ans2
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# eqn -> list, solve for a variable, list -> eqn to generate mapping
# -------------------------------------------------------------------
def list2equation(myeqn, flag):
    "return myeqn/flag"
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
    arg1 = lambda: helper_create_tag_val('BINARY_OPERATOR','/')
    arg3 = lambda x: helper_create_tag_val('number', str(x))
    anslistp = []
    anslistn = []
    if myeqn.has_key('number'):
        if myeqn['number'] != 0:
            value = myeqn['number']/flag 
            anslistp.append( helper_create_tag_val('number', str(value)) )
        del myeqn['number']
    if myeqn.has_key('pos'):
        poss = myeqn['pos']
        pbyf = [helper_create_app('BAPP', [arg1(),i,arg3(flag)]) for i in poss]
        anslistp.extend( pbyf )
        del myeqn['pos']
    if myeqn.has_key('neg'):
        nflag = -flag
        poss = myeqn['neg']
        pbyf = [helper_create_app('BAPP', [arg1(),i,arg3(nflag)]) for i in poss]
        anslistp.extend( pbyf )
        del myeqn['neg']
    for (k,v) in myeqn.items():
        newv = v/flag
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# occurs check -- to solve an eqn, make sure var is not elsewhere
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Simplification routines
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Code for going from daexml -> daexml1 -> daexml2
# -------------------------------------------------------------------
def SimplifyEqnsPPDaeXML(dom, cstate, dstate, options, filepointer=sys.stdout):
    '''perform substitutions in the dom; output new dom'''
    knownVars = dom.getElementsByTagName('knownVariables')[0]
    eqns = dom.getElementsByTagName('equations')[0]
    initsL = dom.getElementsByTagName('initializations')
    inits = initsL[0] if initsL != None and len(initsL) > 0 else None

    # apply var->cst or var->var substitutions
    done = False
    newknownvars = knownVars
    neweqns = eqns
    newinits = inits

    # collect var->val mapping from knownVars
    while not done:
      done = True
      varvals = newknownvars.getElementsByTagName('variablevalue')
      (mapping,newknownvars) = getMapping(varvals, newknownvars, cstate, dstate, options)
      arity = int( newknownvars.getAttribute('arity') )
      newknownvars.setAttribute('arity',str(arity-len(mapping)))
 
      # if no such mapping found, try to get it from equations!
      if len(mapping) == 0:
        varvals = neweqns.getElementsByTagName('equation')
        (mapping,neweqns) = getMapping(varvals, neweqns, cstate, dstate, options)
        arity = int( neweqns.getAttribute('arity') )
        neweqns.setAttribute('arity',str(arity-len(mapping)))

      # if a nonzero mapping is found, apply it.
      if len(mapping) > 0:
        newknownvars = substitute(newknownvars, mapping)
        neweqns = substitute(neweqns, mapping)
        if newinits != None:
          newinits = substitute(newinits, mapping)
        done = False
      else:
        pass

      # application of mapping may trigger simplifications. Do them.
      done &= simplify3(newknownvars)
      done &= simplify3(neweqns)	# simplify special tapp,bapp,etc.
      done &= simplify1(newknownvars)
      done &= simplify1(neweqns)	# simplify arithmetic
      done &= simplify2(newknownvars)
      done &= simplify2(neweqns)	# setaccess
      done &= simplify0(newknownvars)
      done &= simplify0(neweqns)	# ite,set,uapp,bapp,bool
      done &= simplifyPreDer(newknownvars, neweqns, cstate, dstate)

    # All done. Update dom. Return.
    dom = replace(knownVars, newknownvars, dom)
    dom = replace(eqns, neweqns, dom)
    if newinits != None:
      dom = replace(inits, newinits, dom)
    return dom
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Code for going from daexml2 -> daexml3
# -------------------------------------------------------------------
def SimplifyEqnsPhase4(dom, cstate, dstate):
    '''x = expr or -x = expr : replace x by its value in new dom'''
    # apply var -> expr substitution from knownVars and equations
    knownVars = dom.getElementsByTagName('knownVariables')[0]
    eqns = dom.getElementsByTagName('equations')[0]
    initsL = dom.getElementsByTagName('initializations')
    inits = initsL[0] if initsL != None and len(initsL) > 0 else None
    neweqns = eqns
    newknownvars = knownVars
    newinits = inits
    varvals = newknownvars.getElementsByTagName('variablevalue')

    # First, get mappings from knownVariables and apply them...
    while varvals != None and len(varvals) > 0:
      done = False
      mapping = {}
      i = varvals[0]
      var = getArg(i,1)
      assert var!=None, 'var=None for {0}'.format(i.toxml())
      varname = valueOf(var).strip()

      # if lhsVar not identifier, or if trackPreserve, then move to eqn
      if var.tagName != 'identifier' or i.getAttribute('trackPreserve')=='1':
        newknownvars.removeChild( i )
        i.tagName = 'equation'
        neweqns.appendChild( i )
      # elif lhsVar is a state variable, then also move to eqn
      elif varname in cstate or varname in dstate:
        print >> sys.stderr, 'knownVar {0} is a state var?'.format(varname)
        newknownvars.removeChild( i )
        i.tagName = 'equation'
        neweqns.appendChild( i )
      # else create a mapping, and apply it to rest
      else:
        val = getArg(i,2)
        mapping[varname] = val
        newknownvars.removeChild( i )
        newknownvars = substitute(newknownvars, mapping)
        neweqns = substitute(neweqns, mapping)
        if newinits != None:
          newinits = substitute(newinits, mapping)
      varvals = newknownvars.getElementsByTagName('variablevalue')
      # print 'len(newknownvars) = {0}'.format( len(varvals) )

    # All knownVars have been eliminated. Now proceed to equations.
    newknownvars.setAttribute('arity', '0')
    done = False
    while not done:
      done = True
      varvals = neweqns.getElementsByTagName('equation')
      mapping = {}

      # generate a mapping from the equations
      for i in varvals:
        if i.getAttribute('trackPreserve')=='1':
          continue
        myeqn = equation2list(i)
        variable = None
        for (k,v) in myeqn.items():
          if k != 'pos' and k != 'neg' and k != 'number':
            if not occurs(k, myeqn) and k not in cstate and k not in dstate and k not in TRUE and k not in FALSE:
              variable = k
              freq = v
              break
        if variable != None:
          del myeqn[variable]
          value = list2equation(myeqn, -1.0*freq)
          neweqns.removeChild( i )
          mapping[variable] = value
          #print '{0} --> {1}'.format(variable,daexmlPP.ppExpr(value))
          print 's',
          break
        else:
          pass

      # Now I have generated a mapping. Apply it if its nonzero.
      if len(mapping) > 0:
        neweqns = substitute(neweqns, mapping)
        if newinits != None:
          newinits = substitute(newinits, mapping)
        done = False
      else:
        pass

      # Some simplifications may be enabled now. So apply them.
      done &= simplify3(neweqns)
      done &= simplify1(neweqns)
      done &= simplify2(neweqns)
      done &= simplify0(neweqns)

    # All done. Update eqns and inits in the dom.
    neweqns.setAttribute('arity', str(len(varvals)))
    dom = replace(eqns, neweqns, dom)
    if newinits != None:
      dom = replace(inits, newinits, dom)
    return dom
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Going from daexml3 -> daexml4
# -------------------------------------------------------------------
def SimplifyEqnsPhase5(dom, cstate, dstate):
    "IF ( ) - c --> IF ( );  IF ( ) < c --> IF"
    done = False
    while not done:
        (done,dom) = distributeOverIf(dom, cstate, dstate)
        done &= simplify3(dom)  # ASHISH: Adding next 4 lines
        done &= simplify1(dom)
        done &= simplify2(dom)
        done &= simplify0(dom)
    done = False
    while not done:
        (done,dom) = ite2boolexpr(dom, cstate, dstate)
        done &= simplify3(dom)  # ASHISH: Adding next 4 lines
        done &= simplify1(dom)
        done &= simplify2(dom)
        done &= simplify0(dom)
    return dom
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Write to file
# -------------------------------------------------------------------
def create_output_file(filename, z, new_ext='.daexml1'):
    basename,ext = os.path.splitext(filename)
    # if ext != '.daexml':
        # print 'ERROR: Unknown file extension; expecting .daexml ... Quitting'
        # return 1
    xmlfilename = basename + new_ext	# ".dae_flat_xml"
    # moveIfExists(xmlfilename)
    with open(xmlfilename, "w") as fp:
        z.writexml(fp, indent='', addindent='', newl='\n')
        # print >> fp, z.toprettyxml()
    print "Created file %s containing XML representation" % xmlfilename
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Substitute Library functions 
# -------------------------------------------------------------------
def SubstituteLibraryFunctions(dom, library):
    def f2name_args_val(f):
        fname = valueOf(getArg(f, 1)).strip()
        fargs = getArg(f, 2)
        if fargs.tagName == 'formals':
            fval  = getArg(f, 3)
        else:
            fval = fargs
            fargs = None
        args = []
        if fargs != None:
            arity = int(fargs.getAttribute('arity'))
            for i in range(arity):
                args.append( getArg(fargs, i+1) )
        return (fname, args, fval)
    def substituteFunction(dom, allfunctions):
        '''fs = list of (fname, fargs, fval) where 
        fname = string, fargs = list of EXPRS-XML, fval = a DOM element'''
        tagNames = ['identifier', 'UAPP', 'BAPP', 'TAPP', 'QAPP', 'NAPP']
        partition = {0:[],1:[],2:[],3:[],4:[],5:[]}
        for (fname, fargs, fval) in allfunctions:
          arity = len(fargs) 
          arity = arity if arity <= 5 else 5
          partition[arity].append( (fname, fargs, fval) )
        for arity in partition.keys():
          tagName = tagNames[arity]
          instances = dom.getElementsByTagName(tagName)
          for node in instances:
            if arity >= 1:
                actualfname = valueOf(getArg(node, 1)).strip()
            else:
                actualfname = valueOf(node).strip()
            for (fname, fargs, fval) in partition[arity]:
              if actualfname == fname:
                mapping = match_args(node, fargs)
                if mapping != None:
                  newnode = fval.cloneNode(True)
                  newnode = substitute(newnode, mapping)
                  print 'r', fname,  # node.toxml(), newnode.toxml()
                  dom = replace(node, newnode, dom)
                  break
        return dom
    def match(formal, actual, mapping):
        "formal,actual are XML nodes, mapping is a dict from str to expr"
        # base case, if formal is an identifier
        #print 'matching formal {0} and actual {1}'.format(formal.toxml(),actual.toxml())
        if formal.tagName == 'identifier':
            var_name = valueOf(formal).strip()
            assert not mapping.has_key(var_name),'Nonlinear library definition'
            mapping[var_name] = actual
            return mapping
        elif formal.tagName == 'number':
            if actual.tagName == 'number':
                formal_val = float(valueOf(formal).strip())
                actual_val = float(valueOf(actual).strip())
                if abs(formal_val-actual_val) < 1e-3:
                    return mapping
                else:
                    return None
            else:
                return None # matching failed!!!
        elif formal.tagName.endswith('APP'): # UAPP,BAPP,TAPP,QAPP,NAPP...
            if actual.tagName != formal.tagName:
                return None # matching failed!!!
            formal_fname_node = getArg(formal, 1)
            formal_fname = valueOf(formal_fname_node).strip() 
            actual_fname_node = getArg(actual, 1)
            actual_fname = valueOf(actual_fname_node).strip()
            if actual_fname != formal_fname:
                return None # matching failed!!!
            arity = int(formal.getAttribute('arity'))
            for i in range(arity):
                formali = getArg(formal, i+2)
                actuali = getArg(actual, i+2)
                mapping = match(formali, actuali, mapping)
                if mapping == None:
                    return None # matching failed!!!
            return mapping
        elif formal.tagName == 'set':
            if actual.tagName != 'set':
                return None
            formal_arity = int(formal.getAttribute('cardinality'))
            actual_arity = int(actual.getAttribute('cardinality'))
            if actual_arity != formal_arity:
                return None
            for i in range(actual_arity):
                formali = getArg(formal, i+1)
                actuali = getArg(actual, i+1)
                mapping = match(formali, actuali, mapping)
                if mapping == None:
                    return None # matching failed!!!
            return mapping 
        else:
            print 'missing code? {0} {1}'.format(formal.tagName,actual.tagName)
            return None # matching failed!!!
    def replaceNodeByNewNode(dom, node, fargs, fval):
        "replace node by fval, but after replacing formals in fval by actuals"
        arity = len(fargs)
        newnode = fval.cloneNode(True)
        if arity == 0:
            dom = replace(node, newnode, dom)
            return dom
        mapping = {}
        for i in range(arity):
            mapping = match( fargs[i], getArg(node,i+2), mapping )
            if mapping == None:
                return dom	# match failed
            # mapping[fargs[i]] = getArg( node, i+2)
        newnode = substitute(newnode, mapping)
        dom = replace(node, newnode, dom)
        return dom
    def match_args(node, fargs):
        "match fargs with node.args, return None or mapping"
        arity = len(fargs)
        mapping = {}
        for i in range(arity):
            mapping = match( fargs[i], getArg(node,i+2), mapping )
            if mapping == None:
                return None	# match failed
        return mapping
    def remove_small_constants(dom):
      '''map constants <= e-9 to 0'''
      numbers = dom.getElementsByTagName('number')
      for i in numbers:
        valstr = valueOf(i).strip()
        if valstr == 'NoName':
          val = 1e-10
        else:
          val = float( valueOf(i).strip() )
        if abs(val) < 1e-8 and val != 0:
          newnode = helper_create_tag_val('number', '0')
          print 'e-10',
          dom = replace(i, newnode, dom)
      return dom
    dom = remove_small_constants(dom)
    if library == None:
        print 'Warning: No library being used for simplification'
        return dom
    # library is a dom file
    # print library.toxml()
    allfunctions = library.getElementsByTagName('libequation')
    if len(allfunctions) == 0:
        print 'Warning: No function definitions found in the library'
    fs = [ f2name_args_val(f) for f in allfunctions ]
    dom = substituteFunction(dom, fs)
    return dom
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# get continuous and discrete state variables.
# -------------------------------------------------------------------
def get_cd_state(dom):
    tmp = dom.getElementsByTagName('continuousState')[0]
    tmp2 = tmp.getElementsByTagName('identifier')
    cstate = [ valueOf(i).strip() for i in tmp2 ]
    tmp = dom.getElementsByTagName('discreteState')[0]
    tmp2 = tmp.getElementsByTagName('identifier')
    dstate = [ valueOf(i).strip() for i in tmp2 ]
    return (cstate, dstate)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Main function to simplify daexml in stages
# -------------------------------------------------------------------
def simplifydaexml(dom1, filename, library = None, ctxt = None):
    def existsAndNew(filename1, filename2):
        if os.path.isfile(filename1) and os.path.getctime(filename1) >= os.path.getctime(filename2):
            print "File {0} exists and is new".format(filename1)
            return True
        return False
    global dom
    basename,ext = os.path.splitext(filename)
    if existsAndNew(basename+'.daexml4', filename):
        print >> sys.stderr, 'Using existing {0} file'.format('.daexml4')
        return xml.dom.minidom.parse(basename+'.daexml4')
    elif existsAndNew(basename+'.daexml3', filename):
        print >> sys.stderr, 'Using existing {0} file'.format('daexml3')
        dom = xml.dom.minidom.parse(basename+'.daexml3')
        print '----------Simplification: Library Substitution starting...'
        dom = SubstituteLibraryFunctions(dom, library)
        print '----------Simplification: Library Substitution over.......'
        print '-------------Simplification: IF-lifting starting......'
        (cstate, dstate) = get_cd_state(dom)
        # dom = arrayselect2if(dom)
        dom = SimplifyEqnsPhase5(dom, cstate, dstate)
        create_output_file(filename, dom, '.daexml4') 
        print '-------------Simplification: IF-lifting over..........'
        return dom
    elif existsAndNew(basename+'.daexml2', filename):
        print >> sys.stderr, 'Using existing {0} file'.format('daexml2')
        dom = xml.dom.minidom.parse(basename+'.daexml2')
        print '----------Simplification: Library Substitution starting...'
        dom = SubstituteLibraryFunctions(dom, library)
        print '----------Simplification: Library Substitution over.......'
        print '----------Simplification: Expression Propagation starting..'
        (cstate, dstate) = ctxt if ctxt != None else get_cd_state(dom)
        dom = SimplifyEqnsPhase4(dom, cstate, dstate)
        create_output_file(filename, dom, '.daexml3') 
        print '----------Simplification: Expression propagation over......'
        return simplifydaexml(dom, filename, library, (cstate,dstate))
    elif existsAndNew(basename+'.daexml1', filename):
        print >> sys.stderr, 'Using existing {0} file'.format('daexml1')
        dom = xml.dom.minidom.parse(basename+'.daexml1')
        print '----------Simplification: Library Substitution starting...'
        dom = SubstituteLibraryFunctions(dom, library)
        print '----------Simplification: Library Substitution over.......'
        print '----------Simplification: Variable Propagation starting...'
        options = ['number', 'identifier', 'set', 'string']
        (cstate, dstate) = ctxt if ctxt != None else get_cd_state(dom)
        dom = SimplifyEqnsPPDaeXML(dom, cstate, dstate, options)
        create_output_file(filename, dom, '.daexml2') 
        print '----------Simplification: Variable Propagation over......'
        return simplifydaexml(dom, filename, library, (cstate,dstate))
    else:
        #print dom.toxml()
        print '----------Simplification: Library Substitution starting...'
        dom = dom1
        dom1 = SubstituteLibraryFunctions(dom1, library)
        print '----------Simplification: Library Substitution over.......'
        (cstate, dstate) = ctxt if ctxt!=None else get_cd_state(dom1)
        print '----------Simplification: Constant Propagation starting...'
        options = ['number', 'set', 'string']
        dom = dom1
        dom = SimplifyEqnsPPDaeXML(dom, cstate, dstate, options)
        create_output_file(filename, dom, '.daexml1') 
        print '----------Simplification: Constant Propagation over......'
        return simplifydaexml(dom, filename, library, (cstate,dstate))
    return dom  # unreachable code
# -------------------------------------------------------------------

# -------------------------------------------------------------------
if __name__ == "__main__":
    #xmlparser = xml.parsers.expat.ParserCreate()
    dom = xml.dom.minidom.parse(sys.argv[1])
    dom = simplifydaexml(dom, sys.argv[1])
    create_output_file(sys.argv[1], dom) # do not create .dae_flat_xml file
    #xmlparser.StartElementHandler = start_element
    #xmlparser.ElementDeclHandler = elmtdeclhandle
    #xmlparser.AttlistDeclHandler = attlistdeclhandler
    #fp = open(sys.argv[1])
    #dom = xmlparser.ParseFile(fp)
# -------------------------------------------------------------------
