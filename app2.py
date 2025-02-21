import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# === Charger les données ===
file_path = "GEURS25_France Special Questions_240827.xlsx"
xls = pd.ExcelFile(file_path)

df_results_overview = xls.parse("Results Overview")
df_results_overview = df_results_overview.dropna(subset=["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"])

# === Calcul de la matrice de corrélation ===
correlation_matrix = df_results_overview[["% Employabilité (QF1)", "% Collaboration (QF2)", "Brand \nIndex"]].corr()

# === Création du scatter plot ===
fig_scatter = px.scatter(
    df_results_overview,
    x="% Employabilité (QF1)", 
    y="% Collaboration (QF2)", 
    color="Brand \nIndex",  
    size="Brand \nIndex",  
    hover_name="University name in survey",  
    labels={"% Employabilité (QF1)": "Les étudiants avec les meilleures compétences",
            "% Collaboration (QF2)": "La meilleure collaboration avec les entreprises",
            "Brand \nIndex": "Réputation"},
    color_continuous_scale="RdBu"
)

# === Ajout des lignes moyennes ===
moyenne_employabilite = df_results_overview["% Employabilité (QF1)"].mean()
moyenne_collaboration = df_results_overview["% Collaboration (QF2)"].mean()

fig_scatter.add_vline(x=moyenne_employabilite, line_dash="dash", line_color="red", annotation_text="Moyenne Employabilité")
fig_scatter.add_hline(y=moyenne_collaboration, line_dash="dash", line_color="red", annotation_text="Moyenne Coopération")

# === Création de la heatmap de corrélation ===
column_labels = {
    "% Employabilité (QF1)": "Les étudiants avec les meilleures compétences",
    "% Collaboration (QF2)": "La meilleure collaboration avec les entreprises",
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
    width=600, height=500,
)

# === Initialisation de l'application Dash ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# === Mise en page avec Dash ===
app.layout = dbc.Container([
    html.H2("📊 Projection du Employability Ranking sur 71 Établissements Français", className="text-center mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_scatter), width=8),  # Scatter plot à gauche
        dbc.Col(dcc.Graph(figure=fig_heatmap), width=4)   # Heatmap à droite
    ])
], fluid=True)

# === Lancement de l'application ===
if __name__ == '__main__':
    app.run_server(debug=True)