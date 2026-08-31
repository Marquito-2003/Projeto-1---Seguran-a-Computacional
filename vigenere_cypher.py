# -*- coding: utf-8 -*-
from collections import Counter
import string
import textwrap
import unicodedata

# ----------------------------------------------------------------------
# 1. Tabelas de Frequência Esperada (%) - Alfabeto A-Z (26 letras)
# ----------------------------------------------------------------------
FREQ_PT = {
    'A': 14.63, 'B': 1.04, 'C': 3.88, 'D': 4.99, 'E': 12.57, 'F': 1.02,
    'G': 1.30,  'H': 1.28, 'I': 6.18, 'J': 0.40, 'K': 0.02,  'L': 2.78,
    'M': 4.74,  'N': 5.05, 'O': 10.73,'P': 2.52, 'Q': 1.20,  'R': 6.53,
    'S': 7.81,  'T': 4.74, 'U': 4.63, 'V': 1.67, 'W': 0.01,  'X': 0.21,
    'Y': 0.01,  'Z': 0.47
}

FREQ_EN = {
    'A': 8.17,  'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.70, 'F': 2.23,
    'G': 2.02,  'H': 6.09, 'I': 6.97, 'J': 0.15, 'K': 0.77,  'L': 4.03,
    'M': 2.41,  'N': 6.75, 'O': 7.51, 'P': 1.93, 'Q': 0.10,  'R': 5.99,
    'S': 6.33,  'T': 9.06, 'U': 2.76, 'V': 0.98, 'W': 2.36,  'X': 0.15,
    'Y': 1.97,  'Z': 0.07
}


def remover_acentos(texto):
    """Remove diacríticos/acentos mantendo maiúsculas, minúsculas e símbolos."""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def extrair_apenas_letras(texto):
    """Extrai apenas letras A-Z para a matemática da criptoanálise estatística."""
    texto_sem_acento = remover_acentos(texto)
    return "".join(filter(str.isalpha, texto_sem_acento.upper()))


# ----------------------------------------------------------------------
# 2. Parte I – Cifrador e Decifrador (Preservando Espaços e Símbolos)
# ----------------------------------------------------------------------
def vigenere_processar(texto, chave, decifrar=False):
    """
    Processa a cifra mantendo espaços, quebras de linha e maiúsculas/minúsculas.
    Avança o índice da chave apenas quando encontra letras alfabéticas.
    """
    texto_sem_acento = remover_acentos(texto)
    chave_limpa = extrair_apenas_letras(chave)

    if not chave_limpa:
        raise ValueError("A chave deve conter ao menos uma letra válida.")

    resultado = []
    len_chave = len(chave_limpa)
    chave_idx = 0

    for char in texto_sem_acento:
        if char.isalpha() and char.isascii():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(chave_limpa[chave_idx % len_chave]) - ord('A')

            if decifrar:
                shift = -shift

            novo_char = chr(((ord(char) - base + shift) % 26) + base)
            resultado.append(novo_char)
            chave_idx += 1
        else:
            resultado.append(char)

    return "".join(resultado)


def vigenere_cifrar(texto_claro, chave):
    return vigenere_processar(texto_claro, chave, decifrar=False)


def vigenere_decifrar(criptograma, chave):
    return vigenere_processar(criptograma, chave, decifrar=True)


# ----------------------------------------------------------------------
# 3. Parte II – Ataque de Criptoanálise Estatística
# ----------------------------------------------------------------------
def indice_de_coincidencia(texto):
    n = len(texto)
    if n <= 1:
        return 0.0
    freq = Counter(texto)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))


def estimar_tamanho_chave(criptograma, max_key_len=20, limiar_ic=0.060):
    texto_puro = extrair_apenas_letras(criptograma)
    ics_medios = []

    print("\n" + "=" * 60)
    print("ETAPA 1: Estimativa do Tamanho da Chave (Análise de IC)")
    print("=" * 60)
    print(f"{'Tamanho (k)':<12} | {'IC Médio':<12} | {'Hipótese'}")
    print("-" * 60)

    for k in range(1, max_key_len + 1):
        ics = [indice_de_coincidencia(texto_puro[i::k]) for i in range(k)]
        avg_ic = sum(ics) / len(ics)
        ics_medios.append((k, avg_ic))

        status = "Possível chave natural" if avg_ic >= limiar_ic else "Polialfabético / Aleatório"
        print(f"{k:<12} | {avg_ic:<12.4f} | {status}")

    # Filtra os candidatos acima do limiar e escolhe o menor divisor com pico significativo
    candidatos = [k for k, ic in ics_medios if ic >= limiar_ic]
    if candidatos:
        # Pega o maior IC e verifica se algum divisor menor também possui IC alto
        melhor_k = max(candidatos, key=lambda k: ics_medios[k-1][1])
        for cand in sorted(candidatos):
            if melhor_k % cand == 0 and ics_medios[cand-1][1] >= 0.065:
                melhor_k = cand
                break
    else:
        melhor_k = max(ics_medios, key=lambda x: x[1])[0]

    print(f"\n=> Tamanho sugerido automaticamente: {melhor_k}\n")
    return melhor_k


def qui_quadrado(contagens, total, freq_esperada):
    qui = 0.0
    for letra, perc in freq_esperada.items():
        esperado = (perc / 100.0) * total
        observado = contagens.get(letra, 0)
        if esperado > 0:
            qui += ((observado - esperado) ** 2) / esperado
    return qui


def descobrir_chave(criptograma, freq_esperada, key_len, top_candidatos=3):
    texto_puro = extrair_apenas_letras(criptograma)
    chave = []

    print("=" * 60)
    print(f"ETAPA 2: Análise de Frequência por Posição (Chave tam = {key_len})")
    print("=" * 60)

    for i in range(key_len):
        bloco = texto_puro[i::key_len]
        total_bloco = len(bloco)
        scores = []

        for shift in range(26):
            decifrado = [chr(((ord(c) - ord('A') - shift) % 26) + ord('A')) for c in bloco]
            contagens = Counter(decifrado)
            score_qui = qui_quadrado(contagens, total_bloco, freq_esperada)
            letra_hipotese = chr(shift + ord('A'))
            scores.append((letra_hipotese, score_qui))

        scores.sort(key=lambda x: x[1])
        melhor_letra = scores[0][0]
        chave.append(melhor_letra)

        top_str = ", ".join([f"'{letra}' (χ²={qui:.1f})" for letra, qui in scores[:top_candidatos]])
        print(f"Posição {i + 1:02d} -> Escolhida: '{melhor_letra}' | Melhores: {top_str}")

    chave_final = "".join(chave)
    print(f"\n=> Chave recuperada: {chave_final}\n")
    return chave_final


# ----------------------------------------------------------------------
# 4. Interface Interativa / Menu Principal
# ----------------------------------------------------------------------
def ler_texto_multilinhas(prompt):
    print(prompt)
    linhas = []
    while True:
        try:
            linha = input()
            if not linha and linhas:
                break
            linhas.append(linha)
        except EOFError:
            break
    return "\n".join(linhas)


def formatar_saida(rotulo, texto, largura=80):
    print(f"\n[{rotulo}]")
    print("-" * largura)
    print(textwrap.fill(texto, width=largura, replace_whitespace=False))
    print("-" * largura)


def main():
    while True:
        print("\n" + "=" * 55)
        print("   SISTEMA DE CIFRA DE VIGENÈRE E CRIPTOANÁLISE")
        print("=" * 55)
        print("1. Cifrar mensagem")
        print("2. Decifrar mensagem com chave conhecida")
        print("3. Criptoanálise (Recuperar chave e decifrar)")
        print("4. Sair")

        opcao = input("\nEscolha uma opção (1-4): ").strip()

        if opcao == "1":
            msg = input("Digite a mensagem em texto claro:\n")
            key = input("Digite a chave (senha): ")
            try:
                cifrado = vigenere_cifrar(msg, key)
                formatar_saida("TEXTO CIFRADO", cifrado)
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "2":
            cifrado = input("Digite o criptograma:\n")
            key = input("Digite a chave (senha): ")
            try:
                decifrado = vigenere_decifrar(cifrado, key)
                formatar_saida("TEXTO DECIFRADO", decifrado)
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "3":
            print("Cole o texto cifrado (pressione ENTER duas vezes para confirmar):")
            linhas = []
            while True:
                l = input()
                if not l:
                    break
                linhas.append(l)
            cifrado = " ".join(linhas)

            if not extrair_apenas_letras(cifrado):
                print("Erro: Criptograma não contém letras válidas.")
                continue

            print("\nQual idioma esperado do texto original?")
            print("1. Português (PT)")
            print("2. Inglês (EN)")
            idioma = input("Escolha (1 ou 2): ").strip()
            freq_tabela = FREQ_PT if idioma != "2" else FREQ_EN

            sugestao_k = estimar_tamanho_chave(cifrado)
            ajuste = input(f"Pressione [ENTER] para usar tamanho {sugestao_k} ou digite outro valor: ").strip()
            tam_chave = int(ajuste) if ajuste.isdigit() else sugestao_k

            chave_encontrada = descobrir_chave(cifrado, freq_tabela, tam_chave)
            mensagem_recuperada = vigenere_decifrar(cifrado, chave_encontrada)

            formatar_saida("MENSAGEM FINAL RECUPERADA", mensagem_recuperada)

        elif opcao == "4":
            print("\nEncerrando programa...")
            break
        else:
            print("Opção inválida, tente novamente.")


if __name__ == "__main__":
    main()