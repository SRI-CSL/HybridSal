# Use python26/python setup.py py2exe to 
# create a windows executable modelica2sal.exe
from distutils.core import setup
import py2exe
import sys
import os.path

sys.path.insert(0, os.path.join('modelica2hsal','src'))
sys.path.insert(0, os.path.join('src'))
sys.path.insert(0, os.path.join('cc2hsal','src'))

#setup(console=['modelica2hsal/src/modelica2sal.py'], packages = ['src','modelica2hsal.src'])
#setup(console=['modelica2hsal/src/modelica2sal.py'], package_dir = {'':'src'})
#setup(console=['modelica2hsal/src/modelica2sal.py'], packages = ['../modelica2hsal/src'], packages_dir = {'':'src'})
#setup(console=['modelica2hsal/src/modelica2sal.py'], py_modules = ['src/HSalRelAbsCons','modelica2hsal/src/modelica2hsal'])
#setup(console=['modelica2hsal/src/modelica2sal.py'])
#setup(console=['modelica2hsal/src/hsalRA.py', 'cc2hsal/src/cc_modelica_hra_verifier.py'])
setup(console=['src/HSalRelAbsCons.py', 'cc2hsal/src/cc_modelica_hra_verifier.py'])
