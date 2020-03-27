
#python src/HSalRelAbsCons.py -ta time,10,10,2 examples/cav15_real_jordan2.hsal
#cd examples; sal-inf-bmc -d 1 cav15_real_jordan2 correct; cd ..

python src/HSalRelAbsCons.py -ta time,10,10,2 examples/cav15_real_jordan3.hsal
cd examples; sal-inf-bmc -d 1 cav15_real_jordan3 correct; cd ..

#python src/HSalRelAbsCons.py -ta time,10,10,2 examples/cav15_real_jordan4.hsal
#cd examples; sal-inf-bmc -d 1 cav15_real_jordan4 correct; cd ..

# python src/HSalRelAbsCons.py -ta time,5,5,3 examples/cav15_complex_jordan4.hsal
# cd examples; sal-inf-bmc -d 1 cav15_complex_jordan4 correct; cd ..
