import sys
import ply.lex as lex
import ply.yacc as yacc

# ==========================================
# 1. ANALISADOR LÉXICO (LEXER)
# ==========================================

# Palavras reservadas da linguagem em Latim
reserved = {
    'initium': 'INITIUM',
    'finis': 'FINIS',
    'numerus': 'NUMERUS',
    'decimalis': 'DECIMALIS',
    'textus': 'TEXTUS',
    'logicum': 'LOGICUM',
    'si': 'SI',
    'aliter': 'ALITER',
    'dum': 'DUM',
    'pro': 'PRO',
    'scribe': 'SCRIBE',
    'lege': 'LEGE'
}

# Lista de Tokens básicos
tokens = [
    'ID', 'NUM_INT', 'NUM_DEC', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'ASSIGN', 'SEMI', 'DOT', 'COMMA',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE'
] + list(reserved.values())

# Expressões Regulares para os tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_SEMI = r';'
t_DOT = r'\.'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'

# Operadores Relacionais (necessários para as Expressões Lógicas)
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_EQ = r'=='
t_NE = r'!='


# Regra para Strings (ex: "texto")
def t_STRING(t):
    r'\"([^\\\"]|\\.)*\"'
    return t


# Regra para Números Decimais (deve vir antes do Inteiro para não fundir)
def t_NUM_DEC(t):
    r'\d+\.\d+'
    return t


# Regra para Números Inteiros
def t_NUM_INT(t):
    r'\d+'
    return t


# Regra para Identificadores e Palavras Reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica se é palavra reservada
    return t


# Ignorar espaços, tabs e quebras de linha (atendendo ao barema)
t_ignore = ' \t\r\n'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Tratamento de erros léxicos
def t_error(t):
    print(
        f"Erro Léxico: Caractere inválido '{t.value[0]}' na linha {t.lineno}"
    )
    t.lexer.skip(1)


# Construindo o Lexer
lexer = lex.lex()


# ==========================================
# 2. TABELA DE SÍMBOLOS & VALIDAÇÃO
# ==========================================
# Armazena as variáveis declaradas e seus respectivos tipos
symbol_table = {}


def declare_variable(name, var_type, lineno):
    if name in symbol_table:
        print(
            f"Erro Semântico: Variável '{name}' já declarada (Linha {lineno})."
        )
        sys.exit(1)
    symbol_table[name] = var_type


def check_variable(name, lineno):
    if name not in symbol_table:
        print(
            f"Erro Semântico: Variável '{name}' utilizada mas não foi"
            f" declarada (Linha {lineno})."
        )
        sys.exit(1)
    return symbol_table[name]


# ==========================================
# 3. ANALISADOR SINTÁTICO (PARSER) & TRANSPILADOR
# ==========================================

# Regra Inicial: initium Bloco finis.
def p_prog(p):
    'prog : INITIUM bloco FINIS DOT'
    p[0] = p[2]


# Bloco: Acumula zero ou mais Comandos ou Declarações
def p_bloco_vazio(p):
    'bloco : '
    p[0] = ""


def p_bloco_lista(p):
    '''bloco : bloco comando
             | bloco declaracao'''
    # Concatena o código Python gerado linha por linha
    p[0] = p[1] + p[2]


# Declarações de Variáveis (Ex: numerus a. )
def p_declaracao(p):
    '''declaracao : NUMERUS ID DOT
                  | DECIMALIS ID DOT
                  | TEXTUS ID DOT
                  | LOGICUM ID DOT'''
    tipo_latim = p[1]
    var_name = p[2]

    # Registra na tabela de símbolos para checagem semântica
    declare_variable(var_name, tipo_latim, p.lineno(2))

    # Em Python não precisamos tipar explicitamente na declaração,
    # mas podemos inicializá-la com valores default equivalentes
    defaults = {
        'numerus': '0', 'decimalis': '0.0',
        'textus': '""', 'logicum': 'False'
    }
    p[0] = f"{var_name} = {defaults[tipo_latim]}\n"


# Comandos Estruturados
def p_comando_atribuicao(p):
    'comando : ID ASSIGN expressao DOT'
    var_name = p[1]
    check_variable(var_name, p.lineno(1))  # Validação Semântica
    p[0] = f"{var_name} = {p[3]}\n"


def p_comando_scribe(p):
    'comando : SCRIBE LPAREN expressao RPAREN DOT'
    p[0] = f"print({p[3]})\n"


def p_comando_lege(p):
    'comando : LEGE LPAREN ID RPAREN DOT'
    var_name = p[3]
    tipo = check_variable(var_name, p.lineno(3))  # Validação Semântica

    # Faz o cast do input em Python baseado no tipo declarado em Latim
    if tipo == 'numerus':
        p[0] = f"{var_name} = int(input())\n"
    elif tipo == 'decimalis':
        p[0] = f"{var_name} = float(input())\n"
    elif tipo == 'logicum':
        p[0] = f"{var_name} = bool(input())\n"
    else:
        p[0] = f"{var_name} = input()\n"


# Estrutura Condicional: si / aliter
def p_comando_si(p):
    'comando : SI LPAREN expr_logica RPAREN LBRACE bloco RBRACE'
    # Identação das linhas internas do bloco para o padrão Python
    corpo_if = "".join(
        [f"    {line}\n" for line in p[6].splitlines() if line.strip()]
    )
    if not corpo_if:
        corpo_if = "    pass\n"
    p[0] = f"if {p[3]}:\n{corpo_if}"


def p_comando_si_aliter(p):
    'comando : SI LPAREN expr_logica RPAREN LBRACE bloco RBRACE ALITER LBRACE bloco RBRACE'  # noqa: E501
    corpo_if = "".join(
        [f"    {line}\n" for line in p[6].splitlines() if line.strip()]
    )
    if not corpo_if:
        corpo_if = "    pass\n"
    corpo_else = "".join(
        [f"    {line}\n" for line in p[10].splitlines() if line.strip()]
    )
    if not corpo_else:
        corpo_else = "    pass\n"
    p[0] = f"if {p[3]}:\n{corpo_if}else:\n{corpo_else}"


# Estrutura de Repetição: dum (while)
def p_comando_dum(p):
    'comando : DUM LPAREN expr_logica RPAREN LBRACE bloco RBRACE'
    corpo_while = "".join(
        [f"    {line}\n" for line in p[6].splitlines() if line.strip()]
    )
    if not corpo_while:
        corpo_while = "    pass\n"
    p[0] = f"while {p[3]}:\n{corpo_while}"


# Estrutura de Repetição: pro (for)
# Sintaxe Latim: pro (Atribuicao; ExpressaoLogica; Atribuicao) { Bloco }
# Nota: Como o for em C/Java/Latim mapeia diferente do range() do Python,
# simulamos usando controle de fluxo clássico para garantir fidelidade.
def p_comando_pro(p):
    'comando : PRO LPAREN ID ASSIGN expressao SEMI expr_logica SEMI ID ASSIGN expressao RPAREN LBRACE bloco RBRACE'  # noqa: E501
    var_init = p[3]
    check_variable(var_init, p.lineno(3))
    check_variable(p[9], p.lineno(9))

    init_step = f"{var_init} = {p[5]}\n"
    increment_step = f"    {p[9]} = {p[11]}\n"

    corpo_for = "".join(
        [f"    {line}\n" for line in p[14].splitlines() if line.strip()]
    )
    p[0] = f"{init_step}while {p[7]}:\n{corpo_for}{increment_step}"


# Expressões Lógicas (Para Si, Dum e Pro)
def p_expr_logica(p):
    '''expr_logica : expressao LT expressao
                   | expressao GT expressao
                   | expressao LE expressao
                   | expressao GE expressao
                   | expressao EQ expressao
                   | expressao NE expressao'''
    p[0] = f"{p[1]} {p[2]} {p[3]}"


# Expressões Matemáticas Fatoradas
# (sem recursividade à esquerda, com precedência correta)
def p_expressao_operacao(p):
    '''expressao : expressao PLUS termo
                 | expressao MINUS termo'''
    p[0] = f"{p[1]} {p[2]} {p[3]}"


def p_expressao_termo(p):
    'expressao : termo'
    p[0] = p[1]


def p_termo_operacao(p):
    '''termo : termo TIMES fator
             | termo DIVIDE fator'''
    p[0] = f"{p[1]} {p[2]} {p[3]}"


def p_termo_fator(p):
    'termo : fator'
    p[0] = p[1]


def p_fator_num_int(p):
    'fator : NUM_INT'
    p[0] = p[1]


def p_fator_num_dec(p):
    'fator : NUM_DEC'
    p[0] = p[1]


def p_fator_string(p):
    'fator : STRING'
    p[0] = p[1]


def p_fator_id(p):
    'fator : ID'
    check_variable(p[1], p.lineno(1))  # Garante que foi declarada
    p[0] = p[1]


def p_fator_expr(p):
    'fator : LPAREN expressao RPAREN'
    p[0] = f"({p[2]})"


# Tratamento de Erros Sintáticos
def p_error(p):
    if p:
        # Identifica o tipo de erro com base no token onde o parser travou
        token_type = p.type
        token_value = p.value
        line_number = p.lineno

        print("-" * 60)
        print(f"❌ ERRO SINTÁTICO DETECTADO na linha {line_number}")
        print(f"Próximo ao termo: '{token_value}'")

        # Sugestões inteligentes do tipo de erro
        prev_line = p.lexer.lexdata.splitlines()[line_number - 2].strip()
        if (token_type in ['ID', 'SI', 'DUM', 'SCRIBE', 'LEGE']
                and prev_line[-1] != '.'):
            print(
                "💡 Diagnóstico: Provavelmente faltou um ponto final ('.')"
                " no comando da linha anterior."
            )
        elif token_type == 'LBRACE':
            print(
                "💡 Diagnóstico: Erro na estrutura da condição ou laço."
                " Verifique o uso de parênteses antes das chaves '{'."
            )
        elif token_type == 'FINIS':
            print(
                "💡 Diagnóstico: Estrutura de bloco incompleta."
                " Verifique se fechou todas as chaves '{ }' antes do 'finis.'."
            )
        elif token_type == 'RPAREN':
            print(
                "💡 Diagnóstico: Parêntese de fechamento ')'"
                " inesperado ou mal posicionado."
            )
        else:
            print(
                f"💡 Diagnóstico: O termo '{token_value}'"
                f" (Tipo: {token_type}) quebra as"
                " regras gramaticais estabelecidas."
            )

        print("-" * 60)
    else:
        print("-" * 60)
        print("❌ ERRO SINTÁTICO: Fim de arquivo inesperado (EOF).")
        print(
            "💡 Diagnóstico: O programa terminou abruptamente."
            " Você provavelmente esqueceu de fechar o bloco com"
            " 'finis.' ou deixou chaves '{' abertas."
        )
        print("-" * 60)

    sys.exit(1)


# Construindo o Parser
parser = yacc.yacc()


# ==========================================
# 4. EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso correto: python transpiler.py <arquivo_entrada.latio>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
        sys.exit(1)

    # Executa o parser que retorna a string do código compilado em Python
    python_code = parser.parse(data)

    # Nome do arquivo de saída gerado
    output_file = input_file.replace('.latio', '.py')
    if output_file == input_file:
        output_file = 'output_compiled.py'

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(
            "# Código gerado automaticamente pelo "
            "Transpilador Latim -> Python\n"
        )
        out.write(python_code)

    print(
        f"Transpilação concluída com sucesso! Arquivo gerado: '{output_file}'"
    )
