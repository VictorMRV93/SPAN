
import pandas as pd
import os
import subprocess

# Caminho da pasta onde o script está sendo executado
caminho_pasta = os.path.dirname(os.path.abspath(__file__))

# Ler os arquivos
df_base = pd.read_excel(os.path.join(caminho_pasta, "Alocacao_Todos_Cenarios_Corrigido_AnalistaGI_EPL_OK.xlsx"))
df_clusters = pd.read_excel(os.path.join(caminho_pasta, "Tabelas_Projeto.xlsx"), sheet_name="TabelaCluster")

# Capacidade por cargo
capacidade = {
    "AUXILIAR APROVADOR": 10,
    "ANALISTA GI": 9
}

# DataFrame acumulador
df_completo = pd.DataFrame()

# Iterar sobre os cenários
for cenario in df_base["Cenário"].unique():
    df_cenario = df_base[df_base["Cenário"] == cenario].copy()
    df_cenario = df_cenario[~df_cenario["Cargo"].isin(["CONSULTOR MO", "CONSULTOR MAT"])]  # Remove consultores MO/MAT

    regionais = df_cenario["Regional"].unique()

    novos_regionais = []
    for reg in regionais:
        novos_regionais.extend([
            (reg, "Todos da Regional", 0, "Reports", "ANALISTA DE REPORTS", 1, cenario),
            (reg, "Todos da Regional", 0, "Suporte", "COORDENADOR DE SUPORTE", 1, cenario)
        ])

    novos_clusters = []
    for _, row in df_clusters.iterrows():
        regional = row["Regional"]
        cluster = row["CLUSTER CORRIGID"]
        obras = row["Obras"]

        qtd_aprovador = obras // capacidade["AUXILIAR APROVADOR"] + (1 if obras % capacidade["AUXILIAR APROVADOR"] > 0 else 0)
        qtd_gi = obras // capacidade["ANALISTA GI"] + (1 if obras % capacidade["ANALISTA GI"] > 0 else 0)

        novos_clusters.extend([
            (regional, cluster, obras, "Aprovação", "AUXILIAR APROVADOR", qtd_aprovador, cenario),
            (regional, cluster, obras, "GI", "ANALISTA GI", qtd_gi, cenario),
        ])

    df_novos = pd.DataFrame(novos_regionais + novos_clusters, columns=df_cenario.columns)
    df_cenario_final = pd.concat([df_cenario, df_novos], ignore_index=True)
    df_completo = pd.concat([df_completo, df_cenario_final], ignore_index=True)

# Exportar
nome_saida = "Alocacao_Todos_Cenarios_Sem_EPL.xlsx"
caminho_saida = os.path.join(caminho_pasta, nome_saida)
df_completo.to_excel(caminho_saida, index=False)

# Abrir Excel automaticamente
subprocess.run(["start", "excel", caminho_saida], shell=True)
print(f"Arquivo gerado com sucesso: {caminho_saida}")
