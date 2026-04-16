import zipfile
import pandas as pd
import ftplib
import os

layout = [("Ano",1,4),("Trimestre",5,1),("UF",6,2),("Capital",8,2),("RM_RIDE",10,2),("UPA",12,9),("Estrato",21,7),("V1008",28,2),("V1014",30,2),("V1016",32,1),("V1022",33,1),("V1023",34,1),("V1027",35,15),("V1028",50,15),("V1029",65,9),("V1033",74,9),("posest",83,3),("posest_sxi",86,3),("V2001",89,2),("V2007",95,1),("V2009",104,3),("V2010",107,1),("V3009A",125,2),("V3014",135,1),("V4002",137,1),("V4012",156,1),("V4013",158,5),("V40132A",164,1),("V4015",166,1),("V40151",167,1),("V401511",168,1),("V401512",169,2),("V4016",171,1),("V40161",172,1),("V40162",173,2),("V40163",175,2),("V4017",177,1),("V40171",178,1),("V401711",179,1),("V4018",180,1),("V40181",181,1),("V40182",182,2),("V40183",184,2),("V4019",186,1),("V4020",187,1),("V4021",188,1),("V4022",189,1),("V4024",190,1),("V4025",191,1),("V4026",192,1),("V4027",193,1),("V4028",194,1),("V4029",195,1),("V4032",196,1),("V4033",197,1),("V40331",198,1),("V403312",200,8),("V403322",210,8),("V4034",220,1),("V403412",223,8),("V403422",233,8),("V4039",241,3),("V4039C",244,3),("V4043",258,1),("V4044",260,5),("V4045",265,1),("V4046",266,1),("V4048",268,1),("V4050",270,1),("V40501",271,1),("V405012",273,8),("V4051",293,1),("V40511",294,1),("V405112",296,8),("V405122",306,8),("V405912",348,8),("V405922",358,8)]
colspecs = []
nomes_colunas = []
lista_de_dataframes = []
anos_alvo = []
trimestres_alvo = []

print("\n=== Extrator de Microdados PNAD Contínua ===")
pergunta_ano = input("Qual ano deseja extrair? (Digite 0 para carregar o padrão 2023 a 2025, ou o ano específico): ").strip()
pergunta_trimestre = input("Qual trimestre deseja extrair? (Digite 0 para carregar todos, ou 1, 2, 3 ou 4): ").strip()

# Definindo a lista de anos
if pergunta_ano == "0":
    anos_alvo = [2023, 2024, 2025]
else:
    anos_alvo = [int(pergunta_ano)]

# Definindo a lista de trimestres
if pergunta_trimestre == "0":
    trimestres_alvo = [1, 2, 3, 4]
else:
    trimestres_alvo = [int(pergunta_trimestre)]

for nome, inicio, tamanho in layout:
    inicio_py = inicio - 1
    fim_py = inicio_py + tamanho 
    colspecs.append((inicio_py, fim_py))
    nomes_colunas.append(nome)
    
def baixar_e_extrair_pnadc(ano, trimestre):
    FTP_HOST = "ftp.ibge.gov.br"
    FTP_PATH = f"/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/{ano}/"
    
    print(f"\n--- Conectando ao FTP para Ano: {ano} | Trimestre: {trimestre} ---")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login() 
        ftp.cwd(FTP_PATH)
        
        # Filtra apenas os .zip e ORDENA
        arquivos = [arq for arq in ftp.nlst() if arq.endswith('.zip')]
        arquivos.sort() 
        arquivo_alvo = arquivos[trimestre - 1]
        caminho_zip = os.path.join(os.getcwd(), arquivo_alvo)
        
        print(f"Baixando '{arquivo_alvo}'...")
        with open(caminho_zip, "wb") as file:
            ftp.retrbinary(f"RETR {arquivo_alvo}", file.write)
            
        print("Download concluído! Extraindo o arquivo .txt...")
        
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            nome_txt = zip_ref.namelist()[0] 
            zip_ref.extract(nome_txt, os.getcwd())
            caminho_txt = os.path.join(os.getcwd(), nome_txt)
            
        print(f"Arquivo extraído com sucesso: {nome_txt}")
        
        # Remove o ZIP local para economizar espaço
        os.remove(caminho_zip)
        
        return caminho_txt
        
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None
        
    finally:
        ftp.quit()

for ano_atual in anos_alvo:
    for tri_atual in trimestres_alvo:

        caminho_arquivo_txt = baixar_e_extrair_pnadc(ano_atual, tri_atual)
        
        # Filtrar só da Bahia e carregar
        if caminho_arquivo_txt:
            print(f"Iniciando a pré-filtragem dos dados para o UF 29...")
            
            caminho_txt_uf29 = os.path.join(os.getcwd(), f"PNADC_{ano_atual}_T{tri_atual}_UF29.txt")
            linhas_filtradas = 0
            
            # Lê o TXT gigante e escreve apenas o UF 29 no TXT menor
            with open(caminho_arquivo_txt, 'r', encoding='utf-8') as f_in, \
                 open(caminho_txt_uf29, 'w', encoding='utf-8') as f_out:
                
                for linha in f_in:
                    if linha[5:7] == '29':
                        f_out.write(linha)
                        linhas_filtradas += 1

            print(f"Pré-filtragem concluída! {linhas_filtradas} registros encontrados.")
            print("Carregando o arquivo filtrado no Pandas...")

            # Carrega o TXT menor no DataFrame
            df_temp = pd.read_fwf(caminho_txt_uf29,colspecs=colspecs,names=nomes_colunas,dtype=str)
            lista_de_dataframes.append(df_temp)
            # Limpeza do disco (remove o TXT do Brasil e o TXT da Bahia após carregar na RAM)
            os.remove(caminho_arquivo_txt)
            os.remove(caminho_txt_uf29)
#Finalização e exibição do DataFrame final
if len(lista_de_dataframes) > 1:
    df_final = pd.concat(lista_de_dataframes, ignore_index=True)
    print("Ordenando cronologicamente por Ano e Trimestre...")
    df_final = df_final.sort_values(by=['Ano', 'Trimestre'], ascending=[True, True])
    df_final = df_final.reset_index(drop=True)
    print(f"Tamanho do DataFrame final: {df_final.shape[0]} linhas e {df_final.shape[1]} colunas.")
    print(df_final[['Ano', 'Trimestre']].value_counts(sort=False))
    print("\nDataFrame final criado com sucesso! Exibindo as primeiras linhas:")
    print(df_final.head())
elif len(lista_de_dataframes) == 1:
    df_final = lista_de_dataframes[0]
    print("Apenas um arquivo processado. DataFrame final criado com sucesso.")
    print(f"Tamanho do DataFrame final: {df_final.shape[0]} linhas e {df_final.shape[1]} colunas.")
    print(df_final[['Ano', 'Trimestre']].value_counts(sort=False))
    print("\nExibindo as primeiras linhas do DataFrame final:")
    print(df_final.head())
else:
    print("\nNão foi possível gerar o DataFrame final (nenhum arquivo processado com sucesso).")