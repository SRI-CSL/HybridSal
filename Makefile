vpath %.hsal examples
vpath %.hxml examples
vpath %.sal  examples

exhsal=examples/

example1=Linear1
example2=Linear2
example3=Linear3
example4=SimpleThermo4
example5=Linear4
example6=nav
example7=RLC
example8=nav01

EXPLS=Linear1.hsal Linear2.hsal Linear3.hsal Linear4.hsal SimpleThermo4.hsal nav.hsal nav01.hsal RLC.hsal nav01b.hsal
HXMLS=$(EXPLS:.hsal=.hxml)
SALS=$(EXPLS:.hsal=.sal)

all: $(SALS) src/HSalRelAbsCons.py

install: install.py
	python install.py

%.sal: %.hxml
	bin/hsal2hasal $<

%.sal: %.hsal
	bin/hsal2hasal $<

%.hxml: %.hsal hybridsal2xml/hybridsal2xml hybridsal2xml/HybridSal2Xml.class 
	hybridsal2xml/hybridsal2xml -o $@ $<

linearalgebra: src/linearAlgebra.py
	python src/linearAlgebra.py

hasal2sal: src/HSalExtractRelAbs.py
	bin/hasal2sal ${exhsal}/${example1}.haxml > ${exhsal}/${example1}.xml

hxml2hsal:  src/HSalXMLPP.py
	bin/hxml2hsal ${exhsal}/${example1}.hxml > /tmp/${example1}.hsal
	bin/hxml2hsal ${exhsal}/${example2}.hxml > /tmp/${example2}.hsal
	bin/hxml2hsal ${exhsal}/${example3}.hxml > /tmp/${example3}.hsal
	bin/hxml2hsal ${exhsal}/${example4}.hxml > /tmp/${example4}.hsal

sal2xml: $(HXMLS)
	hybridsal2xml/hybridsal2xml -o ${exhsal}/${example1}.hxml ${exhsal}/${example1}.hsal
	if [ -s ${exhsal}/${example1}.hxml ] ; then echo "hybridsal2xml installation successfully tested" ; fi

powertrain:  ${exhsal}/powertrain.hsal
	hybridsal2xml/hybridsal2xml -o ${exhsal}/powertrain.hxml $<
	python src/HSalPreProcess.py ${exhsal}/powertrain.hxml
	bin/hsal2hasal ${exhsal}/powertrain.hxml

clean: 
	rm -f ${HXMLS} $(EXPLS:.hsal=.hasal) $(EXPLS:.hsal=.haxml) $(EXPLS:.hsal=.xml)

cleanall:
	rm -f ${HXMLS} $(EXPLS:.hsal=.hasal) $(EXPLS:.hsal=.haxml) $(EXPLS:.hsal=.xml) $(EXPLS:.hsal=.sal)
