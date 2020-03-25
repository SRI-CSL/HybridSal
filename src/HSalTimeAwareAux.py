
# Mar 10, 2014: Fixed quadInvModTime definition

import math
from xmlHelpers import mystr

def createLogLB( m, n ):
    "m,n are integers; LB for ln on intervals [-infty,e^-m, ...,e^n, infty]"
    ans = "loglb(x:REAL): REAL =\n"
    lbi = math.exp(n)
    eminus1inv = 1/(math.e - 1)
    ans += " IF ({0} <= x) THEN {1}\n".format( mystr(lbi), n )
    for i in range(n, -m, -1):
        ubi = lbi
        lbi = math.exp(i-1)
        coeff = 1/lbi  * eminus1inv
        ans += " ELSIF ({0} <= x AND x < {1}) THEN ".format( mystr(lbi), mystr(ubi) )
        ans += "{0} + {1}*x - 0.58\n".format(i-1, mystr(coeff))
    ans += " ELSE 0 ENDIF;\n\n"
    return ans
 
def createLogUB( m, n):
    ans = "logub(x:REAL): REAL =\n"
    lb = math.exp(-m)
    ub = math.exp(n)
    slopeatlb = 1/math.exp(-m)
    slopeatub = 1/math.exp(n)
    ans += " IF ({0} <= x AND x < {1}) THEN loglb(x) + 0.12\n".format(mystr(lb),mystr(ub))
    ans += " ELSIF x < {0} THEN {1}*x - {2}\n".format(mystr(lb), mystr(slopeatlb), m+1)
    ans += " ELSE {0}*x + {1} ENDIF;\n\n".format(mystr(slopeatub), n-1)
    return ans

def createExpTimeBnd1( m ):
    ans = "expTimeBnd1(x:REAL, y:REAL, z:REAL): BOOLEAN =\n"
    ans+= " (x < {0} OR loglb(x) - logub(y) <= z);\n\n".format(mystr(math.exp(-m)))
    return ans

def createExpTimeBnd2( m ):
    ans = "expTimeBnd2(x:REAL, y:REAL, z:REAL): BOOLEAN =\n"
    # ans+= " (x < {0} OR y < {0} OR z <= logub(x) - loglb(y));\n\n".format(mystr(math.exp(-m)))
    ans+= " (y < {0} OR z <= logub(x) - loglb(y));\n\n".format(mystr(math.exp(-m)))
    return ans

def createEigenInvTime():
    ans = '''
eigenInvTime(xold:REAL,xnew:REAL,lamb:REAL,told:REAL,tnew:REAL):BOOLEAN =
 tnew >= told AND (
 (xold = 0 AND xnew = 0) OR
 (xold > 0 AND xnew >= xold AND
  expTimeBnd1(xnew, xold, (tnew-told)*lamb) AND
  expTimeBnd2(xnew, xold, (tnew-told)*lamb)) OR
 (xold < 0 AND xnew <= xold AND
  expTimeBnd1(-xnew, -xold, (tnew-told)*lamb) AND
  expTimeBnd2(-xnew, -xold, (tnew-told)*lamb)) ) ;
'''
    return ans

def createModLBUBPhaseDiff():
    ans = '''
modlb(x:REAL, y:REAL): REAL =
 IF x >= 0 AND y >= 0 THEN (IF x < y THEN y ELSE x ENDIF)
 ELSIF x >= 0 AND y < 0 THEN (IF x < -y THEN -y ELSE x ENDIF)
 ELSIF x < 0 AND y >= 0 THEN (IF -x < y THEN y ELSE -x ENDIF)
 ELSE (IF -x < -y THEN -y ELSE -x ENDIF) ENDIF;

modub(x:REAL, y:REAL): REAL =
 IF x >= 0 AND y >= 0 THEN x+y
 ELSIF x >= 0 AND y < 0 THEN x-y
 ELSIF x < 0 AND y >= 0 THEN y-x
 ELSE -x-y ENDIF;

phase(x:REAL, y:REAL): REAL =
 IF x >= 0 AND y > 0 THEN 0 ELSIF x > 0 AND y <= 0 THEN 1
 ELSIF x <= 0 AND y < 0 THEN 2 ELSE 3 ENDIF;

phasediff(xold:REAL, yold:REAL, xnew:REAL, ynew:REAL): [# lb:REAL,ub:REAL #] =
 LET phi1:REAL = phase(xold,yold) IN
  LET phi2:REAL = phase(xnew,ynew) IN
   (IF phi2 >= phi1 THEN (# lb:=1.57*(phi2-phi1-1), ub:=1.57*(phi2-phi1+1) #)
    ELSE (# lb:=1.57*(phi2-phi1+4-1), ub:=1.57*(phi2-phi1+4+1) #) ENDIF);
'''
    return ans

def createQuadInvModTime():
    ans = '''

quadInvModTime(xold:REAL, yold:REAL, xnew:REAL, ynew:REAL, lamb:REAL, told: REAL, tnew: REAL): BOOLEAN =
 (xold = 0 AND yold = 0 AND xnew = 0 AND ynew = 0) OR (
   expTimeBnd1(modlb(xnew,ynew), modub(xold,yold), lamb*(tnew-told)) AND
   expTimeBnd2(modub(xnew,ynew), modlb(xold,yold), lamb*(tnew-told)) );
'''
    return ans

def createQuadInvPhaseTime( n ):
    ans = '''
quadInvPhaseTime(xold:REAL, yold:REAL, xnew:REAL, ynew:REAL, omega:REAL, told: REAL, tnew: REAL): BOOLEAN =
 ((xold = 0 AND yold = 0 AND xnew = 0 AND ynew = 0) OR
  LET phi:[# lb:REAL,ub:REAL #] = phasediff(xold,yold,xnew,ynew) IN
   (EXISTS(n:[0..{0}]):
   (omega*(tnew-told) <= 2*3.14*n + phi.ub AND
    omega*(tnew-told) >= 2*3.14*n + phi.lb)) OR
   omega*(tnew-told) >= 2*3.14*({0}+1) + phi.lb);
'''.format(n)
    return ans

def createQuadInvTime():
    ans = '''
quadInvTime(xold:REAL, yold:REAL, xnew:REAL, ynew:REAL, lamb:REAL, omega:REAL, told: REAL, tnew: REAL): BOOLEAN =
 (tnew >= told) AND
 quadInvModTime(xold, yold, xnew, ynew, lamb, told, tnew) AND
 quadInvPhaseTime(xold, yold, xnew, ynew, omega, told, tnew);

'''
    return ans

def createSALAuxFunc( eigenNegN, eigenPosN, phaseN):
    ans = createLogLB( eigenNegN, eigenPosN )
    ans += createLogUB( eigenNegN, eigenPosN )
    ans += createExpTimeBnd1( eigenNegN )
    ans += createExpTimeBnd2( eigenNegN )
    ans += createEigenInvTime()
    ans += createModLBUBPhaseDiff()
    ans += createQuadInvModTime()
    ans += createQuadInvPhaseTime( phaseN )
    ans += createQuadInvTime()
    return ans

if __name__ == '__main__':
    print('Testing the SAL auxiliary function generation for time-aware RA')
    print((createSALAuxFunc( 3, 4, 2)))

