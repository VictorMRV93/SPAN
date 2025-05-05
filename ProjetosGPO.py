import pandas as pd
import streamlit as st
from io import BytesIO

st.title("📊 Alocação de Cargos por Cenário")

# Upload dos arquivos
df_base_file = st.file_uploader("📎 Envie o arquivo de alocação", type=["xlsx"])
df_clusters_file = st.file_uploader("📎 Envie o arquivo de clusters (Tabelas_Projeto.xlsx)", type=["xlsx"])

if df_base_file and df_clusters_file:
    df_base = pd.read_excel(df_base_file)
    df_clusters = pd.read_excel(df_clusters_file, sheet_name="TabelaCluster")

    # Capacidades padrão
    capacidade_gi = 9
    capacidade_aprovador = 10
    capacidade_mo_mat = 10
    capacidade_urb = 10

    # Tolerância por cenário para MO e MAT
    tolerancia_mo_mat = {
        "Cenário Sensível P&C/URB/HBT": 1.2,
        "Cenário Múltiplos Sem Sensibilidade": 1.0,
        "Cenário Sensível Todos Cargos": 1.0
    }

    df_completo = pd.DataFrame()

    for cenario in df_base["Cenário"].unique():
        df_cenario = df_base[df_base["Cenário"] == cenario].copy()

        # Remover EPL e substituir consultores MO/MAT
        df_cenario = df_cenario[~df_cenario["Cargo"].str.contains("EPL", na=False)]
        df_cenario["Cargo"] = df_cenario["Cargo"].replace({
            "CONSULTOR MO": "ANALISTA MO",
            "CONSULTOR MAT": "ANALISTA MAT"
        })

        # Tratar URB como regional
        df_cenario.loc[df_cenario["Cargo"].isin(["CONSULTOR URB", "ANALISTA URB"]), "Cluster"] = "Todos da Regional"

        regionais = df_cenario["Regional"].unique()
        novos_regionais = []

        for reg in regionais:
            obras_reg = df_clusters[df_clusters["Regional"] == reg]["Obras"].sum()
            cap_mo = capacidade_mo_mat * tolerancia_mo_mat[cenario]
            cap_mat = capacidade_mo_mat * tolerancia_mo_mat[cenario]
            qtd_mo = obras_reg // cap_mo + (1 if obras_reg % cap_mo > 0 else 0)
            qtd_mat = obras_reg // cap_mat + (1 if obras_reg % cap_mat > 0 else 0)
            qtd_aprovador = obras_reg // capacidade_aprovador + (1 if obras_reg % capacidade_aprovador > 0 else 0)
            qtd_urb = obras_reg // capacidade_urb + (1 if obras_reg % capacidade_urb > 0 else 0)

            novos_regionais.extend([
                (reg, "Todos da Regional", obras_reg, "Reports", "ANALISTA DE REPORTS", 1, cenario),
                (reg, "Todos da Regional", obras_reg, "Suporte", "COORDENADOR DE SUPORTE", 1, cenario),
                (reg, "Todos da Regional", obras_reg, "Aprovação", "AUXILIAR APROVADOR", int(qtd_aprovador), cenario),
                (reg, "Todos da Regional", obras_reg, "MO", "ANALISTA MO", int(qtd_mo), cenario),
                (reg, "Todos da Regional", obras_reg, "MAT", "ANALISTA MAT", int(qtd_mat), cenario),
                (reg, "Todos da Regional", obras_reg, "URB", "CONSULTOR URB", int(qtd_urb), cenario),
                (reg, "Todos da Regional", obras_reg, "URB", "ANALISTA URB", int(qtd_urb), cenario)
            ])

        # Cálculo por cluster apenas para ANALISTA GI
        novos_clusters = []
        for _, row in df_clusters.iterrows():
            regional = row["Regional"]
            cluster = row["CLUSTER CORRIGID"]
            obras = row["Obras"]
            qtd_gi = -(-obras // capacidade_gi)
            novos_clusters.append((regional, cluster, obras, "GI", "ANALISTA GI", qtd_gi, cenario))

        # Unir regionais e clusters
        df_novos = pd.DataFrame(novos_regionais + novos_clusters, columns=df_cenario.columns)
        df_cenario_final = pd.concat([df_cenario, df_novos], ignore_index=True)

        # Remover duplicatas internas por cargo/cenário/localização
        df_cenario_final = (
            df_cenario_final
            .sort_values("Quantidade", ascending=False)
            .drop_duplicates(subset=["Regional", "Cluster", "Cargo", "Cenário"], keep="first")
        )

        df_completo = pd.concat([df_completo, df_cenario_final], ignore_index=True)

    st.success("✅ Processamento concluído!")
    st.write("📄 Resultado final da alocação:")
    st.dataframe(df_completo)

    # Download
    output = BytesIO()
    df_completo.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Baixar resultado", data=output.getvalue(), file_name="Alocacao_Cenarios_Final.xlsx")

else:
    st.warning("⚠️ Por favor, envie os dois arquivos para começar.")
