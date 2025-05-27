import requests
import pandas as pd

def buscar_ids(sku, id_prod_hub, token):
    url = f"http://api.anymarket.com.br/v2/products/{id_prod_hub}"
    headers = {"Content-Type": "application/json", "gumgaToken": token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sku_hub = data.get("skus", [{}])[0].get("id")

        if sku_hub is not None:
            return sku, id_prod_hub, int(sku_hub)
        else:
            print("❌ Erro: ID do SKU não encontrado na resposta da API.")
    else:
        print(f"❌ Erro ao buscar SKU {sku}: {response.status_code} - {response.text}")
    return None

def encontrar_bloco_vazio(arquivo):
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("❌ Erro: Arquivo não encontrado.")
        return 3  # Começa na linha 4 (índice 3)

    bloco_tamanho = 26
    linha_inicial = 3  # Começa na linha 4 (índice 3)

    while True:
        bloco = df.iloc[linha_inicial:linha_inicial + bloco_tamanho]

        # Verificar se as colunas B, C e D estão todas vazias nesse bloco
        colunas_verificar = bloco[[1, 2, 3]]  # Colunas B, C, D
        if colunas_verificar.isnull().all().all() or (colunas_verificar == "").all().all():
            return linha_inicial

        linha_inicial += bloco_tamanho

        # Se passou do tamanho atual do dataframe, significa que precisa adicionar um bloco novo
        if linha_inicial >= len(df):
            return linha_inicial


def encontrar_proxima_linha(arquivo):
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("❌ Erro: Arquivo não encontrado.")
        return 3  # Começa na linha 4 caso não encontre

    # Verifica até a última linha que contém algum dado na coluna A
    linhas_ocupadas = df[df[0].notnull()].index.tolist()

    if not linhas_ocupadas:
        return 3  # Se não houver dados, começa na linha 4

    ultima_linha = max(linhas_ocupadas)
    proxima_linha = ultima_linha +1

    # Mantém sempre o intervalo de 27 linhas por bloco
    if (proxima_linha - 3) % 26 != 0:
        proxima_linha = 3 + (((proxima_linha - 3) // 26) +1 ) * 26

    return proxima_linha


def atualizar_planilha(arquivo, sku, id_prod_hub, sku_hub, inicio):
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("❌ Erro: Arquivo não encontrado.")
        return

    fim = inicio + 25  # Bloco de 27 linhas

    while len(df) <= fim:
        df.loc[len(df)] = [""] * len(df.columns)

    # Replica colunas A, E, F e G (linhas 4 a 30 da planilha)
    valores_coluna_a = df.iloc[3:30, 0].tolist()
    valores_coluna_e = df.iloc[3:30, 4].tolist()
    valores_coluna_f = df.iloc[3:30, 5].tolist()
    valores_coluna_g = df.iloc[3:30, 6].tolist()

    for i in range(inicio, fim + 1):
        df.loc[i, 0] = valores_coluna_a[i - inicio]
        df.loc[i, 4] = valores_coluna_e[i - inicio]
        df.loc[i, 5] = valores_coluna_f[i - inicio]
        df.loc[i, 6] = valores_coluna_g[i - inicio]

    # Preenche colunas B, C e D nas primeiras 20 linhas do bloco
    for i in range(inicio, inicio + 20):
        df.loc[i, 1] = sku
        df.loc[i, 2] = id_prod_hub
        df.loc[i, 3] = sku_hub

    df.to_csv(arquivo, sep=";", index=False, encoding="latin1", header=False)
    print(f"✅ SKU {sku} (ANY=1) atualizado nas linhas {inicio + 1} a {fim + 1}.")


# 🔧 Configuração
arquivo = r"C:\Automações\Vincular Ids Anymarket\SKUxCANAL_Release_ATT.csv"
token = "259025663L259026924E1621429706599C152811770659900O1.I"

# 🔁 Loop
# Encontra o primeiro bloco vazio (inclusive o da linha 4 se estiver vazio)
bloco_atual = encontrar_bloco_vazio(arquivo)

while True:
    sku_input = input("Digite o SKU: ")
    id_prod_hub_input = input("Digite o ID Prod Hub: ")

    resultado = buscar_ids(sku_input, id_prod_hub_input, token)
    if resultado:
        atualizar_planilha(arquivo, *resultado, bloco_atual)

    if input("Deseja adicionar outro SKU? (s/n): ").strip().lower() != "s":
        break

    bloco_atual = encontrar_bloco_vazio(arquivo)  # Atualiza para o próximo bloco livre
