
import sys
import os
import os.path
import subprocess

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath,os.X_OK)
    fpath,fname = os.path.split(program)
    if fpath:
        if is_exe(program):    # check in current working directory
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def checkProg(name):
    """Check if name is installed on this machine"""
    #proc = subprocess.Popen(['which', name], stdout=subprocess.PIPE)
    #output = proc.stdout.read()
    #if output == '' or output == '\n':
    output = which(name) or which(name + '.exe')
    if not output:
        #print 'Warning: %s not found...trying...' % name
        return False
    return output

    
def isFile(filename):
    tmp = os.path.normpath(filename)
    return os.path.isfile(tmp)

def findFile(baseList, dirList, fileList):
    """See if you can find rt.jar in any directory in baseList"""
    # On Macs: /System/Library/Frameworks/JavaVM.framework/Versions/1.4.1/Classes/classes.jar
    done = False
    for i in fileList:
        for k in baseList:
            for j in dirList:
                rtjar = os.path.join(k, j, i)
                if isFile(rtjar):
                    done = True
                    break
            if done:
                break
        if done:
            break
    if done:
        rtjar = os.path.normpath(rtjar)
    else:
        rtjar = None
    return rtjar

def sed(f1, f2, assgn):
    fp1 = open(f1, 'r')
    fp2 = open(f2, 'w')
    for line in fp1:
        for (s1,s2) in assgn:
            line = line.replace(s1,s2)
        fp2.write(line)
    fp1.close()
    fp2.close()

def main():
    #
    # Search for java and JAVA_HOME
    #
    # checkProg('sed')
    #checkProg('chmod')

    print "-------------------------------------------------"
    print "Installing HybridSal Relational Abstraction Tool."
    print "     Copyright (c) SRI International 2011.       "
    print "-------------------------------------------------"
    print 'Searching for java...',
    output = checkProg('java')
    if not output:
        print 'Failed. Install java and retry.'
        return 1
    else:
        print 'Successful. Found {0}'.format(output)


    #
    # Check that we're in the right directory
    #
    output = os.getcwd()
    if output == '' or output == '\n':
        print 'Error: pwd failed!'
        return 1
    if output[-1] == '\n':
        pwd = output[0:-1]
    else:
        pwd = output
    #hybridsal2xml = os.path.normpath(pwd + "/hybridsal2xml")
    hybridsal2xml = os.path.normpath(os.path.join(pwd, "hybridsal2xml.jar"))
    if os.path.isfile(hybridsal2xml):
        pass # print 'Everything looks fine until now.'
    else:
        print 'Error: RUN THIS SCRIPT FROM THE HSAL ROOT DIRECTORY'
        print '***The HSAL root directory is the directory created by tar -xz'
        return 1
    # print '-------------------------'

    # set value of shell
    shell = checkProg( 'sh' )
    if not shell and 'SHELL' in os.environ.keys():
        shell = os.environ['SHELL']
    #if not shell:
        #print 'ERROR: Environment variable SHELL not set!'
        #return 1

    #
    # Run a test
    #
    print "Testing hybridsal2xml...",
    ex4 = os.path.join('examples','SimpleThermo4.xml')
    if os.path.isfile(ex4):
        os.remove( ex4 )
    # subprocess.call([ 'rm', '-f', 'examples/SimpleThermo4.xml'])
    ex4sal = os.path.join('examples','SimpleThermo4.sal')
    if not os.path.isfile(ex4sal):
        print 'Failed.'
        print '***ERROR: hybridsal2xml/examples/SimpleThermo4.sal missing'
        print '***Download of hsalRelAbs.tgz was incomplete???'
        print '***Continuing without testing hybridsal2xml...'
    else:
        exe = 'java' 
        retCode = subprocess.call(["java", "-jar", "hybridsal2xml.jar", "-o", ex4, ex4sal])
        if os.path.isfile( ex4 ):
            print 'Successful.'
        else:
            print 'Failed.'
            print '***hybridsal2xml installation failed. See earlier warnings/error messages to determine cause of failure.'
            return 1

    # 
    # python version test
    # 
    if sys.version < '2.6':
        print '****Warning: Preferably use python version 2.6 or higher****'

    # 
    # Test if numpy and scipy are installed
    # 
    print 'Searching for numpy...',
    try:
        import numpy
    except ImportError, e:
        print 'Failed.'
        print '***Warning: python modules numpy and scipy may be required.'
        print '***On Ubuntu: sudo aptitude install python-numpy'
        print '***On Ubuntu: sudo aptitude install python-scipy'
        print '***On Windows: get numpy-1.6.2-win32-superpack-python2.7.exe'
        print '***On Windows: get scipy-0.11.Orc1-superpack-python2.7.exe'
    else:
        print 'Found.'
    print 'Searching for scipy...',
    try:
        import scipy
    except ImportError, e:
        print 'Failed.'
        print '***Warning: python modules numpy and scipy may be required.'
        print '***On Ubuntu: sudo aptitude install python-scipy'
        print '***On Windows: get scipy-0.11.Orc1-superpack-python2.7.exe'
    else:
        print 'Found.'

    #
    # Test dparser and swig for modelica2hxml converter
    #
    # print 'Testing modelica2hybridsal converter...',
    print "-------------------------------------------------"

    print "Searching for sal installation..."
    output = checkProg('sal-inf-bmc')
    iswin = sys.platform.startswith('win')	# is windows
    if not(output) and not(iswin):	# not windows
        print "***Download and install SAL; otherwise you can create SAL abstractions of HybridSal models, but you won't be able to model check them"
        print "***Update PATH with location of sal-inf-bmc"
        return 1
    elif not(iswin):
        print 'sal-inf-bmc found at {0}'.format(output)
    else:  # windows
        print 'Checking for cygwin at c:\cygwin'
        cygwin = os.path.join('C:',os.path.sep,'cygwin')
        if '--cygwin' in sys.argv:
            index = sys.argv.index('--cygwin')
            if index+1 < len(sys.argv):
                cygwin = sys.argv[index+1]
        if not os.path.isdir(cygwin):
            print '***Unable to find cygwin; install and rerun script'
            print '***If installed in non-standard location, rerun script as'
            print '***  python install.py [--rtjar <absolute-path/filename.jar>] [--cygwin <cygwin root directory>]'
            return 1
        print 'cygwin found at {0}'.format(cygwin)
        print 'searching for sal...'
        saldir = None
        if '--sal' in sys.argv:
            index = sys.argv.index('--sal')
            if index+1 < len(sys.argv):
                saldir = sys.argv[index+1]
        if saldir == None or not(os.path.isdir(saldir)):
            for root, dirnames, filenames in os.walk(cygwin):
                for dirname in dirnames:
                    if dirname.startswith('sal-'):
                        saldir = os.path.join(root, dirname)
                        break
                if saldir != None:
                    break
        if saldir != None and os.path.isdir(saldir):
            print 'sal found at {0}'.format(saldir)
        else:
            print '***Unable to find SAL; download from sal.csl.sri.com'
            print '***install and rerun script'
            print '***If installed in non-standard location, rerun script as'
            print '***  python install.py [--rtjar <absolute-path/filename.jar>] [--cygwin <cygwin root directory>] [--sal <sal-root-directory>]'
            return 1
        # now we have saldir and cygwin both set...
        outfile = createSALfile(cygwin, saldir)
        print 'created file {0}'.format(outfile)
    print 'HybridSal Relational Abstracter, Modelica front-end, and sal-inf-bmc successfully installed.'
    print "-------------------------------------------------"
    return 0

def createSALfile(cygwin, saldir):
    binfile = 'sal-inf-bmc.bat'
    fp = open( binfile, 'w')
    cygwinbash = os.path.join(cygwin, 'bin', 'bash')
    salinfbmc = os.path.join(saldir, 'bin', 'sal-inf-bmc')
    print >> fp, "{0} -li {1} %1 %2 %3 %4 %5 %6 %7 %8 %9".format( repr(cygwinbash)[1:-1], repr(salinfbmc)[1:-1])
    fp.close()
    os.chmod( binfile, 0775 )
    return binfile

if __name__ == '__main__':
    main()

