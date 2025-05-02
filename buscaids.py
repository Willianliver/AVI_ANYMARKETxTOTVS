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
            print("Erro: ID do SKU não encontrado na resposta da API.")
    else:
        print(f"Erro ao buscar SKU {sku}: {response.status_code} - {response.text}")

    return None

def atualizar_planilha(arquivo, sku, id_prod_hub, sku_hub, inicio):
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    fim = inicio + 24

    while len(df) < fim:
        df.loc[len(df)] = [""] * len(df.columns)

    # Replica colunas A, E, F e G (linhas 4 a 27)
    valores_coluna_a = df.iloc[3:27, 0].tolist()
    valores_coluna_e = df.iloc[3:27, 4].tolist()
    valores_coluna_f = df.iloc[3:27, 5].tolist()
    valores_coluna_g = df.iloc[3:27, 6].tolist()

    for i in range(inicio, fim):
        df.loc[i, 0] = valores_coluna_a[i - inicio]
        df.loc[i, 4] = valores_coluna_e[i - inicio]
        df.loc[i, 5] = valores_coluna_f[i - inicio]
        df.loc[i, 6] = valores_coluna_g[i - inicio]

    for i in range(inicio, inicio + 20):  # linhas 4 a 22
        df.loc[i, 1] = sku
        df.loc[i, 2] = id_prod_hub
        df.loc[i, 3] = sku_hub

    df.to_csv(arquivo, sep=";", index=False, encoding="latin1", header=False)
    print(f"SKU {sku} (ANY=1) atualizado nas linhas {inicio + 1} a {fim}.")

# Configuração
arquivo = "C:\Automações\Vincular Ids Anymarket\SKUxCANAL_Release_ATT.csv"
token = "259025663L259026924E1621429706599C152811770659900O1.I"

# Loop
bloco_atual = 3  # Começa na linha 4
while True:
    sku_input = input("Digite o SKU: ")
    id_prod_hub_input = input("Digite o ID Prod Hub: ")

    resultado = buscar_ids(sku_input, id_prod_hub_input, token)
    if resultado:
        atualizar_planilha(arquivo, *resultado, bloco_atual)

    if input("Deseja adicionar outro SKU? (s/n): ").strip().lower() != "s":
        break

    bloco_atual += 24
