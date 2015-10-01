import sys
from subprocess import call
from gen import *
from llvm.passes import *


if (__name__ == "__main__"):
    if (len(sys.argv) == 3):
        import sys
        code = open(sys.argv[1])
        codigo = Gen(code)
        f = open(sys.argv[1], 'r')
        
        # passManagerBuida = PassManagerBuilder.new()
        # pmb.opt_level = 3
        # pm = PassManager.new()
        # pmb.populate(pm)
        # pm.run(codigo.module)

        saida = open('build/program.ll', 'w')
        saida.write(str(codigo.module))
        saida.close()
        print("Compilando...")
        call(["llc-3.3", "build/program.ll"])
        call(["gcc", "-c", "mylib.c", "-o", "build/mylib.o"])
        call(["gcc", "build/program.s", "build/mylib.o", "-o", sys.argv[2]])
        # call(["chmod", "u+x", sys.argv[2]])
        print("Pronto.")
    else:
        print("Erro, parametros incorretos.\nUtilização: " + sys.argv[0] + " 'entrada' 'saida'")