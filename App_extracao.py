import zipfile
import pandas as pd
import ftplib
import os

CNAE_MACRO = {
    '01': 'AGRICULTURA, PECUÁRIA, CAÇA E SERVIÇOS RELACIONADOS',
    '02': 'PRODUÇÃO FLORESTAL',
    '03': 'PESCA E AQÜICULTURA',
    '05': 'EXTRAÇÃO DE CARVÃO MINERAL',
    '06': 'EXTRAÇÃO DE PETRÓLEO E GÁS NATURAL',
    '07': 'EXTRAÇÃO DE MINERAIS METÁLICOS',
    '08': 'EXTRAÇÃO DE MINERAIS NÃO-METÁLICOS',
    '09': 'ATIVIDADES DE APOIO À EXTRAÇÃO DE MINERAIS',
    '10': 'FABRICAÇÃO DE PRODUTOS ALIMENTÍCIOS',
    '11': 'FABRICAÇÃO DE BEBIDAS',
    '12': 'FABRICAÇÃO DE PRODUTOS DO FUMO',
    '13': 'FABRICAÇÃO DE PRODUTOS TÊXTEIS',
    '14': 'CONFECÇÃO DE ARTIGOS DO VESTUÁRIO E ACESSÓRIOS',
    '15': 'PREPARAÇÃO DE COUROS E FABRICAÇÃO DE ARTEFATOS DE COURO, ARTIGOS DE VIAGEM E CALÇADOS',
    '16': 'FABRICAÇÃO DE PRODUTOS DE MADEIRA',
    '17': 'FABRICAÇÃO DE CELULOSE, PAPEL E PRODUTOS DE PAPEL',
    '18': 'IMPRESSÃO E REPRODUÇÃO DE GRAVAÇÕES',
    '19': 'FABRICAÇÃO DE COQUE; PRODUTOS DERIVADOS DE PETRÓLEO E DE BIOCOMBUSTÍVEIS',
    '20': 'FABRICAÇÃO DE PRODUTOS QUÍMICOS',
    '21': 'FABRICAÇÃO DE PRODUTOS FARMOQUÍMICOS E FARMACÊUTICOS',
    '22': 'FABRICAÇÃO DE PRODUTOS DE BORRACHA E DE MATERIAL PLÁSTICO',
    '23': 'FABRICAÇÃO DE PRODUTOS DE MINERAIS NÃO-METÁLICOS',
    '24': 'METALURGIA',
    '25': 'FABRICAÇÃO DE PRODUTOS DE METAL, EXCETO MÁQUINAS E EQUIPAMENTOS',
    '26': 'FABRICAÇÃO DE EQUIPAMENTOS DE INFORMÁTICA, PRODUTOS ELETRÔNICOS E ÓPTICOS',
    '27': 'FABRICAÇÃO DE MÁQUINAS, APARELHOS E MATERIAIS ELÉTRICOS',
    '28': 'FABRICAÇÃO DE MÁQUINAS E EQUIPAMENTOS',
    '29': 'FABRICAÇÃO DE VEÍCULOS AUTOMOTORES, REBOQUES E CARROCERIAS',
    '30': 'FABRICAÇÃO DE OUTROS EQUIPAMENTOS DE TRANSPORTE, EXCETO VEÍCULOS AUTOMOTORES',
    '31': 'FABRICAÇÃO DE MÓVEIS',
    '32': 'FABRICAÇÃO DE PRODUTOS DIVERSOS',
    '33': 'MANUTENÇÃO, REPARAÇÃO E INSTALAÇÃO DE MÁQUINAS E EQUIPAMENTOS',
    '35': 'ELETRICIDADE, GÁS E OUTRAS UTILIDADES',
    '36': 'CAPTAÇÃO, TRATAMENTO E DISTRIBUIÇÃO DE ÁGUA',
    '37': 'ESGOTO E ATIVIDADES RELACIONADAS',
    '38': 'COLETA, TRATAMENTO E DISPOSIÇÃO DE RESÍDUOS; RECUPERAÇÃO DE MATERIAIS',
    '39': 'DESCONTAMINAÇÃO E OUTROS SERVIÇOS DE GESTÃO DE RESÍDUOS',
    '41': 'CONSTRUÇÃO E INCORPORAÇÃO DE EDIFÍCIOS',
    '42': 'OBRAS DE INFRA-ESTRUTURA',
    '43': 'SERVIÇOS ESPECIALIZADOS PARA CONSTRUÇÃO',
    '45': 'COMÉRCIO E REPARAÇÃO DE VEÍCULOS AUTOMOTORES E MOTOCICLETAS',
    '48': 'COMÉRCIO, EXCETO DE VEICULOS AUTOMOTORES E MOTOCICLETAS',
    '49': 'TRANSPORTE TERRESTRE',
    '50': 'TRANSPORTE AQUAVIÁRIO',
    '51': 'TRANSPORTE AÉREO',
    '52': 'ARMAZENAMENTO E ATIVIDADES AUXILIARES DOS TRANSPORTES',
    '53': 'CORREIO E OUTRAS ATIVIDADES DE ENTREGA',
    '55': 'ALOJAMENTO',
    '56': 'ALIMENTAÇÃO',
    '58': 'EDIÇÃO E EDIÇÃO INTEGRADA À DE IMPRESSÃO',
    '59': 'ATIVIDADES CINEMATOGRÁFICAS, PRODUÇÃO DE VÍDEOS E DE PROGRAMAS DE TELEVISÃO; GRAVAÇÃO DE SOM E DE MÚSICA',
    '60': 'ATIVIDADES DE RÁDIO E DE TELEVISÃO',
    '61': 'TELECOMUNICAÇÕES',
    '62': 'ATIVIDADES DOS SERVIÇOS DE TECNOLOGIA DA INFORMAÇÃO',
    '63': 'ATIVIDADES DE PRESTAÇÃO DE SERVIÇOS DE INFORMAÇÃO',
    '64': 'ATIVIDADES DE SERVIÇOS FINANCEIROS',
    '65': 'SEGUROS, RESSEGUROS, PREVIDÊNCIA COMPLEMENTAR E PLANOS DE SAÚDE',
    '66': 'ATIVIDADES AUXILIARES DOS SERVIÇOS FINANCEIROS, SEGUROS, PREVIDÊNCIA COMPLEMENTAR E PLANOS DE SAÚDE',
    '68': 'ATIVIDADES IMOBILIÁRIAS',
    '69': 'ATIVIDADES JURÍDICAS, DE CONTABILIDADE E DE AUDITORIA',
    '70': 'ATIVIDADES DE CONSULTORIA EM GESTÃO EMPRESARIAL',
    '71': 'SERVIÇOS DE ARQUITETURA E ENGENHARIA; TESTES E ANÁLISES TÉCNICAS',
    '72': 'PESQUISA E DESENVOLVIMENTO CIENTÍFICO',
    '73': 'PUBLICIDADE E PESQUISAS DE MERCADO',
    '74': 'OUTRAS ATIVIDADES PROFISSIONAIS, CIENTÍFICAS E TÉCNICAS',
    '75': 'ATIVIDADES VETERINÁRIAS',
    '77': 'ALUGUÉIS NÃO IMOBILIÁRIOS E GESTÃO DE ATIVOS INTANGÍVEIS NÃO FINANCEIROS',
    '78': 'SELEÇÃO, AGENCIAMENTO E LOCAÇÃO DE MÃO-DE-OBRA',
    '79': 'AGÊNCIAS DE VIAGENS, OPERADORES TURÍSTICOS E SERVIÇOS DE RESERVAS',
    '80': 'ATIVIDADES DE VIGILÂNCIA, SEGURANÇA E INVESTIGAÇÃO',
    '81': 'SERVIÇOS PARA EDIFICIOS E ATIVIDADES PAISAGISTICAS',
    '82': 'SERVIÇOS DE ESCRITÓRIO, DE APOIO ADMINISTRATIVO E OUTROS SERVIÇOS PRESTADOS A EMPRESAS',
    '84': 'ADMINISTRAÇÃO PÚBLICA, DEFESA E SEGURIDADE SOCIAL',
    '85': 'EDUCAÇÃO',
    '86': 'ATIVIDADES DE ATENÇÃO À SAÚDE HUMANA',
    '87': 'ATIVIDADES DE ATENÇÃO À SAÚDE HUMANA INTEGRADAS COM ASSISTÊNCIA SOCIAL, INCLUSIVE PRESTADAS EM RESIDÊNCIAS COLETIVAS E PARTICULARES',
    '88': 'SERVIÇOS DE ASSISTÊNCIA SOCIAL SEM ALOJAMENTO',
    '90': 'ATIVIDADES ARTÍSTICAS, CRIATIVAS E DE ESPETÁCULOS',
    '91': 'ATIVIDADES LIGADAS AO PATRIMÔNIO CULTURAL E AMBIENTAL',
    '92': 'ATIVIDADES DE EXPLORAÇÃO DE JOGOS DE AZAR E APOSTAS',
    '93': 'ATIVIDADES ESPORTIVAS E DE RECREAÇÃO E LAZER',
    '94': 'ATIVIDADES DE ORGANIZAÇÕES ASSOCIATIVAS',
    '95': 'REPARAÇÃO E MANUTENÇÃO DE EQUIPAMENTOS DE INFORMATICA E COMUNICAÇÃO E DE OBJETOS PESSOAIS E DOMÉSTICOS',
    '96': 'OUTRAS ATIVIDADES DE SERVIÇOS PESSOAIS',
    '97': 'SERVIÇOS DOMÉSTICOS',
    '99': 'ORGANISMOS INTERNACIONAIS E OUTRAS INSTITUIÇÕES EXTRATERRITORIAIS',
    '00': 'Atividades mal definidas',
}
 
# Chave: 5 dígitos do código CNAE (string com zeros à esquerda)
CNAE_MICRO = {
    '01101': 'Cultivo de arroz',
    '01102': 'Cultivo de milho',
    '01103': 'Cultivo de outros cereais',
    '01104': 'Cultivo de algodão',
    '01105': 'Cultivo de cana-de-açúcar',
    '01106': 'Cultivo de fumo',
    '01107': 'Cultivo de soja',
    '01108': 'Cultivo de mandioca',
    '01109': 'Cultivo de outras lavouras temporárias não especificadas anteriormente',
    '01110': 'Horticultura',
    '01111': 'Cultivo de flores e plantas ornamentais',
    '01112': 'Cultivo de frutas cítricas',
    '01113': 'Cultivo de café',
    '01114': 'Cultivo de cacau',
    '01115': 'Cultivo de uva',
    '01116': 'Cultivo de banana',
    '01117': 'Cultivo de outras plantas e frutas de lavoura permanente não especificadas anteriormente',
    '01118': 'Produção de sementes e mudas certificadas',
    '01119': 'Lavoura não especificada',
    '01201': 'Criação de bovinos',
    '01202': 'Criação de outros animais de grande porte não especificados anteriormente',
    '01203': 'Criação de caprinos e ovinos',
    '01204': 'Criação de suínos',
    '01205': 'Criação de aves',
    '01206': 'Apicultura',
    '01207': 'Sericicultura',
    '01208': 'Criação de outros animais não especificados anteriormente',
    '01209': 'Pecuária não especificada',
    '01401': 'Atividades de apoio à agricultura e pós-colheita',
    '01402': 'Atividades de apoio à pecuária',
    '01500': 'Caça e serviços relacionados',
    '01999': 'Agropecuária',
    '02000': 'Produção florestal',
    '03001': 'Pesca',
    '03002': 'Aqüicultura',
    '05000': 'Extração de carvão mineral',
    '06000': 'Extração de petróleo e gás natural',
    '07001': 'Extração de minérios de metais preciosos',
    '07002': 'Extração de minerais metálicos não especificados anteriormente',
    '08001': 'Extração de pedras, areia e argila',
    '08002': 'Extração de gemas (pedras preciosas e semi-preciosas)',
    '08009': 'Extração de minerais não metálicos não especificados anteriormente',
    '09000': 'Atividades de apoio à extração de minerais',
    '10010': 'Abate e fabricação de produtos de carne e pescado',
    '10020': 'Fabricação de conservas de frutas, legumes e outros vegetais',
    '10030': 'Fabricação de óleos e gorduras vegetais e animais',
    '10040': 'Fabricação de produtos de laticínios',
    '10050': 'Moagem, fabricação de produtos amiláceos e de alimentos para animais',
    '10060': 'Fabricação de produtos de padaria e farináceos',
    '10070': 'Fabricação de açúcar e derivados',
    '10080': 'Torrefação e moagem de café',
    '10090': 'Fabricação de outros produtos alimentícios',
    '11000': 'Fabricação de bebidas',
    '12000': 'Fabricação de produtos do fumo',
    '13000': 'Fabricação de produtos têxteis',
    '14000': 'Confecção de artigos do vestuário e acessórios',
    '15000': 'Preparação de couros e fabricação de artefatos de couro, artigos de viagem e calçados',
    '16000': 'Fabricação de produtos de madeira',
    '17000': 'Fabricação de celulose, papel e produtos de papel',
    '18000': 'Impressão e reprodução de gravações',
    '19000': 'Fabricação de coque, de produtos derivados do petróleo e de biocombustíveis',
    '20000': 'Fabricação de produtos químicos',
    '21000': 'Fabricação de produtos farmoquímicos e farmacêuticos',
    '22000': 'Fabricação de produtos de borracha e de material plástico',
    '23000': 'Fabricação de produtos de minerais não-metálicos',
    '24000': 'Metalurgia',
    '25000': 'Fabricação de produtos de metal, exceto máquinas e equipamentos',
    '26000': 'Fabricação de equipamentos de informática, produtos eletrônicos e ópticos',
    '27000': 'Fabricação de máquinas, aparelhos e materiais elétricos',
    '28000': 'Fabricação de máquinas e equipamentos',
    '29000': 'Fabricação de veículos automotores, reboques e carrocerias',
    '30000': 'Fabricação de outros equipamentos de transporte, exceto veículos automotores',
    '31000': 'Fabricação de móveis',
    '32000': 'Fabricação de produtos diversos',
    '33000': 'Manutenção, reparação e instalação de máquinas e equipamentos',
    '35000': 'Eletricidade, gás e outras utilidades',
    '36000': 'Captação, tratamento e distribuição de água',
    '37000': 'Esgoto e atividades relacionadas',
    '38000': 'Coleta, tratamento e disposição de resíduos; recuperação de materiais',
    '39000': 'Descontaminação e outros serviços de gestão de resíduos',
    '41000': 'Construção de edifícios',
    '42000': 'Construção de obras de infra-estrutura',
    '43000': 'Serviços especializados para construção',
    '45010': 'Comércio de veículos automotores',
    '45020': 'Manutenção e reparação de veículos automotores',
    '45030': 'Comércio de peças e acessórios para veículos automotores',
    '45040': 'Comércio, manutenção e reparação de motocicletas, peças e acessórios',
    '48010': 'Representantes comerciais e agentes do comércio, exceto de veículos automotores e motocicletas',
    '48020': 'Comércio de matérias-primas agrícolas e animais vivos',
    '48030': 'Comércio de produtos alimentícios, bebidas e fumo',
    '48041': 'Comércio de tecidos, artefatos de tecidos e armarinho',
    '48042': 'Comércio de artigos do vestuário, complementos, calçados e artigos de viagem',
    '48050': 'Comércio de madeira, material de construção, ferragens e ferramentas',
    '48060': 'Comércio de combustíveis para veículos automotores',
    '48071': 'Comércio de produtos farmaceuticos, médicos, ortopédicos, odontológicos e de cosméticos e perfumaria',
    '48072': 'Comércio de artigos de escritório e de papelaria; livros, jornais e outras publicações',
    '48073': 'Comércio de eletrodomésticos, móveis e outros artigos de residência',
    '48074': 'Comércio de equipamentos e produtos de tecnologias de informação e comunicação',
    '48075': 'Comércio de máquinas, aparelhos e equipamentos, exceto eletrodomésticos',
    '48076': 'Comércio de combustíveis sólidos, líquidos e gasosos, exceto para veículos automotores',
    '48077': 'Comércio de produtos usados',
    '48078': 'Comercio de residuos e sucatas',
    '48079': 'Comércio de produtos novos não especificados anteriormente',
    '48080': 'Supermercado e hipermercado',
    '48090': 'Lojas de departamento e outros comércios não especializados, sem predominância de produtos alimentícios',
    '48100': 'Comércio ambulante e feiras',
    '49010': 'Transporte ferroviário e metroferroviário',
    '49030': 'Transporte rodoviário de passageiros',
    '49040': 'Transporte rodoviário de carga',
    '49090': 'Outros transportes terrestres',
    '50000': 'Transporte Aquaviário',
    '51000': 'Transporte Aéreo',
    '52010': 'Armazenamento, carga e descarga',
    '52020': 'Atividades auxiliares dos transportes e atividades relacionadas à organização do transporte de carga',
    '53001': 'Atividades de Correio',
    '55000': 'Alojamento',
    '56011': 'Restaurantes e outros estabelecimentos de serviços de alimentação e bebidas',
    '56012': 'Serviços de catering, bufê e outros serviços de comida preparada',
    '56020': 'Serviços ambulantes de alimentação',
    '58000': 'Edição e Edição integrada à impressão',
    '59000': 'Atividades cinematográficas, produção de vídeos e de programas de televisão, gravação de som e de música',
    '60001': 'Atividades de rádio',
    '60002': 'Atividades de televisão',
    '61000': 'Telecomunicações',
    '62000': 'Atividades dos serviços de tecnologia da informação',
    '63000': 'Atividades de prestação de serviços de informação',
    '64000': 'Serviços financeiros',
    '65000': 'Seguros e previdência privada',
    '66001': 'Atividades auxiliares dos serviços financeiros',
    '66002': 'Atividades auxiliares dos seguros, da previdência complementar e dos planos de saúde',
    '68000': 'Atividades imobiliárias',
    '69000': 'Atividades jurídicas, de contabilidade e de auditoria',
    '70000': 'Atividades de consultoria em gestão empresarial',
    '71000': 'Serviços de arquitetura e engenharia e atividades técnicas relacionadas; Testes e análises técnicas',
    '72000': 'Pesquisa e desenvolvimento científico',
    '73010': 'Publicidade',
    '73020': 'Pesquisas de mercado e opinião pública',
    '74000': 'Outras atividades profissionais, científicas e técnicas não especificadas anteriormente',
    '75000': 'Atividades veterinárias',
    '77010': 'Aluguel de objetos pessoais e domésticos',
    '77020': 'Aluguel de meios de transportes, maquinas e equipamentos sem operador e gestão de ativos intangíveis não financeiros',
    '78000': 'Seleção, agenciamento e locação de mão-de-obra',
    '79000': 'Agências de viagens, operadores turísticos e serviços de reservas',
    '80000': 'Atividades de vigilância, segurança, transporte de valores e investigação',
    '81011': 'Serviços de limpeza e de apoio a edifícios, exceto condomínios prediais',
    '81012': 'Condomínios prediais',
    '81020': 'Atividades paisagísticas',
    '82001': 'Serviços de escritório e apoio administrativo',
    '82002': 'Atividades de teleatendimento',
    '82003': 'Atividades de organização de eventos, exceto culturais e esportivos',
    '82009': 'Outras atividades de serviços prestados principalmente às empresas',
    '84011': 'Administração publica e regulação da política econômica e social - Federal',
    '84012': 'Administração publica e regulação da política econômica e social - Estadual',
    '84013': 'Administração publica e regulação da política econômica e social - Municipal',
    '84014': 'Defesa',
    '84015': 'Outros serviços coletivos prestados pela administração pública - Federal',
    '84016': 'Outros serviços coletivos prestados pela administração pública - Estadual',
    '84017': 'Outros serviços coletivos prestados pela administração pública - Municipal',
    '84020': 'Seguridade social obrigatória',
    '85011': 'Creche',
    '85012': 'Pré-escola e ensino fundamental',
    '85013': 'Ensino médio',
    '85014': 'Educação superior',
    '85021': 'Serviços auxiliares à educação',
    '85029': 'Outras atividades de ensino',
    '86001': 'Atividades de atendimento hospitalar',
    '86002': 'Atividades de atenção ambulatorial executadas por médicos e odontólogos',
    '86003': 'Atividades de serviços de complementação diagnóstica e terapêutica',
    '86004': 'Atividades de profissionais da área de saúde, exceto médicos e odontólogos',
    '86009': 'Atividades de atenção à saúde humana não especificadas anteriormente',
    '87000': 'Atividades de assistência à saude humana integradas com assistencia social, inclusive prestadas em residencias',
    '88000': 'Serviços de assistência social sem alojamento',
    '90000': 'Atividades artísticas, criativas e de espetáculos',
    '91000': 'Atividades ligadas ao patrimônio cultural e ambiental',
    '92000': 'Atividades de exploração de jogos de azar e apostas',
    '93011': 'Atividades esportivas',
    '93012': 'Atividades de condicionamento físico',
    '93020': 'Atividades de recreação e lazer',
    '94010': 'Atividades de organizações associativas patronais, empresariais e profissionais',
    '94020': 'Atividades de organizações sindicais',
    '94091': 'Atividades de organizações religiosas e filosóficas',
    '94099': 'Outras atividades associativas não especificadas anteriormente',
    '95010': 'Reparação e manutenção de equipamentos de informática e comunicação',
    '95030': 'Reparação e manutenção de objetos e equipamentos pessoais e domésticos',
    '96010': 'Lavanderias, tinturarias e toalheiros',
    '96020': 'Cabeleireiros e outras atividades de tratamento de beleza',
    '96030': 'Atividades funerárias e serviços relacionados',
    '96090': 'Outras atividades de serviços pessoais',
    '97000': 'Serviços domésticos',
    '99000': 'Organismos internacionais e outras instituições extraterritoriais',
    '00000': 'Atividades mal definidas',
}

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
    df_final = None
 
if df_final is not None:
    # Classificação CNAE a partir de V4013
    print("Classificando CNAE (macro e micro)...")
    df_final['CNAE_MACRO'] = df_final['V4013'].str[:2].map(CNAE_MACRO).fillna('Não classificado')
    df_final['CNAE_MICRO'] = df_final['V4013'].map(CNAE_MICRO).fillna('Não classificado')
    print(f"Tamanho do DataFrame final: {df_final.shape[0]} linhas e {df_final.shape[1]} colunas.")
    print(df_final[['Ano', 'Trimestre']].value_counts(sort=False))
    print("\nExibindo as primeiras linhas (colunas CNAE incluídas):")
    print(df_final[['Ano', 'Trimestre', 'V4013', 'CNAE_MACRO', 'CNAE_MICRO']].head(10))
 
    csv = input("Deseja exportar o dataframe como um arquivo .csv? (0 para não e 1 para sim): ").strip()
    if csv == "1":
        df_final.to_csv("Banco_de_dados.csv", index=False, encoding='utf-8')
    else:
        print("Fim do código!")