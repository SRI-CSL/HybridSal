ANTLRPATH=/homes/tiwari/softwares/antlr-2.7.1/
JAVAC=/homes/tiwari/softwares/jikes-1.22/src/jikes
RTJARPATH=/csl/java/current_version/jre/lib/rt.jar

# Do not modify below.
JAVAFLAGS =
JAVACLASSPATH = .:./hybridsal2xml/:${ANTLRPATH}:${ANTLRPATH}/antlr.jar:${RTJARPATH}::

.SUFFIXES:
.SUFFIXES: .java .class
.java.class : ; (export CLASSPATH=${JAVACLASSPATH}; $(JAVAC) $(JAVAFLAGS) $<)

exhsal=examples/

example1=Linear3
example2=Linear2
example3=Linear3
example4=SimpleThermo4

all: src/HSalRelAbsCons.py
	python src/HSalRelAbsCons.py ${exhsal}/${example1}.hsal
	python src/HSalRelAbsCons.py ${exhsal}/${example4}.hsal

linearalgebra: src/linearAlgebra.py
	python src/linearAlgebra.py

xml2axml: src/HSalExtractRelAbs.py
	python src/HSalExtractRelAbs.py ${exhsal}/${example5}.haxml > ${exhsal}/${example5}.xml
	python src/HSalExtractRelAbs.py ${exhsal}/${example1}.haxml > ${exhsal}/${example1}.xml

xml2sal:  src/HSalXMLPP.py
	python src/HSalXMLPP.py ${exhsal}/${example1}.hxml > /tmp/${example1}.hsal
	python src/HSalXMLPP.py ${exhsal}/${example2}.hxml > /tmp/${example2}.hsal
	python src/HSalXMLPP.py ${exhsal}/${example3}.hxml > /tmp/${example3}.hsal
	python src/HSalXMLPP.py ${exhsal}/${example4}.hxml > /tmp/${example4}.hsal
	python src/HSalXMLPP.py ${exhsal}/${example5}.hxml > /tmp/${example5}.hsal

sal2xml: hybridsal2xml/hybridsal2xml examples/hsal/Linear1.hsal hybridsal2xml/HybridSal2Xml.class 
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example1}.hxml ${exhsal}/${example1}.hsal 
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example2}.hxml ${exhsal}/${example2}.hsal
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example3}.hxml ${exhsal}/${example3}.hsal
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example4}.hxml ${exhsal}/${example4}.hsal
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example5}.hxml ${exhsal}/${example5}.hsal
	if [ -s ${exhxml}/${example1}.hxml ] ; then echo "hybridsal2xml installation successfully tested" ; fi
