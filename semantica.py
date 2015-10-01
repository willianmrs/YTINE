from parser import *


class Semantica():

    def __init__(self, code):
        self.table = {}
        self.scope = "global"
        self.tree = parse_tree(code)

    def inicio(self):
        if self.tree.name == "programa-proc":
            self.dec_procedimento(self.tree.children[0])
            self.inst_composta(self.tree.children[1])

        else:
            self.inst_composta(self.tree.children[0])

    def dec_procedimento(self, no):
        proc = no.children[0]
        self.scope = proc.leaf[0]
        qtd_param = self.list_param_real(proc.children[0])

        if proc.leaf[0] in self.table.keys():
            print(
                "Erro Semantico. Procedimento '"+proc.leaf[0] + "' já declarado")
            exit(1)

        self.table[proc.leaf[0]] = ['procedimento', qtd_param]

        self.inst_composta(proc.children[1])

        self.scope = 'global'

        if len(no.children) > 1:
            self.dec_procedimento(no.children[1])

    def list_param_real(self, no):
        tipos = []
        if len(no.children) > 0:
            tipo = self.get_tipo(no.children[0])
            tipos.append(tipo)
            self.table[str(self.scope+"."+no.leaf[0])] = ['var', 0, tipo]
            if len(no.children) > 1:
                tipos = tipos+self.list_param_real(no.children[1])
        return tipos

    def inst_composta(self, no):
        self.instrucao(no.children[0])
        if len(no.children) > 1:
            self.inst_composta(no.children[1])

    def get_tipo(self, no):
        return no.leaf[0]

    def instrucao(self, no):
        # declaracao
        if no.children[0].name == 'declaracao_tipo':
            self.declaracao(no.children[0])

        # repita
        if no.children[0].name == 'repita':
            self.repita(no.children[0])

        # condicional
        if no.children[0].name == 'condicional':
            self.condicional(no.children[0])

        # atribuicao
        if no.children[0].name == 'atribuicao':
            self.atribuicao(no.children[0])

        # leitura
        if no.children[0].name == 'leitura':
            self.leitura(no.children[0])

        # escrita
        if no.children[0].name == 'escrita':
            self.expr(no.children[0].children[0])

        # chamada_procedimento
        if no.children[0].name == 'call_procedimento':
            self.chamada_procedimento(no.children[0])

    def declaracao(self, no):
        tipo = self.get_tipo(no.children[0])
        if self.scope+"."+no.leaf[0] in self.table.keys():
            print("Erro Semantico. Variavel '"+no.leaf[0] + "' já declarada")
            exit(1)

        if no.leaf[0] in self.table.keys():
            print("Erro Semantico. '"+no.leaf[0] + "' é um procedimento," +
                  " não pode criar variaveis com o mesmo nome do procedimento")
            exit(1)
        self.table[self.scope+"."+no.leaf[0]] = ["var", 0, tipo]

    def repita(self, no):
        self.inst_composta(no.children[0])
        self.expr(no.children[1])

    def condicional(self, no):
        self.expr(no.children[0])
        self.inst_composta(no.children[1])
        if len(no.children) == 3:
            self.inst_composta(no.children[2])

    def atribuicao(self, no):
        if self.scope+"."+no.leaf[0] not in self.table.keys():
            print("Erro Semantico. Variavel '"+no.leaf[0] + "' não encontrada")
            exit(1)
        self.expr(no.children[0])

    def leitura(self, no):
        if self.scope+"."+no.leaf[0] not in self.table.keys():
            print("Erro Semantico. Variavel '"+no.leaf[0] + "' não encontrada")
            exit(1)

    def chamada_procedimento(self, no):
        if no.leaf[0] not in self.table.keys():
            print(
                "Erro Semantico. Procedimento '"+no.leaf[0] + "' não declarado")
            exit(1)
        param = self.list_param(no.children[0])
        if len(self.table[no.leaf[0]][1]) != param:
            print("Erro Semantico. Esperado(s) '"+str(len(self.table[no.leaf[0]][1])) +
                  "' argumento(s), mais foi(ram) passado(s) '"+str(param)+"'")
            exit(1)

    def list_param(self, no):
        if len(no.children) > 1:
            return self.list_param(no.children[1])+1
        elif len(no.children) == 1:
            return 1
        else:
            return 0

    
    def get_op(self, no):
        return no.leaf[0]

    def expr(self, no):
        self.expr_simples(no.children[0])
        if len(no.children) > 1:
            op = self.get_op(no.children[1])
            self.expr_simples(no.children[2])

    def expr_simples(self, no):
        if len(no.children) == 1:
            self.termo(no.children[0])
        else:
            self.expr_simples(no.children[0])
            self.expr_simples(no.children[1])

    def termo(self, no):
        if len(no.children) > 1:
            self.termo(no.children[0])
            self.fator(no.children[2])
        else:
            self.fator(no.children[0])

    def fator(self, no):
        if no.name == 'id':
            if self.scope+"."+no.leaf[0] not in self.table.keys():
                print(
                    "Erro Semantico. Variavel '"+no.leaf[0] + "' não encontrada")
                exit(1)
        if no.name == 'fator_1':
            self.expr(no.children[0])


if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    s = Semantica(code.read())
    s.inicio()
    print("Tabela de Simbolos:", s.table)
