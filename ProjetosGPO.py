import pandas as pd
import streamlit as st
from io import BytesIO

st.title("📊 Alocação de Cargos")

# Upload de arquivos
df_base_file = st.file_uploader("📎 Envie o arquivo de alocação", type=["xlsx"])
df_clusters_file = st.file_uploader("📎 Envie o arquivo de clusters (Tabelas_Projeto.xlsx)", type=["xlsx"])

if df_base_file and df_clusters_file:
    df_base = pd.read_excel(df_base_file)
    df_clusters = pd.read_excel(df_clusters_file, sheet_name="TabelaCluster")

    # Capacidade por cargo (sem EPL)
    capacidade = {
        "AUXILIAR APROVADOR": 10,
        "ANALISTA GI": 9
    }

    df_completo = pd.DataFrame()

    for cenario in df_base["Cenário"].unique():
        df_cenario = df_base[df_base["Cenário"] == cenario].copy()
        df_cenario = df_cenario[~df_cenario["Cargo"].isin(["CONSULTOR MO", "CONSULTOR MAT"])]

        regionais = df_cenario["Regional"].unique()

        novos_regionais = [
            (reg, "Todos da Regional", 0, "Reports", "ANALISTA DE REPORTS", 1, cenario)
            for reg in regionais
        ] + [
            (reg, "Todos da Regional", 0, "Suporte", "COORDENADOR DE SUPORTE", 1, cenario)
            for reg in regionais
        ]

        novos_clusters = []
        for _, row in df_clusters.iterrows():
            regional = row["Regional"]
            cluster = row["CLUSTER CORRIGID"]
            obras = row["Obras"]

            qtd_aprovador = -(-obras // capacidade["AUXILIAR APROVADOR"])  # arredondamento para cima
            qtd_gi = -(-obras // capacidade["ANALISTA GI"])

            novos_clusters.extend([
                (regional, cluster, obras, "Aprovação", "AUXILIAR APROVADOR", qtd_aprovador, cenario),
                (regional, cluster, obras, "GI", "ANALISTA GI", qtd_gi, cenario)
            ])

        df_novos = pd.DataFrame(novos_regionais + novos_clusters, columns=df_cenario.columns)
        df_cenario_final = pd.concat([df_cenario, df_novos], ignore_index=True)
        df_completo = pd.concat([df_completo, df_cenario_final], ignore_index=True)

    # Mostrar dados
    st.success("✅ Processamento concluído!")
    st.write("📄 Resultado da alocação:")
    st.dataframe(df_completo)

    # Download
    output = BytesIO()
    df_completo.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Baixar resultado", data=output.getvalue(), file_name="Alocacao_Todos_Cenarios_Sem_EPL.xlsx")

else:
    st.warning("⚠️ Por favor, envie os dois arquivos para começar.")
