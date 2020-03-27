vpath %.hsal    examples
vpath %.hxml    examples
vpath %.sal     examples
vpath %mcmt     examples
vpath %logsal   examples
vpath %logsally examples

exhsal=examples/

example1=Linear1
example2=Linear2
example3=Linear3
example4=SimpleThermo4
example5=Linear4
example6=nav
example7=RLC
example8=nav01

# EXPLS=Linear1.hsal Linear2.hsal Linear3.hsal Linear4.hsal SimpleThermo4.hsal nav.hsal nav01.hsal RLC.hsal nav01b.hsal
EXPLS:=$(wildcard examples/*.hsal)
HXMLS=$(EXPLS:.hsal=.hxml)
SALS=$(EXPLS:.hsal=.sal)
SALLYS=$(EXPLS:.hsal=.mcmt)
VERIFSAL=$(EXPLS:.hsal=.logsal)
VERIFSALLY=$(EXPLS:.hsal=.logsally)

.PHONY : all release install test 

all: $(SALS) $(SALLYS) src/HSalRelAbsCons.py

release: install.py
	python install.py dist

install: install.py
	python install.py

test: $(VERIFSALLY)

%.sal: %.hxml
	bin/hsal2hasal $<

%.sal: %.hsal
	bin/hsal2hasal $<

%.mcmt: %.hxml
	bin/hsal2hasally $<

%.mcmt: %.hsal
	bin/hsal2hasally $<

# No %.logsal rules, as sal-inf-bmc needs the formula name

%.logsally: %.mcmt
	-sally --engine bmc $< > $@ 2>&1

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
	bin/hsal2hasal $<

RCEngine:  modelica2hsal/${exhsal}/RCEngine.xml
	bin/modelica2hsal $<

RCEngineFull:  modelica2hsal/${exhsal}/RCEngine.xml
	bin/modelica2sal $<  modelica2hsal/examples/context-property.xml

PTimed: ${exhsal}/PTimed.hsal
	echo "***************************************************************"
	echo "******** Constructing timed abstraction with T=0.01************"
	bin/hsal2hasal -t 0.01 ${exhsal}/PTimed.hsal
	echo "*********** Verifying timed abstraction with T=0.01************"
	cd ${exhsal}; sal-inf-bmc -i -d 4 PTimed stable
	echo "******** Constructing timed abstraction with T=0.1*************"
	bin/hsal2hasal -t 0.1 ${exhsal}/PTimed.hsal
	echo "*********** Verifying timed abstraction with T=0.1*************"
	cd ${exhsal}; sal-inf-bmc -i -d 4 PTimed stable

InvPenTimed: ${exhsal}/InvPenTimed.hsal
	echo "************* Constructing untimed abstraction ****************"
	bin/hsal2hasal ${exhsal}/InvPenTimed.hsal
	echo "*********** Verifying untimed abstraction *********************"
	cd ${exhsal}; sal-inf-bmc -i -d 2 InvPenTimed stableCont; sal-inf-bmc -i -d 4 InvPenTimed stableCont
	echo "******** Constructing timed abstraction with T=0.01************"
	bin/hsal2hasal -t 0.01 ${exhsal}/InvPenTimed.hsal
	echo "*********** Verifying timed abstraction with T=0.01************"
	cd ${exhsal}; sal-inf-bmc -i -d 14 InvPenTimed stableTimed; sal-inf-bmc -d 18 InvPenTimed stable

PITimed: ${exhsal}/PITimed.sal
	echo "*********** Verifying timed abstraction for T=0.01s************"
	cd ${exhsal}; sed -e "s|__N__|0|g" PITimed.sal.proved > PITimed.sal; sal-inf-bmc -i -d 22 PITimed stable
	echo "*********** Verifying timed abstraction for T=0.1s************"
	cd ${exhsal}; sed -e "s|__N__|1|g" PITimed.sal.proved > PITimed.sal; sal-inf-bmc -i -d 10 PITimed stable
	echo "*********** Verifying timed abstraction for T=0.5s************"
	cd ${exhsal}; sed -e "s|__N__|2|g" PITimed.sal.proved > PITimed.sal; sal-inf-bmc -i -d 5 PITimed stable

clean: 
	rm -f ${HXMLS} $(EXPLS:.hsal=.hasal) $(EXPLS:.hsal=.haxml) $(EXPLS:.hsal=.xml)

cleanall:
	rm -f ${HXMLS} $(EXPLS:.hsal=.hasal) $(EXPLS:.hsal=.haxml) $(EXPLS:.hsal=.xml) $(EXPLS:.hsal=.sal)

print-%:
	@echo '$*=$($*)'
