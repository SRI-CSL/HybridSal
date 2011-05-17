
import sys
import os.path
import subprocess

def main():
    proc = subprocess.Popen(['which', 'java'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Error: Java not found, Install java first'
        return 1
    javapath = os.path.realpath(output[0:-1])
    (javabase, javafile) = os.path.split(javapath)
    if os.path.isdir(javabase):
        print 'Java found in %s' % javabase
    else:
        print 'Error: Failed to find JAVA_HOME'
        return 1
    javahome = os.path.normpath(javabase + "/..")
    if os.path.isdir(javahome):
        print 'JAVA_HOME found in %s' % javahome
    rtjar = os.path.normpath(javahome + "/lib/rt.jar")
    if os.path.isfile(rtjar):
        print 'rt.jar found as %s' % rtjar
    else:
        print 'Error: Failed to find rt.jar in JAVA_HOME/lib/rt.jar'
        return 1

    proc = subprocess.Popen(['which', 'jikes'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Warning: jikes not found; You can not COMPILE hybridsal2xml'
        print ' But you may be able to use the class files already present'
        print ' The class files were built on 64-bit Ubuntu'
        print 'Optionally, you can try to install jikes and rerun this script'
        jikespath = ''
    else:
        jikespath = os.path.realpath(output[0:-1])
    
    proc = subprocess.Popen(['pwd'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    if output == '' or output == '\n':
        print 'Error: pwd failed!'
        return 1
    if output[-1] == '\n':
        pwd = output[0:-1]
    else:
        pwd = output
    hybridsal2xml = os.path.normpath(pwd + "/hybridsal2xml")
    if os.path.isdir(pwd+'/src') and os.path.isdir(hybridsal2xml):
        print 'Everything looks fine until now.'
    else:
        print 'Error: RUN THIS SCRIPT FROM THE HSAL ROOT DIRECTORY'
        print ' The HSAL root directory is the directory created by tar -xz'
        return 1
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
    subprocess.call([ 'rm', '-f', 'examples/SimpleThermo4.xml'])
    subprocess.call([ 'hybridsal2xml', '-o', 'examples/SimpleThermo4.xml', 'examples/SimpleThermo4.sal' ])
    if os.path.isfile('examples/SimpleThermo3.xml'):
        print 'hybridsal2xml successfully installed'
    else:
        print 'Error: hybridsal2xml test failed'
        return 1
    # create bin/ files
    bindir = pwd + "/bin"
    if not(os.path.isdir(bindir)):
        print 'Error: Directory %s does not exist' % bindir
        return 1
    #os.chdir(pwd + "/bin")
    fp = open(bindir + "/hxml2hsal", 'w')
    if 'SHELL' in os.environ.keys():
        shell = os.environ['SHELL']
    else:
        print 'ERROR: Environment variable SHELL not set!'
        return 1
    print >> fp, '#!', shell
    print >> fp, 'python ', pwd + '/src/HSalXMLPP.py $1'
    fp.close()
    fp = open(bindir + "/hsal2hasal", 'w')
    print >> fp, '#!', shell
    print >> fp, 'python ', pwd + '/src/HSalRelAbsCons.py $1'
    fp.close()
    fp = open(bindir + "/hasal2sal", 'w')
    print >> fp, '#!', shell
    print >> fp, 'python ', pwd + '/src/HSalExtractRelAbs.py $1'
    fp.close()
    subprocess.call(['chmod', '+x', pwd+'/bin/hasal2sal'])
    subprocess.call(['chmod', '+x', pwd+'/bin/hsal2hasal'])
    subprocess.call(['chmod', '+x', pwd+'/bin/hxml2hsal'])
    return 0

if __name__ == '__main__':
    main()

