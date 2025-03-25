import requests
import pandas as pd

def buscar_ids(sku, id_prod_hub, token):
    """Busca o ID do SKU na API do AnyMarket."""
    url = f"http://api.anymarket.com.br/v2/products/{id_prod_hub}"
    headers = {"Content-Type": "application/json", "gumgaToken": token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sku_hub = data.get("skus", [{}])[0].get("id")

        if sku_hub is not None:
            return sku, id_prod_hub, int(sku_hub)  # Garante que seja um número inteiro
        else:
            print("Erro: ID do SKU não encontrado na resposta da API.")
    else:
        print(f"Erro ao buscar SKU {sku}: {response.status_code} - {response.text}")

    return None

def atualizar_planilha(arquivo, sku, id_prod_hub, sku_hub, inicio):
    """Atualiza um bloco mantendo a estrutura original da planilha, preenchendo apenas as colunas B, C e D de 23 a 27."""
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    # Atualizar apenas as linhas 23 a 27 dentro do bloco
    for i in range(inicio + 19, inicio + 24):  # 23 a 27 (índices 22 a 26 no pandas)
        df.loc[i, 1] = sku        # Coluna B -> "Produto"
        df.loc[i, 2] = id_prod_hub # Coluna C -> "Id Prd Hub"
        df.loc[i, 3] = sku_hub     # Coluna D -> "SKU Hub"

    # Salvar sem modificar cabeçalhos e estrutura original
    df.to_csv(arquivo, sep=";", index=False, encoding="latin1", header=False)
    print(f"SKU {sku} atualizado com sucesso nas linhas {inicio + 20} a {inicio + 24}!")

# Configuração inicial
arquivo = "SKUxCANAL MODELO - Copia.csv"
token = "259037346L1E1706474176096C161316217609600O1.I"

# Loop para adicionar múltiplos SKUs
bloco_atual = 3  # Começa na linha 4 (índice 3)
while True:
    sku_input = input("Digite o SKU: ")
    id_prod_hub_input = input("Digite o ID Prod Hub: ")

    resultado = buscar_ids(sku_input, id_prod_hub_input, token)
    if resultado:
        atualizar_planilha(arquivo, *resultado, bloco_atual)

    opcao = input("Deseja adicionar outro SKU? (s/n): ").strip().lower()
    if opcao != "s":
        break

    bloco_atual += 24  # Corrigido para garantir alinhamento correto

print("Processamento concluído para todos os SKUs!")
