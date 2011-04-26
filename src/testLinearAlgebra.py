
import linearAlgebra

def test1():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    #print multiplyAv(xx,[0,0,1])
    print "Test of largest eigevalue computation of:"
    print xx
    [lamb, v] = linearAlgebra.eigenvalueLargest(xx) 
    print lamb
    print v
    print "The largest eigenvalue should be 3"
    print "*************************************"

def test2():
    print "Testing equation solving"
    A = [ [1,2,3], [1,3,6], [1,3,2] ]
    b = [ 6, 10, 6 ]
    ans = linearAlgebra.solve(A, b)
    print ans
    print "The solution above should be [[1 1 1]]"
    print "*************************************"

def test3():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    print "Test of ALL eigevalue computation of:"
    print xx
    eigens = linearAlgebra.neigenvalues(xx) 
    print eigens
    print "The above list should be [1,2,3]"
    print "*************************************"

def test4():
    xx = [ [1,2,3], [0,2,6], [0,0,3] ]
    sqrt2 = pow(2,0.5)
    a = sqrt2 / 2
    basis = [ [ a, a, 0], [a, -a, 0], [0, 0, 1] ]
    xx = linearAlgebra.changeOfBasis(xx, basis)
    print "Test of ALL eigevalue computation of:"
    print xx
    eigens = linearAlgebra.neigenvalues(xx) 
    print eigens
    print "The above list should be [1,2,3]"
    print "*************************************"

def test5():
    xx = [ [0,1], [-1,0] ]
    eigens = linearAlgebra.neigenvalues(xx)
    print eigens
    print "The above list should be [1,1]"
    print "*************************************"

def test6():
    xx = [ [0,1], [-1,0] ]
    yy = linearAlgebra.copyA(xx)
    eigens = linearAlgebra.neigenvalues(yy)
    eigenvectors = linearAlgebra.allEigenvectors(xx, eigens)
    linearAlgebra.delA(xx)
    print eigens
    print "The above list should be [1,1]"
    print eigenvectors
    print "The above list should be [1, [[0,0]], -1, [[0,0]]]"
    print "*************************************"

test1()
test2()
test3()
test4()
test5()
test6()
