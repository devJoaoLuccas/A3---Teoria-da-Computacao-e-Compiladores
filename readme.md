# Transpilador Latim ➔ Python (PLY)

Curso: Teoria da Computação e Compiladores
Faculdade: UNIFACS
Grupo: João Luccas Lordelo Marques - 12725224055
       Maurício Gabriel leal da Silva - 12724157145 
       Pablo Ernesto da Cunha Guerreiro - 12724111921

## 📌 Sobre o Projeto

O objetivo principal é a criação de um transpilador robusto capaz de ler um arquivo de código-fonte escrito em uma linguagem customizada baseada em **Latim** (`.latio`) e convertê-lo em código **Python** (`.py`) equivalente, limpo e pronto para execução, sem erros de sintaxe ou de identação.

---

## 🛠️ Estratégia de Criação e Ferramental
Para o desenvolvimento das fases do compilador, foi utilizada a estrutura clássica do **PLY (Python Lex-Yacc)**:
* **Lex (Analisador Léxico):** Mapeia o fluxo de caracteres em tokens significativos utilizando Expressões Regulares (Regex).
* **Yacc (Analisador Sintático):** Utiliza uma gramática LALR(1) para validar a estrutura do programa e, simultaneamente, realizar a síntese e tradução do código de saída.

---

## 🏗️ Funcionamento Interno Passo a Passo

### 1. Análise Léxica (O Lexer)
O analisador lê o arquivo de entrada caractere por caractere. Espaços em branco, tabs e quebras de linha são ignorados de forma nativa antes do processamento sintático.
* **Palavras Reservadas:** Termos estruturais em Latim como `initium`, `finis`, `numerus`, `decimalis`, `textus`, `logicum`, `si`, `aliter`, `dum` e `pro` são protegidos para evitar conflitos com nomes de variáveis.
* **Tokens Identificados:** Operadores matemáticos (`+`, `-`, `*`, `/`), relacionais (`<`, `>`, `==`, `<=`, `>=`, `!=`) e delimitadores (`.`, `,`, `;`, `(`, `)`, `{`, `}`).

### 2. Tabela de Símbolos & Validação Semântica
O transpilador gerencia uma tabela de símbolos dinâmica (escopo) para garantir o cumprimento das seguintes regras de validação exigidas no barema:
* **Detecção de Redundância:** Se o usuário tentar declarar a mesma variável duas vezes, o transpilador acusa erro semântico de duplicidade e interrompe a execução informando a linha exata.
* **Checagem de Existência:** Toda atribuição, leitura (`lege`) ou exibição (`scribe`) valida se a variável envolvida foi previamente declarada. O uso de variáveis não declaradas gera uma interrupção semântica imediata.

### 3. Ausência de Recursividade à Esquerda e Precedência Matemática
Para respeitar a precedência natural dos operadores sem causar loops infinitos no Parser (recursão à esquerda), a gramática de expressões aritméticas foi estritamente fatorada em 3 níveis hierárquicos:
1. **Expressao ➔** Termo (`+` ou `-` Termo)*
2. **Termo ➔** Fator (`*` ou `/` Fator)*
3. **Fator ➔** Número Inteiro | Número Decimal | Identificador | `( Expressao )`

### 4. Mapeamento Gramatical (Latim ➔ Python)

| Sintaxe em Latim | Equivalente em Python | Descrição / Ação do Parser |
| :--- | :--- | :--- |
| `initium ... finis.` | *Escopo principal* | Define o início e o fim obrigatório do programa. |
| `numerus a.` | `a = 0` | Declara um tipo Inteiro e inicializa o valor padrão. |
| `decimalis b.` | `b = 0.0` | Declara um tipo Decimal e inicializa o valor padrão. |
| `textus t.` | `t = ""` | Declara uma String e inicializa o valor padrão. |
| `logicum s.` | `s = False` | Declara um Booleano e inicializa o valor padrão. |
| `scribe(item).` | `print(item)` | Exibição de dados no console. |
| `lege(var).` | `var = int(input())` ou `float(input())` | Captura entrada do teclado aplicando o *cast* correto baseado no tipo da variável. |
| `si (expr) { ... }` | `if expr:` | Estrutura condicional simples (identada automaticamente). |
| `aliter { ... }` | `else:` | Estrutura condicional composta. |
| `dum (expr) { ... }` | `while expr:` | Laço de repetição condicional. |
| `pro (init; expr; inc)` | `while expr:` *(Simulado via iteração)* | Laço de repetição por contagem contínua. |

---

## 🚀 Como Executar o Ecossistema

### Pré-requisitos
Certifique-se de ter o Python 3 e a biblioteca PLY instalados na sua máquina:
```bash
pip install ply
fluxo acima e escreve um arquivo final de extensão .py limpo, estruturado, identado e pronto
para ser executado nativamente pelo interpretador Python.
