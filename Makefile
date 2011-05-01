ANTLRPATH=/homes/tiwari/softwares/antlr-2.7.1/
JAVAC=/homes/tiwari/softwares/jikes-1.22/src/jikes
RTJARPATH=/csl/java/current_version/jre/lib/rt.jar

# Do not modify below.
JAVAFLAGS =
JAVACLASSPATH = .:./hybridsal2xml/:${ANTLRPATH}:${ANTLRPATH}/antlr.jar:${RTJARPATH}::

.SUFFIXES:
.SUFFIXES: .java .class
.java.class : ; (export CLASSPATH=${JAVACLASSPATH}; $(JAVAC) $(JAVAFLAGS) $<)

examplexml=examples/hsal-xml/
examplesal=examples/hsal/
example1=Linear1
example2=Linear2
example3=Linear3
example4=SimpleThermo4
example5=SimpleThermo5

all: src/HSalRelAbsCons.py
	python src/HSalRelAbsCons.py ${examplexml}/${example1}.xml
	python src/HSalExtractRelAbs.py ${examplexml}/${example1}.hxml > ${examplexml}/${example1}.absxml
	python src/HSalXMLPP.py ${examplexml}/${example1}.absxml > examples/${example1}.sal

linearalgebra: src/linearAlgebra.py
	python src/linearAlgebra.py

full: src/HSalExtractRelAbs.py src/HSalXMLPP.py
	python src/HSalExtractRelAbs.py ${examplexml}/${example5}.xml > /tmp/5.xml
	python src/HSalXMLPP.py /tmp/5.xml > /tmp/5.sal
	hybridsal2xml/hybridsal2xml /tmp/5.sal > /tmp/5.xml.copy

xml2axml: src/HSalExtractRelAbs.py
	python src/HSalExtractRelAbs.py ${examplexml}/${example5}.xml > /tmp/5.xml
	python src/HSalExtractRelAbs.py ${examplexml}/${example1}.xml > /tmp/1.xml

xml2sal:  src/HSalXMLPP.py
	python src/HSalXMLPP.py ${examplexml}/${example1}.xml > /tmp/${example1}.sal
	python src/HSalXMLPP.py ${examplexml}/${example2}.xml > /tmp/${example2}.sal
	python src/HSalXMLPP.py ${examplexml}/${example3}.xml > /tmp/${example3}.sal
	python src/HSalXMLPP.py ${examplexml}/${example4}.xml > /tmp/${example4}.sal
	python src/HSalXMLPP.py ${examplexml}/${example5}.xml > /tmp/${example5}.sal

sal2xml: hybridsal2xml/hybridsal2xml examples/hsal/Linear1.sal hybridsal2xml/HybridSal2Xml.class 
	hybridsal2xml/hybridsal2xml ${examplesal}/${example1}.sal > ${examplexml}/${example1}.xml
	hybridsal2xml/hybridsal2xml ${examplesal}/${example2}.sal > ${examplexml}/${example2}.xml
	hybridsal2xml/hybridsal2xml ${examplesal}/${example3}.sal > ${examplexml}/${example3}.xml
	hybridsal2xml/hybridsal2xml ${examplesal}/${example4}.sal > ${examplexml}/${example4}.xml
	hybridsal2xml/hybridsal2xml ${examplesal}/${example5}.sal > ${examplexml}/${example5}.xml
	if [ -s ${examplexml}/${example1}.xml ] ; then echo "hybridsal2xml installation successfully tested" ; fi
