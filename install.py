
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

    # Set rtjar 
    print 'Searching for rt.jar...',
    rtjar = 'rt.jar'
    if '--rtjar' in sys.argv:
        index = sys.argv.index('--rtjar')
        if index+1 < len(sys.argv):
            rtjar = sys.argv[index+1]
    if not(isFile(rtjar)):
        javapath = os.path.realpath(output)
        (javabase, javafile) = os.path.split(javapath)
        baseList = [javabase]
        forMacs = os.path.join(os.path.sep, 'System', 'Library', 'Frameworks', 'JavaVM', 'framework', 'Versions', 'CurrentJDK', 'Classes')
        #baseList.append('/System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Classes')
        baseList.append(forMacs)
        forWindows = os.path.join('C:',os.path.sep,'Program Files','Java','jre6','lib')
        baseList.append(forWindows)
        if os.environ.has_key('JAVA_HOME'):
            baseList.append( os.environ['JAVA_HOME'] )
        if os.environ.has_key('JDK_HOME'):
            baseList.append( os.environ['JDK_HOME'] )
        p1 = os.path.join('..','lib')
        p2 = os.path.join('..','Classes')
        rtjar = findFile(baseList, [p1, p2], ['rt.jar', 'classes.jar'])
    if rtjar == None:
        print 'Failed.'
        print '***Warning: Failed to find rt.jar in all possible places'
        print '***Continuing without giving explicit rt.jar path; if this does not work, then...Make sure the system has rt.jar'
        print '***Mac: it is sometimes called classes.jar and is located at /System/Library/Frameworks/JavaVM.framework/Versions/CurrentJDK/Classes/classes.jar)'
        print '***Win: often located at C:\Program Files\Java\jre6\lib....Once you have rt.jar...'
        print '***Rerun install script as: python install.py --rtjar <absolute-path/filename.jar>'
        rtjar = '.'
    else:
        print 'Successful. Found {0}'.format(rtjar)
    rtjar = os.path.abspath(rtjar)
    if rtjar.find('java-6-openjdk') >= 0:
        print '****Warning: rt.jar in java-6-openjdk is buggy; use java-6-sun/jre instead****'
        print '****Rerun install script as: python install.py --rtjar <absolute-path/filename.jar>'

    #
    # Search for jikes? 
    # NOTE: BD I don't have jikes but it still compile fine??
    #
    print 'Searching for jikes or javac...',
    jikespath = ''
    output = checkProg('jikes')
    if not output:
        # print 'Warning: jikes not found; Trying to find javac ...'
        jikespath = ''
    else:
        jikespath = os.path.realpath(output)
    if jikespath == '':
        output = checkProg('javac')
        if not output:
            pass
        else:
            jikespath = os.path.realpath(output)
    if jikespath == '':
        print 'Failed.'
        print '***Warning: jikes/javac not found; You can not COMPILE hybridsal2xml'
        print '*** But you may be able to use the class files already present'
        print '*** The class files were built on {0} {1}'.format(sys.platform,sys.version)
        print '***Optionally, you can try to install jikes/javac and rerun this script'
        #sourceforge.net/projects/jikes/files/Jikes/1.22/jikes-1.22-1.windows.zip
        jikespath = 'javac'
    else:
        print 'Successful. Found {0}'.format(jikespath)

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
    hybridsal2xml = os.path.normpath(os.path.join(pwd, "hybridsal2xml"))
    if os.path.isdir(os.path.join(pwd,'src')) and os.path.isdir(hybridsal2xml):
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
    # Run the install.sh script in hybridsal2xml
    #
    os.chdir(hybridsal2xml)
    # run ./install.sh antlrpath rtjar jikespath
    print 'Searching for antlr...',
    antlrpath = os.path.join(hybridsal2xml, 'antlr-2.7.1')
    if os.path.isdir(antlrpath):
        print 'Successful. Found {0}'.format(antlrpath)
    else:
        print 'Failed. Failed to find antlr-2.7.1/'
        return 1
    # subprocess.call(['sh', 'install.sh', antlrpath, rtjar, jikespath ])
    print "Installing hybridsal2xml at {0}".format(os.getcwd())
    scriptArgs = ''
    topshell = ''
    if sys.platform.startswith('win'):	# windows
        classpathsep = ';'
        scriptArgs = '%1 %2 %3'
        topshell = ''
    else:	# linux or mac
        classpathsep = ':'
        scriptArgs = '$*'
        topshell = '#!{0}'.format(shell)
    javaclasspath = classpathsep.join([ '.', antlrpath, os.path.join(antlrpath, 'antlr'), rtjar ])
    if 'CLASSPATH' in os.environ.keys():
        javaclasspath = classpathsep.join([ javaclasspath, os.environ['CLASSPATH']])
    tmp = '"{0}"'.format(javaclasspath)
    assgn = [ ("__ANTLR_PATH__", antlrpath), ("__JIKES_PATH__",repr(jikespath)), ("__RTJAR_PATH__",rtjar), ("__JAVACLASSPATH__",tmp) ]
    sed( 'Makefile.in', 'Makefile', assgn)
    javaclasspath = classpathsep.join([ hybridsal2xml, javaclasspath])
    tmp = '"{0}"'.format(javaclasspath)
    assgn = [ ("__JAVACLASSPATH__", tmp), ("__ARGS__", scriptArgs), ("__SH__",topshell) ]
    # hybridsal2xmltemplate = os.path.join('hybridsal2xml', 'hybridsal2xml.template')
    hybridsal2xmltemplate = 'hybridsal2xml.template'
    # hybridsal2xml = os.path.join('hybridsal2xml','hybridsal2xml')
    hybridsal2xml = 'hybridsal2xml'
    if sys.platform.startswith('win'):
        if os.path.isfile(hybridsal2xml):
            os.remove(hybridsal2xml)
        hybridsal2xml += '.bat'
    #else:
        #hybridsal2xml += '.sh'
    sed( hybridsal2xmltemplate, hybridsal2xml, assgn )
    os.chmod( hybridsal2xml, 0775 )
    print "Created script {0}.".format(hybridsal2xml)
    print 'Searching for make...',
    output = checkProg('make')
    if not output:
        print 'Failed.'
        print '***To build hybridsal2xml, you need to run make in the directory hybridsal2xml/'
        print '***Perhaps the existing built version suffices, so continuing...'
    else:
        print 'Successful. Found {0}'.format(output)
        subprocess.call([ 'make' ])

    if os.path.isfile('HybridSal2Xml.class'):
        print "hybridsal2xml installation complete."
    else:
        print "hybridsal2xml installation failed."
        print "***See error messages above and fix***"
        return 1

    #
    # Run a test
    #
    print "Testing hybridsal2xml...",
    ex4 = os.path.join('examples','SimpleThermo4.xml')
    if os.path.isfile(ex4):
        os.remove( ex4 )
    # subprocess.call([ 'rm', '-f', 'examples/SimpleThermo4.xml'])
    exe = os.path.join('.', hybridsal2xml)
    ex4sal = os.path.join('examples','SimpleThermo4.sal')
    if not os.path.isfile(ex4sal):
        print 'Failed.'
        print '***ERROR: hybridsal2xml/examples/SimpleThermo4.sal missing'
        print '***Download of hsalRelAbs.tgz was incomplete???'
        print '***Continuing without testing hybridsal2xml...'
    else:
        subprocess.call([ exe, '-o', ex4, ex4sal ])
        if os.path.isfile( ex4 ):
            print 'Successful.'
        else:
            print 'Failed.'
            print '***hybridsal2xml installation failed. See earlier warnings/error messages to determine cause of failure.'
            return 1
    os.chdir('..')

    #
    # create bin/ files
    #
    print 'Creating bin/ files...',
    bindir = os.path.join(pwd, "bin")
    if not(os.path.isdir(bindir)):
        os.makedirs(bindir)
        #print 'Error: Directory %s does not exist; create it and rerun install.' % bindir
        #return 1
    #os.chdir(pwd + "/bin")
    try:
        createBinFile(topshell, pwd, bindir, 'hxml2hsal', os.path.join('src','HSalXMLPP.py'))
        createBinFile(topshell, pwd, bindir, 'hsal2hasal', os.path.join('src','HSalRelAbsCons.py'))
        createBinFile(topshell, pwd, bindir, 'hasal2sal', os.path.join('src','HSalExtractRelAbs.py'))
        createBinFile(topshell, pwd, bindir, 'hsal2Tsal', os.path.join('src','HSalTimedRelAbsCons.py'))
        createBinFile(topshell, pwd, bindir, 'modelica2hsal', os.path.join('modelica2hsal', 'src','modelica2hsal.py'))
        createBinFile(topshell, pwd, bindir, 'modelica2sal', os.path.join('modelica2hsal', 'src','modelica2sal.py'))
    #filename = os.path.join(pwd, 'bin', 'hsal2hxml')
    #if os.path.isfile(filename):
        #os.remove(filename)
    #subprocess.call(['ln', '-s', os.path.join('..','hybridsal2xml',hybridsal2xml), os.path.join(pwd, 'bin', 'hsal2hxml')])
    except Exception, e:
        print 'Failed.'
        print '***Unable to create executable scripts. Perhaps permission issues??'
        print e
        return 1
    else:
        print 'Successful.'

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
        print '***Install python modules numpy and scipy first.'
        print '***On Ubuntu: sudo aptitude install python-numpy'
        print '***On Ubuntu: sudo aptitude install python-scipy'
        print '***On Windows: get numpy-1.6.2-win32-superpack-python2.7.exe'
        print '***On Windows: get scipy-0.11.Orc1-superpack-python2.7.exe'
        return 1
    else:
        print 'Found.'
    print 'Searching for scipy...',
    try:
        import scipy
    except ImportError, e:
        print 'Failed.'
        print '***Install python modules numpy and scipy first.'
        print '***On Ubuntu: sudo aptitude install python-scipy'
        print '***On Windows: get scipy-0.11.Orc1-superpack-python2.7.exe'
        return 1
    else:
        print 'Found.'

    # 
    # Test relational abstracter itself
    # 
    print "Testing HybridSal relational abstracter...",
    ex4 = os.path.join('examples','Linear1.sal')
    if os.path.isfile(ex4):
        os.remove( ex4 )
    # subprocess.call([ 'rm', '-f', 'examples/SimpleThermo4.xml'])
    hsal2hasal = 'hsal2hasal'
    if sys.platform.startswith('win'):
        hsal2hasal += '.bat'
    exe = os.path.join('bin',hsal2hasal)
    try:
        subprocess.call([ exe, os.path.join('examples','Linear1.hsal') ])
    except Exception, e:
        print 'Failed.'
        print '***Failed to execute generated script {0} using python subprocess.call'.format(hsal2hasal)
        print '***Check if the script looks ok; and if you can execute it from command line'
        return 1
    else:
        if os.path.isfile( ex4 ):
            print 'Successful.'
        else:
            print 'Failed.'
            print '***Executed the generated script {0}, but it did not generate expected output'.format(hsal2hasal)
            return 1
    
    #
    # Test dparser and swig for modelica2hxml converter
    #
    print 'The HybridSal Relational Abstracter is correctly installed.'
    print 'Now we need to make sure that Modelica2HybridSal converter is working'

    print "Testing dparser...",
    make_dparser = checkProg('make_dparser')
    if not make_dparser:
        print 'Failed.'
        print '***Could not find dparser installed in your system'
        print '***Install dparser AND python support for dparser'
        print '***From dparser.sourceforge.net'
        print '***Continuing with the hope that python support for dparser was installed'
    else:
        print 'Successful.'
    print "Testing python support for dparser...",
    try:
        import dparser
    except ImportError:
        print 'Failed.'
        print '***Install python support for dparser'
        print 'Checking if swig is installed...',
        swig = checkProg('swig')
        if not swig:
            print 'Failed.'
            print '***You need to install swig first: www.swig.org/download.html'
            print '***Swig installation steps: download swigwin-2.0.7.zip file; unzip; ./configure; make; make install'
            print '***Swig uses pcre from www.pcre.org; but it may not be required'
        else:
            print 'Successful. Found {0}'.format(swig)
        print '***Install dparser and its python support from dparser.sourceforge.net'
        print '***modelica2hybridsal converter installation failed'
        print 'My Notes: swig and dparser installation required configure and make utilities'
        print '***I installed mingw on my windows machine; and then installed unix-like utilities, such as,'
        print '***mingw-get install gcc g++ msys-base msys-make mingw32-autotools'
        print '***And then installed pcre; swig; dparser; dparser-python-support;'
        print '***For python support for dparser: In the python subdirectory of dparser: python setup.py build --compile=mingw32'
        print '***I had to edit distutils/cygwinccompiler.py and remove all -mno-cygwin from python'
        return 1
    else:
        print 'Successful.'

    print 'Testing modelica2hybridsal converter...',
    # python  /export/u1/homes/tiwari/sal/sal-devel/ashish-tools/modelica2hsal/src/modelica2hsal.py $*
    ex4 = os.path.join('modelica2hsal', 'examples','RCEngine.xml')
    if not os.path.isfile(ex4):
        print 'Failed.'
        print '***Unable to find modelical RCEngine model file called RCEngine.xml'
    else:
        hsal2hasal = 'modelica2hsal'
        if sys.platform.startswith('win'):
            hsal2hasal += '.bat'
        exe = os.path.join('bin',hsal2hasal)
        try:
            subprocess.call([ exe, ex4 ])
        except Exception, e:
            print 'Failed.'
            print '***Failed to execute generated script {0} using python subprocess.call'.format(hsal2hasal)
            print '***Check if the script looks ok; and if you can execute it from command line with one argument {0}'.format(ex4)
        else:
            print 'Successful.'
    print 'HybridSal Relational Abstracter and Modelica front-end successfully installed.'
    print "-------------------------------------------------"
    return 0

def createBinFile(shell, pwd, bindir, filename, pythonfile):
    binfile = os.path.join(bindir, filename)
    if sys.platform.startswith('win'):
        binfile += '.bat'
    fp = open( binfile, 'w')
    if sys.platform.startswith('win'):
        pyfile = repr(os.path.join(pwd, pythonfile))
        print >> fp, 'python ', pyfile[1:-1], '%1', '%2', '%3', '%4', '%5', '%6', '%7', '%8'
    else:
        print >> fp, shell
        print >> fp, 'python ', os.path.join(pwd, pythonfile), '$*' 
    fp.close()
    # subprocess.call(['chmod', '+x', binfile])
    os.chmod( binfile, 0775 )

if __name__ == '__main__':
    main()

