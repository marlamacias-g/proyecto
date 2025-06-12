import logging
from typing import Tuple
import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
import base64
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

COLORS = {
    'primary': '#C51D34',
    'secondary': '#F5F5F5',
    'accent': '#8B1538',
    'light_red': '#E85A70',
    'dark_gray': '#2C3E50',
    'success': '#27AE60',
    'warning': '#F39C12',
    'info': '#3498DB',
    'white': '#FFFFFF'
}
def datoss() -> Tuple[pd.DataFrame, pd.DataFrame]:
    try:
        ruta = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = ruta["LasEstadisticasMundial"]
        losequipos = pd.DataFrame(list(db["goles_por_equipo"].find()))
        goleadores = pd.DataFrame(list(db["goleadores_mundiales"].find()))
        # Eliminar campo _id
        for df in (losequipos, goleadores):
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)
            df["G"] = pd.to_numeric(df["G"], errors="coerce")
            df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
        logger.info("Datos cargados desde MongoDB")
        return losequipos, goleadores
    except Exception as e:
        logger.error(f"Error conectando a MongoDB: {e}")
        losequipos = pd.DataFrame({
            'Equipo': ['Brasil','Alemania','Argentina','España','Francia'],
            'Año': [2022]*5,
            'G': [8,7,6,5,4]
        })
        goleadores = pd.DataFrame({
            'Jugador': ['Messi','Mbappé','Giroud','Álvarez','Gakpo'],
            'Equipo': ['Argentina','Francia','Francia','Argentina','Países Bajos'],
            'Año': [2022]*5,
            'G': [7,8,4,4,3]
        })
        return losequipos, goleadores
losequipos, goleadores = datoss()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/style.css"]
)
def create_metric_card(title: str, value: str, icon: str, color: str = COLORS['primary']):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([html.I(className=f"fas fa-{icon} fa-2x", style={'color': color})],
                         className="metric-icon"),
                html.Div([
                    html.H3(value, className="metric-value"),
                    html.P(title, className="metric-title")
                ], className="metric-content")
            ], className="metric-card-inner")
        ])
    ], className="metric-card")

def elheader(title: str, subtitle: str = None):
    return html.Div([
        html.H2(title, className="section-main-title"),
        html.P(subtitle, className="section-subtitle") if subtitle else None,
        html.Div(className="section-divider")
    ], className="section-header")

# — Layout Principal —
app.layout = html.Div([

    html.Div(
        className="about-us-section",
        style={
            "backgroundColor": "#6D0C2E",
            "padding": "60px 0"
        },
        children=[
            html.H1(
                "EstadistiGOL",
                style={"color": "#FFFFFF", "textAlign": "center"}
            ),
            html.P(
                "Estadísticas del mundial que marcaron en la historia",
                style={"color": "#FFFFFF", "textAlign": "center"}
            ),
        ]
    ),
    html.Div(className="hero-section", children=[
        html.Div(className="hero-overlay"),
        html.Div(className="hero-container", children=[
            html.Div(className="hero-content", children=[
                html.H1("ESTADÍSTICAS  MUNDIAL", className="hero-title"),
                html.P("Analisis de los datos referentes a los mundiales pasados", className="hero-subtitle"),
                html.Div([
                    html.Span("🏆", className="hero-emoji"),
                    html.Span("⚽", className="hero-emoji"),
                    html.Span("📊", className="hero-emoji"),
                ], className="hero-emojis")
            ])
        ])
    ]),

    dbc.Container(fluid=True, className="description-section", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("📊 DASHBOARD INTERACTIVO DE ESTADÍSTICAS FIFA WORLD CUP 🏆",
                                className="description-title"),
                        html.Hr(className="description-divider"),
                        html.P([
                            "Este proyecto consta de ", html.Strong("2 dashboards"),
                            " de análisis interactivo, desarrollado con ", html.Strong("Dash"),
                            ", ", html.Strong("Plotly"), " y ", html.Strong("MongoDB"),
                            ", que permite explorar de manera visual y dinámica las estadísticas históricas más relevantes de la Copa Mundial de la FIFA."
                        ], className="description-text"),

                        html.H4("🧠 FUNCIONALIDADES DESTACADAS:", className="description-subtitle"),
                        html.Ul([
                            html.Li("Análisis por año de las selecciones más goleadoras en cada Mundial."),
                            html.Li(
                                "Visualización de los máximos goleadores por torneo, con múltiples filtros y comparativas."),
                            html.Li(
                                "Gráficos dinámicos: barras, líneas, mapas de calor, treemaps, radar charts y más."),
                            html.Li("Tablas detalladas para consulta de datos específicos."),
                            html.Li("Sección de datos curiosos que resaltan momentos históricos únicos del torneo."),
                            html.Li("Diseño moderno, responsivo y visualmente atractivo.")
                        ], className="description-list"),

                        html.H4("💾 FUENTE DE DATOS:", className="description-subtitle"),
                        html.P([
                            "Los datos son obtenidos desde una base de datos MongoDB con dos colecciones principales: ",
                            html.Code("goles_por_equipo"), " y ", html.Code("goleadores_mundiales"), "."
                        ], className="description-text"),

                        html.H4("🎯 OBJETIVO:", className="description-subtitle"),
                        html.P(
                            "Ofrecer una herramienta educativa, informativa y entretenida para todos los fanáticos del fútbol.",
                            className="description-text")
                    ])
                ], className="description-card")
            ], md=12)
        ])
    ]),

dbc.Container(fluid=True, className="feature-section", children=[
    dbc.Row([
        dbc.Col(
            html.Img(
                src="C:/Users/mg_ma/PycharmProjects/pythonProject/templates/.venv/share/assets/messi_copa.jpg",
                style={"width": "100%", "borderRadius": "8px"}
            ),
            md=6
        ),
        dbc.Col(
            html.Div([
                html.H3("Visión general del Campeonato"),
                html.P(
                    "Los dashboards sintetizan datos históricos de goles, equipos y estadísticas clave, "
                    "facilitando la toma de decisiones y la comparación de rendimientos."
                )
            ], style={"padding": "20px"}),
            md=6
        )
    ], align="center", style={"margin": "60px 0"}),
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H3("Cobertura de Momentos Clave"),
                html.P(
                    "Con gráficos interactivos puedes seguir cada jugada importante y entender "
                    "cómo influyen en el resultado global del torneo."
                )
            ], style={"padding": "20px"}),
            md=6
        ),
        dbc.Col(
            html.Img(
                src="C:/Users/mg_ma/PycharmProjects/pythonProject/templates/.venv/share/assets/portada.jpg",
                style={"width": "100%", "borderRadius": "8px"}
            ),
            md=6
        )
    ], align="center", style={"margin": "60px 0"}),
]),


    # === MÉTRICAS GENERALES ===
    dbc.Container(fluid=True, className="metrics-section", children=[
        dbc.Row(className="metrics-row", children=[
            dbc.Col(create_metric_card("Mundiales Analizados", "21", "trophy"), md=3),
            dbc.Col(create_metric_card("Países Participantes", "200+", "flag", COLORS['info']), md=3),
            dbc.Col(create_metric_card("Goles Registrados", "2,500+", "futbol", COLORS['success']), md=3),
            dbc.Col(create_metric_card("Leyendas del Fútbol", "1,000+", "star", COLORS['warning']), md=3),
        ])
    ]),

    dbc.Container(fluid=True, className="analysis-section", children=[
        elheader(
            "🏆 ANÁLISIS DE EQUIPOS GOLEADORES",
            "Descubre qué selecciones han dominado en cada Mundial"
        ),
        # Controles
        dbc.Row(className="controls-row", children=[
            dbc.Col(md=4, children=[
                html.Div(className="control-container", children=[
                    html.Label("📅 Selecciona el Mundial:", className="control-label"),
                    dcc.Dropdown(
                        id="anio-equipos",
                        options=[{"label": f"Mundial {a}", "value": a} for a in sorted(losequipos["Año"].unique())],
                        value=max(losequipos["Año"].unique()),
                        clearable=False, className="custom-dropdown"
                    )
                ])
            ]),
            dbc.Col(md=4, children=[
                html.Div(className="control-container", children=[
                    html.Label("📊 Tipo de Vista:", className="control-label"),
                    dcc.RadioItems(
                        id="vista-equipos",
                        options=[
                            {"label": "Top 10", "value": "top10"},
                            {"label": "Todos", "value": "todos"}
                        ],
                        value="top10", inline=True, className="custom-radio"
                    )
                ])
            ])
        ]),
        # 4 Gráficas
        dbc.Row(className="dashboard-row", children=[
            dbc.Col(dbc.Card([dbc.CardHeader("Ranking de Goleadores"), dbc.CardBody(dcc.Graph(id="bar-equipos"))],
                            className="dashboard-card"), md=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Distribución de Goles"), dbc.CardBody(dcc.Graph(id="pie-equipos"))],
                            className="dashboard-card"), md=6),
        ]),
        dbc.Row(className="dashboard-row", children=[
            dbc.Col(dbc.Card([dbc.CardHeader("Evolución Histórica"), dbc.CardBody(dcc.Graph(id="heatmap-equipos"))],
                            className="dashboard-card"), md=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Tendencia Temporal"), dbc.CardBody(dcc.Graph(id="line-equipos"))],
                            className="dashboard-card"), md=6),
        ]),
        # Tabla
        dbc.Row(className="table-row", children=[
            dbc.Col(dbc.Card([
                dbc.CardHeader("Datos Detallados"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="tabla-equipos",
                        columns=[{"name": "Equipo", "id": "Equipo"},
                                 {"name": "Año", "id": "Año"},
                                 {"name": "Goles", "id": "G"}],
                        data=[], page_size=10,
                        style_table={"overflowX": "auto"},
                        style_header={"backgroundColor": COLORS['primary'], "color": "white", "textAlign": "center"},
                        style_cell={"padding": "12px", "textAlign": "center"},
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': COLORS['secondary']}]
                    )
                ])
            ], className="table-card"), md=12)
        ])
    ]),

    html.Hr(className="section-separator"),

    dbc.Container(fluid=True, className="analysis-section", children=[
        elheader(
            "⚽ ANÁLISIS DE GOLEADORES HISTÓRICOS",
            "Los máximos artilleros que han marcado la historia del fútbol"
        ),
        # Controles
        dbc.Row(className="controls-row", children=[
            dbc.Col(md=4, children=[
                html.Div(className="control-container", children=[
                    html.Label("📅 Selecciona el Mundial:", className="control-label"),
                    dcc.Dropdown(
                        id="anio-goleadores",
                        options=[{"label": f"Mundial {a}", "value": a} for a in sorted(goleadores["Año"].unique())],
                        value=max(goleadores["Año"].unique()),
                        clearable=False, className="custom-dropdown"
                    )
                ])
            ]),
            dbc.Col(md=8, children=[
                html.Div(className="control-container", children=[
                    html.Label("🎯 Filtro por Goles:", className="control-label"),
                    dcc.RangeSlider(
                        id="goles-range",
                        min=0, max=int(goleadores["G"].max()), step=1,
                        marks={i: str(i) for i in range(0, int(goleadores["G"].max())+1, 2)},
                        value=[0, int(goleadores["G"].max())],
                        className="custom-slider"
                    )
                ])
            ])
        ]),
        # 4 Gráficas
        dbc.Row(className="dashboard-row", children=[
            dbc.Col(dbc.Card([dbc.CardHeader("Top Goleadores"), dbc.CardBody(dcc.Graph(id="bar-goleadores"))],
                            className="dashboard-card"), md=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Goles por País"), dbc.CardBody(dcc.Graph(id="treemap-goleadores"))],
                            className="dashboard-card"), md=6),
        ]),
        dbc.Row(className="dashboard-row", children=[
            dbc.Col(dbc.Card([dbc.CardHeader("Comparativa Top 5"), dbc.CardBody(dcc.Graph(id="radar-goleadores"))],
                            className="dashboard-card"), md=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Rendimiento Individual"), dbc.CardBody(dcc.Graph(id="scatter-goleadores"))],
                            className="dashboard-card"), md=6),
        ]),
        # Tabla
        dbc.Row(className="table-row", children=[
            dbc.Col(dbc.Card([
                dbc.CardHeader("Ranking Completo"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="tabla-goleadores",
                        columns=[{"name": "Jugador", "id": "Jugador"},
                                 {"name": "Equipo", "id": "Equipo"},
                                 {"name": "Goles", "id": "G"},
                                 {"name": "Año", "id": "Año"}],
                        data=[], page_size=12,
                        style_table={"overflowX": "auto"},
                        style_header={"backgroundColor": COLORS['primary'], "color": "white", "textAlign": "center"},
                        style_cell={"padding": "12px", "textAlign": "center"},
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': COLORS['secondary']}]
                    )
                ])
            ], className="table-card"), md=12)
        ])
    ]),

    html.Hr(className="section-separator"),
dbc.Container(fluid=True, className="feature-section", children=[
    dbc.Row([
        dbc.Col(
            html.Img(
                src="C:/Users/mg_ma/PycharmProjects/pythonProject/templates/.venv/share/assets/portero_pateando_pelota.jpg",
                style={"width": "100%", "borderRadius": "8px"}
            ),
            md=6
        ),
        dbc.Col(
            html.Div([
                html.H3("Análisis de Rendimiento Individual"),
                html.P(
                    "El desglose por jugador permite identificar fortalezas y áreas de mejora, "
                    "comparando estadísticas de pases, tiros y atajadas."
                )
            ], style={"padding": "20px"}),
            md=6
        )
    ], align="center", style={"margin": "60px 0"}),
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H3("Perspectiva Estratégica"),
                html.P(
                    "Los dashboards convierten datos detallados en información accionable, permitiendo identificar rápidamente tendencias y oportunidades para optimizar el rendimiento."
                )
            ], style={"padding": "20px"}),
            md=6
        ),
        dbc.Col(
            html.Img(
                src="abrazo_brazil.gif",
                style={"width": "100%", "borderRadius": "8px"}
            ),
            md=6
        )
    ], align="center", style={"margin": "60px 0"})

]),
    dbc.Container(fluid=True, className="facts-section", children=[
        elheader(
            "🎯 DATOS CURIOSOS DEL MUNDIAL",
            "Los momentos más increíbles de la historia"
        ),
        dbc.Row(className="facts-row", children=[
            dbc.Col(dbc.Card(className="fact-card-modern", children=[
                dbc.CardBody(html.Div(className="fact-content", children=[
                    html.I(className="fas fa-rocket fa-3x", style={'color': COLORS['primary']}),
                    html.H4("Primer Gol Histórico", className="fact-title"),
                    html.P("Lucien Laurent (Francia) anotó el primer gol en Uruguay 1930 vs México.", className="fact-text")
                ]))
            ]), md=4),
            dbc.Col(dbc.Card(className="fact-card-modern", children=[
                dbc.CardBody(html.Div(className="fact-content", children=[
                    html.I(className="fas fa-fire fa-3x", style={'color': COLORS['warning']}),
                    html.H4("Mayor Goleada", className="fact-title"),
                    html.P("Hungría 10–1 El Salvador (España 1982) la mayor goleada registrada.", className="fact-text")
                ]))
            ]), md=4),
            dbc.Col(dbc.Card(className="fact-card-modern", children=[
                dbc.CardBody(html.Div(className="fact-content", children=[
                    html.I(className="fas fa-bolt fa-3x", style={'color': COLORS['info']}),
                    html.H4("Gol más Rápido", className="fact-title"),
                    html.P("Bryan Robson anotó a los 27s contra Francia en España 1982.", className="fact-text")
                ]))
            ]), md=4),
        ]),
        dbc.Row(className="facts-row", children=[
            dbc.Col(dbc.Card(className="fact-card-modern", children=[
                dbc.CardBody(html.Div(className="fact-content", children=[
                    html.I(className="fas fa-crown fa-3x", style={'color': COLORS['success']}),
                    html.H4("El Rey Pelé", className="fact-title"),
                    html.P("Pelé es el único tricampeón: 1958, 1962 y 1970.", className="fact-text")
                ]))
            ]), md=6),
            dbc.Col(dbc.Card(className="fact-card-modern", children=[
                dbc.CardBody(html.Div(className="fact-content", children=[
                    html.I(className="fas fa-trophy fa-3x", style={'color': COLORS['primary']}),
                    html.H4("Campeones Históricos", className="fact-title"),
                    html.P("Brasil (5), Alemania (4), Italia (4), Argentina (3), Uruguay (2)…", className="fact-text")
                ]))
            ]), md=6),
        ])
    ]),

    html.Footer(className="footer", children=[
        html.Div(className="footer-content", children=[
            html.P("Marla Macias Gonzalez 2025 ", className="footer-text")
        ])
    ])
])

@app.callback(
    [Output("bar-equipos", "figure"),
     Output("pie-equipos", "figure"),
     Output("heatmap-equipos", "figure"),
     Output("line-equipos", "figure"),
     Output("tabla-equipos", "data")],
    [Input("anio-equipos", "value"), Input("vista-equipos", "value")]
)
def actualizar_equipos(año: int, vista: str):
    df_año = losequipos[losequipos["Año"] == año].sort_values("G", ascending=False)
    df_mostrar = df_año.head(10) if vista == "top10" else df_año

    fig_bar = px.bar(df_mostrar, x="Equipo", y="G", title=f"Goles por Equipo - Mundial {año}",
                     color_continuous_scale=[COLORS['light_red'], COLORS['primary']], text="G")
    fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color=COLORS['dark_gray'])
    fig_bar.update_traces(textposition='outside')

    fig_pie = px.pie(df_mostrar.head(8), names="Equipo", values="G", title="Distribución de Goles")
    fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          font_color=COLORS['dark_gray'])

    pivot = losequipos.pivot_table(index="Equipo", columns="Año", values="G", aggfunc="sum", fill_value=0)
    fig_heat = px.imshow(pivot, title="Evolución Histórica de Goles")
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           font_color=COLORS['dark_gray'])

    df_temp = losequipos.groupby("Año")["G"].sum().reset_index()
    fig_line = px.line(df_temp, x="Año", y="G", title="Tendencia Total de Goles", markers=True)
    fig_line.update_traces(line_color=COLORS['primary'], marker_color=COLORS['primary'])
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            font_color=COLORS['dark_gray'])

    return fig_bar, fig_pie, fig_heat, fig_line, df_mostrar.to_dict("records")

@app.callback(
    [Output("bar-goleadores","figure"),
     Output("treemap-goleadores","figure"),
     Output("radar-goleadores","figure"),
     Output("scatter-goleadores","figure"),
     Output("tabla-goleadores","data")],
    [Input("anio-goleadores","value"), Input("goles-range","value")]
)
def actualizar_goleadores(año: int, rng: list):
    df_año = goleadores[(goleadores["Año"]==año)&
                           (goleadores["G"]>=rng[0])&(goleadores["G"]<=rng[1])].sort_values("G", ascending=False)

    fig1 = px.bar(df_año.head(10), x="Jugador", y="G", color="Equipo",
                  title=f"Top Goleadores - Mundial {año}", text="G")
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       font_color=COLORS['dark_gray'])
    fig1.update_traces(textposition='outside')

    df_eq_sum = df_año.groupby("Equipo")["G"].sum().reset_index()
    fig2 = px.treemap(df_eq_sum, path=["Equipo"], values="G",
                      title="Goles por País")
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       font_color=COLORS['dark_gray'])

    top5 = df_año.head(5)
    fig3 = go.Figure()
    for _, row in top5.iterrows():
        fig3.add_trace(go.Scatterpolar(
            r=[row["G"]]*5,
            theta=["Goles","Goles","Goles","Goles","Goles"],
            fill='toself', name=row["Jugador"]
        ))
    fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(df_año["G"])])),
                       title="Comparativa Top 5")

    fig4 = px.scatter(df_año, x="G", y="Jugador", size="G", color="Equipo",
                      title="Rendimiento Individual")
    fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                       font_color=COLORS['dark_gray'])

    return fig1, fig2, fig3, fig4, df_año.head(15).to_dict("records")
if __name__ == "__main__":
    app.run(debug=True)
