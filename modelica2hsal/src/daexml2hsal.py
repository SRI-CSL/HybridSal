"Convert DAE XML into HybridSal"

import xml.dom.minidom
import xml.parsers.expat
import sys
import os.path
import daexmlPP
import ddae
import HSalXMLPP

def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            #return(i.data)
            return(i.nodeValue)

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

def helper_create_tag_val(tag, val, position = None):
    global dom
    node = dom.createElement(tag)
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    node.appendChild( dom.createTextNode( val ) )
    return node 

def replace(node, newnode, root):
    '''replace node by newnode and call simplify'''
    if node == root:	# I am the expr
        root = newnode
    else:
        parentnode = node.parentNode
        parentnode.replaceChild(newChild=newnode,oldChild=node)
        # root = simplify(parentnode, newnode, root)
    return root

def getPredsInConds(contEqns):
    '''get all predicates used in IF conditions'''
    def add2Preds(preds, name, val):
        if preds.has_key(name):
            if val != None and val not in preds[name]:
                preds[name].append(val)
        else:
            preds[name] = [] if val == None else [val]
        return preds
    def getPredsInBapp(c, preds):
        op = getArg(c, 1)
        a1 = getArg(c, 2)
        a2 = getArg(c, 3)
        s1 = valueOf(op).strip()
        if a1.tagName in ['identifier','pre'] and a2.tagName == 'number':
            name = valueOf(a1).strip() if a1.tagName == 'identifier' else valueOf(getArg(a1,1)).strip()
            # print 'trying to add {0}'.format(name)
            return add2Preds(preds, name, float(valueOf(a2)))
        elif s1 in ['or', 'and']:
            preds = getPredsInExpr(a1, preds)
            preds = getPredsInExpr(a2, preds)
            return preds
        elif s1 in ['>', '<'] and a2.tagName == 'number' and a1.tagName == 'BAPP':
            s11 = valueOf(getArg(a1,1)).strip()
            a11 = getArg(a1,2)
            a12 = getArg(a1,3)
            if (a12.tagName == 'identifier' and a11.tagName == 'number') or (a12.tagName == 'number' and a11.tagName == 'identifier'):
                if (a12.tagName == 'number' and a11.tagName == 'identifier'):
                    a11, a12 = a12, a11
                name = valueOf(a12).strip()
                val1 = float(valueOf(a11))
                val2 = float(valueOf(a2))
                if s11 == '-':
                    val = val1 - val2
                elif s11 == '+':
                    val = val2 - val1
                elif s11 == '*':
                    val = val2 / val1
                elif s11 == '/':
                    val = val1 / val2
                else:
                    assert False, 'Missing operator {0}'.format(s11)
                #print 'trying to add {0} {1}'.format(name,val)
                return add2Preds(preds, name, val)
            elif a11.tagName == 'identifier' and a12.tagName == 'identifier':
                name1 = valueOf(a11).strip()
                name2 = valueOf(a12).strip()
                val = float(valueOf(a2))
                return add2Preds(preds, (s11,name1,name2), val)
            else:
                #assert False, 'MISSING BAPP CODE: Found {0} expression...'.format(daexmlPP.ppExpr(c))
                print 'Warning: MISSING BAPP CODE: Found {0} expression...'.format(daexmlPP.ppExpr(c))
                return preds	# CHECK here ASHISH Ashish
        elif s1 in ['>', '<'] and a2.tagName == 'number' and a1.tagName == 'number':
            return preds
        else:
            # assert False, 'MISSING BAPP CODE: Found {0} expression.'.format(daexmlPP.ppExpr(c))
            print 'Warning: MISSING BAPP CODE: Found {0} expression.'.format(daexmlPP.ppExpr(c))
            return preds
    def getPredsInExpr(c, preds):
        # print 'entering', preds
        if c.tagName == 'identifier':
            return add2Preds(preds, valueOf(c).strip(), None)
        elif c.tagName == 'pre':
            return getPredsInExpr(getArg(c,1), preds)
        elif c.tagName == 'number':
            assert False, 'number can not be a Boolean'
        elif c.tagName == 'INITIAL' or c.tagName == 'string':
            return preds
        elif c.tagName == 'UAPP':
            return getPredsInExpr(getArg(c,2), preds)
        elif c.tagName == 'BAPP':
            return getPredsInBapp(c, preds)
        else:
            assert False, 'MISSING CODE: Found {0} expression.'.format(c.tagName)
    def getPredsInEqn(e, preds):
        ifs = e.getElementsByTagName('IF')
        for ite in ifs:
            cond = getArg(ite,1)
            preds = getPredsInExpr(cond, preds)
        return preds
    preds = {}
    for e in contEqns:
        preds = getPredsInEqn(e, preds)
    return preds

def getElementsByTagTagName(root, tag1, tag2):
    node = root.getElementsByTagName(tag1)
    if node == None or len(node) == 0:
        return []
    nodes = node[0].getElementsByTagName(tag2)
    ans = nodes if nodes != None else []
    return ans    

def getIdentifiersIn(root, tag1):
    ids = getElementsByTagTagName(root, tag1, 'identifier')
    return [ valueOf(i).strip() for i in ids ]

def isCont(e):
    ders = e.getElementsByTagName('der')
    return e.tagName == 'der' or (ders != None and len(ders) > 0)

def preprocessEqn(e):
    'convert e into der(x) = rhs form, if possible'
    def mkBOp(op,v1,v2):
        op = helper_create_tag_val('BINARY_OPERATOR',op)
        return helper_create_app('BAPP',[op,v1.cloneNode(True),v2.cloneNode(True)])
    def mkUOp(op,v1):
        op = helper_create_tag_val('UNARY_OPERATOR',op)
        return helper_create_app('UAPP',[op,v1.cloneNode(True)])
    def swapContLHS(lhs, rhs):
        isContLHS = isCont(lhs)
        isContRHS = isCont(rhs)
        assert not(isContLHS and isContRHS) #'ERROR: Unable to write DAE as dx/dt=Ax+b'
        if isContLHS:
            return (lhs, rhs)
        else:
            return (rhs, lhs)
    def isOp(v, tagName, op):
        return v.tagName==tagName and valueOf(getArg(v,1)).strip()==op
    def preprocessEqnAux(lhs, rhs):
        'lhs has der(); rhs does not have der() term'
        if lhs.tagName == 'der':
            return helper_create_app('equation',[lhs,rhs])
        elif isOp(lhs, 'BAPP', '+'):
            lhs1 = getArg(lhs,2)
            lhs2 = getArg(lhs,3)
            (lhs1, lhs2) = swapContLHS( lhs1, lhs2 )
            return preprocessEqnAux( lhs1, mkBOp('-',rhs,lhs2) )
        elif isOp(lhs, 'BAPP', '-'):
            lhs1old = getArg(lhs,2)
            lhs2old = getArg(lhs,3)
            (lhs1, lhs2) = swapContLHS( lhs1old, lhs2old )
            if lhs1 == lhs1old:
                return preprocessEqnAux( lhs1, mkBOp('+',rhs,lhs2) )
            else:
                return preprocessEqnAux( lhs1, mkBOp('-',lhs2,rhs) )
        elif isOp(lhs, 'BAPP', '*'):
            lhs1 = getArg(lhs,2)
            lhs2 = getArg(lhs,3)
            (lhs1, lhs2) = swapContLHS( lhs1, lhs2 )
            return preprocessEqnAux( lhs1, mkBOp('/',rhs,lhs2) )
        elif isOp(lhs, 'BAPP', '/'):
            lhs1old = getArg(lhs,2)
            lhs2old = getArg(lhs,3)
            (lhs1, lhs2) = swapContLHS( lhs1old, lhs2old )
            if lhs1 == lhs1old:
                return preprocessEqnAux( lhs1, mkBOp('*',rhs,lhs2) )
            else:
                return preprocessEqnAux( lhs1, mkBOp('/',lhs2,rhs) )
        elif isOp(lhs, 'UAPP', '-'):
            lhs = getArg(lhs,2)
            return preprocessEqnAux( lhs, mkUOp('-',rhs) )
        else:
            print 'unable to handle lhs: {0} == rhs:{1}'.format( lhs.toxml(), rhs.toxml() )
            assert False,'ERROR: Unreachable code; Unable to convert DAE to dx/dt=Ax+b'
    lhs = getArg(e, 1)
    rhs = getArg(e, 2)
    (lhs, rhs) = swapContLHS( lhs, rhs )
    return preprocessEqnAux(lhs, rhs)

def evalCond(c):
    if c.tagName == 'string':
        val = valueOf(c).strip()
        if val == 'TRUE':
            return True
        elif val == 'FALSE':
            return False
        else:
            return None
    elif c.tagName == 'BAPP' and valueOf(getArg(c,1)).strip() == 'AND':
        c1 = evalCond( getArg( c, 2 ) )
        c2 = evalCond( getArg( c, 3 ) )
        if c1 == False or c2 == False:
            return False
        else:
            return c1 and c2
    elif c.tagName == 'UAPP' and valueOf(getArg(c,1)).strip() == 'NOT':
        c1 = evalCond( getArg( c, 2 ) )
        ans = None if c1 == None else not c1
        return ans
    else:
        return None

def preprocessEqnNEW(eL,cstate,dstate):
    'convert e into der(x) = rhs form, if possible'
    def mkBOp(op,v1,v2):
        op = helper_create_tag_val('BINARY_OPERATOR',op)
        return helper_create_app('BAPP',[op,v1.cloneNode(True),v2.cloneNode(True)])
    def mkUOp(op,v1):
        op = helper_create_tag_val('UNARY_OPERATOR',op)
        return helper_create_app('UAPP',[op,v1.cloneNode(True)])
    def mkc(v):
        return helper_create_tag_val('number',str(v))
    def mkv(v):
        return helper_create_tag_val('identifier',v)
    def mkdv(v):
        var = helper_create_tag_val('identifier',v)
        return helper_create_app('der',[var])
    def mkprev(v):
        var = helper_create_tag_val('identifier',v)
        return helper_create_app('pre',[var])
    def polyrep2xmlL( lrL ):
        return [ polyrep2xmle(lr) for lr in lrL ]
    def polyrep2xmle( lr ):
        lhs = polyrep2xml(lr[0])
        rhs = polyrep2xml(lr[1])
        return helper_create_app('equation',[lhs,rhs])
    def polyrep2xml( p ):
        ans = None
        for (v,cnum) in p.items():
            if v == None:
                continue
            c = mkc(cnum)
            if isinstance(v,str) or isinstance(v,unicode):
                v = mkv(v)
            elif isinstance(v,tuple) and v[1] == True:
                v = mkdv(v[0])
            elif isinstance(v,tuple) and v[1] == False:
                v = mkprev(v[0])
            # elif v == None or else: pass
            cv = v if cnum==1 else mkBOp('*',c,v)
            ans = mkBOp('+',ans,cv) if ans != None else cv
        if p.has_key(None):
            cnum = p[None]
            if ans != None and cnum == 0:
                return ans
            c = mkc(cnum)
            if ans == None:
                return c
            ans = mkBOp('+',ans,c)
        if ans == None:
            ans = mkc(0)
        return ans
    def isOp(v, tagName, op):
        return v.tagName==tagName and valueOf(getArg(v,1)).strip()==op
    def ispolyrepc(p):
        n = len(p.items())
        return n==0 or (n==1 and p.has_key(None))
    def polyrepBOp(op,p,q):
        if op in ['+','-']:
            for (x,c) in q.items():
                if p.has_key(x):
                    p[x] = p[x] + c if op=='+' else p[x]-c
                else:
                    p[x] = c if op=='+' else -c
                if p[x] == 0 and x != None:
                    p.pop(x)
            return p
        elif op=='*':
            if not(ispolyrepc(p) or ispolyrepc(q)):
                print 'ERROR: Nonlinear expression found {0}*{1}'.format(p,q)
                print 'ERROR: Nonlinear expression found. UNSOUND'
                return p
            #assert ispolyrepc(p) or ispolyrepc(q), 'ERROR: Nonlinear expression found {0}*{1}'.format(p,q)
            (p,q) = (q,p) if ispolyrepc(p) else (p,q)
            d = q[None]
            if d==0:
                return {None:0}
            for (x,c) in p.items():
                p[x] = c*d
            return p
        elif op=='/':
            if not ispolyrepc(q):
                print 'ERROR: Dividing by non-constant; cannot handle {0}/{1}'.format(p,q)
                return p
            assert ispolyrepc(q), 'ERROR: Dividing by non-constant; cannot handle {0}/{1}'.format(p,q)
            d = q[None]
            for (x,c) in p.items():
                p[x] = c/d
            return p
        elif op=='max' or op=='min':
            print 'WARNING: Max/Min applied to polynomial. Unsound handling'
            return p
        elif op=='>' or op=='>=':
            print 'WARNING: >/>= applied to polynomial. Unsound handling'
            return None
        elif op=='^':
            print 'WARNING: ^ applied to polynomial. Unsound handling'
            return p
        else:
            assert False, 'Error: Unknown binary operator {0} applied on {1},{2}; cannot handle'.format(op, p, q)
    def polyrepUOp(op,p):
        if op == '-':
            for (x,c) in p.items():
                p[x] = -c
            return p
        else:
            assert False, 'Error: Unknown unary operator {0}; cannot handle'.format(op)
    def expr2polyrep(e):
        if e.tagName == 'identifier':
            return { valueOf(e).strip():1 }
        elif e.tagName == 'number':
            return { None: float( valueOf(e)) }
        elif e.tagName == 'der':
            return { (valueOf(getArg(e,1)).strip(),True):1 }
        elif e.tagName == 'pre':
            return { (valueOf(getArg(e,1)).strip(),False):1 }
        elif e.tagName == 'BAPP':
            e1 = expr2polyrep( getArg(e,2) )
            e2 = expr2polyrep( getArg(e,3) )
            if e1 != None and e2 != None:
                return polyrepBOp( valueOf(getArg(e,1)).strip(), e1, e2 )
            else:
                return None
        elif e.tagName == 'UAPP':
            e1 = expr2polyrep( getArg(e,2) )
            if e1 != None:
                return polyrepUOp( valueOf(getArg(e,1)).strip(), e1 )
            else:
                return None
        elif e.tagName == 'IF':
            c = getArg(e, 1)
            if evalCond(c) == True:
                return expr2polyrep( getArg(e,2) )
            elif evalCond(c) == False:
                return expr2polyrep( getArg(e,3) )
            else:
                return { e:1 }
        else:
            print 'unable to convert expr {0} to polyrep form'.format(e.toxml())
            assert False,'ERROR: Unable to convert expression to linear form'
    def freevar(p, dstate, cstate):
        varList = p.keys()
        for v in varList:
            if (isinstance(v,str) or isinstance(v,unicode)) and v not in cstate and v not in dstate:
                return v
        return None
    def dervar(varList, dstate, cstate):
        for v in varList:
            if isinstance(v,tuple) and v[0] in cstate:
                return v
        return None
    def moveDerLeft(p, q):
        p = polyrepBOp('-',p,q)
        q.clear()
        q[None] = 0
        # is there a derivative in p ?
        for i in p.keys():
            if p[i] == 0:
                p.pop(i)
        x = freevar(p, dstate, cstate)
        if x != None:
            substitution = polyrepsolve(p, q, x)
            return (substitution, None, None)
        x = dervar(p.keys(), dstate, cstate)
        if x != None:
            ode = polyrepsolve(p, q, x)
            return (None, ode, None)
        return (None,None,(p,q))
    def polyrepsolve(p,q,x):
        c = p.pop(x)
        q = polyrepBOp('-',q,p)
        lhs = { None:c} 
        q = polyrepBOp('/',q,lhs)
        lhs.clear()
        lhs[x] = 1
        return (lhs,q)
    def polyrepapplySub(p, subL):
        for (prepv,val) in subL:
            v = prepv.keys()[0]
            if p.has_key(v):
                c = p.pop(v)
                q = val.copy()
                q = polyrepBOp('*',{None:c},q)
                p = polyrepBOp('+',p,q)
        return p
    subL, odeL, othersL = [],[],[]
    for e in eL:
        lhs = getArg(e, 1)
        rhs = getArg(e, 2)
        #print 'debuggin printing ......................................'
        #print expr2sal(lhs), '=', expr2sal(rhs)
        p = expr2polyrep(lhs)
        q = expr2polyrep(rhs)
        #print p, '=', q
        #print 'debuggin printing ......................................'
        if p == None or q == None:
            print 'WARNING: Ignoring equation'
            continue
        p = polyrepapplySub(p, subL)
        q = polyrepapplySub(q, subL)
        (sub,ode,others) = moveDerLeft(p,q)
        if sub != None:
            subL.append(sub)
        if ode != None:
            odeL.append(ode)
        if others != None:
            othersL.append(others)
    # now I have subL, odeL, othersL
    # I dont have to apply later found subs to initially found odes becos that is impossible
    odeL = polyrep2xmlL(odeL)
    othersL = polyrep2xmlL(othersL)
    return (odeL, othersL)

def classifyEqns(eqns, cstate, dstate):
    "partition eqns into 2 sets: dx/dt=f(x) and x'=f(x)"
    def isDisc(e):
        lhs = getArg(e,1)
        return lhs.tagName == 'identifier' and valueOf(lhs).strip() in dstate
    (d,c,others) = ( [], [], [])
    for e in eqns:
        if isCont(e):
            # c.append(e)
            c.append( preprocessEqn(e) )	# THIS MESSES up eqns becos it uses nodes to create new equations
        elif isDisc(e):
            d.append(e)
        else:
            others.append(e)
    return (d,c,others)

def classifyEqnsNEW(eqns, cstate, dstate):
    "partition eqns into 2 sets: dx/dt=f(x) and x'=f(x)"
    def isDisc(e):
        lhs = getArg(e,1)
        return lhs.tagName == 'identifier' and valueOf(lhs).strip() in dstate
    def isInit(e):
        lhs = getArg(e,1)
        rhs = getArg(e,2)
        if lhs.tagName == 'initidentifier':
            return True
        elif rhs.tagName == 'initidentifier':
            e.appendChild(lhs)
            return True
        return False
    (d,c,others,init) = ( [], [], [], {})
    for e in eqns:
        if isCont(e):
            c.append(e)
        elif isDisc(e):
            d.append(e)
        elif isInit(e):
            init[valueOf(getArg(e,1)).strip()] = getArg(e,2)
        else:
            c.append(e)
    (c, others) = preprocessEqnNEW(c, cstate, dstate)
    return (d,c,others,init)

def findState(Eqn, cstate, dstate, var_details):
    "return (bools, reals, integers) from the give equations"
    def myappend(lst, v):
        if v not in lst:
            lst.append(v)
        return lst
    def find(name, allvars):
        for i in allvars:
            name1 = i.getAttribute('name').strip()
            if name1 == name:
                return i
        print 'ERROR: Unknown variable found! Can not handle.'
        assert False, "Model Error: Variable {0} is not declared".format(name)
        return None
    def getEnums(allvars):
        enums = {}
        for i in allvars:
            typ = i.getAttribute('type')
            if typ.startswith('enumeration'):
                evals = typ[12:-1]	# 12 is the length of 'enumeration(' -1 is for ')'
                evals = [x.strip() for x in evals.split(',')]
                enums[i.getAttribute('name')] = evals
        return enums
    def isEnumValue(name, enums):
        for k in enums.keys():
            for v in enums[k]:
                if name.endswith('.'+v) or name==v:
                    return v
        return None
    ids = Eqn.getElementsByTagName('identifier')
    #print 'Number of equations in Eqn is {0}'.len(Eqn.getElementsByTagName('equation'))
    #sys.stdout.flush()
    bools, reals, integers = [], [], []
    nonstates, inputs = [], []
    varmap = {}
    enums = getEnums(var_details)
    print 'There are {0} enums'.format(len(enums))
    for identifier in ids:
        name = valueOf(identifier).strip()
        # print name,
        # sys.stdout.flush()
        val = isEnumValue(name, enums)
        if val:
            newid = helper_create_tag_val('identifier', val)
            parentnode = identifier.parentNode
            parentnode.replaceChild(newChild=newid,oldChild=identifier)
            continue
        ovar = find(name, var_details)
        vtype = ovar.getAttribute('type')
        variability = ovar.getAttribute('variability')
        varmap[name] = ovar
        if variability != 'continuousState' and name not in dstate:
            myappend(nonstates, name)
        direction = ovar.getAttribute('direction')
        if direction == 'input':
            myappend(inputs, name)
        if vtype == 'Real':
            myappend(reals, name)
        elif vtype == 'Boolean':
            myappend(bools, name)
        elif vtype == 'Integer':
            myappend(integers, name)
        else:
            # assert False, "Type {0} not found".format(vtype)
            print >> sys.stderr, "IGNORING variable of Type {0}".format(vtype)
    print >> sys.stderr, 'bools', bools
    print >> sys.stderr, 'reals', reals
    print >> sys.stderr, 'integers', integers
    print >> sys.stderr, 'inputs', inputs
    print >> sys.stderr, 'nonstates', nonstates
    print >> sys.stderr, 'cstate', cstate
    print >> sys.stderr, 'dstate', dstate
    return (bools, reals, integers, inputs, nonstates, varmap, enums)
 
# -----------------------------------------------------------------
def expr2sal(node, flag=True):
    opmap = {'==':'=', 'and':'AND', 'or':'OR', 'not':'NOT'}
    def op2sal(node):
        op = valueOf(node).strip()
        ans = opmap[op] if opmap.has_key(op) else op
        return ans
    if node.tagName == 'identifier':
        ans = valueOf(node).strip() 
        if ans in ['false','true','False','True']:
            ans = ans.upper()
        else:
            ans += "'" if flag else ""
        return ans
    elif node.tagName == 'pre':
        return valueOf(getArg(node,1)).strip()
    elif node.tagName == 'der':
        return valueOf(getArg(node,1)).strip() + "dot'"
    elif node.tagName == 'number' or node.tagName == 'string':
        return valueOf(node).strip()
    elif node.tagName == 'INITIAL':
        return ''
    elif node.tagName == 'BAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        a2 = getArg(node, 3)
        s1 = op2sal(op)
        #print s1
        s2 = expr2sal(a1, flag)
        #print s2
        s3 = expr2sal(a2, flag)
        if s2 == '':	# hack to deal with initial()
            return s3
        if s3 == '':
            return s2
        return '(' + s2 + ')' + s1 + '(' + s3 + ')'
    elif node.tagName == 'UAPP':
        op = getArg(node, 1)
        a1 = getArg(node, 2)
        s1 = op2sal(op)
        s2 = expr2sal(a1, flag)
        return s1 + '(' + s2 + ')'
    elif node.tagName == 'IF':
        c  = getArg(node, 1)
        v1 = getArg(node, 2)
        v2 = getArg(node, 3)
        s1 = expr2sal(c, flag)
        #print s1
        s2 = expr2sal(v1, flag)
        #print s2
        s3 = expr2sal(v2, flag)
        return 'IF ' + s1 + ' THEN ' + s2 + ' ELSE ' + s3 + ' ENDIF '
    elif node.tagName == 'set':
        assert False, 'expr2sal missing code for set'
    else:
        print >> sys.stderr, 'MISSING CODE: Found {0} expression.'.format(node.tagName)
        print >> sys.stderr, 'MISSING CODE: {0}'.format(node.toprettyxml())
    return ""

def getInitialValue(vmap, var, iEqns):
    if iEqns.has_key(var):
        node = iEqns[var]
        return expr2sal(node,flag=False)
    if not vmap.has_key(var):
        return None
    node = vmap[var]	# node is from Modelica XML dom
    ival = node.getElementsByTagName('initialValue')
    if ival == None or len(ival) == 0:
        return None
    istr = ival[0].getAttribute('string')
    z = ddae.parse_expr(istr)
    # print 'Parsed expr as {0}'.format(z.toprettyxml())
    # convert2sal
    ans = expr2sal(z,flag=False)
    # print 'Converted to SAL as {0}'.format(ans)
    return ans

# need to handle INITIAL properly
def createControl(state, deqns, guard, iEqns = {}):
    "print the control HSAL module"
    def extractInitE(eqn):
        var = getArg(eqn,1)
        val = getArg(eqn,2)
        inits = val.getElementsByTagName('INITIAL')
        if inits == None or len(inits) == 0:
            return (var,val,None)
        assert len(inits) == 1, 'Assumed atmost one initial in expression'
        init = inits[0]
        p = init.parentNode
        while p != val and p.tagName == 'BAPP' and valueOf(getArg(p,1)).strip() == 'and':
            init = p
            p = p.parentNode
        false_node = helper_create_tag_val('string','FALSE')
        val = replace(init, false_node, val)
        return (var,val,init)
    def extractInit(deqns):
        return [ extractInitE(i) for i in deqns ]
    ans = "\n control: MODULE = \n BEGIN"
    (bools,reals,ints,inputs,nonstates,vmap,enums) = state
    for i in bools:
        ans += "\n  OUTPUT {0}: BOOLEAN".format(i)
    for i in ints:
        ans += "\n  OUTPUT {0}: NATURAL".format(i)
    for i in reals:
        ans += "\n  INPUT  {0}: REAL".format(i)
    for (k,v) in enums.items():
        ans += "\n  OUTPUT {0}: {1}".format(k,k+'Type')
    varValInitL = extractInit(deqns)
    first = True
    for (var, val, init) in varValInitL:
        lhs = expr2sal(var, flag = False)
        if init != None:
            sep = ";" if not(first) else "\n  INITIALIZATION"
            first = False if first else first
            rhs = expr2sal(init, flag = False)
            ans += "{2}\n\t {0} = {1}".format(lhs,rhs,sep)
        else:  # get initialization from vmap[var]
            initval = getInitialValue(vmap,lhs,iEqns)
            if initval != None:
                sep = ";" if not(first) else "\n  INITIALIZATION"
                first = False if first else first
                ans += "{2}\n\t {0} = {1}".format(lhs,initval,sep)
    ans  += "\n  TRANSITION\n  ["
    guard = guard if guard != "" else "TRUE"
    ans  += "\n  {0} -->".format(guard)
    first = True
    for (var, val, init) in varValInitL:
        lhs = expr2sal(var)
        rhs = expr2sal(val)
        sep = ";" if not(first) else ""
        first = False if first else first
        ans += "{2}\n\t {0} = {1}".format(lhs,rhs,sep)
    ans += "\n  ]"
    ans += "\n END;\n"
    return ans

def helper_create_app(tag, childs):
    global dom
    node = dom.createElement(tag)
    for i in childs:
        node.appendChild( i )
    return node 

def simplifyITEeq(e1, e2, var=None):
    "e1, e2 are conditional expressions; generate condition assigment"
    def isVar(v,name):
        return v.tagName=='identifier' and valueOf(v).strip()==name
    def isBOp(v,op):
        return v.tagName=='BAPP' and valueOf(getArg(v,1)).strip()==op
    def isUOp(v,op):
        return v.tagName=='UAPP' and valueOf(getArg(v,1)).strip()==op
    def mkBOp(op,v1,v2):
        op = helper_create_tag_val('BINARY_OPERATOR',op)
        return helper_create_app('BAPP',[op,v1.cloneNode(True),v2.cloneNode(True)])
    def mkUOp(op,v1):
        op = helper_create_tag_val('UNARY_OPERATOR',op)
        return helper_create_app('UAPP',[op,v1.cloneNode(True)])
    def xml2vars(v):
        ans = set()
        ids = v.getElementsByTagName('identifier')
        for i in ids:
            ans.add( valueOf(i).strip() )
        return ans
    def solve(v1, v2, var):
        if isVar(v1,var):
            return v2.cloneNode(True)
        if isVar(v2,var):
            return v1.cloneNode(True)
        if isBOp(v1,'+'):
            a1 = getArg(v1,2)
            a2 = getArg(v1,3)
            return solve(a1,mkBOp('-',v2,a2),var)
        if isBOp(v1,'-'):
            a1 = getArg(v1,2)
            a2 = getArg(v1,3)
            return solve(a1, mkBOp('+',v2,a2), var)
        if isBOp(v1,'*'):
            a1 = getArg(v1,2)
            a2 = getArg(v1,3)
            return solve(a2, mkBOp('/',v2,a1), var)
        if isUOp(v1,'-'):
            a1 = getArg(v1,2)
            return solve(a1, mkUOp('-',v2), var)
        print 'Unable to solve equation'
        # assert False, 'Expr is {0}'.format(daexmlPP.ppExpr(v1))
        print 'WARNING: UNABLE TO SOLVE Expr {0}'.format(daexmlPP.ppExpr(v1))
        return None
    assert len(e1) > 0, 'Error: expecting nonempty list'
    if var == None:
        allX = xml2vars(e1[0][2])
        for (c,d,v) in e1[1:]:
            vX = xml2vars(v)
            allX.intersection_update(vX)
            if len(allX) == 0:
                print 'Failed to find variable to solve'
                return None
        if len(allX) == 0:
            print 'Failed to find variable to solve'
            return None
        var = allX.pop()
    # assert var != None, 'Error: Cant handle arbitrary equations'
    if var == None:
        return None
    ans = []
    for (c0i,d0i,v0i) in e1:
        for (c1i,d1i,v1i) in e2:
            ai = list(c0i)
            bi = list(d0i)
            ai.extend(c1i)
            bi.extend(d1i)
            vi = solve(v0i, v1i, var)
            if vi != None:
                ans.append((ai,bi,vi))
    print >> sys.stderr, 'SimplifyITEeq input has {0} = {1} cases'.format(len(e1),len(e2))
    print >> sys.stderr, 'SimplifyITEeq output has {0} cases'.format(len(ans))
    return (var, ans)

def others2salmonitorNew(oeqns, bools, ints, reals):
    def xml2vars(v):
        ans = set()
        ids = v.getElementsByTagName('identifier')
        for i in ids:
            ans.add( valueOf(i).strip() )
        return ans
    if len(oeqns) == 0:
        return None
    ans = "\n monitor: MODULE = \n BEGIN"
    first = True
    guard = ""
    variables = set()
    for e in oeqns:
        lhs = getArg(e,1) 
        rhs = getArg(e,2) 
        sep = " AND" if not first else ""
        first = False
        guard += "{2}\n   {0} = {1}".format(expr2sal(lhs,flag=True),expr2sal(rhs,flag=True),sep)
        variables = variables.union( xml2vars( lhs ))	# a set
        variables = variables.union( xml2vars( rhs ))	# a set
    for v in variables:
        # assert v in reals or v in bools or v in ints
        if not(v in reals or v in bools or v in ints):
            print 'WARNING: VARIABLE {0} not in reals/bools/ints'.format(v)
            tval = 'REAL'
        else:
            tval = 'REAL' if v in reals else ('BOOLEAN' if v in bools else 'NATURAL')
        ans += '\n  INPUT {0}: {1}'.format(v, tval)
    ans += '\n  TRANSITION\n  ['
    ans += '\n  {0} --> '.format(guard)
    ans += '\n  ]'
    ans += "\n END;\n"
    return ans

def others2salmonitor(varvall, bools, ints, reals):
    "varvall is a list of (var,ans) as above; output it as sal definition"
    def ite2sal(val):
        if len(val) == 1:
            ans = expr2sal(val[0][2],flag=True)
            return ans
        first, ans = True, ""
        for (c,d,v) in val:
            sep = "ELSIF" if not first else "IF"
            first = False
            ans += " {2} {0} AND {1} ".format(toSal(c,0,primeflag=True),toSal(d,1,primeflag=True),sep)
            ans += " THEN {0}".format(expr2sal(v,flag = True))
        # Repeating last value in ELSE clause.....
        ans += " ELSE {0} ENDIF".format(expr2sal(v,flag=True))
        return ans
    def xml2vars(v):
        ans = set()
        ids = v.getElementsByTagName('identifier')
        for i in ids:
            ans.add( valueOf(i).strip() )
        return ans
    def xmlList2vars(c):
        ans = set()
        for i in c:
            ans = ans.union( xml2vars( i ) )
        return ans
    def condE2vars( val ):
        ans = set()
        for (c,d,e) in val:
            ans = ans.union( xmlList2vars(c) )
            ans = ans.union( xmlList2vars(d) )
            ans = ans.union( xml2vars(e) )
        return ans
    if len(varvall) == 0:
        return None
    ans = "\n monitor: MODULE = \n BEGIN"
    first = True
    guard = ""
    variables = set()
    for (var,val) in varvall:
        sep = " AND " if not first else ""
        first = False
        guard += "{1}\n   {0}' = ".format(var,sep)
        guard += ite2sal(val)
        variables = variables.union(condE2vars( val ))	# a set
        variables.add( var )		# add var to set
    # now we have guard and the variables
    for v in variables:
        assert v in reals or v in bools or v in ints
        tval = 'REAL' if v in reals else ('BOOLEAN' if v in bools else 'NATURAL')
        ans += '\n  INPUT {0}: {1}'.format(v, tval)
    ans += '\n  TRANSITION\n  ['
    ans += '\n  {0} --> '.format(guard)
    ans += '\n  ]'
    ans += "\n END;\n"
    return ans

def others2saldef(varvall):
    "varvall is a list of (var,ans) as above; output it as sal definition"
    def ite2sal(val):
        first, ans = True, ""
        for (c,d,v) in val:
            sep = "ELSIF" if not first else "IF"
            first = False
            ans += "\n    {2} {0} AND {1} ".format(toSal(c,0),toSal(d,1),sep)
            ans += "\n    THEN {0}".format(expr2sal(v,flag = False))
        # Repeating last value in ELSE clause.....
        ans += "\n    ELSE {0} ENDIF".format(expr2sal(v,flag=False))
        return ans
    ans = ""
    if len(varvall) == 0:
        return ans
    ans += "\n  DEFINITION"
    first = True
    for (var,val) in varvall:
        sep = ";" if not first else ""
        first = False
        ans += "{1}\n   {0} = ".format(var,sep)
        ans += ite2sal(val)
    return ans
    
def replace(node, newnode, root):
    '''replace node by newnode and call simplify'''
    if node == root:	# I am the expr
        root = newnode
    else:
        parentnode = node.parentNode
        parentnode.replaceChild(newChild=newnode,oldChild=node)
    return root

def toSal(pn, flag, primeflag = False):
    ans = ""
    first = True
    if len(pn) == 0:
        ans = 'TRUE'
    for i in pn:
        ans += ' AND ' if not first else ''
        first = False
        if flag == 0:
            ans += '(' + expr2sal(i, flag = primeflag) + ')' # CHECK flag setting
        else:
            ans += 'NOT(' + expr2sal(i, flag = primeflag) + ')'
    return ans

def createPlant(state, ceqns, oeqns, iEqns = {}):
    "print the PLANT HSAL module"
    def occurs(var, node):
        ids = node.getElementsByTagName('identifier')
        for i in ids:
            if valueOf(i).strip() == var:
                return True
        if node.tagName == 'identifier' and valueOf(node).find(var) != -1:
            return True
        return False
    def applySubstitution(expr, mapping):
        for (var,val) in mapping:
            expr = applySubstitution1(expr, var, val)
        return expr
    def applySubstitution1(expr, var, val):
        ans = []
        for (ci,di,vi) in expr:
            if not occurs(var,vi):
                ans.append( (ci,di,vi) )
            else:
                for (ai,bi,wi) in val:
                    u1 = list( ci )
                    u1.extend( ai )
                    v1 = list( di )
                    v1.extend( bi )
                    ans.append( (u1,v1, applySubBase(vi,var,wi)) )
        return ans
    def applySubBase(node, var, val):
        expr = node.cloneNode(True)
        ids = expr.getElementsByTagName('identifier')
        for i in ids:
            varname = valueOf(i).strip()
            if varname == var:
                valuecopy = val.cloneNode(True)
                expr = replace(i, valuecopy, expr)
        return expr
    def applyOpUnary(op, e1):
        "multiply two conditional exprs"
        ans = []
        if valueOf(op).strip() == '-':
            for (p1,n1,v1) in e1:
                p12 = p1
                n12 = n1
                v12 = helper_create_app('UAPP',[op.cloneNode(True),v1.cloneNode(True)])
                ans.append((p12,n12,v12))
        else:
            print 'Found unhandled operator {0} applied on an ITE'.format(valueOf(op).strip())
            assert False, 'No other operator supported'
        return ans
    def applyOp(op, e1, e2):
        "multiply two conditional exprs"
        ans = []
        if valueOf(op).strip() in ['*', '+', '-', '/']:
            for (p1,n1,v1) in e1:
                for (p2,n2,v2) in e2:
                    p12 = list(p1)
                    n12 = list(n1)
                    v12 = helper_create_app('BAPP',[op.cloneNode(True),v1.cloneNode(True),v2.cloneNode(True)])
                    p12.extend(p2)
                    n12.extend(n2)
                    ans.append((p12,n12,v12))
        else:
            print 'Found unhandled operator {0} combining ITEs'.format(valueOf(op).strip())
            assert False, 'No other operator supported'
        return ans
    def expr2cexpr2( val ):
        if val.tagName == 'BAPP':
            op = getArg(val, 1)
            a1 = getArg(val, 2)
            a2 = getArg(val, 3)
            e1 = expr2cexpr2( a1 )
            e2 = expr2cexpr2( a2 )
            return applyOp( op, e1, e2 )
        else:
            return expr2cexpr(val)
    def expr2cexpr( val ):
        "expr 2 conditional expr"
        if val.tagName != 'IF' and len(val.getElementsByTagName('IF')) == 0:
            return [([], [], val)]
        elif val.tagName == 'IF': # val.tagName == 'IF':
            iteCond = getArg(val, 1)
            iteThen = getArg(val, 2)
            iteElse = getArg(val, 3)
            thenv = expr2cexpr( iteThen )
            elsev = expr2cexpr( iteElse )
            for (p,n,v) in thenv:
                p.append( iteCond )
            for (p,n,v) in elsev:
                n.append( iteCond )
            thenv.extend( elsev )
            return thenv
            '''ans = []
            while val.tagName == 'IF':
                iteCond = getArg(val, 1)
                iteThen = getArg(val, 2)
                val = getArg(val, 3)
                ans.append( ([iteCond], [], iteThen) )
            ans.append( ( [], [iteCond], val ) )
            return ans '''
        elif val.tagName == 'BAPP':
            op = getArg(val, 1)
            a1 = getArg(val, 2)
            a2 = getArg(val, 3)
            e1 = expr2cexpr( a1 )
            e2 = expr2cexpr( a2 )
            return applyOp( op, e1, e2 )
        elif val.tagName == 'UAPP':
            op = getArg(val, 1)
            a1 = getArg(val, 2)
            v1 = expr2cexpr( a1 )
            return applyOpUnary( op, v1 )
        else:
             assert False, 'Can not convert nested IF-THEN-ELSE to HybridSal'
    def myproduct( vvl ):
        "vvl = list of (var, (p,n,v)-list). OUTPUT (p,n,(var,v)-list)"
        ans = []
        for (var,val) in vvl:
            tmp = []
            for (p,n,v) in val:
                tmp.append( (p,n,[(var,v)]) )
            ans.append(tmp)
        assert len(ans) >= 1
        # if len(ans) <= 1:
            # return ans
        # else:
        return myproductAux( ans[1:], ans[0] )
    def myproductAux( pnvvlll, pnvvll ):
        if len(pnvvlll) == 0:
            return pnvvll
        pnvvll2 = pnvvlll[0]
        ans = []
        for (p,n,vvl) in pnvvll2:
            for (p1,n1,vvl1) in pnvvll:
                x = list(p)
                y = list(n)
                x.extend(p1)
                y.extend(n1)
                z = list(vvl)
                z.extend(vvl1)
                ans.append( (x,y,z) )
        return myproductAux( pnvvlll[1:], ans )
    ans = "\n plant: MODULE = \n BEGIN"
    (bools,reals,ints,inputs,nonstates,vmap,enums) = state
    for i in bools:
        ans += "\n  INPUT {0}: BOOLEAN".format(i)
    for i in ints:
        ans += "\n  INPUT {0}: NATURAL".format(i)
    for (k,v) in enums.items():
        ans += "\n  INPUT {0}: {1}".format(k, k+'Type')
    for i in reals:
        if i in inputs:
            ans += "\n  INPUT {0}: REAL".format(i)
        else:
            ans += "\n  OUTPUT  {0}: REAL".format(i)
    ans  += "\n  INITIALIZATION"
    first = True
    for i in reals:
        initval = getInitialValue(vmap,i,iEqns)
        if initval != None:
            sep = ";" if not(first) else ""
            first = False if first else first
            ans += "{2}\n\t {0} = {1}".format(i,initval,sep)
    # ASHISH: get init values from dom2 ????
    # first get conditional diff eqns ; then print
    # ans  += "\n  TRUE -->"
    ode = []
    for e in ceqns:
        lhs = getArg(e,1) 
        rhs = getArg(e,2) 
        (var,val) = (rhs,lhs) if rhs.tagName == 'der' else (lhs,rhs)
        assert var.tagName == 'der', 'ERROR: Unable to covert DAE to dx/dt = Ax+b'
        name = valueOf(getArg(var,1)).strip()
        rhs =  expr2cexpr(val)
        ode.append( (name, rhs) )
        print >> sys.stderr, 'ODE for {0} has {1} cases'.format(name,len(rhs))
    others = []
    for e in oeqns:
        lhs = getArg(e,1) 
        rhs = getArg(e,2) 
        e1 =  expr2cexpr(lhs)
        e2 =  expr2cexpr(rhs)
        others.append( (e1, e2) )
        print >> sys.stderr, 'Other equation has {0} and {1} cases'.format(len(e1),len(e2))
        # print 'lhs = {0}'.format(daexmlPP.ppExpr(lhs))
        # print 'rhs = {0}'.format(daexmlPP.ppExpr(rhs))
        # print 'e1 = {0}'.format(e1)
        # print 'e2 = {0}'.format(e2)
    others = [ simplifyITEeq(e1,e2) for (e1,e2) in others ]
    others[:] = filter(None, others)
    # now I have the substitution in others; apply it to ode
    # ans += others2saldef(others)
    # print '#####-----****************ode', ode
    newode = [(var,applySubstitution(val, others)) for (var,val) in ode]
    # print '#####-----****************newode', newode
    finalode = myproduct(newode)
    # print '#####-----****************finalode', finalode
    ans  += "\n  TRANSITION\n  ["
    first = True
    for (p,n,vvl) in finalode:
        sep = "\n  []" if not(first) else ""
        first = False
        ans += "{2}\n  {0} AND {1} -->".format(toSal(p,0),toSal(n,1),sep)
        ffirst = True
        for (var,val) in vvl:
            sep = ";" if not(ffirst) else ""
            ffirst = False if ffirst else ffirst
            ans += "{2}\n\t {0} = {1}".format(var+"dot'",expr2sal(val,flag=False),sep)
    ans += "\n  ]"
    ans += "\n END;\n"
    #monitor = others2salmonitor(others, bools, ints, reals)
    monitor = others2salmonitorNew(oeqns, bools, ints, reals)
    if monitor != None:
        ans += monitor
        ans += "\n\n system: MODULE = control || plant || monitor ;"
    else:
        ans += "\n\n system: MODULE = control || plant ;"
    return ans
# -----------------------------------------------------------------

def createEventsFromPreds(preds, reals, inputs):
    "preds = list of (var,val-list) or ((bop,e1,e2), val-list)"
    "output formula that says that one event is generated at each time step on reals"
    ans,first = "", True
    for (e,vl) in preds.items():
        if isinstance(e,tuple):
            (bop,e1,e2) = e
            assert isinstance(e1,str) or isinstance(e1,unicode)
            assert isinstance(e2,str) or isinstance(e2,unicode)
            estr = e1 + "'" + bop + e2 + "'"
        else:
            assert isinstance(e,str) or isinstance(e,unicode), 'Error: Expecting str/unicode, found {0}'.format(type(e))
            estr = e + "'"
            if (e not in reals) or (e in inputs):
                continue
        for v in vl:
            sep = " OR" if not first else ""
            first = False
            ans += "{2} {0} = {1}".format(estr,str(v),sep)
    return ans
            

# -----------------------------------------------------------------
def convert2hsal(dom1, dom2, dom3 = None):
    '''dom1: DAE XML; dom2: original modelica XML; dom3: property XML
     return (HSal,PropHSal) as strings'''
    def alpha_rename_aux(ans, ans2, bools):
        for i in bools:
            j = i.replace('.','_')
            j = j.replace('$','S')
            if i != j:
                # j = i.replace('.','_')
                ans = ans.replace(i, j)
                ans2 = ans2.replace(i, j)
        return (ans, ans2)
    def alpha_rename(ans, ans2, state):
        (bools,reals,ints,inputs,nonstates,vmap,enums) = state
        (ans, ans2) = alpha_rename_aux(ans, ans2, bools)
        (ans, ans2) = alpha_rename_aux(ans, ans2, ints)
        (ans, ans2) = alpha_rename_aux(ans, ans2, reals)
        return (ans, ans2)
    def printEqn(e):
        lhs = getArg(e,1)
        rhs = getArg(e,2)
        # print 'lhs = {0}'.format(daexmlPP.ppExpr(lhs))
        # print 'rhs = {0}'.format(daexmlPP.ppExpr(rhs))
        print >> sys.stderr, '{0} = {1}'.format(daexmlPP.ppExpr(lhs),daexmlPP.ppExpr(rhs))
    def printE(eqns):
        for i in eqns:
            printEqn(i)
    def createEnumDecl(enums):
        ans = ''
        for k in enums.keys():
            ans += '{0}: TYPE = '.format(k+'Type')
            first = True
            for v in enums[k]:
                ans += '{0}{1}'.format(',' if not(first) else '{', v)
                first = False
            ans += '};\n'
        return ans
    # decide later if creating hsal XML or hsal string
    cstate = getIdentifiersIn(dom1,'continuousState')
    dstate = getIdentifiersIn(dom1,'discreteState')
    knownvars = dom1.getElementsByTagName('knownVariables')[0]
    varvals = knownvars.getElementsByTagName('variablevalue')
    if varvals != None and len(varvals) > 0:
        print 'ERROR: Unable to eliminate knownVariable equations'
        return -1
    Eqn = dom1.getElementsByTagName('equations')[0]
    eqns = getElementsByTagTagName(dom1, 'equations', 'equation')
    print >> sys.stderr, 'Found {0} equations. Processing...'.format(len(eqns))
    var_details = getElementsByTagTagName(dom2, 'orderedVariables', 'variable')
    var_details2 = getElementsByTagTagName(dom2, 'knownVariables', 'variable')
    var_details.extend(var_details2)
    # find and classify all variables that occur in Eqn -- do this before classifyEqns becos it messes up eqns
    print 'var_details has {0} elmnts'.format(len(var_details))
    state = findState(Eqn,cstate,dstate,var_details)
    (bools,reals,ints,inputs,nonstates,vmap,enums) = state
    print '------------final size of state---------------'
    print >> sys.stderr, 'Found {0} bools, {1} reals, {2} ints'.format(len(bools),len(reals),len(ints))
    print >> sys.stderr, 'Found {0} inputs, {1} non-states'.format(len(inputs),len(nonstates))
    print >> sys.stderr, 'Found {0} vmap, {1} enums'.format(len(vmap),len(enums))
    print '-----------------------------------------------'
    #print >> sys.stderr, 'State: {0}'.format(state)
    # find and classify all equations in Eqn -- this messes up contEqns (essentially deletes them from Eqn)
    (discEqns,contEqns,oEqns,iEqns) = classifyEqnsNEW(eqns,cstate,dstate)
    print >> sys.stderr, 'Classified eqns into {0} discrete, {1} cont, {2} others'.format(len(discEqns),len(contEqns),len(oEqns))
    print >> sys.stderr, 'discrete eqns: ', printE(discEqns)
    print >> sys.stderr, 'cont eqns: ', printE(contEqns)
    print >> sys.stderr, 'other eqns: ', printE(oEqns)
    print >> sys.stderr, 'init eqns: ',
    for (i,j) in iEqns.items():
        print >> sys.stderr, '{0} = {1}'.format(i,daexmlPP.ppExpr(j)),
    print >> sys.stderr, ''
    # preds = getPredsInConds(contEqns)
    # Note: dom1 is MESSED UP; contEqns have been DELETED; so we can't get eqns from dom1.
    eqns = list(discEqns)
    eqns.extend(contEqns)
    eqns.extend(oEqns)
    preds = getPredsInConds(eqns)
    print >> sys.stderr, 'Found {0} preds'.format(len(preds))
    print >> sys.stderr, 'Preds: {0}'.format(preds)
    ans = createEnumDecl(enums)
    ans0 = createEventsFromPreds(preds, reals, inputs)	# Should events on inputs be included?
    print >> sys.stderr, 'created events from preds'
    ans1 = createControl(state, discEqns, ans0, iEqns)
    print >> sys.stderr, 'created control'
    ans2 = createPlant(state, contEqns, oEqns, iEqns)
    print >> sys.stderr, 'created plant'
    # replace varname.var -> varname_var
    ans += ans1 + ans2
    propStr = createProperty(dom3)
    (ans, propStr) = alpha_rename(ans, propStr, state)
    return (ans, propStr)

def createProperty(dom3):
    if dom3 != None and not(isinstance(dom3, dict)):
        return createPropertyXML(dom3)
    if dom3 != None and isinstance(dom3, dict):
        return createPropertyJSON(dom3)
    return ''

def createPropertyXML(dom3):
    def mkG(dom3, arg1):
        implopstr = dom3.createTextNode('G')
        implop = dom3.createElement('NAMEEXPR')
        implop.appendChild(implopstr)
        arg = dom3.createElement('TUPLELITERAL')
        arg.appendChild(arg1)
        impl = dom3.createElement('APPLICATION')
        impl.appendChild(implop)
        impl.appendChild(arg)
        return impl
    def mkImpl(dom3, arg1, arg2):
        impl = dom3.createElement('APPLICATION')
        impl.setAttribute('INFIX', 'YES')
        impl.setAttribute('PARENS', '1')
        implop = dom3.createElement('NAMEEXPR')
        implopstr = dom3.createTextNode('=>')
        implop.appendChild(implopstr)
        arg = dom3.createElement('TUPLELITERAL')
        arg.appendChild(arg1)
        arg.appendChild(arg2)
        impl.appendChild(implop)
        impl.appendChild(arg)
        return impl
    propStr = ''
    if dom3 != None:
        ccl = dom3.getElementsByTagName('CONTEXT')
        if ccl != None and len(ccl) > 0:
           ctxtExpr = getArg(ccl[0], 1)
        else:
           ctxtExpr = None
        ccl = dom3.getElementsByTagName('PROPERTY')
        if ccl != None and len(ccl) > 0:
            propExpr = getArg(ccl[0], 1)
            #print 'Printing propExpr {0}'.format(propExpr.toxml())
            LTLOpl = propExpr.getElementsByTagName('LTLOP')
            for i in LTLOpl:
                i.tagName = 'NAMEEXPR'
            if ctxtExpr != None:
                if LTLOpl == None or len(LTLOpl) == 0:
                    print >> sys.stderr, 'Error: Property has no temporal operator; assuming G'
                    propExpr = mkImpl(dom3,ctxtExpr,propExpr)
                    propExpr = mkG(dom3,propExpr)
                else:
                    op = valueOf(LTLOpl[0])
                    if op == 'G' or op == 'ALWAYS' or op == 'always':
                        propExpr1 = getArg(LTLOpl[0].parentNode,2)
                        if propExpr1 == None:
                            print 'Error: Incorrect syntax for property...'
                            print LTLOpl[0].toxml()
                            print propExpr.toxml()
                            sys.exit(-1)
                        arg2 = getArg(propExpr1,1)
                        propExpr1.removeChild(arg2)
                        impl = mkImpl(dom3,ctxtExpr, arg2)
                        propExpr1.appendChild(impl)
                    else:
                        propExpr = mkImpl(dom3,ctxtExpr,propExpr)
                        propExpr = mkG(dom3,propExpr)
            else:	# if ctxtExpr is None
                if LTLOpl == None or len(LTLOpl) == 0:
                    print >> sys.stderr, 'Error: Property has no temporal operator; assuming G'
                    propExpr = mkG(dom3,propExpr)
           # at this point, propExpr is our desired property   
        else:	# no property in the given file   
            print >> sys.stderr, 'There is no property in the given file'
            propExpr = None
        # at this point, propExpr is None OR is our desired property   
        if propExpr != None:
            propStr = HSalXMLPP.HSalPPExpr(propExpr)
        else:
            propStr = ''
    # propStr is the desired property; 
    return propStr

def createPropertyJSON(dom3):
    def json2str(expr):
        if isinstance(expr, int):
            return str(expr)
        elif isinstance(expr, str) or isinstance(expr, unicode):
            return expr
        elif isinstance(expr, dict):
            try:
                if expr['nargs'] == 2:
                    s1 = json2str(expr['args'][0])
                    s2 = json2str(expr['args'][1])
                    return '(' + s1 + ' ' + expr['f'] + ' ' + s2 + ')'
                elif expr['nargs'] == 1:
                    s1 = json2str(expr['args'][0])
                    return expr['f'] + '(' + s1 + ')'
                else:
                    print expr
                    print >> sys.stderr, 'Error: expecting 1 or 2, found {0}'.format(expr['nargs'])
                    sys.exit(-1)
            except Exception, e:
                print e, expr
                print >> sys.stderr, 'Error: json2str: Ill-formed JSON'
                sys.exit(-1)
        else:
            print expr, type(expr)
            print >> sys.stderr, 'Error: json2str: Ill-formed JSON'
            sys.exit(-1)
    def isG(op):
        return (op in ['G','Always','always'])
    def isF(op):
        return (op in ['F','Eventually','eventually'])
    def isLTLOp(op):
        return (isG(op) or isF(op))
    propStr = ''
    try:
        if dom3.has_key('context'):
            ctxtExpr = dom3['context']
        else:
            ctxtExpr = None
        if dom3.has_key('property'):
            propExpr = dom3['property']
        else:
            propExpr = None
        # output G( ctxt => prop )
        if isinstance(propExpr, dict) and isG(propExpr['f']):
            propExpr['f'] = 'G'
            if ctxtExpr != None:
                propExpr1 = propExpr['args'][0]
                argsL = [ ctxtExpr, propExpr1 ]
                newExpr = { 'f':'=>', 'nargs':2, 'args': argsL }
                propExpr['args'] = [ newExpr ]
        elif isinstance(propExpr, dict) and isLTLOp(propExpr['f']):
            assert False, 'Error: Can not handle liveness properties'
        elif propExpr != None:
            print >> sys.stderr, 'Warning: Property has no temporal operator; assuming G'
            if ctxtExpr != None:
                argsL = [ ctxtExpr, propExpr ]
                tmp = { 'f':'=>', 'nargs':2, 'args': argsL }
                propExpr = { 'f':'G', 'nargs':1, 'args': [ tmp ] }
            else:	# if ctxtExpr is None
                propExpr = { 'f':'G', 'nargs':1, 'args': [ propExpr ] }
        else:	# no property in the given file   
            print >> sys.stderr, 'There is no property in the given file'
            propExpr = None
        # at this point, propExpr is None OR is our desired property   
        if propExpr != None:
            propStr = json2str(propExpr)
        else:
            propStr = ''
    except Exception, e:
        print e
        print >> sys.stderr, 'Error: Ill-formed JSON for property/context at TOP'
        sys.exit(-1)
    # propStr is the desired property; 
    return propStr


def create_output_file(filename, hsalstr, propStr = ''):
    "dom3: context_property.xml"
    def moveIfExists(filename):
        import shutil
        if os.path.isfile(filename):
            print >> sys.stderr, "Output file {0} exists.".format(filename),
            print >> sys.stderr, "Renaming old file to {0}.".format(filename+"~")
            shutil.move(filename, filename + "~")
    basename,ext = os.path.splitext(filename)
    dirname, filebasename = os.path.split(basename)
    filebasename = filebasename.replace('.','_')
    basename = os.path.join(dirname, filebasename)
    basename += "Model"
    outfile = basename + ".hsal"
    moveIfExists(outfile)
    (dirname,basefilename) = os.path.split(basename)
    ansBEGIN = basefilename
    ansBEGIN += ": CONTEXT ="
    ansBEGIN += "\nBEGIN"
    ansEND = "\nEND"
    with open(outfile, "w") as fp:
        print >> fp, '% Generated automatically by daexml2hsal'
        print >> fp, ansBEGIN
        print >> fp, hsalstr
        if propStr != '':
            print >> fp, ' p1: THEOREM\n   system |- {0} ;'.format(propStr)
        print >> fp, ansEND
    print "Created file %s containing the HybridSAL representation" % outfile
    return outfile

def printUsage():
    print '''
daexml2hsal -- a converter from differential algebraic equations to HybridSal

Usage: python daexml2hsal <daexml_file> <modelica_xmlfile> [--addTime|--removeTime]
    '''

def daexml2hsal(dom1, dom2, filename, dom3):
    "dom3: context_property.xml; dom1: daexml, dom2: original modelica"
    global dom
    dom = dom1
    try:
        (hsalstr, propStr) = convert2hsal(dom1, dom2, dom3)
    except AssertionError, e:
        # print 'Assertion Violation Found'
        print e
        print 'Unable to handle such models...quitting'
        sys.exit(-1)
    return create_output_file(filename, hsalstr, propStr)

def addTime(dom2):
    'add time as a new continuousState variable in the model'
    node = dom2.createElement('variable')
    node.setAttribute('name', 'time')
    node.setAttribute('variability', 'continuousState')
    node.setAttribute('direction', 'none')
    node.setAttribute('type', 'Real')
    node.setAttribute('index', '-1')
    node.setAttribute('fixed', 'false')
    node.setAttribute('flow', 'NonConnector')
    node.setAttribute('stream', 'NonStreamConnector')
    orderedVars_varlists = getElementsByTagTagName(dom2, 'orderedVariables', 'variablesList')
    assert orderedVars_varlists != None and len(orderedVars_varlists) > 0
    orderedVars_varlist = orderedVars_varlists[0]
    orderedVars_varlist.appendChild(node)
    equations = dom2.getElementsByTagName('equations')
    newequation = dom2.createElement('equation')
    newequation.appendChild( dom2.createTextNode('der(time) = 1') )
    assert equations != None and len(equations) > 0
    equations[0].appendChild(newequation)
    return dom2

def removeTime(dom1):
    'remove all equations that mention time in them'
    def hasTime(e):
        ids = e.getElementsByTagName('identifier')
        for identifier in ids:
            name = valueOf(identifier).strip()
	    if name.strip() == 'time':
                return True
        return False
    Eqn = dom1.getElementsByTagName('equations')[0]
    eqns = Eqn.getElementsByTagName('equation')
    for e in eqns:
        if hasTime(e):
            Eqn.removeChild(e)
    Eqn = dom1.getElementsByTagName('knownVariables')[0]
    eqns = Eqn.getElementsByTagName('variablevalue')
    for e in eqns:
        if hasTime(e):
            Eqn.removeChild(e)
    return dom1

def main():
    global dom
    if not len(sys.argv) >= 3:
        printUsage()
        return -1
    basename,ext1 = os.path.splitext(sys.argv[1])
    basename,ext2 = os.path.splitext(sys.argv[2])
    if not(ext1 in ['.xml','.daexml','.dae_flat_xml'] and ext2 == '.xml'):
        print 'ERROR: Unknown files; expecting XML files'
        printUsage()
        return -1
    if not(os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2])):
        print 'ERROR: File does not exist'
        printUsage()
        return -1
    dom1 = xml.dom.minidom.parse(sys.argv[1])
    dom2 = xml.dom.minidom.parse(sys.argv[2])
    if '--addTime' in sys.argv[1:]:
        dom2 = addTime(dom2)
    if '--removeTime' in sys.argv[1:]:
        dom1 = removeTime(dom1)
    dom = dom1
    (hsalstr,propStr) = convert2hsal(dom1, dom2)
    create_output_file(sys.argv[1], hsalstr)
    return 0

if __name__ == "__main__":
    main()

