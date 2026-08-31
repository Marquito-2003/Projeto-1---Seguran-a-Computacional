Segurança Computacional - 2026/2<br>
Professora Priscila Solis<br>

Alex Batista Resende (231025261)<br>
Marco Aurelio Gonçalves Fonseca (221021509)<br>
Thomas Jefferson (202033561)<br>

# Projeto 1 — Cifra de Vigenère e Criptoanálise Estatística

Este repositório contém a implementação completa da **Cifra de Vigenère** (cifragem e decifragem com chave conhecida) e de um módulo autônomo de **Criptoanálise Estatística** (recuperação de tamanho de chave via Índice de Coincidência e quebra das posições via teste de Qui-Quadrado $\chi^2$).

O projeto conta com interface interativa de terminal (CLI), suporte a textos com múltiplas linhas, normalização de caracteres acentuados mantendo o layout original (espaços, maiúsculas, minúsculas e pontuações) e tabelas de frequência para **Português (PT)** e **Inglês (EN)**.

---

## Estrutura dos Arquivos

- `vigenere_cypher.py`: Código-fonte completo em Python contendo a lógica de cifragem/decifragem, funções estatísticas de criptoanálise ($IC$ e $\chi^2$) e menu interativo.
- `README.md`: Documentação e guia de execução do projeto.

---

## Funcionalidades

### 1. Cifragem e Decifragem (`vigenere_cifrar` / `vigenere_decifrar`)

- **Preservação de Formatação:** Espaços, quebras de linha e caracteres especiais/pontuações são mantidos intactos na saída; apenas letras do alfabeto são deslocadas.
- **Preservação de Caixa (Case-sensitive):** Mantém distinção entre letras maiúsculas e minúsculas.
- **Normalização Unicode:** Remove diacríticos (acentos) antes do processamento para adequação ao alfabeto latino padrão de 26 letras ($A\text{–}Z$).

### 2. Criptoanálise Estatística

- **Etapa 1 — Estimativa do Período/Tamanho da Chave ($k$):**
  - Utiliza o **Índice de Coincidência ($IC$)**, fatiando o texto cifrado em $k$ subgrupos para $k \in [1, 20]$.
  - Compara a média com o limiar de língua natural ($IC \ge 0.060$) e busca a menor frequência fundamental para evitar falsos positivos causados por múltiplos periódicos (harmônicos).
  - Permite confirmação automática ou intervenção/ajuste manual pelo usuário.
- **Etapa 2 — Recuperação da Chave por Qui-Quadrado ($\chi^2$):**
  - Isola as $k$ fatias monoalfabéticas (Cifras de César independentes).
  - Para cada posição de 0 a 25 deslocamentos, calcula a aderência da distribuição observada em relação à esperada para o idioma selecionado (Português ou Inglês).
  - Elege o deslocamento que minimiza o resíduo do $\chi^2$, montando a palavra-chave e decifrando a mensagem completa.

---

## Como Executar

### Pré-requisitos

- Python 3.8 ou superior (apenas bibliotecas nativas: `collections`, `unicodedata`, `textwrap`, `string`).

### Executando o programa:

```bash
python3 vigenere_cypher.py
```
