# -*- coding: utf-8 -*-
import ply.lex as lex

# Lista de Palavras Reservadas
reservadas = {
    'se': 'SE',
    'então': 'ENTAO',
    'senão': 'SENAO',
    'fim': 'FIM',
    'repita': 'REPITA',
    'até': 'ATE',
    'leia': 'LEIA',
    'escreve': 'ESCREVE',
    'procedimento': 'PROCEDIMENTO',
    'flutuante': 'FLUTUANTE',
    'inteiro': 'INTEIRO',
}

# Lista de Tokens.
tokens = [
    'N_FLUTUANTE',
    'N_INTEIRO',
    'MAIS',
    'MENOS',
    'VEZES',
    'DIVIDIR',
    'IGUAL',
    'VIRGULA',
    'MENOR',
    'ABREPARENTES',
    'FECHAPARENTES',
    'PONTOEVIRGULA',
    'RECEBE',
    'ID'
] + list(reservadas.values())


# Expressões regulares simples.
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DIVIDIR = r'\/'
t_IGUAL = r'\='
t_VIRGULA = r'\,'
t_MENOR = r'\<'
t_ABREPARENTES = r'\('
t_FECHAPARENTES = r'\)'
t_PONTOEVIRGULA = r';'
t_RECEBE = r':='


# Expressões regulares mais complexas
def t_ID(t):
    r'[a-zA-Zà-ú][0-9a-zà-úA-Z]*'
    t.type = reservadas.get(t.value, 'ID')
    return t


# Define expressão regular para numeros de ponto flutuante
def t_N_FLUTUANTE(t):
    r'[0-9]+(\.[0-9]+)(e(\+|\-)?(\d+))?'
    # t.type = "NUMERO"
    t.value = float(t.value)
    return t


# Define expressão regular para numeros inteiros
def t_N_INTEIRO(t):
    r'\d+'
    # t.type = "NUMERO"
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Ignorar Comentarios
def t_COMMENT(t):
    r'{[^\{^\}]*}'
    pass


# Erro
def t_error(t):
    print("Caracter Ilegal '%s', linha %d" % (t.value[0], t.lineno))
    print(type(t.value))
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    lex.input(code.read())
    while True:
        tok = lex.token()
        if not tok:
            break
        print(tok)
