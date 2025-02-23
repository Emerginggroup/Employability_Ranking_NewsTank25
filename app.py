import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from io import BytesIO

# === Load Excel File from GitHub ===
github_url = "https://raw.githubusercontent.com/Emerginggroup/Employability_Ranking_NewsTank25/main/GEURS25_France%20Special%20Questions_240827.xlsx"

try:
    response = requests.get(github_url)
    response.raise_for_status()  # Raise an error if the request fails
    excel_data = BytesIO(response.content)  # Convert the content into a file-like object
    xls = pd.ExcelFile(excel_data)
    df_results_overview = xls.parse("Results Overview")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement du fichier Excel : {e}")
    st.stop()

# === Suppression des valeurs manquantes ===
df_results_overview = df_results_overview.dropna(subset=["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"])

# === Calcul de la matrice de corrélation ===
correlation_matrix = df_results_overview[["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"]].corr()

# === Remplacement des valeurs dans la colonne "Type" ===
df_results_overview["Type"] = df_results_overview["Type"].replace({
    "UNIV": "Université",
    "SCHOOL": "École"
})

# === Arrondir les colonnes concernées à 2 décimales ===
df_results_overview["% Employabilité (QF1)"] = df_results_overview["% Employabilité (QF1)"].round(2)
df_results_overview["% Collaboration (QF2)"] = df_results_overview["% Collaboration (QF2)"].round(2)
df_results_overview["Brand \nIndex"] = df_results_overview["Brand \nIndex"].round(2)

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
    color_continuous_scale="RdBu"
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
    width=400, height=300,
)

# === Interface Streamlit ===
# === Titre Principal ===
st.title("📊 Classement des Établissements Français")

# === Sous-Titre Stylisé avec Fond Bleu Transparent et Bordures Arrondies ===
st.markdown(
    """
    <style>
        .custom-box {
            background-color: rgba(0, 123, 255, 0.1); /* ✅ Fond bleu transparent */
            padding: 20px; /* ✅ Plus grand espace interne */
            border-radius: 12px; /* ✅ Bords arrondis */
            box-shadow: 2px 4px 12px rgba(0, 0, 0, 0.2); /* ✅ Effet d’ombre */
            text-align: left;
            font-size: 18px;
            font-weight: bold;
            color: #003366; /* ✅ Bleu foncé pour contraste */
            width: 100%;
            display: block;
        }
    </style>
    <div class="custom-box">
        L'Employability Ranking met en avant les établissements selon leur capacité 
        à former des étudiants aux meilleures compétences et à collaborer efficacement avec les entreprises.
    </div>
    """,
    unsafe_allow_html=True
)

# Barre latérale pour les filtres
st.sidebar.header("Filtres")
selected_university = st.sidebar.selectbox("Sélectionner un établissement", ["Tous"] + df_results_overview["University name in survey"].unique().tolist())

# Filtrer les données (si un établissement est sélectionné)
if selected_university != "Tous":
    df_results_overview = df_results_overview[df_results_overview["University name in survey"] == selected_university]

# Sélectionner les colonnes spécifiques pour affichage
df_display = df_results_overview[["University name in survey", "Type", "French Employability Ranking (50/50)", "Rang Employabilité (QF1)", "Rang Collaboration (QF2)"]]

# Renommer les colonnes
df_display = df_display.rename(columns={
    "Rang Employabilité (QF1)": "Compétences Étudiants",
    "Rang Collaboration (QF2)": "Collaboration Entreprise",
    "French Employability Ranking (50/50)": "Score Final",
    "University name in survey": "Établissement"
})

# Appliquer un tri croissant basé sur "Score Final"
df_display = df_display.sort_values(by="Score Final", ascending=True)

# Affichage des données triées par Score Final sans l'indice
st.subheader("🏅 Performances des Établissements")
st.dataframe(df_display.reset_index(drop=True), hide_index=True)



# Affichage du Scatter Plot et de la Heatmap
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Visualisation des résultats")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Matrice de corrélation entre les variables")
    st.plotly_chart(fig_heatmap, use_container_width=True)
