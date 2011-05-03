ANTLRPATH=/homes/tiwari/softwares/antlr-2.7.1/
JAVAC=/homes/tiwari/softwares/jikes-1.22/src/jikes
RTJARPATH=/csl/java/current_version/jre/lib/rt.jar

# Do not modify below.
JAVAFLAGS =
JAVACLASSPATH = .:./hybridsal2xml/:${ANTLRPATH}:${ANTLRPATH}/antlr.jar:${RTJARPATH}::

.SUFFIXES:
.SUFFIXES: .java .class
.java.class : ; (export CLASSPATH=${JAVACLASSPATH}; $(JAVAC) $(JAVAFLAGS) $<)

exhsal=examples/hsal/
exhxml=examples/hsal-xml/
exhabssal=examples/habssal/
exhabsxml=examples/habssal-xml/
exsal=examples/sal/
exxml=examples/sal-xml/

example1=Linear3
example2=Linear2
example3=Linear3
example4=SimpleThermo4
example5=SimpleThermo5

all: src/HSalRelAbsCons.py
	hybridsal2xml/hybridsal2xml ${exhsal}/${example1}.hsal > ${exhxml}/${example1}.hxml
	python src/HSalRelAbsCons.py ${exhxml}/${example1}.hxml
	mv ${exhxml}/${example1}.haxml ${exhabsxml}/${example1}.haxml
	mv ${exhxml}/${example1}.hasal ${exhabssal}/${example1}.hasal
	python src/HSalExtractRelAbs.py ${exhabsxml}/${example1}.haxml > ${exxml}/${example1}.xml
	python src/HSalXMLPP.py ${exxml}/${example1}.xml > ${exsal}/${example1}.sal

linearalgebra: src/linearAlgebra.py
	python src/linearAlgebra.py

full: src/HSalExtractRelAbs.py src/HSalXMLPP.py
	hybridsal2xml/hybridsal2xml ${exhsal}/${example5}.hsal > ${exhxml}/${example5}.hxml
	cp -p ${exhxml}/${example5}.hxml ${exhabsxml}/${example5}.haxml
	python src/HSalExtractRelAbs.py ${exhabsxml}/${example5}.haxml > ${exxml}/${example5}.xml
	python src/HSalXMLPP.py ${exxml}/${example5}.xml > ${exsal}/${example5}.sal
	hybridsal2xml/hybridsal2xml ${exsal}/${example5}.sal > ${exxml}/${example5}.xml.copy

xml2axml: src/HSalExtractRelAbs.py
	mv ${exhxml}/${example1}.hxml ${exhabsxml}/${example1}.haxml 
	mv ${exhxml}/${example5}.hxml ${exhabsxml}/${example5}.haxml 
	python src/HSalExtractRelAbs.py ${exhabsxml}/${example5}.haxml > ${exxml}/${example5}.xml
	python src/HSalExtractRelAbs.py ${exhabsxml}/${example1}.haxml > ${exxml}/${example1}.xml

xml2sal:  src/HSalXMLPP.py
	python src/HSalXMLPP.py ${exhxml}/${example1}.hxml > /tmp/${example1}.hsal
	python src/HSalXMLPP.py ${exhxml}/${example2}.hxml > /tmp/${example2}.hsal
	python src/HSalXMLPP.py ${exhxml}/${example3}.hxml > /tmp/${example3}.hsal
	python src/HSalXMLPP.py ${exhxml}/${example4}.hxml > /tmp/${example4}.hsal
	python src/HSalXMLPP.py ${exhxml}/${example5}.hxml > /tmp/${example5}.hsal

sal2xml: hybridsal2xml/hybridsal2xml examples/hsal/Linear1.hsal hybridsal2xml/HybridSal2Xml.class 
	hybridsal2xml/hybridsal2xml ${exhsal}/${example1}.hsal > ${exhxml}/${example1}.hxml
	hybridsal2xml/hybridsal2xml ${exhsal}/${example2}.hsal > ${exhxml}/${example2}.hxml
	hybridsal2xml/hybridsal2xml ${exhsal}/${example3}.hsal > ${exhxml}/${example3}.hxml
	hybridsal2xml/hybridsal2xml ${exhsal}/${example4}.hsal > ${exhxml}/${example4}.hxml
	hybridsal2xml/hybridsal2xml ${exhsal}/${example5}.hsal > ${exhxml}/${example5}.hxml
	if [ -s ${exhxml}/${example1}.hxml ] ; then echo "hybridsal2xml installation successfully tested" ; fi
