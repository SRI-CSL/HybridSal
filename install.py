
import sys
import os
import os.path
import subprocess

def checkProg(name):
    """Check if name is installed on this machine"""
    proc = subprocess.Popen(['which', name], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Error: %s not found, Install it first' % name
        return False
    return True
    
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
        print 'rt.jar found as %s' % rtjar
    else:
        rtjar = None
    return rtjar

def main():
    #
    # Search for java and JAVA_HOME
    #
    checkProg('sed')
    checkProg('chmod')

    print '\nSearching for java'
    proc = subprocess.Popen(['which', 'java'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Error: Java not found, Install java first'
        return 1

    # Set rtjar 
    rtjar = 'rt.jar'
    if '--rtjar' in sys.argv:
        index = sys.argv.index('--rtjar')
        if index+1 < len(sys.argv):
            rtjar = sys.argv[index+1]
    if not(isFile(rtjar)):
        javapath = os.path.realpath(output[0:-1])
        (javabase, javafile) = os.path.split(javapath)
        baseList = [javabase]
        path = os.path.join(os.path.sep, 'System', 'Library', 'Frameworks', 'JavaVM', 'framework', 'Versions', 'CurrentJDK', 'Classes')
        #baseList.append('/System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Classes')
        baseList.append(path)
        if os.environ.has_key('JAVA_HOME'):
            baseList.append( os.environ['JAVA_HOME'] )
        if os.environ.has_key('JDK_HOME'):
            baseList.append( os.environ['JDK_HOME'] )
        p1 = os.path.join('..','lib')
        p2 = os.path.join('..','Classes')
        rtjar = findFile(baseList, [p1, p2], ['rt.jar', 'classes.jar'])
        if rtjar == None:
            print 'Warning: Failed to find rt.jar in all possible places'
            print 'Continuing without giving explicit rt.jar path; if this does not work, then...Make sure the system has rt.jar (on Mac, it is sometimes called classes.jar and is located at /System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Classes/classes.jar) and then ...'
            print 'Rerun install script as: python install.py --rtjar <absolute-path/filename.jar>'
            rtjar = '.'
    rtjar = os.path.abspath(rtjar)

    #
    # Search for jikes? 
    # NOTE: BD I don't have jikes but it still compile fine??
    #
    print '\nSearching for jikes'
    proc = subprocess.Popen(['which', 'jikes'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Warning: jikes not found; Trying to find javac ...'
        jikespath = ''
    else:
        jikespath = os.path.realpath(output[0:-1])
    if jikespath == '':
        proc = subprocess.Popen(['which', 'javac'], stdout=subprocess.PIPE)
        output = proc.stdout.read()
        if output == '' or output == '\n':
            print 'Warning: jikes not found; You can not COMPILE hybridsal2xml'
            print ' But you may be able to use the class files already present'
            print ' The class files were built on 64-bit Ubuntu'
            print 'Optionally, you can try to install jikes/javac and rerun this script'
        else:
            jikespath = os.path.realpath(output[0:-1])

    #
    # Check that we're in the right directory
    #
    proc = subprocess.Popen(['pwd'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Error: pwd failed!'
        return 1
    if output[-1] == '\n':
        pwd = output[0:-1]
    else:
        pwd = output
    #hybridsal2xml = os.path.normpath(pwd + "/hybridsal2xml")
    hybridsal2xml = os.path.normpath(os.path.join(pwd, "hybridsal2xml"))
    if os.path.isdir(os.path.join(pwd,'src')) and os.path.isdir(hybridsal2xml):
        print 'Everything looks fine until now.'
    else:
        print 'Error: RUN THIS SCRIPT FROM THE HSAL ROOT DIRECTORY'
        print ' The HSAL root directory is the directory created by tar -xz'
        return 1
    print '-------------------------'

    #
    # Run the install.sh script in hybridsal2xml
    #
    print 'Installing hybridsal2xml'
    os.chdir(hybridsal2xml)
    # run ./install.sh antlrpath rtjar jikespath
    antlrpath = hybridsal2xml + '/antlr-2.7.1/'
    if os.path.isdir(antlrpath):
        print 'antlr-2.7.1/ found as %s' % antlrpath
    else:
        print 'Error: Failed to find antlr-2.7.1/'
        return 1
    subprocess.call([ './install.sh', antlrpath, rtjar, jikespath ])

    #
    # Run a test
    #
    os.remove(os.path.join('examples','SimpleThermo4.xml'))
    # subprocess.call([ 'rm', '-f', 'examples/SimpleThermo4.xml'])
    exe = os.path.join('.','hybridsal2xml')
    subprocess.call([ exe, '-o', os.path.join('examples','SimpleThermo4.xml'), os.path.join('examples','SimpleThermo4.sal') ])
    if os.path.isfile(os.path.join('examples','SimpleThermo4.xml')):
        print 'hybridsal2xml successfully installed'
    else:
        print 'Error: hybridsal2xml test failed'
        return 1

    #
    # create bin/ files
    #
    bindir = os.path.join(pwd, "bin")
    if not(os.path.isdir(bindir)):
        print 'Error: Directory %s does not exist; create it and rerun install.' % bindir
        return 1
    #os.chdir(pwd + "/bin")
    if 'SHELL' in os.environ.keys():
        shell = os.environ['SHELL']
    else:
        print 'ERROR: Environment variable SHELL not set!'
        return 1
    createBinFile(shell, pwd, bindir, 'hxml2hsal', os.path.join('src','HSalXMLPP.py'))
    createBinFile(shell, pwd, bindir, 'hsal2hasal', os.path.join('src','HSalRelAbsCons.py'))
    createBinFile(shell, pwd, bindir, 'hasal2sal', os.path.join('src','HSalExtractRelAbs.py'))
    createBinFile(shell, pwd, bindir, 'hsal2Tsal', os.path.join('src','HSalTimedRelAbsCons.py'))
    createBinFile(shell, pwd, bindir, 'modelica2hsal', os.path.join('modelica2hsal', 'src','modelica2hsal.py'))
    createBinFile(shell, pwd, bindir, 'modelica2sal', os.path.join('modelica2hsal', 'src','modelica2sal.py'))
    filename = os.path.join(pwd, 'bin', 'hsal2hxml')
    if os.path.isfile(filename):
        os.remove(filename)
    subprocess.call(['ln', '-s', os.path.join('..','hybridsal2xml','hybridsal2xml'), os.path.join(pwd, 'bin', 'hsal2hxml')])
    return 0

def createBinFile(shell, pwd, bindir, filename, pythonfile):
    binfile = os.path.join(bindir, filename)
    fp = open( binfile, 'w')
    print >> fp, '#!', shell
    print >> fp, 'python ', os.path.join(pwd, pythonfile), '$*' 
    fp.close()
    subprocess.call(['chmod', '+x', binfile])

if __name__ == '__main__':
    main()

