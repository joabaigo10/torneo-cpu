import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG GOOGLE SHEETS ---
SHEET_NAME = "Torneo CPU"
RESULTS_SHEET = "resultados"
SCORERS_SHEET = "goleadores"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# abrir hoja resultados
try:
    ws_results = client.open(SHEET_NAME).worksheet(RESULTS_SHEET)
except:
    sh = client.open(SHEET_NAME)
    ws_results = sh.add_worksheet(title=RESULTS_SHEET, rows="1000", cols="10")
    ws_results.append_row(["Grupo", "Fecha", "Equipo", "GolesEquipo", "GolesCPU"])

# abrir hoja goleadores
try:
    ws_scorers = client.open(SHEET_NAME).worksheet(SCORERS_SHEET)
except:
    sh = client.open(SHEET_NAME)
    ws_scorers = sh.add_worksheet(title=SCORERS_SHEET, rows="1000", cols="10")
    ws_scorers.append_row(["Equipo", "Jugador", "Goles"])

# --- DATOS TORNEO ---
grupos = {
    "Grupo A": ["España", "México", "Australia", "Noruega", "Polonia", "Venezuela", "Ghana", "Albania"],
    "Grupo B": ["Francia", "Marruecos", "Austria", "Canadá", "Paraguay", "Nigeria", "Eslovenia", "Bosnia"],
    "Grupo C": ["Argentina", "Alemania", "Corea", "Suecia", "Escocia", "Costa de Marfil", "Islandia", "Angola"],
    "Grupo D": ["Inglaterra", "Uruguay", "Dinamarca", "Egipto", "Checa", "Zambia", "Jamaica", "Finlandia"],
    "Grupo E": ["Portugal", "Colombia", "Senegal", "Serbia", "Grecia", "Rumania", "Nueva Zelanda", "Gambia"],
    "Grupo F": ["Brasil", "Croacia", "Japón", "Ucrania", "Hungría", "Camerún", "Irlanda", "Guinea"],
    "Grupo G": ["Holanda", "Italia", "Ecuador", "Turquía", "Eslovaquia", "Mali", "Congo", "Haití"],
    "Grupo H": ["Bélgica", "Estados Unidos", "Suiza", "Gales", "Argelia", "Arabia", "Georgia", "Kosovo"]
}
fechas = [f"Fecha {i+1}" for i in range(7)]
cpu = "CPU"

# --- BANDERAS ---
def bandera_html(nombre):
    especiales = {
        "Escocia": "https://flagcdn.com/w20/gb-sct.png",
        "Gales": "https://flagcdn.com/w20/gb-wls.png",
        "Inglaterra": "https://flagcdn.com/w20/gb-eng.png",
        "Kosovo": "https://flagcdn.com/w20/xk.png"
    }
    if nombre in especiales:
        return f"<img src='{especiales[nombre]}' width='20'> {nombre}"

    codigos = {
        "España":"es","México":"mx","Australia":"au","Noruega":"no","Polonia":"pl","Venezuela":"ve","Ghana":"gh","Albania":"al",
        "Francia":"fr","Marruecos":"ma","Austria":"at","Canadá":"ca","Paraguay":"py","Nigeria":"ng","Eslovenia":"si","Bosnia":"ba",
        "Argentina":"ar","Alemania":"de","Corea":"kr","Suecia":"se","Costa de Marfil":"ci","Islandia":"is","Angola":"ao",
        "Uruguay":"uy","Dinamarca":"dk","Egipto":"eg","Checa":"cz","Zambia":"zm","Jamaica":"jm","Finlandia":"fi",
        "Portugal":"pt","Colombia":"co","Senegal":"sn","Serbia":"rs","Grecia":"gr","Rumania":"ro","Nueva Zelanda":"nz","Gambia":"gm",
        "Brasil":"br","Croacia":"hr","Japón":"jp","Ucrania":"ua","Hungría":"hu","Camerún":"cm","Irlanda":"ie","Guinea":"gn",
        "Holanda":"nl","Italia":"it","Ecuador":"ec","Turquía":"tr","Eslovaquia":"sk","Mali":"ml","Congo":"cd","Haití":"ht",
        "Bélgica":"be","Estados Unidos":"us","Suiza":"ch","Argelia":"dz","Arabia":"sa","Georgia":"ge",
    }
    code = codigos.get(nombre)
    if code:
        return f"<img src='https://flagcdn.com/w20/{code}.png' width='20'> {nombre}"
    elif nombre == "CPU":
        return f"🤖 {nombre}"
    return nombre

# --- FUNCIONES GOOGLE SHEETS ---
def guardar_resultado(grupo, fecha, equipo, goles_eq, goles_cpu):
    ws_results.append_row([grupo, fecha, equipo, goles_eq, goles_cpu])

def guardar_goleadores(equipo, jugadores):
    for j in jugadores:
        ws_scorers.append_row([equipo, j, 1])

def cargar_resultados():
    data = ws_results.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["Grupo","Fecha","Equipo","GolesEquipo","GolesCPU"])

def cargar_goleadores():
    data = ws_scorers.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["Equipo","Jugador","Goles"])

# --- APP ---
st.title("🏆 Torneo vs CPU (Google Sheets)")

grupo_sel = st.selectbox("Elegí un grupo", list(grupos.keys()))
fecha_sel = st.selectbox("Elegí una fecha", fechas)

st.write(f"### {grupo_sel} - {fecha_sel}")

# cargar datos ya existentes
df_res = cargar_resultados()
df_gol = cargar_goleadores()

# --- FORMULARIO DE PARTIDOS ---
for equipo in grupos[grupo_sel]:
    titulo = f"{bandera_html(equipo)} vs {bandera_html(cpu)}"

    # ver si ya existe este resultado en la hoja
    ya_cargado = ((df_res["Grupo"] == grupo_sel) & 
                  (df_res["Fecha"] == fecha_sel) & 
                  (df_res["Equipo"] == equipo)).any()

    cols = st.columns([2,1,1,1])
    if ya_cargado:
        cols[0].markdown(f"<div style='background-color:#f0f0f0;padding:4px;border-radius:4px'>{titulo}</div>", unsafe_allow_html=True)
    else:
        cols[0].markdown(f"**{titulo}**", unsafe_allow_html=True)

    g_eq = cols[1].number_input("",0,10,0,key=f"{grupo_sel}_{fecha_sel}_{equipo}_eq")
    g_cpu = cols[2].number_input("",0,10,0,key=f"{grupo_sel}_{fecha_sel}_{equipo}_cpu")

    if cols[3].button("💾", key=f"save_{grupo_sel}_{fecha_sel}_{equipo}"):
        if not ya_cargado:
            guardar_resultado(grupo_sel, fecha_sel, equipo, g_eq, g_cpu)
            st.success(f"✅ Guardado: {equipo} vs CPU {g_eq}-{g_cpu}", icon="⚽")
        else:
            st.warning("⚠️ Ya cargaste este partido.")

    with st.expander(f"Goleadores de {equipo}"):
        goles_txt = st.text_input("Jugadores", key=f"gol_{grupo_sel}_{fecha_sel}_{equipo}")
        if st.button("⚽ Guardar goleadores", key=f"save_gol_{grupo_sel}_{fecha_sel}_{equipo}"):
            if goles_txt.strip():
                jugadores = [j.strip() for j in goles_txt.split(",")]
                guardar_goleadores(equipo, jugadores)
                st.success("✅ Goleadores guardados")

# --- TABLA DE POSICIONES ---
st.subheader(f"📊 Tabla de {grupo_sel}")
if not df_res.empty and "Grupo" in df_res.columns:
    stats = {eq: {"PJ":0,"PG":0,"PE":0,"PP":0,"GF":0,"GC":0,"Pts":0} for eq in grupos[grupo_sel]}
    for _,r in df_res[df_res["Grupo"]==grupo_sel].iterrows():
        eq, gf, gc = r["Equipo"], r["GolesEquipo"], r["GolesCPU"]
        s = stats[eq]
        s["PJ"]+=1; s["GF"]+=gf; s["GC"]+=gc
        if gf>gc: s["PG"]+=1; s["Pts"]+=3
        elif gf==gc: s["PE"]+=1; s["Pts"]+=1
        else: s["PP"]+=1

    df = pd.DataFrame.from_dict(stats, orient="index")
    df["DG"]=df["GF"]-df["GC"]
    df = df.sort_values(by=["Pts","DG","GF"],ascending=[False,False,False]).reset_index().rename(columns={"index":"Equipo"})
    df.insert(0,"Pos",range(1,len(df)+1))
    df.insert(0," ",df["Pos"].apply(lambda p: f"<div style='width:4px;height:20px;background-color:{'#2ecc71' if p<=5 else '#e74c3c'}'></div>"))
    df["Equipo"]=df["Equipo"].apply(bandera_html)
    st.markdown(df[[" ","Pos","Equipo","Pts","PJ","PG","PE","PP","GF","GC","DG"]].to_html(escape=False,index=False), unsafe_allow_html=True)
else:
    st.info("Todavía no hay resultados cargados en este grupo.")

# --- RANKING GOLEADORES ---
st.subheader("⚽ Ranking de goleadores global")
if not df_gol.empty and "Equipo" in df_gol.columns:
    df_rank = df_gol.groupby(["Jugador","Equipo"])["Goles"].sum().reset_index().sort_values("Goles",ascending=False)
    df_rank["Equipo"] = df_rank["Equipo"].apply(bandera_html)
    st.markdown(df_rank.to_html(escape=False,index=False), unsafe_allow_html=True)
else:
    st.info("Todavía no hay goles cargados.")
