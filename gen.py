from llvm.core import *
from semantica import Semantica
from parser import *
from sys import exit
from llvm.ee import ExecutionEngine
from llvm.passes import (FunctionPassManager, PASS_INSTCOMBINE, PASS_GVN,
    PASS_REASSOCIATE, PASS_SIMPLIFYCFG, PASS_MEM2REG)

class Gen:

    def __init__(self, code, optz=True, debug=True):
        # parse = Semantica(code.read())
        s = Semantica(code.read())
        s.inicio()
        self.tree = s.tree
        self.module = Module.new('program')
        self.symbols = s.table
        self.scope = "global"
        self.builder = None
        self.func = None
        self.debug = debug  
        self.printf_f = Function.new(self.module, Type.function(Type.float(), [Type.float()]), "printf_f")
        self.scanf_f = Function.new(self.module, Type.function(Type.float(), []), "scanf_f")


        ###OTIMIZAÇÕES###
        self.optz = optz
        self.passes = FunctionPassManager.new(self.module)
        # combina e remove instruções redundantes
        self.passes.add(PASS_INSTCOMBINE)
        # reassocia instruções para otimizar aritmética de constantes
        self.passes.add(PASS_REASSOCIATE)
        # elimina subexpressões comuns
        self.passes.add(PASS_GVN)
        # self.passes.add(PASS_MEM2REG)
        # remove blocos básicos sem predecessor, elimina nó PHI para blocos básicos
        # com um único predecessor e elimina blocos que contém salto incondicional
        self.passes.add(PASS_SIMPLIFYCFG)
        # inicializa as otimizações
        self.passes.initialize()
        ###FIM_OTIMIZAÇÕES####

        self.gen_inicio(self.tree)
        self.builder.ret(Constant.int(Type.int(), 0))

        print('\n\n;=== Código LLVM final ===')
        if(self.optz==True):
            print("----SEM OTIMIZAÇÃO----\n",self.module)
            self.passes.run(self.func)
            print("----COM OTIMIZAÇÃO----\n",self.module)
        else:
            print(self.module)

    def gen_inicio(self, no):
        if no.name == "programa-proc":
            self.gen_procedimento(no.children[0])
            func_type = Type.function(Type.int(), [])
            self.func = self.module.add_function(func_type, "main")
            self.gen_block()
            self.gen_inst_composta(no.children[1])
        else:
            func_type = Type.function(Type.int(), [])
            self.func = self.module.add_function(func_type, "main")
            self.gen_block()
            self.gen_inst_composta(no.children[0])
            

    def gen_procedimento(self, no):
        proc=no.children[0]
        self.scope = proc.leaf[0]
        args = self.args_name(proc.children[0])
        func_type = Type.function(Type.int(), [args[i][0] for i in range(0,len(args))])
        self.func = self.module.add_function(func_type, proc.leaf[0])
        self.gen_block() #TESTE EXCLUIR DEPOIS

        for i, arg in enumerate(args):
            self.func.args[i].name = arg[1]
            # print(self.symbols)
            #Descomentar apos o teste
            # self.symbols[self.scope+"."+arg[1]][1] = self.func.args[i]
            # self.symbols[self.scope+"."+arg[1]].append(arg[0])

            #TESTE
            #################
            # Testar melhor mais acho que funciona..
            ################
            # print (arg[0])
            a = self.builder.alloca(arg[0])
            self.builder.store(self.func.args[i], a)
            self.symbols[self.scope+"."+arg[1]][1] = a
            self.symbols[self.scope+"."+arg[1]].append(Type.pointer(arg[0]))

            #FIM TESTE#

            # self.builder.store(b, self.symbols[self.scope+"."+no.leaf[0]][1])
            # self.symbols[self.scope+"."+no.leaf[0]][1] = self.builder.alloca(tipo, name = no.leaf[0])

        # self.gen_block() #DESCOMENTAR APOS O TESTE
        self.gen_inst_composta(proc.children[1])
        self.builder.ret(Constant.int(Type.int(), 0)) #Função teria que ser void.
        self.scope = "global"
        if(self.optz==True):
            self.passes.run(self.func)

        if len(no.children)>1:
            self.gen_procedimento(no.children[1])

        
    def gen_block(self):
        block = self.func.append_basic_block('entry')
        self.builder = Builder.new(block)

    def args_name(self, no):
        tipos=[]
        if len(no.children)>0:
            tipo = self.get_tipo(no.children[0])
            tipos.append([tipo,no.leaf[0]])
            if len(no.children)>1:
                tipos=tipos+self.args_name(no.children[1])
        return tipos

    def get_tipo(self, no):
        if(no.leaf[0]=="inteiro"):
            return Type.int()
        else:
            return Type.float()

    def gen_inst_composta(self, no):
        self.gen_instrucao(no.children[0])
        if len(no.children)>1:
            self.gen_inst_composta(no.children[1])

    def gen_instrucao(self, no):
        # declaracao 
        if no.children[0].name == 'declaracao_tipo':
            self.gen_declaracao(no.children[0])

        # repita
        if no.children[0].name == 'repita':
            self.gen_repita(no.children[0])
            
        # condicional
        if no.children[0].name == 'condicional':
            self.gen_condicional(no.children[0])
            
        # atribuicao 
        if no.children[0].name == 'atribuicao':
            self.gen_atribuicao(no.children[0])
            
        # leitura 
        if no.children[0].name == 'leitura':
            self.gen_leitura(no.children[0])
            
        # escrita 
        if no.children[0].name == 'escrita':
            self.gen_escrita(no.children[0])
            

        # chamada_procedimento 
        if no.children[0].name == 'call_procedimento':
            self.gen_chamada_procedimento(no.children[0])


    # declaracao 
    def gen_declaracao(self, no):
        tipo = self.get_tipo(no.children[0])
        self.symbols[self.scope+"."+no.leaf[0]][1] = self.builder.alloca(tipo, name = no.leaf[0])
        self.symbols[self.scope+"."+no.leaf[0]].append(Type.pointer(tipo))


    # repita
    def gen_repita(self,no):
        repeat = self.func.append_basic_block('repeat')
        end_repeat = self.func.append_basic_block('end_repeat')
        self.builder.branch(repeat)
        self.builder.position_at_beginning(repeat)
        self.gen_inst_composta(no.children[0])
        cond = self.gen_expr(no.children[1])
        bool_cond = self.builder.fcmp(FCMP_UGT, cond, #Testar com "FCMP_UGT"
            Constant.real(Type.float(), 0), 'ifcond')
        self.builder.cbranch(bool_cond, end_repeat, repeat)
        self.builder.position_at_beginning(end_repeat)
    
    # condicional
    def gen_condicional(self, no):
        cond = self.gen_expr(no.children[0])
        bool_cond = self.builder.fcmp(FCMP_UGT, cond, #Testar melhor as condições.
            Constant.real(Type.float(), 0), 'ifcond')
        then_if = self.func.append_basic_block('then_if')
        if (len(no.children)== 3): 
            else_if = self.func.append_basic_block('else_if')
        end_if = self.func.append_basic_block('end_if')
        if (len(no.children)==3):
            self.builder.cbranch(bool_cond, then_if, else_if)
        else:
            self.builder.cbranch(bool_cond, then_if, end_if)
        self.builder.position_at_beginning(then_if)
        self.gen_inst_composta(no.children[1])
        self.builder.branch(end_if)
        if (len(no.children)==3):
            self.builder.position_at_beginning(else_if)
            self.gen_inst_composta(no.children[2])
            self.builder.branch(end_if)
        self.builder.position_at_beginning(end_if)


    # atribuicao 
    def gen_atribuicao(self, no):
        b = self.gen_expr(no.children[0]);

        if self.symbols[self.scope+"."+no.leaf[0]][2] == "inteiro":
            b = self.c_f2i(b)

        self.builder.store(b, self.symbols[self.scope+"."+no.leaf[0]][1])


    # leitura
    def gen_leitura(self, no):
        var = self.builder.call(self.scanf_f, [])
        if self.symbols[self.scope+"."+no.leaf[0]][2] == "inteiro":
            var = self.c_f2i(var)
        self.builder.store(var, self.symbols[self.scope+"."+no.leaf[0]][1])
            
    # escrita
    def gen_escrita(self, no):
        arg = self.gen_expr(no.children[0])
        self.builder.call(self.printf_f, [arg])



    # chamada_procedimento 
    def gen_chamada_procedimento(self, no):
        args = self.gen_call_args(no.children[0])
        for i  in range(len(args)):
            if self.symbols[no.leaf[0]][1][i] == "inteiro":
                args[i] = self.c_f2i(args[i])
        func = self.module.get_function_named(no.leaf[0])
        return self.builder.call(func, args, 'calltmp')


    def gen_call_args(self, no):
        args = []
        if(no.name == "empty"):
            return args
        while no:
            args.append(self.gen_expr_simples(no.children[0]))
            if len(no.children) > 1:
                no = no.children[1]
            else:
                break
        return args


    def gen_expr(self, no):
        left = self.gen_expr_simples(no.children[0])
        result = left
        if len(no.children)>1:
            right = self.gen_expr_simples(no.children[2])
            op = no.children[1].name
            if op =='igual':
                result = self.builder.fcmp(FCMP_UEQ, left, right, 'cmptmp')
                result = self.c_i2f(result)
                result = self.builder.fmul(result, Constant.real(Type.float(), -1), 'multmp')
            elif op == 'menor':
                result = self.builder.fcmp(FCMP_ULT, left, right, 'cmptmp')
                result = self.c_i2f(result)
                result = self.builder.fmul(result, Constant.real(Type.float(), -1), 'multmp')
        return result


    def gen_expr_simples(self, no):
        if len(no.children) == 1:
            return self.termo(no.children[0])
        else:
            left = self.gen_expr_simples(no.children[0])
            right = self.gen_expr_simples(no.children[1])
            op = no.leaf[0]
            if op == '+':
                return self.builder.fadd(left, right, 'addtmp')
            elif op == '-':
                return self.builder.fsub(left, right, 'subtmp')

    
    def termo(self, no):##FAZER MULLTIPLICAÇÂO
        if len(no.children)>1:
            left = self.termo(no.children[0])
            right = self.fator(no.children[2])
            op = no.children[1].leaf[0]
            if op == '*':
                return self.builder.fmul(left, right, 'multmp')
            elif op == '/':
                return self.builder.fdiv(left, right, 'divtmp')
        else:
            return self.fator(no.children[0])

    def c_i2ptr(self,v):
        if (type(v) == ConstantInt):
            return v.inttoptr(Type.pointer(Type.float()))
        else:
            return self.builder.inttoptr(v, Type.pointer(Type.float()))

    def c_f2i(self, v):
        if (type(v) == ConstantInt):
            return v.fptosi(Type.int())
        else:
            return self.builder.fptosi(v, Type.int())


    def c_i2f(self, v):
        if (type(v) == ConstantInt):
            return v.sitofp(Type.float())
        else:
            return self.builder.sitofp(v, Type.float())

    def fator(self, no):
        if no.name == "fator_1":
            return self.gen_expr(no.children[0])

        # print(self.scope, no.leaf[0])
        if no.name == 'id':

            identificador = self.symbols[self.scope+"."+no.leaf[0]][1]

            if self.symbols[self.scope+"."+no.leaf[0]][3] != Type.float() \
                and self.symbols[self.scope+"."+no.leaf[0]][3] != Type.int():
                identificador = self.builder.load(identificador)   
            if self.symbols[self.scope+"."+no.leaf[0]][2] == "inteiro":
                identificador = self.c_i2f(identificador)
            return identificador
            
        if no.name=='numero':
            return Constant.real(Type.float(), no.children[0].leaf[0])
if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    driver = Gen(code)