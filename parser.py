import ply.yacc as yacc
from lex import tokens
from ast import *

precedence = (
    ('left', 'MAIS', 'MENOS'),
    ('left', 'VEZES', 'DIVIDIR'),
)


def p_programa_1(p):
    'programa : def_procedimento inst_composta '
    p[0] = AST('programa-proc', [p[1], p[2]])


def p_programa_2(p):
    'programa : inst_composta '
    p[0] = AST('programa', [p[1]])


def p_dec_procedimento_1(p):
    ' def_procedimento : procedimento '
    p[0] = AST('def_procedimento', [p[1]])


def p_def_procedimento_2(p):
    'def_procedimento : procedimento def_procedimento'
    p[0] = AST('def_procedimento', [p[1], p[2]])


def p_procedimento(p):
    'procedimento : PROCEDIMENTO ID ABREPARENTES list_param_real FECHAPARENTES inst_composta  FIM'
    p[0] = AST('procedimento', [p[4], p[6]], [p[2]])


def p_list_param_real_1(p):
    'list_param_real : tipo_numerico  ID VIRGULA list_param_real'
    p[0] = AST('lista_param_real', [p[1], p[4]], [p[2]])


def p_list_param_real_2(p):
    'list_param_real : tipo_numerico  ID'
    p[0] = AST('lista_param_real', [p[1]], [p[2]])


def p_list_param_real_3(p):
    'list_param_real : empty'
    p[0] = AST('list_param_real', [])


def p_tipo_numerico_1(p):
    'tipo_numerico : INTEIRO'
    p[0] = AST('tipo_numerico', [], [p[1]])


def p_tipo_numerico_2(p):
    'tipo_numerico : FLUTUANTE'
    p[0] = AST('tipo_numerico', [], [p[1]])


def p_inst_composta_1(p):
    'inst_composta : instrucao inst_composta'
    p[0] = AST('inst_composta', [p[1], p[2]])


def p_inst_composta_2(p):
    'inst_composta : instrucao'
    p[0] = AST('inst_composta', [p[1]])


def p_instrucao(p):
    '''instrucao : repita PONTOEVIRGULA
                | condicional
                | atribuicao PONTOEVIRGULA
                | leitura PONTOEVIRGULA
                | escrita PONTOEVIRGULA
                | declaracao PONTOEVIRGULA
                | chamada_procedimento PONTOEVIRGULA'''

    p[0] = AST('instrucao', [p[1]])


def p_repita(p):
    'repita : REPITA inst_composta ATE expr'
    p[0] = AST('repita', [p[2], p[4]])


def p_condicional_1(p):
    'condicional : SE expr ENTAO inst_composta FIM'
    p[0] = AST('condicional', [p[2], p[4]])


def p_condicional_2(p):
    'condicional : SE expr ENTAO inst_composta SENAO inst_composta FIM'
    p[0] = AST('condicional', [p[2], p[4], p[6]])


def p_atribuicao(p):
    'atribuicao : ID RECEBE expr'
    p[0] = AST('atribuicao', [p[3]], [p[1]])


def p_leitura(p):
    'leitura : LEIA ID'
    p[0] = AST('leitura', [], [p[2]])


def p_escrita(p):
    'escrita : ESCREVE expr'
    p[0] = AST('escrita', [p[2]])


def p_declaracao_1(p):
    'declaracao : tipo_numerico ID'
    p[0] = AST('declaracao_tipo', [p[1]], [p[2]])


def p_chamada_procedimento(p):
    'chamada_procedimento : ID ABREPARENTES list_param FECHAPARENTES'
    p[0] = AST('call_procedimento', [p[3]], [p[1]])


def p_list_param_1(p):
    'list_param : expr_simples VIRGULA list_param'
    p[0] = AST('list_param', [p[1], p[3]])


def p_lista_param_2(p):
    'list_param : expr_simples'
    p[0] = AST('list_param', [p[1]])


def p_lista_param_3(p):
    'list_param : empty'
    p[0] = AST('empty', [])


def p_comp_op_1(p):
    'comp_op : MENOR'
    p[0] = AST('menor', [], [p[1]])


def p_comp_op_2(p):
    'comp_op : IGUAL'
    p[0] = AST('igual', [], [p[1]])


def p_expr_1(p):
    'expr : expr_simples comp_op expr_simples'
    p[0] = AST('expr', [p[1], p[2], p[3]])


def p_expr_2(p):
    'expr : expr_simples'
    p[0] = AST('expr_2', [p[1]])


def p_expr_simples_1(p):
    ''' expr_simples : expr_simples MAIS expr_simples
                     | expr_simples MENOS expr_simples'''
    p[0] = AST('expr_simples-soma', [p[1], p[3]], [p[2]])


def p_expr_simples_2(p):
    'expr_simples : termo'
    p[0] = AST('expr_simples_termo', [p[1]])


def p_termo_1(p):
    'termo : termo mult fator'
    p[0] = AST('termo', [p[1], p[2], p[3]])


def p_termo_2(p):
    'termo : fator'
    p[0] = AST('termo_fator', [p[1]])


def p_mult(p):
    ''' mult : VEZES
            | DIVIDIR '''
    p[0] = AST('mult', [], [p[1]])


def p_fator_1(p):
    'fator : ABREPARENTES expr FECHAPARENTES'
    p[0] = AST('fator_1', [p[2]])


def p_fator_2(p):
    'fator : numero'
    p[0] = AST('numero', [p[1]])


def p_fator_3(p):
    'fator : ID'
    p[0] = AST('id', [], [p[1]])


def p_numero(p):
    '''numero : N_FLUTUANTE
            | N_INTEIRO'''
    p[0] = AST('int_float', [], [p[1]])


def p_empty(p):
    ' empty : '


def p_error(p):
    if p:
        print("Erro sintatico: '%s' linha %d" % (p.value, p.lineno))
        exit(1)
    else:
        yacc.restart()
        print('Erro sintatico')
        exit(1)


def parse_tree(code):
    parser = yacc.yacc(debug=True)
    return parser.parse(code)

if __name__ == '__main__':
    import sys
    parser = yacc.yacc(debug=True)
    code = open(sys.argv[1])
    if 'a' in sys.argv:
        print(parser.parse(code.read()))
    else:
        parser.parse(code.read())
