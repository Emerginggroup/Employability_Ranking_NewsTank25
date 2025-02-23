import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from io import BytesIO

# === Configuration de la page pour affichage pleine largeur ===
st.set_page_config(page_title="Classement Employabilité", layout="wide")

# === Style CSS pour forcer l'affichage à 100% ===
st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 100% !important; /* ✅ Étend tout le contenu */
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .custom-box {
            background-color: rgba(0, 123, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 2px 4px 12px rgba(0, 0, 0, 0.2);
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #003366;
            width: 100%;
            display: block;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# === Chargement du fichier Excel depuis GitHub ===
github_url = "https://raw.githubusercontent.com/Emerginggroup/Employability_Ranking_NewsTank25/main/GEURS25_France%20Special%20Questions_240827.xlsx"

try:
    response = requests.get(github_url)
    response.raise_for_status()
    excel_data = BytesIO(response.content)
    xls = pd.ExcelFile(excel_data)
    df_results_overview = xls.parse("Results Overview")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement du fichier Excel : {e}")
    st.stop()

# === Nettoyage des données ===
df_results_overview = df_results_overview.dropna(subset=["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"])

# === Remplacement des valeurs dans la colonne "Type" ===
df_results_overview["Type"] = df_results_overview["Type"].replace({
    "UNIV": "Université",
    "SCHOOL": "École"
})

# === Arrondir les valeurs à 2 décimales ===
df_results_overview["% Employabilité (QF1)"] = df_results_overview["% Employabilité (QF1)"].round(2)
df_results_overview["% Collaboration (QF2)"] = df_results_overview["% Collaboration (QF2)"].round(2)
df_results_overview["Brand \nIndex"] = df_results_overview["Brand \nIndex"].round(2)

# === Calcul de la matrice de corrélation ===
correlation_matrix = df_results_overview[["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"]].corr()

# === Création du Scatter Plot ===
fig_scatter = px.scatter(
    df_results_overview,
    x="% Employabilité (QF1)", 
    y="% Collaboration (QF2)", 
    color="Brand \nIndex",  
    size="Brand \nIndex",  
    hover_name="University name in survey",  
    labels={"% Employabilité (QF1)": "Compétences Étudiants",
            "% Collaboration (QF2)": "Collaboration Entreprise",
            "Brand \nIndex": "Réputation"},
    color_continuous_scale="RdBu",
    width=900, height=600
)
# === Ajout des lignes de moyenne ===
moyenne_employabilite = df_results_overview["% Employabilité (QF1)"].mean()
moyenne_collaboration = df_results_overview["% Collaboration (QF2)"].mean()

fig_scatter.add_vline(x=moyenne_employabilite, line_dash="dash", line_color="red", annotation_text="Moyenne Compétences")
fig_scatter.add_hline(y=moyenne_collaboration, line_dash="dash", line_color="red", annotation_text="Moyenne Collaboration")

# === Création de la Heatmap ===
column_labels = {
    "% Employabilité (QF1)": "Compétences Étudiants",
    "% Collaboration (QF2)": "Collaboration Entreprise",
    "Brand \nIndex": "Réputation"
}
correlation_matrix_renamed = correlation_matrix.rename(columns=column_labels, index=column_labels)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=correlation_matrix_renamed.values,
    x=correlation_matrix_renamed.columns,
    y=correlation_matrix_renamed.index,  
    colorscale="RdBu",  
    text=np.round(correlation_matrix_renamed.values, 2),  
    hoverinfo="text"
))

fig_heatmap.update_layout(
    width=500, height=400,
)

# === Interface Streamlit ===
st.title("📊 Classement des Établissements Français")

# === Sous-Titre avec Fond Bleu Transparent ===
st.markdown(
    """
    <div class="custom-box">
        L'Employability Ranking met en avant les établissements selon leur capacité 
        à former des étudiants aux meilleures compétences et à collaborer efficacement avec les entreprises.
    </div>
    """,
    unsafe_allow_html=True
)

# === Barre latérale pour les filtres ===
st.sidebar.header("Filtres")
selected_university = st.sidebar.selectbox("Sélectionner un établissement", ["Tous"] + df_results_overview["University name in survey"].unique().tolist())

# Appliquer le filtre
if selected_university != "Tous":
    df_results_overview = df_results_overview[df_results_overview["University name in survey"] == selected_university]

# === Sélection des colonnes pour affichage ===
df_display = df_results_overview[["University name in survey", "Type", "French Employability Ranking (50/50)", "Rang Employabilité (QF1)", "Rang Collaboration (QF2)"]]

# === Renommage des colonnes ===
df_display = df_display.rename(columns={
    "Rang Employabilité (QF1)": "Compétences Étudiants",
    "Rang Collaboration (QF2)": "Collaboration Entreprise",
    "French Employability Ranking (50/50)": "Score Final",
    "University name in survey": "Établissement"
})

# === Tri des établissements par "Score Final" ===
df_display = df_display.sort_values(by="Score Final", ascending=True)

# === Affichage du tableau des établissements sans indice ===
st.subheader("🏅 Performances des Établissements")
st.dataframe(df_display.reset_index(drop=True), hide_index=True)

# === Affichage du Scatter Plot et de la Heatmap en pleine largeur ===
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Visualisation des résultats")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Matrice de corrélation entre les variables")
    st.plotly_chart(fig_heatmap, use_container_width=True)
