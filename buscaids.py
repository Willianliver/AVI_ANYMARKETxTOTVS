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
    """Atualiza um bloco de 24 linhas mantendo a estrutura original da planilha,
    preenchendo corretamente as colunas sem sobrescrever dados errados."""
    
    try:
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", header=None, dtype=str)
    except FileNotFoundError:
        print("Erro: Arquivo não encontrado.")
        return

    fim = inicio + 24  # Define o intervalo do bloco de 24 linhas

    # Se a planilha não tiver espaço suficiente, adiciona novas linhas vazias
    while len(df) < fim:
        df.loc[len(df)] = [""] * len(df.columns)

    # Replicando os valores das colunas A, E, F e G (linhas 4 até 27) logo abaixo
    valores_coluna_a = df.iloc[3:27, 0].tolist()  # Pega os valores da coluna A
    valores_coluna_e = df.iloc[3:27, 4].tolist()  # Pega os valores da coluna E
    valores_coluna_f = df.iloc[3:27, 5].tolist()  # Pega os valores da coluna F
    valores_coluna_g = df.iloc[3:27, 6].tolist()  # Pega os valores da coluna G
    
    for i in range(inicio, fim):
        df.loc[i, 0] = valores_coluna_a[i - inicio]  # Replica os valores na coluna A
        df.loc[i, 4] = valores_coluna_e[i - inicio]  # Replica os valores na coluna E
        df.loc[i, 5] = valores_coluna_f[i - inicio]  # Replica os valores na coluna F
        df.loc[i, 6] = valores_coluna_g[i - inicio]  # Replica os valores na coluna G

    # Atualizar as colunas B, C e D apenas nas linhas 4 a 22 (índice 3 a 21)
    for i in range(inicio, inicio + 19):  # Apenas até a linha 22 do bloco
        df.loc[i, 1] = sku        # Coluna B -> "Produto"
        df.loc[i, 2] = id_prod_hub # Coluna C -> "Id Prd Hub"
        df.loc[i, 3] = sku_hub     # Coluna D -> "SKU Hub"

    # Salvar sem modificar os cabeçalhos e estrutura original
    df.to_csv(arquivo, sep=";", index=False, encoding="latin1", header=False)
    print(f"SKU {sku} atualizado com sucesso nas linhas {inicio + 1} a {fim}!")

# Configuração inicial
arquivo = "SKUxCANAL MODELO - Copia.csv"
token = "259025663L259026924E1621429706599C152811770659900O1.I"

# Loop para adicionar múltiplos SKUs
bloco_atual = 3  # Começa na quarta linha (índice 3)
while True:
    sku_input = input("Digite o SKU: ")
    id_prod_hub_input = input("Digite o ID Prod Hub: ")

    resultado = buscar_ids(sku_input, id_prod_hub_input, token)
    if resultado:
        atualizar_planilha(arquivo, *resultado, bloco_atual)

    opcao = input("Deseja adicionar outro SKU? (s/n): ").strip().lower()
    if opcao != "s":
        break

    bloco_atual += 24  # Avança para o próximo bloco de 24 linhas

print("Processamento concluído para todos os SKUs!")
