# This is based on dparser - http://dparser.sourceforge.net/
# Install dparser from source in above link.
# It comes with a verilog.g parser that works (but no actions)
# It also comes with a python extension in a python subdirectory
# This depends on swig (available as an Ubuntu package)

# This file is a translation of the verilog.g grammar to python
# It's a bit slower - about 2:37 to parse voting_machine_flat_nc.v
# compared to about 1:30 for parser.g

# To use, assuming you have dparser available, start python,
# >>> from dverilog import *
# >>> f = open('voting_machine_flat_nc.v', 'r')
# >>> x = f.read()
# >>> y = Parser().parse(x)    # y is now a dparser.ParsedStructure instance

from dparser import Parser, SyntaxError
from xml.dom.minidom import getDOMImplementation
import sys
import os.path
import pprint
from ModelicaXML import getArg

# /* Source Text */
def d_source_text(s, nodes):
    "source_text : cstate dstate knownVariables equations initializations"
    return helper_create_app('source_text', [s[0],s[1],s[2],s[3],s[4]], nodes[0].start_loc)

def d_initializations(s, nodes):
    "initializations: '#####initializations' variablevalue*"
    for i in s[1]:
        i.tagName = 'equation'
        var = getArg(i,1)
        var.tagName = 'initidentifier'
    return helper_create_app('initializations', s[1], nodes[0].start_loc)

def d_cstate(s, nodes):
    "cstate: '#####continuousState' variablename*"
    return helper_create_app('continuousState', s[1], nodes[0].start_loc)

def d_dstate(s, nodes):
    "dstate: '#####discreteState' variablename*"
    return helper_create_app('discreteState', s[1], nodes[0].start_loc)

def d_variablename(s, nodes):
    "variablename: identifier"
    return s[0]

def d_knownVariables(s, nodes):
    "knownVariables: '#####knownVariables' variablevalue*"
    return helper_create_app('knownVariables', s[1], nodes[0].start_loc)

##    "variablevalue: identifier '=' expression ACCESS?"
def d_variablevalue(s, nodes):
    "variablevalue: identifier '=' expression"
    return helper_create_app('variablevalue', [s[0],s[2]], nodes[0].start_loc)

def mkfullname(s):
    fullname = s[0]
    if len(s) == 1:
        pass
    else:
        for i in s[1]:
            fullname += '.'
            fullname += i[1]
    return fullname

def d_identifier(s, nodes):
    "identifier : identifier_access ( '.' identifier_access)*"
    fullname = mkfullname(s)
    node = helper_create_tag_val('identifier', fullname, nodes[0].start_loc)
    if fullname.strip() in ['true','false','True','False']:
        node.tagName = 'string'
    return node

def d_string(s, nodes):
    '''string : '"' "[a-zA-Z_][a-zA-Z_0-9]*" '"' '''
    node = helper_create_tag_val('string', s[1], nodes[0].start_loc)
    return node

def d_pre_or_der(s, nodes):
    "pre_or_der: 'pre' | 'der' "
    return s[0]

def d_pre_der(s, nodes):
    "pre_der: pre_or_der '(' identifier_access ( '.' identifier_access)* ')'"
    fullname = mkfullname(s[2:])
    # node = helper_create_tag_val('sidentifier', s[0]+'('+fullname+')', nodes[0].start_loc)
    node1 = helper_create_tag_val('identifier', fullname, nodes[0].start_loc)
    node = helper_create_app(s[0], [node1], nodes[0].start_loc)
    return node

def d_identifier_access(s, nodes):
    "identifier_access: IDENTIFIER | IDENTIFIER '[' NUMBER ']' "
    # print type(s[0])
    if len(s) == 1:
        return s[0]
    else:
        return s[0]+'['+s[2]+']'

def d_IDENTIFIER(t, s, nodes):
    'IDENTIFIER :\
        "\\\\[^ ]+ " |\
        "[a-zA-Z_$][a-zA-Z_0-9]*" '
    return s[0]

def d_ACCESS(s, nodes):
    "ACCESS: '[' NUMBER ']'"
    # print 'access = {0}'.format(s[0]+s[1]+s[2])
    # return s[0] + s[1] + s[2]
    return helper_create_tag_val('access', s[1], nodes[0].start_loc)

def d_NUMBER(t, s, nodes):
    'NUMBER : "[0-9]+[,0-9]*"'
    # print 'number = {0}'.format(s[0])
    return s[0]
    #return helper_create_tag_val('NUMBER', s[0], nodes[0].start_loc)

def d_number(s, nodes):
    "number : DECIMAL_NUMBER | REAL_NUMBER"
    return helper_create_tag_val('number', s[0], nodes[0].start_loc)

def d_DECIMAL_NUMBER(t, s, nodes):
    'DECIMAL_NUMBER : "[\+\-]?[0-9_]+"'
    return s[0]

def d_REAL_NUMBER(t, s, nodes):
    'REAL_NUMBER :	"[\+\-]?[0-9_]+\.[0-9_]+" |\
         		"[\+\-]?[0-9_]+(\.[0-9_]+)?[Ee][\+\-][0-9_]+"'
    return s[0]


# Expressions
def d_prefix_expression(s, nodes):
    "prefix_expression :\
        identifier |\
        PREFIX_BINARY_OPERATOR '(' expression ',' expression ')' |\
        SPECIAL_BINARY_OPERATOR '(' expression ',' expression ')' ACCESS? |\
        TERNARY_OPERATOR '(' expression ',' expression ',' expression ')' |\
        QUAD_OPERATOR '(' expression ',' expression ',' expression ',' expression ')' "
    if len(s) == 1:
        return s[0]
    elif len(s) == 6 and s[1] == '(':
        return helper_create_app('BAPP', [ s[0], s[2], s[4] ], nodes[0].start_loc )
    elif len(s) == 7:	# 'cross' ( expr , expr ) Access? 
        node = helper_create_app('BAPP', [ s[0], s[2], s[4] ])
        if len(s[6]) == 0:
            return node
        else:
            return helper_create_app('setaccess', [ node, s[6][0] ])
    elif len(s) == 8:
        return helper_create_app('TAPP', [s[0], s[2], s[4], s[6]], nodes[0].start_loc )
    elif len(s) == 10:	# ASHISH: CHECK....
        return helper_create_app('QAPP', [ s[0], s[2], s[4], s[6], s[8] ], nodes[0].start_loc )
    else:
        print 'ERROR: prefix_expression missing code {0} {1}'.format(len(s),s)
        sys.exit()

def d_expression(s, nodes):
    "expression :\
        number | identifier | string |\
        pre_der  |\
        prefix_expression |\
        UNARY_OPERATOR prefix_expression |\
        'noEvent' expression |\
        '(' expression ')' |\
        'initial' '(' ')' |\
        expression BINARY_OPERATOR expression |\
        UNARY_OPERATOR '(' expression ')' |\
        '{' expression ( ',' expression)* '}' ACCESS? |\
        'if' expression 'then' expression 'else' expression"
    if len(s) == 1:
        return s[0]
    elif len(s) == 2 and s[0] == 'noEvent':
        return s[1]
    elif len(s) == 2:
        return helper_create_app('UAPP', [ s[0], s[1] ], nodes[0].start_loc )
    elif len(s) == 3 and s[0] == '(':
        return s[1]
    elif len(s) == 3 and s[0] == 'initial':
        return helper_create_app('INITIAL', [ ], nodes[0].start_loc )
    elif len(s) == 3:
        return helper_create_app('BAPP', [ s[1], s[0], s[2] ], nodes[0].start_loc )
    elif len(s) == 4: 	# unary_operator
        return helper_create_app('UAPP', [ s[0], s[2] ], nodes[0].start_loc )
    elif len(s) == 5 and s[0] == '{': 	# { expr (, expr)* } ACCESS
        n = 1
        children = [  s[1] ]
        for i in s[2]:
            children.append( i[1] )
            n += 1
        node = helper_create_app('set', children, nodes[0].start_loc)
        node.setAttribute('cardinality', str(n))
        if len(s[4]) == 0:
            return node
        else:
            return helper_create_app('setaccess', [node, s[4][0]])
    elif len(s) == 6 and s[0] == 'if':
        return helper_create_app('IF', [ s[1], s[3], s[5] ], nodes[0].start_loc )
    else:
        print 'ERROR: expression missing code'
        sys.exit()

def d_UNARY_OPERATOR(t, s, nodes):
    "UNARY_OPERATOR : '-' | 'sqrt' | 'abs' | 'cos' | 'sin' | 'Real' | 'not' "
    # print s[0]
    return helper_create_tag_val('UNARY_OPERATOR', s[0], nodes[0].start_loc)

def d_BINARY_OPERATOR(t, s, nodes):
    "BINARY_OPERATOR : '*' $binary_op_left 5 |\
        '/' $binary_op_left 6 |\
        '+' $binary_op_left 4 |\
        '-' $binary_op_left 4 |\
        '^' $binary_op_left 7 |\
        '>' $binary_op_left 3 |\
        '>=' $binary_op_left 3 |\
        '&gt;' $binary_op_left 3 |\
        '<' $binary_op_left 3 |\
        '<=' $binary_op_left 3 |\
        '&lt;' $binary_op_left 3 |\
        '==' $binary_op_left 3 |\
        'and' $binary_op_left 2 |\
        'or' $binary_op_left 1"
    return helper_create_tag_val('BINARY_OPERATOR', s[0], nodes[0].start_loc)

def d_PREFIX_BINARY_OPERATOR(t, s, nodes):
    "PREFIX_BINARY_OPERATOR : 'max' | 'min' | 'cross' | 'atan2' "
    return helper_create_tag_val('PREFIX_BINARY_OPERATOR', s[0], nodes[0].start_loc)

def d_SPECIAL_BINARY_OPERATOR(t, s, nodes):
    "SPECIAL_BINARY_OPERATOR : 'Modelica.Mechanics.MultiBody.Frames.TransformationMatrices.from_nxy' | 'cross' "
    return helper_create_tag_val('SPECIAL_BINARY_OPERATOR', s[0], nodes[0].start_loc)

def d_TERNARY_OPERATOR(t, s, nodes):
    "TERNARY_OPERATOR : 'Modelica.Math.tempInterpol1' | 'Modelica.Blocks.Tables.CombiTable1D.tableIpo' "
    return helper_create_tag_val('TERNARY_OPERATOR', s[0], nodes[0].start_loc)

def d_QUAD_OPERATOR(t, s, nodes):
    "QUAD_OPERATOR : 'Modelica.Mechanics.MultiBody.Visualizers.Advanced.Shape.PackMaterial' | 'Modelica.Blocks.Tables.CombiTable1D.tableInit' "
    return helper_create_tag_val('QUAD_OPERATOR', s[0], nodes[0].start_loc)

def d_equations(s, nodes):
    "equations : '#####equations' equation*"
    return helper_create_app('equations', s[1], nodes[0].start_loc)

##    "equation: expression '=' expression ACCESS?"
def d_equation(s, nodes):
    "equation: expression '=' expression"
    # print 'equation for {0} processed'.format(s[0].toprettyxml())
    return helper_create_app('equation', [s[0], s[2]], nodes[0].start_loc)

def helper_create_app(tag, childs, position = None):
    global dom
    node = dom.createElement(tag)
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    for i in childs:
        if i == None:
            print 'ERROR: Null node found, tag = %s', tag
            for j in childs:
                if j != None:
                    print j.toprettyxml() 
        else:
            node.appendChild(i)
    return node 

def helper_create_tag_val(tag, val, position = None):
    global dom
    node = dom.createElement(tag)
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    node.appendChild( dom.createTextNode( val ) )
    return node 

def helper_collect_child(node, base=0):
    ans = list()
    for i in node:
        ans.append(i[base])
    return ans

def moveIfExists(filename):
    import shutil
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def create_output_file(filename, z):
    basename,ext = os.path.splitext(filename)
    if ext != '.dae':
        print 'ERROR: Unknown file extension; expecting .dae ... Quitting'
        return 1
    xmlfilename = basename + ".daexml"
    moveIfExists(xmlfilename)
    with open(xmlfilename, "w") as fp:
        print >> fp, z.toprettyxml()
    print "Created file %s containing XML representation" % xmlfilename

def printUsage():
    print """
NAME: dae2daexml - converter from DAE to XML
SYNOPSIS: bin/dae2daexml <filename.dae>
DESCRIPTION: ...
 Output is written to a file named <filename.daexml>
EXAMPLE: ...
CAVEATS:
"""
    sys.exit()

def parse_expr(x):
    global dom
    impl = getDOMImplementation()
    dom = impl.createDocument(None, "daexml", None)
    y = Parser().parse(x,start_symbol='expression')    # y is now a dparser.ParsedStructure instance
    z = y.getStructure()
    return z
    #print z.toprettyxml()

def dae2daexml(filename):
    global dom
    impl = getDOMImplementation()
    dom = impl.createDocument(None, "daexml", None)
    with open(filename, 'r') as f:
        x = f.read()
        # x = x.replace('$','S')	# $dummy variables -> Sdummy variables
    try:
        y = Parser().parse(x)    # y is now a dparser.ParsedStructure instance
    # except Exception, e:
    except SyntaxError, e:
        print e
        # print sys.exc_info()[0]
        print 'DAE Parse Error: Unable to handle this model currently'
        sys.exit(-1)
    except Exception, e:
        print e
        print 'DAE Parser Unknown Error: Unable to handle this model currently'
        sys.exit(-1)
    z = y.getStructure()
    create_output_file(filename, z)
    return (dom,z)

def main():
    args = sys.argv[1:]
    if len(args) < 1 or len(args) > 1 or args[0][0] == '-':
        printUsage()
        # print 'Need filename'
        return 1
    filename = args[0]
    if not(os.path.isfile(filename)):
        print "File does not exist. Quitting."
        return 1
    (dom,z) = dae2daexml(filename)
    return (dom,z)

if __name__ == '__main__':
    main()
