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

    for i in range(inicio + 21, inicio + 26):  # linhas 25 a 29
        df.loc[i, 1] = sku
        df.loc[i, 2] = id_prod_hub
        df.loc[i, 3] = sku_hub

    df.to_csv(arquivo, sep=";", index=False, encoding="latin1", header=False)
    print(f"SKU {sku} (ANY=2) atualizado nas linhas {inicio + 22} a {inicio + 26}.")

# Configuração
arquivo = "SKUxCANAL Release ATT.csv"
token = "259037346L1E1706474176096C161316217609600O1.I"

# Loop
bloco_atual = 24  # Começa na linha 25
while True:
    sku_input = input("Digite o SKU: ")
    id_prod_hub_input = input("Digite o ID Prod Hub: ")

    resultado = buscar_ids(sku_input, id_prod_hub_input, token)
    if resultado:
        atualizar_planilha(arquivo, *resultado, bloco_atual)

    if input("Deseja adicionar outro SKU? (s/n): ").strip().lower() != "s":
        break

    bloco_atual += 6
