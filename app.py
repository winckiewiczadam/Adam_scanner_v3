"""
Adam Scanner v1 — Single File App
Wszystko w jednym pliku, bez folderu pages/
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json, os, re, time, datetime, warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Adam Scanner v1",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp,[data-testid="stAppViewContainer"]{background:#0d0f14!important;color:#e2e6f0!important}
header[data-testid="stHeader"]{background:#0d0f14!important;border-bottom:1px solid #1e2230}
[data-testid="stToolbar"]{background:#0d0f14!important}
#MainMenu{visibility:hidden}
footer{visibility:hidden}
section[data-testid="stSidebar"]{background:#111318!important;border-right:1px solid #1e2230}
section[data-testid="stSidebar"] *{color:#e2e6f0!important}
section[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:13px!important;padding:6px 0!important}
.stButton>button{background:#6c8eff!important;color:#fff!important;border:none!important;border-radius:7px!important;font-weight:700!important}
[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input,.stTextArea textarea,.stSelectbox>div>div{background:#1e2230!important;color:#e2e6f0!important;border:1px solid #252a3a!important;border-radius:6px!important}
/* Fix nieczytelnych labelow filtrow */
label[data-testid="stWidgetLabel"] p{color:#c8cfe0!important;font-size:12px!important;font-weight:600!important}
label[data-testid="stWidgetLabel"]{color:#c8cfe0!important}
[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label,[data-testid="stTextInput"] label{color:#c8cfe0!important;font-size:12px!important;font-weight:600!important}
div[data-testid="stSelectbox"] > label > div > p{color:#c8cfe0!important;font-weight:600!important}
.stSelectbox label p,.stNumberInput label p,.stTextInput label p,.stCheckbox label p{color:#c8cfe0!important;font-size:12px!important;font-weight:600!important}
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p{color:#e2e6f0!important}
.stSelectbox > div > label{color:#c8cfe0!important;font-weight:600!important}
/* Wszystkie labele w aplikacji */
.stApp label{color:#c8cfe0!important}
p[data-testid="stMarkdownContainer"]{color:#c8cfe0!important}
[data-testid="stMetric"]{background:#161920;border:1px solid #252a3a;border-radius:8px;padding:12px 16px}
[data-testid="stMetricLabel"]{color:#7a8299!important;font-size:11px!important}
[data-testid="stMetricValue"]{color:#e2e6f0!important;font-size:22px!important;font-weight:700!important}
h1,h2,h3{color:#e2e6f0!important}
hr{border-color:#252a3a!important}
.stMarkdown p{color:#b0b8cc}
[data-testid="stTabs"] [role="tab"]{color:#7a8299!important;font-weight:600!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#6c8eff!important;border-bottom-color:#6c8eff!important}
[data-testid="stExpander"]{background:#161920!important;border:1px solid #252a3a!important;border-radius:8px!important}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#0d0f14}
::-webkit-scrollbar-thumb{background:#252a3a;border-radius:3px}
div[data-testid="stFileUploader"]{background:#1e2230!important;border:1px solid #252a3a!important;border-radius:8px!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════
# SECTORS: (nazwa, ETF, kategoria, sektor_matka)
# kategoria: "sektor" = główny sektor S&P500 GICS, "branza" = branża/nisza
SECTORS_DATA = [
    # ── GŁÓWNE SEKTORY S&P500 (GICS) ──────────────────────────
    ("Technologia",           "XLK",  "sektor",  "Technologia"),
    ("Finanse",               "XLF",  "sektor",  "Finanse"),
    ("Ochrona Zdrowia",       "XLV",  "sektor",  "Ochrona Zdrowia"),
    ("Dobra Uznaniowe",       "XLY",  "sektor",  "Dobra Uznaniowe"),
    ("Dobra Podstawowe",      "XLP",  "sektor",  "Dobra Podstawowe"),
    ("Energetyka",            "XLE",  "sektor",  "Energetyka"),
    ("Przemysł",              "XLI",  "sektor",  "Przemysł"),
    ("Usługi Komunikacyjne",  "XLC",  "sektor",  "Komunikacja"),
    ("Surowce (sektor)",      "XLB",  "sektor",  "Surowce"),
    ("Nieruchomości",         "XLRE", "sektor",  "Nieruchomości"),
    ("Użytk. Publiczna",      "XLU",  "sektor",  "Użyteczność"),
    # ── BRANŻE / NISZE ─────────────────────────────────────────
    # Technologia
    ("Półprzewodniki",        "SOXX", "branza",  "Technologia"),
    ("Cyberbezpieczeństwo",   "CIBR", "branza",  "Technologia"),
    ("Oprogramowanie",        "IGV",  "branza",  "Technologia"),
    ("AI i Robotyka",         "ROBT", "branza",  "Technologia"),
    ("Chmura Obliczeniowa",   "WCLD", "branza",  "Technologia"),
    ("Internet i Media",      "FDN",  "branza",  "Technologia"),
    ("Fintech",               "FINX", "branza",  "Technologia"),
    ("Data Center REIT",      "SRVR", "branza",  "Technologia"),
    # Energetyka
    ("Ropa i Gaz",            "XLE",  "branza",  "Energetyka"),
    ("Ropa i Gaz E&P",        "XOP",  "branza",  "Energetyka"),
    ("Usługi Naftowe",        "OIH",  "branza",  "Energetyka"),
    ("Energia Odnawialna",    "ICLN", "branza",  "Energetyka"),
    ("Energia Słoneczna",     "TAN",  "branza",  "Energetyka"),
    ("Energia Uran",          "URA",  "branza",  "Energetyka"),
    ("Lit i Baterie",         "LIT",  "branza",  "Energetyka"),
    # Finanse
    ("Bankowość",             "KBE",  "branza",  "Finanse"),
    ("Ubezpieczenia",         "KIE",  "branza",  "Finanse"),
    ("Usługi Biznesowe",      "VFH",  "branza",  "Finanse"),
    ("Kasyna i Hazard",       "BETZ", "branza",  "Finanse"),
    # Ochrona Zdrowia
    ("Biotechnologia",        "XBI",  "branza",  "Ochrona Zdrowia"),
    ("Urządzenia Medyczne",   "IHI",  "branza",  "Ochrona Zdrowia"),
    ("Farmacja",              "PPH",  "branza",  "Ochrona Zdrowia"),
    ("Genomika",              "ARKG", "branza",  "Ochrona Zdrowia"),
    # Przemysł
    ("Transport i Logistyka", "IYT",  "branza",  "Przemysł"),
    ("Lotnictwo i Obrona",    "ITA",  "branza",  "Przemysł"),
    ("Infrastruktura",        "PAVE", "branza",  "Przemysł"),
    ("Motoryzacja",           "CARZ", "branza",  "Przemysł"),
    # Surowce / Materiały
    ("Surowce",               "DJP",  "branza",  "Surowce"),
    ("Metale Szlachetne",     "DBB",  "branza",  "Surowce"),
    ("Górnicy / Metale",      "PICK", "branza",  "Surowce"),
    ("Stal",                  "SLX",  "branza",  "Surowce"),
    ("Górnictwo Złoto",       "GDX",  "branza",  "Surowce"),
    # Nieruchomości
    ("REIT",                  "VNQ",  "branza",  "Nieruchomości"),
    # Dobra Uznaniowe / Podstawowe
    ("Detaliczny",            "XRT",  "branza",  "Dobra Uznaniowe"),
    ("Budownictwo",           "XHB",  "branza",  "Dobra Uznaniowe"),
    ("Podróże i Hotele",      "PEJ",  "branza",  "Dobra Uznaniowe"),
    ("Żywność",               "MOO",  "branza",  "Dobra Podstawowe"),
    # Komunikacja
    ("Telekomunikacja",       "IYZ",  "branza",  "Komunikacja"),
    ("Linie Lotnicze",        "JETS", "branza",  "Komunikacja"),
    # Inne
    ("Małe Spółki",           "IWM",  "branza",  "Rynek"),
    ("Rynki Wschodzące",      "EEM",  "branza",  "Rynek"),
    ("Materiały",             "XLB",  "branza",  "Surowce"),
]
# Backward-compatible tuple for fetch loops
SECTORS = [(n,e) for n,e,_,__ in SECTORS_DATA]
SECTOR_META = {e:{"name":n,"kat":k,"parent":p} for n,e,k,p in SECTORS_DATA}


BUILTIN_WL = {
    "🔥 Qullamaggie Top 50":["VAL","RIG","PTEN","NE","NBR","HP","NVDA","ARM","AVGO","AMD","ALAB","SMCI","PLTR","NOW","DDOG","RKLB","BKSY","ASTS","CELH","INSP","TMDX","AXON","COIN","MARA","WOLF","COCO","LQDA","ON","DECK","SKX","HWM","LHX","KTOS","LUNR","HIMS","DUOL","SOUN","IONQ","ACHR","JOBY"],
    "📈 Minervini Template":["AAPL","MSFT","NVDA","META","GOOGL","AMZN","TSLA","CRM","NOW","AMD","AVGO","QCOM","MRVL","ARM","GS","JPM","V","MA","LLY","ABBV","CAT","DE","HON","GE","XOM","CVX","COP"],
    "⚡ Mid Cap Growth":["CELH","ELF","DECK","CROX","INSP","AXSM","TMDX","BKSY","RKLB","ALAB","WOLF","IONQ","ASTS","LQDA","COCO"],
    "🛢️ Oil & Gas":["VAL","RIG","PTEN","NE","NBR","HP","VIST","VLO","PSX","MPC","CVX","COP","OXY"],
    "🤖 AI / Semis":["NVDA","AMD","AVGO","ARM","MRVL","ALAB","SMCI","MU","LRCX","AMAT","PLTR","SOUN","IONQ"],
    "📋 Moja lista":["AAPL","MSFT","NVDA","TSLA","META","GOOGL","V","MA","JPM"],
}

WATCHLIST_FILE = "watchlists.json"

# ═══════════════════════════════════════════════════════════════
# TECH CALCULATIONS
# ═══════════════════════════════════════════════════════════════
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
def sma(s,n): return s.rolling(n).mean()
def safe_pct(c,n):
    try: return round((float(c.iloc[-1])/float(c.iloc[-n])-1)*100,2) if len(c)>n else 0.0
    except: return 0.0
def calc_atr(h,l,c,n=14):
    tr=pd.concat([h-l,(h-c.shift(1)).abs(),(l-c.shift(1)).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()
def calc_rs(tr,br):
    idx=tr.index.intersection(br.index)
    if len(idx)<20: return 50.0
    t,b=tr.loc[idx],br.loc[idx]
    q=max(1,len(idx)//4)
    score=(2*((1+t.iloc[-q:]).prod()-1-(1+b.iloc[-q:]).prod()+1)+((1+t).prod()-1-(1+b).prod()+1))*100
    return round(float(np.clip(50+score,1,99)),1)
def calc_adr(c,n=20): return round(float(c.tail(n+1).pct_change().dropna().abs().mean()*100),2)
def calc_rvol(vol,n=50):  # Jeff Sun: 50-Day sessions
    avg=float(vol.tail(n+1).iloc[:-1].mean())
    return round(float(vol.iloc[-1])/avg if avg>0 else 1.0,2)
def calc_vars(c,h,l,n=5):
    rr=(h.tail(n)-l.tail(n)).mean(); ar=(h.tail(20)-l.tail(20)).mean()
    score=max(0,min(5,round(5*(1-rr/ar) if ar>0 else 2.5)))
    if abs(float(c.iloc[-1])/float(ema(c,10).iloc[-1])-1)*100<1: score=min(5,score+1)
    return int(score)
def classify_stage(p,e10,e20,s50,s200):
    if p>e10>e20>s50>s200: return "2A"
    if p>e10>e20 and p>s50>s200: return "2B"
    if p>e20 and p>s50>s200: return "2C"
    if p>s200 and p<s50: return "1B"
    if p>s200 and e10<e20: return "3A"
    if p<s200: return "4A"
    return "1A"
def classify_af(adr,rs,p,s50,s200,vol_m):
    if p<5 or vol_m<5: return "F"
    if p<s200*.95: return "E"
    if rs<50: return "D"
    if adr>5 and rs>90: return "A+"
    if adr>5 and rs>85: return "A"
    if adr>5 and rs>75: return "A-"
    if adr>3 and rs>80: return "B+"
    if adr>3 and rs>70: return "B"
    if adr>3 and rs>60: return "B-"
    if adr>2.5 and rs>70: return "C+"
    if adr>2.5: return "C"
    return "D"
def classify_sign(ext,vars_v,rr):
    if ext<1.5 and vars_v>=4 and rr>=2: return "+"
    if ext>3: return "-"
    return "0"
def comp_score(rs,stage,rv,vars_v,rr):
    ss={'2A':20,'2B':18,'2C':12,'1B':8,'3A':4,'4A':0,'1A':5}.get(stage,5)
    return min(100,round(rs*.4+ss+min(15,rv*7.5)+vars_v*3+min(10,rr*5)))

# ═══════════════════════════════════════════════════════════════
# DATA FETCHING
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800,show_spinner=False)
def get_spy():
    h=yf.Ticker("SPY").history(period="6mo",interval="1d",auto_adjust=True)
    r=h["Close"].pct_change().dropna(); r.index=r.index.normalize(); return r

@st.cache_data(ttl=1800,show_spinner=False)
def get_sector(etf):
    try:
        h=yf.Ticker(etf).history(period="1y",interval="1d",auto_adjust=True)
        if h is None or len(h)<55: return None
        c,v=h["Close"].dropna(),h["Volume"].dropna()
        spy=get_spy(); ret=c.pct_change().dropna(); ret.index=ret.index.normalize()
        common=ret.index.intersection(spy.index)
        rs=calc_rs(ret.loc[common],spy.loc[common]) if len(common)>=20 else 50.0
        # RS direction: teraz vs 5 dni temu
        rs_5d=calc_rs(ret.loc[common].iloc[:-5],spy.loc[common].iloc[:-5]) if len(common)>25 else rs
        rs_dir="up" if rs>rs_5d+1 else ("dn" if rs<rs_5d-1 else "flat")
        # RVOL 50d, SMA50 check
        rvol50=calc_rvol(v,n=50)
        s50v=float(sma(c,50).iloc[-1]) if len(c)>=50 else float(c.mean())
        abv50=1 if float(c.iloc[-1])>=s50v else 0
        h52=float(h["High"].dropna().tail(252).max())
        price_now=float(c.iloc[-1])
        dist52_sec=round((price_now/h52-1)*100,1) if h52>0 else None
        return {"rs":rs,"c1d":safe_pct(c,2),"c3d":safe_pct(c,4),"c5d":safe_pct(c,6),
                "c20d":safe_pct(c,21),"c60d":safe_pct(c,61),
                "rvol":rvol50,"rs_dir":rs_dir,"abv50":abv50,"dist52_sec":dist52_sec}
    except: return None

@st.cache_data(ttl=1800,show_spinner=False)
def get_stock(ticker):
    try:
        h=yf.Ticker(ticker).history(period="1y",interval="1d",auto_adjust=True)
        if h is None or len(h)<60: return None
        c,hh,l,v=h["Close"].dropna(),h["High"].dropna(),h["Low"].dropna(),h["Volume"].dropna()
        p=float(c.iloc[-1])
        e10=float(ema(c,10).iloc[-1]); e20=float(ema(c,20).iloc[-1])
        s50=float(sma(c,50).iloc[-1]); s100=float(sma(c,100).iloc[-1]); s200=float(sma(c,200).iloc[-1])
        atr_v=float(calc_atr(hh,l,c).iloc[-1]); adr=calc_adr(c)
        rv=calc_rvol(v,n=50)  # 50-day RVOL
        avg_dv=round(float(v.tail(50).mean())*p/1e6,1)  # Avg $ Vol 50D
        vol_m=avg_dv
        spy=get_spy(); ret=c.pct_change().dropna(); ret.index=ret.index.normalize()
        common=ret.index.intersection(spy.index)
        rs=calc_rs(ret.loc[common],spy.loc[common]) if len(common)>=20 else 50.0
        ext=round((p-s50)/atr_v,2) if atr_v>0 else 0.0
        vars_v=calc_vars(c,hh,l); stage=classify_stage(p,e10,e20,s50,s200)
        cls=classify_af(adr,rs,p,s50,s200,vol_m)
        h20=float(hh.tail(20).max()); h52=float(hh.tail(252).max())
        rr=round(max(.01,h20-p)/max(.01,p-e10),2)
        sign=classify_sign(ext,vars_v,rr)
        sc=comp_score(rs,stage,rv,vars_v,rr)
        def rn(n): return round((p/float(c.iloc[-n])-1)*100,1) if len(c)>n else None
        low_today=float(l.iloc[-1])
        lod_dist=round((p-low_today)/atr_v*100,1) if atr_v>0 else 0.0
        # Inside Day flag
        range_today=float(hh.iloc[-1])-float(l.iloc[-1])
        range_yest=float(hh.iloc[-2])-float(l.iloc[-2]) if len(hh)>=2 else range_today+1
        inside_day=(range_today<range_yest)
        # VARS score (Jeff Sun: RS × volatility quality)
        vars_score=round(float(np.clip((rs/50.0)*vars_v,0,10)),1)
        # Sector + Float (Opcja A — yfinance info)
        try:
            info=yf.Ticker(ticker).info
            sec_name=info.get("sector","") or info.get("industry","") or "—"
            float_sh=info.get("floatShares",None)
            shares_out=info.get("sharesOutstanding",None)
            short_pct=info.get("shortPercentOfFloat",None)
            float_pct=round(float(float_sh)/float(shares_out)*100,1) if float_sh and shares_out else None
            short_float=round(float(short_pct)*100,1) if short_pct else None
        except:
            sec_name="—"; float_pct=None; short_float=None
        return dict(ticker=ticker,cls=cls,sign=sign,stage=stage,rs=rs,adr=adr,rvol=rv,
                    price=round(p,2),chg1d=safe_pct(c,2),atr_ext=ext,vars=vars_v,
                    vars_score=vars_score,rr=rr,score=sc,
                    ret1m=rn(21),ret3m=rn(63),vol_m=vol_m,avg_dv=avg_dv,
                    dist52=round((p/h52-1)*100,1),lod_dist=lod_dist,
                    inside_day=inside_day,sector=sec_name,
                    float_pct=float_pct,short_float=short_float,
                    ma_e10=(p>=e10),ma_s20=(p>=e20),ma_s50=(p>=s50),ma_s200=(p>=s200),
                    sl1=round(p-atr_v,2),sl2=round(p-2*atr_v,2),
                    t1=round(p+2*atr_v,2),t2=round(p+3*atr_v,2))
    except: return None

# ═══════════════════════════════════════════════════════════════
# HTML HELPERS
# ═══════════════════════════════════════════════════════════════
def rs_color(v):
    if v>=95: return "#26ff7f"
    if v>=90: return "#4ade80"
    if v>=80: return "#f0c040"
    if v>=70: return "#fb923c"
    if v>=50: return "#f87171"
    return "#6b7280"

def chg_color(v):
    if v is None: return "#7a8299"
    if v>=3: return "#26ff7f"
    if v>=1: return "#4ade80"
    if v>=0: return "#6ee7b7"
    if v>=-1: return "#fb923c"
    if v>=-3: return "#f87171"
    return "#dc2626"

def pct_html(v):
    if v is None: return '<span style="color:#7a8299">—</span>'
    s="+"; c=chg_color(v)
    return f'<span style="color:{c}">{s if v>=0 else ""}{v:.1f}%</span>'

def rs_bar_html(v):
    c=rs_color(v); w=int(min(44,v*.44))
    return (f'<div style="display:flex;align-items:center;gap:4px">'
            f'<div style="width:44px;height:4px;background:#252a3a;border-radius:2px">'
            f'<div style="width:{w}px;height:4px;background:{c};border-radius:2px"></div></div>'
            f'<span style="color:{c};font-weight:700;font-size:11px">{v:.0f}</span></div>')

def cls_pill(c):
    m={"A+":("#1a0a4a","#c084fc","#7c3aed"),"A":("#0f3320","#4ade80","#166534"),
       "A-":("#0f2e1e","#86efac","#166534"),"B+":("#0a2a20","#34d399","#065f46"),
       "B":("#0a2820","#6ee7b7","#065f46"),"B-":("#0a2420","#99f6e4","#0f766e"),
       "C+":("#2e1a06","#fb923c","#9a3412"),"C":("#2a1608","#fdba74","#92400e"),
       "D":("#1e1e28","#9ca3af","#374151"),"E":("#2e0a0a","#f87171","#7f1d1d"),
       "F":("#300606","#fca5a5","#991b1b")}
    bg,fg,br=m.get(c,("#252535","#888","#555"))
    return f'<span style="background:{bg};color:{fg};border:1px solid {br};padding:2px 8px;border-radius:12px;font-size:10px;font-weight:800">{c}</span>'

def stg_pill(s):
    m={"2A":("#0f3320","#4ade80"),"2B":("#172a18","#86efac"),"2C":("#1a2c1a","#bbf7d0"),
       "1B":("#1a2030","#93c5fd"),"1A":("#252535","#9ca3af"),
       "3A":("#2e1a06","#fb923c"),"4A":("#2e0a0a","#f87171")}
    bg,fg=m.get(s,("#252535","#888"))
    return f'<span style="background:{bg};color:{fg};padding:1px 6px;border-radius:4px;font-size:9px;font-weight:700">{s}</span>'

def sgn_pill(s):
    if s=="+": return '<span style="background:#0f3320;color:#4ade80;padding:1px 7px;border-radius:4px;font-size:10px;font-weight:700">+ Ready</span>'
    if s=="-": return '<span style="background:#2e0a0a;color:#ff6b6b;padding:1px 7px;border-radius:4px;font-size:10px;font-weight:700">− Ext</span>'
    return '<span style="background:#1e1e28;color:#6b7280;padding:1px 7px;border-radius:4px;font-size:10px">Neutral</span>'

def rvol_html(v):
    # Jeff Sun: >=1.0 = minimum, >=1.5 = ponadnorma, >=2.0 = atak instytucji
    if v>=2.0:  c,w="#60a5fa",700   # jasnoniebieski, bold
    elif v>=1.5: c,w="#93c5fd",700  # niebieski, bold
    elif v>=1.0: c,w="#bfdbfe",400  # bladoniebieski
    else:        c,w="#7a8299",400  # szary = ponizej normy
    return f'<span style="color:{c};font-weight:{w}">{v:.2f}x</span>'

def atr_bar_html(v):
    pct=min(100,v/4*100)
    c="#26ff7f" if v<1 else "#4ade80" if v<2 else "#f0c040" if v<3 else "#e84545"
    return (f'<div style="display:flex;align-items:center;gap:5px">'
            f'<div style="width:50px;height:6px;background:#252a3a;border-radius:3px">'
            f'<div style="width:{pct:.0f}%;height:6px;background:{c};border-radius:3px"></div></div>'
            f'<span style="color:{c};font-size:10px;font-weight:700">{v:.2f}</span></div>')

def vars_html(v):
    return "".join(f'<span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:{"#26a65b" if i<=v else "#252a3a"};margin-right:2px"></span>' for i in range(1,6))

def rr_html(v):
    c="#26ff7f" if v>=2 else "#f0c040" if v>=1.5 else "#e84545"
    return f'<span style="color:{c};font-weight:700">{v:.1f}x</span>'

def score_bar(v):
    c="#26ff7f" if v>=80 else "#4ade80" if v>=60 else "#f0c040" if v>=40 else "#fb923c"
    return (f'<div style="display:flex;align-items:center;gap:4px">'
            f'<div style="width:36px;height:5px;background:#252a3a;border-radius:3px">'
            f'<div style="width:{v}%;height:5px;background:{c};border-radius:3px"></div></div>'
            f'<span style="color:{c};font-size:10px;font-weight:700">{v}</span></div>')

def ma_html(me10,ms20,ms50,ms200):
    def mk(v,l): c="#26a65b" if v else "#e84545"; s="✓" if v else "✗"; return f'<span style="color:{c};font-size:9px;font-weight:700">{s}{l}</span>'
    return f'{mk(me10,"E10")} {mk(ms20,"S20")} {mk(ms50,"S50")} {mk(ms200,"S200")}'

def dist52_html(v):
    c="#26ff7f" if v>=-5 else "#f0c040" if v>=-15 else "#fb923c" if v>=-30 else "#e84545"
    return f'<span style="color:{c};font-weight:600">{v:+.1f}%</span>'

def lod_dist_html(v):
    """Jeff Sun: < 60% = DOBRY entry (blisko Low dnia). > 60% = ZLY entry."""
    if v is None: return '<span style="color:#7a8299">—</span>'
    # < 60% = zielony (dobry), > 60% = czerwony (zly)
    c="#26ff7f" if v<30 else "#4ade80" if v<60 else "#f0c040" if v<80 else "#e84545"
    icon=" ✓" if v<60 else " ✗"
    bar=min(100,v)
    return (f'<div style="display:flex;align-items:center;gap:4px">'
            f'<div style="width:36px;height:4px;background:#252a3a;border-radius:2px">'
            f'<div style="width:{bar:.0f}%;height:4px;background:{c};border-radius:2px"></div></div>'
            f'<span style="color:{c};font-size:10px;font-weight:700">{v:.0f}%{icon}</span></div>')

def inside_day_html(v):
    if v: return '<span style="background:#0f3320;color:#4ade80;padding:1px 6px;border-radius:3px;font-size:9px;font-weight:700">ID</span>'
    return '<span style="color:#252a3a;font-size:9px">—</span>'

def float_pct_html(v):
    if v is None: return '<span style="color:#7a8299;font-size:10px">—</span>'
    c="#26ff7f" if v<20 else "#f0c040" if v<50 else "#7a8299"
    return f'<span style="color:{c};font-size:10px;font-weight:600">{v:.1f}%</span>'


def chg_tag(v):
    if v is None: return "—"
    c=chg_color(v); s="+" if v>=0 else ""
    return f'<span style="background:{c}22;color:{c};border:1px solid {c}33;padding:1px 5px;border-radius:3px;font-size:9px;font-weight:700">{s}{v:.1f}%</span>'

TH="padding:6px 9px;color:#7a8299;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid #252a3a;white-space:nowrap;background:#161920"
TD="padding:5px 9px;white-space:nowrap;vertical-align:middle;border-bottom:1px solid #1a1e2a"

def tbl_wrap(html):
    return f'<div style="overflow-x:auto">{html}</div>'

# ═══════════════════════════════════════════════════════════════
# WATCHLIST PERSISTENCE
# ═══════════════════════════════════════════════════════════════
def load_custom_wl():
    if "custom_wl" not in st.session_state:
        try:
            if os.path.exists(WATCHLIST_FILE):
                with open(WATCHLIST_FILE,"r") as f:
                    st.session_state["custom_wl"]=json.load(f)
            else:
                st.session_state["custom_wl"]={}
        except:
            st.session_state["custom_wl"]={}
    return st.session_state["custom_wl"]

def save_custom_wl(data):
    st.session_state["custom_wl"]=data
    try:
        with open(WATCHLIST_FILE,"w") as f: json.dump(data,f,ensure_ascii=False,indent=2)
    except: pass

def all_wl():
    custom=load_custom_wl()
    result={**BUILTIN_WL}
    for k,v in custom.items(): result[k]=v.get("tickers",[])
    return result

def parse_tickers(text):
    return list(dict.fromkeys([t.strip().upper() for t in re.split(r'[,\s\n;]+',text) if t.strip() and 1<=len(t.strip())<=7 and re.match(r'^[A-Z0-9.]+$',t.strip().upper())]))

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:4px 0 14px'>
      <div style='font-size:16px;font-weight:800;color:#6c8eff'>📈 Adam Scanner v1</div>
      <div style='font-size:10px;color:#7a8299;margin-top:2px'>Qullamaggie × Minervini</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("",
        ["🌍  Market Radar","🔬  Stock Radar","📚  Playbook","📋  Watchlisty"],
        label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-size:9px;color:#555;line-height:1.8">Dane: Yahoo Finance<br>⚠️ Tylko edukacyjnie<br>Nie jest poradą inwest.</div>', unsafe_allow_html=True)

@st.cache_data(ttl=900,show_spinner=False)
def get_market_overview():
    """Pobiera SPY/QQQ/IWM/VIX + Fear&Greed"""
    result={}
    # Indeksy główne
    for ticker,name in [("SPY","S&P 500"),("QQQ","NASDAQ"),("IWM","Russell 2000"),("^VIX","VIX")]:
        try:
            h=yf.Ticker(ticker).history(period="60d",interval="1d",auto_adjust=True)
            if h is None or len(h)<5: continue
            c=h["Close"].dropna()
            price=float(c.iloc[-1])
            chg1d=safe_pct(c,2)
            chg5d=safe_pct(c,6)
            s50=float(sma(c,50).iloc[-1]) if len(c)>=50 else price
            s200=float(sma(c,200).iloc[-1]) if len(c)>=200 else price
            abv50=(price>=s50)
            abv200=(price>=s200)
            # Trend VIX: rośnie czy spada
            vix_dir="up" if len(c)>=3 and float(c.iloc[-1])>float(c.iloc[-3]) else "dn"
            result[ticker]={
                "name":name,"price":round(price,2),"chg1d":chg1d,"chg5d":chg5d,
                "abv50":abv50,"abv200":abv200,"vix_dir":vix_dir,
                "c_series":c
            }
        except: pass
    # Fear & Greed — własne obliczenie na podstawie danych rynkowych (Stock Market)
    # Składowe wzorowane na CNN F&G:
    # 1. RSI SPY 14D (25%) — wysokie RSI = chciwość
    # 2. VIX poziom (25%) — niski VIX = chciwość
    # 3. Momentum SPY vs SMA125 (25%) — cena powyżej długiej średniej = chciwość
    # 4. Siła 52W High SPY (25%) — blisko ATH = chciwość
    try:
        fg_parts=[]
        # 1. RSI SPY
        if "SPY" in result:
            spy_c=result["SPY"].get("c_series")
            if spy_c is not None and len(spy_c)>=16:
                delta=spy_c.diff()
                gain=delta.clip(lower=0).rolling(14).mean()
                loss=(-delta.clip(upper=0)).rolling(14).mean()
                rs=gain/(loss.replace(0,np.nan))
                rsi=float((100-100/(1+rs)).iloc[-1])
                fg_parts.append(rsi)
        # 2. VIX score (odwrócony: niski VIX = wysoki score)
        if "^VIX" in result:
            vix_p=result["^VIX"]["price"]
            vix_score=max(0,min(100,100-(vix_p-10)*2.5))
            fg_parts.append(vix_score)
        # 3. Momentum SPY vs SMA125
        if "SPY" in result:
            spy_c=result["SPY"].get("c_series")
            if spy_c is not None and len(spy_c)>=126:
                s125=float(sma(spy_c,125).iloc[-1])
                p_now=float(spy_c.iloc[-1])
                mom_pct=(p_now/s125-1)*100
                mom_score=max(0,min(100,50+mom_pct*4))
                fg_parts.append(mom_score)
        # 4. 52W High proximity
        if "SPY" in result:
            spy_c=result["SPY"].get("c_series")
            if spy_c is not None and len(spy_c)>=252:
                h52=float(spy_c.tail(252).max())
                p_now=float(spy_c.iloc[-1])
                h52_score=max(0,min(100,(p_now/h52)*100))
                fg_parts.append(h52_score)

        if fg_parts:
            fg_val=round(sum(fg_parts)/len(fg_parts))
            if fg_val<=20:   fg_lbl="Extreme Fear"
            elif fg_val<=40: fg_lbl="Fear"
            elif fg_val<=60: fg_lbl="Neutral"
            elif fg_val<=80: fg_lbl="Greed"
            else:            fg_lbl="Extreme Greed"
            result["fear_greed"]={"value":fg_val,"label":fg_lbl,"source":"calc"}
        else:
            result["fear_greed"]={"value":None,"label":"N/A"}
    except:
        result["fear_greed"]={"value":None,"label":"N/A"}
    return result

# ═══════════════════════════════════════════════════════════════
# PAGE 1: MARKET RADAR
# ═══════════════════════════════════════════════════════════════
if page == "🌍  Market Radar":
    st.markdown("# 🌍 Market & Sector Radar")
    st.markdown("*Ranking 51 sektorów — RS Score, zmiany %, RVOL, Quadrant Chart*")
    st.markdown("---")

    # ══════════════════════════════════════════════════════
    # GÓRNY PASEK: Indeksy + VIX + Fear&Greed
    # ══════════════════════════════════════════════════════
    mkt=get_market_overview()

    def idx_card(ticker, name, data):
        if not data: return ""
        p=data["price"]; c=data["chg1d"]; c5=data["chg5d"]
        a50=data["abv50"]; a200=data["abv200"]
        cc=("#26ff7f" if c>=1 else "#4ade80" if c>=0 else "#fb923c" if c>=-1 else "#e84545")
        s=("+" if c>=0 else "")
        a50_html=('<span style="background:#0f3320;color:#4ade80;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:700">▲SMA50</span>'
                  if a50 else '<span style="background:#2e0a0a;color:#f87171;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:700">▼SMA50</span>')
        a200_html=('<span style="background:#0f3320;color:#4ade80;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:700">▲SMA200</span>'
                   if a200 else '<span style="background:#2e0a0a;color:#f87171;padding:2px 6px;border-radius:3px;font-size:10px;font-weight:700">▼SMA200</span>')
        return (
            f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;padding:14px 16px">'
            f'<div style="font-size:11px;color:#7a8299;font-weight:600;margin-bottom:6px">{name}</div>'
            f'<div style="font-size:24px;font-weight:800;color:#e2e6f0;margin-bottom:4px">${p:,.2f}</div>'
            f'<div style="font-size:16px;font-weight:700;color:{cc};margin-bottom:3px">{s}{c:.2f}% dziś</div>'
            f'<div style="font-size:12px;color:{"#4ade80" if c5>=0 else "#f87171"};margin-bottom:8px">{("+" if c5>=0 else "")}{c5:.1f}% tydzień</div>'
            f'<div style="display:flex;gap:5px">{a50_html}{a200_html}</div>'
            f'</div>'
        )

    def vix_card(data):
        if not data: return ""
        p=data["price"]; c=data["chg1d"]
        d=data.get("vix_dir","dn")
        if p<15:   vc,vl="#26ff7f","Spokój"
        elif p<20: vc,vl="#4ade80","Niski"
        elif p<25: vc,vl="#f0c040","Umiarkowany"
        elif p<30: vc,vl="#fb923c","Podwyższony"
        else:      vc,vl="#e84545","Strach/Panika"
        dir_sym=("↑" if d=="up" else "↓")
        dir_col=("#e84545" if d=="up" else "#26ff7f")
        cc=("#e84545" if c>=0 else "#26ff7f")
        return (
            f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;padding:14px 16px">'
            f'<div style="font-size:11px;color:#7a8299;font-weight:600;margin-bottom:6px">VIX — Zmienność</div>'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
            f'<div style="font-size:28px;font-weight:900;color:{vc}">{p:.1f}</div>'
            f'<div style="font-size:26px;font-weight:900;color:{dir_col}">{dir_sym}</div>'
            f'</div>'
            f'<div style="font-size:14px;font-weight:700;color:{vc};margin-bottom:3px">{vl}</div>'
            f'<div style="font-size:12px;color:{cc};margin-bottom:6px">{"+" if c>=0 else ""}{c:.2f}% dziś</div>'
            f'<div style="font-size:9px;color:#555">VIX↑ = strach · VIX↓ = spokój</div>'
            f'</div>'
        )

    def fg_card(data):
        if not data or data.get("value") is None:
            return (
                '<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;padding:14px 16px">'
                '<div style="font-size:11px;color:#7a8299;font-weight:600;margin-bottom:4px">Fear & Greed Index</div>'
                '<div style="font-size:13px;color:#555;margin-top:6px">Obliczanie...</div></div>'
            )
        v=data["value"]; lbl=data["label"]
        if v<=20:   vc,emoji="#e84545","😱"
        elif v<=40: vc,emoji="#fb923c","😨"
        elif v<=60: vc,emoji="#f0c040","😐"
        elif v<=80: vc,emoji="#4ade80","😊"
        else:       vc,emoji="#26ff7f","🤑"
        return (
            f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;padding:14px 16px">'
            f'<div style="font-size:11px;color:#7a8299;font-weight:600;margin-bottom:6px">Fear & Greed</div>'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">'
            f'<div style="font-size:28px;font-weight:900;color:{vc}">{v}</div>'
            f'<div style="font-size:22px">{emoji}</div>'
            f'</div>'
            f'<div style="font-size:13px;font-weight:700;color:{vc};margin-bottom:5px">{lbl}</div>'
            f'<div style="height:8px;background:#252a3a;border-radius:4px">'
            f'<div style="width:{v}%;height:8px;background:linear-gradient(to right,#e84545,#f0c040,#26ff7f);border-radius:4px"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;font-size:9px;color:#555;margin-top:3px">'
            f'<span>Strach</span><span>Neutral</span><span>Chciwość</span>'
            f'</div>'
            f'<div style="font-size:9px;color:#555;margin-top:4px">Obliczony z: RSI · VIX · Momentum · 52W</div>'
            f'</div>'
        )

    # Render górny pasek
    mc1,mc2,mc3,mc4,mc5=st.columns(5)
    with mc1: st.markdown(idx_card("SPY","S&P 500",mkt.get("SPY")),unsafe_allow_html=True)
    with mc2: st.markdown(idx_card("QQQ","NASDAQ 100",mkt.get("QQQ")),unsafe_allow_html=True)
    with mc3: st.markdown(idx_card("IWM","Russell 2000",mkt.get("IWM")),unsafe_allow_html=True)
    with mc4: st.markdown(vix_card(mkt.get("^VIX")),unsafe_allow_html=True)
    with mc5: st.markdown(fg_card(mkt.get("fear_greed")),unsafe_allow_html=True)

    st.markdown("---")

    sc_f1,sc_f2,sc_f3=st.columns([2,2,2])
    with sc_f1:
        run_sec=st.button("🔄 Odśwież dane sektorów")
        if run_sec: st.cache_data.clear()
    with sc_f2:
        kat_filter=st.selectbox("Kategoria",["Wszystkie","🏛️ Główne sektory S&P500","🔬 Branże / Nisze"],label_visibility="visible")
    with sc_f3:
        parent_filter=st.selectbox("Sektor-matka",["Wszystkie","Technologia","Finanse","Ochrona Zdrowia","Energetyka","Przemysł","Surowce","Komunikacja","Dobra Uznaniowe","Dobra Podstawowe","Nieruchomości","Użyteczność","Rynek"],label_visibility="visible")

    if "sec_data" not in st.session_state or run_sec:
        prog=st.progress(0); txt=st.empty()
        data={}
        for i,(name,etf) in enumerate(SECTORS):
            prog.progress((i+1)/len(SECTORS))
            txt.markdown(f"Pobieram `{etf}` — {i+1}/{len(SECTORS)}")
            sd=get_sector(etf)
            data[name]={"etf":etf,**(sd or {"rs":50,"c1d":0,"c3d":0,"c5d":0,"c20d":0,"c60d":0,"rvol":1})}
            time.sleep(0.1)
        prog.empty(); txt.empty()
        st.session_state["sec_data"]=data

    raw=st.session_state["sec_data"]
    rows=[{"name":n,"etf":v["etf"],"rs":v.get("rs",50),
           "c1d":v.get("c1d",0),"c3d":v.get("c3d",0),"c5d":v.get("c5d",0),
           "c20d":v.get("c20d",0),"c60d":v.get("c60d",0),"rvol":v.get("rvol",1),
           "rs_dir":v.get("rs_dir","flat"),"abv50":v.get("abv50",0),
           "dist52_sec":v.get("dist52_sec",None),
           "kat":SECTOR_META.get(v["etf"],{}).get("kat","branza"),
           "parent":SECTOR_META.get(v["etf"],{}).get("parent","—"),
           } for n,v in raw.items()]
    # Risk-On / Breadth — używa abv50 (cena ETF vs SMA50)
    abv=sum(1 for r in rows if r.get("abv50",0))
    tot=max(1,len(rows)); pct=round(abv/tot*100)
    rs_up=sum(1 for r in rows if r.get("rs_dir")=="up")
    rs_dn=sum(1 for r in rows if r.get("rs_dir")=="dn")
    rs_fl=sum(1 for r in rows if r.get("rs_dir")=="flat")
    # ── Timestamp + session status ───────────────────────────
    import datetime, pytz
    now_utc=datetime.datetime.now(pytz.UTC)
    now_pl=now_utc.astimezone(pytz.timezone("Europe/Warsaw"))
    fetched_at=now_pl.strftime("%H:%M")
    # NYSE otwarte pn-pt 09:30-16:00 ET = 15:30-22:00 PL (zimą) / 15:30-22:00 (latem)
    now_et=now_utc.astimezone(pytz.timezone("America/New_York"))
    is_weekday=now_et.weekday()<5
    mkt_open_time=now_et.replace(hour=9,minute=30,second=0,microsecond=0)
    mkt_close_time=now_et.replace(hour=16,minute=0,second=0,microsecond=0)
    session_open=(is_weekday and mkt_open_time<=now_et<=mkt_close_time)
    session_label="🟢 Sesja OTWARTA" if session_open else "🔴 Sesja ZAMKNIĘTA"
    session_col="#4ade80" if session_open else "#f87171"

    # ── Jeden wiersz: Risk-On | Breadth | RS Direction | Timestamp ───
    ron=pct>=50
    ron_bg="#0f3320" if ron else "#2e0a0a"
    ron_col="#4ade80" if ron else "#f87171"
    ron_border="#166534" if ron else "#7f1d1d"
    bc_col="#26ff7f" if pct>=60 else "#f0c040" if pct>=40 else "#e84545"
    rs_dir_col="#26ff7f" if rs_up>rs_dn else "#e84545" if rs_dn>rs_up else "#f0c040"

    st.markdown(
        f'<div style="display:flex;gap:8px;align-items:stretch;margin-bottom:10px">'

        # 1. Risk-On/Off
        f'<div style="background:{ron_bg};border:1px solid {ron_border};border-radius:8px;'
        f'padding:10px 16px;display:flex;align-items:center;gap:10px;flex:1">'
        f'<div style="font-size:18px">{"🟢" if ron else "🔴"}</div>'
        f'<div><div style="font-size:13px;font-weight:800;color:{ron_col}">{"RISK-ON" if ron else "RISK-OFF"}</div>'
        f'<div style="font-size:10px;color:{ron_col}88">{abv}/{tot} ETF nad SMA50</div></div>'
        f'</div>'

        # 2. Breadth %
        f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;'
        f'padding:10px 16px;flex:2">'
        f'<div style="font-size:10px;color:#7a8299;font-weight:600;margin-bottom:4px">BREADTH — % ETF powyżej SMA50</div>'
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'<div style="flex:1;height:8px;background:#252a3a;border-radius:4px">'
        f'<div style="width:{pct}%;height:8px;background:{bc_col};border-radius:4px"></div></div>'
        f'<span style="font-size:14px;font-weight:800;color:{bc_col};min-width:40px">{pct}%</span>'
        f'<span style="font-size:10px;color:#26ff7f">{abv}↑</span>'
        f'<span style="font-size:10px;color:#e84545">{tot-abv}↓</span>'
        f'</div></div>'

        # 3. RS Line Direction
        f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;'
        f'padding:10px 16px;flex:1.5;display:flex;flex-direction:column;justify-content:center">'
        f'<div style="font-size:10px;color:#7a8299;font-weight:600;margin-bottom:5px">RS LINE vs SPY (5D)</div>'
        f'<div style="display:flex;gap:12px;align-items:center">'
        f'<span style="font-size:13px;font-weight:800;color:#26ff7f">↑ {rs_up}</span>'
        f'<span style="font-size:13px;font-weight:600;color:#7a8299">→ {rs_fl}</span>'
        f'<span style="font-size:13px;font-weight:800;color:#e84545">↓ {rs_dn}</span>'
        f'</div></div>'

        # 4. Timestamp + sesja
        f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;'
        f'padding:10px 16px;display:flex;flex-direction:column;justify-content:center;min-width:180px">'
        f'<div style="font-size:11px;font-weight:700;color:{session_col};margin-bottom:4px">{session_label}</div>'
        f'<div style="font-size:10px;color:#7a8299">Pobrano: <span style="color:#e2e6f0;font-weight:600">{fetched_at} PL</span></div>'
        f'<div style="font-size:10px;color:#7a8299;margin-top:2px">Cache: <span style="color:#e2e6f0">30 min</span></div>'
        f'<div style="font-size:9px;color:#555;margin-top:3px">Yahoo Finance · 15-20min delay</div>'
        f'</div>'

        f'</div>',
        unsafe_allow_html=True
    )
    # Apply category filters
    if kat_filter=="🏛️ Główne sektory S&P500": rows=[r for r in rows if r["kat"]=="sektor"]
    elif kat_filter=="🔬 Branże / Nisze": rows=[r for r in rows if r["kat"]=="branza"]
    if parent_filter!="Wszystkie": rows=[r for r in rows if r["parent"]==parent_filter]
    if "sec_sort" not in st.session_state:
        st.session_state["sec_sort"]="rs"; st.session_state["sec_asc"]=False
    rows.sort(key=lambda x:x.get(st.session_state["sec_sort"],0),reverse=not st.session_state["sec_asc"])
    st.markdown("---")

    # Quadrant Chart
    st.markdown("### Quadrant: Weekly RS vs Monthly RS")
    st.caption("Oś X = zmiana 5D% · Oś Y = zmiana 20D% · Rozmiar = RS Score")
    try:
        import plotly.graph_objects as go
        colors=[]
        for r in rows:
            if r["c5d"]>=0 and r["c20d"]>=0: colors.append("#26a65b")
            elif r["c5d"]>=0 and r["c20d"]<0: colors.append("#6c8eff")
            elif r["c5d"]<0  and r["c20d"]>=0: colors.append("#f0c040")
            else: colors.append("#e84545")
        xs=[r["c5d"] for r in rows]; ys=[r["c20d"] for r in rows]
        sizes=[max(8,min(30,r["rs"]*.28)) for r in rows]
        hover=[f"<b>{r['name']}</b> ({r['etf']})<br>RS: {r['rs']:.0f}<br>5D: {r['c5d']:+.1f}%<br>20D: {r['c20d']:+.1f}%" for r in rows]
        fig=go.Figure()
        mx2=max(abs(v) for v in xs+[1])*1.15; my2=max(abs(v) for v in ys+[1])*1.15
        for x1,y1,x2,y2,fc in [(0,0,mx2,my2,"rgba(38,166,91,0.06)"),(-mx2,0,0,my2,"rgba(240,192,64,0.05)"),(0,-my2,mx2,0,"rgba(108,142,255,0.05)"),(-mx2,-my2,0,0,"rgba(228,69,69,0.07)")]:
            fig.add_shape(type="rect",x0=x1,y0=y1,x1=x2,y1=y2,fillcolor=fc,line_width=0,layer="below")
        fig.add_hline(y=0,line_color="#252a3a",line_width=1)
        fig.add_vline(x=0,line_color="#252a3a",line_width=1)
        for lbl,ax,ay,col in [("STRONG",mx2*.65,my2*.82,"#26a65b"),("IMPROVING",mx2*.65,-my2*.82,"#6c8eff"),("WEAKENING",-mx2*.6,my2*.82,"#f0c040"),("WEAK",-mx2*.6,-my2*.82,"#e84545")]:
            fig.add_annotation(x=ax,y=ay,text=lbl,showarrow=False,font=dict(size=10,color=col),opacity=.55)
        fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",
            marker=dict(size=sizes,color=colors,opacity=.85,line=dict(width=1,color="rgba(255,255,255,0.12)")),
            text=[r["name"][:11] for r in rows],textposition="top center",
            textfont=dict(size=8,color="#8a90a0"),
            hovertemplate="%{customdata}<extra></extra>",customdata=hover))
        fig.update_layout(height=480,paper_bgcolor="#0d0f14",plot_bgcolor="#0d0f14",
            font=dict(family="Segoe UI",color="#e2e6f0"),
            xaxis=dict(title=dict(text="Zmiana 5D%",font=dict(size=11)),gridcolor="#1e2230",zerolinecolor="#252a3a",tickfont=dict(size=10)),
            yaxis=dict(title=dict(text="Zmiana 20D%",font=dict(size=11)),gridcolor="#1e2230",zerolinecolor="#252a3a",tickfont=dict(size=10)),
            showlegend=False,margin=dict(l=60,r=20,t=10,b=50),
            hoverlabel=dict(bgcolor="#161920",bordercolor="#252a3a",font=dict(size=12,color="#e2e6f0")))
        st.plotly_chart(fig,use_container_width=True)
    except Exception as e:
        st.warning(f"Plotly error: {e}")

    # Quad tables
    st.markdown("### Ranking wg kwadrantów")
    def qt(title,items,col):
        if not items: return f"<div style='color:#555;padding:8px'>Brak</div>"
        rows_h="".join(f'<tr style="border-bottom:1px solid #1a1e2a"><td style="padding:5px 8px;font-size:11px;font-weight:600;color:#e2e6f0">{r["name"][:16]}</td><td style="padding:5px 8px;font-size:10px;color:{chg_color(r["c5d"])};text-align:right">{r["c5d"]:+.1f}%</td><td style="padding:5px 8px;font-size:10px;color:{chg_color(r["c20d"])};text-align:right">{r["c20d"]:+.1f}%</td><td style="padding:5px 8px;font-size:10px;font-weight:700;color:{rs_color(r["rs"])};text-align:right">{r["rs"]:.0f}</td></tr>' for r in items[:12])
        return f'<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;overflow:hidden"><div style="background:{col}22;border-bottom:2px solid {col};padding:6px 10px;display:flex;justify-content:space-between"><span style="font-size:11px;font-weight:700;color:{col}">{title}</span><span style="font-size:10px;color:#7a8299">{len(items)}</span></div><table style="width:100%;border-collapse:collapse"><tr style="background:#1a1e2a"><th style="padding:5px 8px;font-size:9px;color:#7a8299;text-align:left">Sektor</th><th style="padding:5px 8px;font-size:9px;color:#7a8299;text-align:right">5D</th><th style="padding:5px 8px;font-size:9px;color:#7a8299;text-align:right">20D</th><th style="padding:5px 8px;font-size:9px;color:#7a8299;text-align:right">RS</th></tr>{rows_h}</table></div>'
    q1,q2,q3,q4=st.columns(4)
    strong_l=sorted([r for r in rows if r["c5d"]>=0 and r["c20d"]>=0],key=lambda x:-x["rs"])
    improv_l=sorted([r for r in rows if r["c5d"]>=0 and r["c20d"]<0], key=lambda x:-x["rs"])
    weakn_l =sorted([r for r in rows if r["c5d"]<0  and r["c20d"]>=0],key=lambda x:-x["rs"])
    weak_l  =sorted([r for r in rows if r["c5d"]<0  and r["c20d"]<0], key=lambda x:-x["rs"])
    with q1: st.markdown(qt(f"Strong ({len(strong_l)})",strong_l,"#26a65b"),unsafe_allow_html=True)
    with q2: st.markdown(qt(f"Improving ({len(improv_l)})",improv_l,"#6c8eff"),unsafe_allow_html=True)
    with q3: st.markdown(qt(f"Weakening ({len(weakn_l)})",weakn_l,"#f0c040"),unsafe_allow_html=True)
    with q4: st.markdown(qt(f"Weak ({len(weak_l)})",weak_l,"#e84545"),unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Pełny ranking sektorów — wszystkie 51")
    # Sort controls
    sc1,sc2,sc3 = st.columns([3,2,1])
    with sc1:
        sort_opts={"RS Score":"rs","Zmiana 1D%":"c1d","Zmiana 5D%":"c5d","Zmiana 20D%":"c20d","Zmiana 60D%":"c60d","RVOL":"rvol","Nazwa":"name"}
        sel_sort=st.selectbox("Sortuj wg",list(sort_opts.keys()),index=list(sort_opts.keys()).index("RS Score"),label_visibility="collapsed")
        if sort_opts[sel_sort]!=st.session_state.get("sec_sort"):
            st.session_state["sec_sort"]=sort_opts[sel_sort]; st.session_state["sec_asc"]=False
    with sc2:
        asc=st.toggle("Rosnąco",value=st.session_state.get("sec_asc",False))
        st.session_state["sec_asc"]=asc
    with sc3:
        st.caption(f"{len(rows)} sektorów")
    rows.sort(key=lambda x:x.get(st.session_state["sec_sort"],0),reverse=not st.session_state["sec_asc"])

    # helper badges
    kat_badge=lambda k:('<span style="background:#1e2a4a;color:#6c8eff;padding:1px 5px;border-radius:3px;font-size:9px">S&P</span>'
                        if k=="sektor" else
                        '<span style="background:#1e2230;color:#7a8299;padding:1px 5px;border-radius:3px;font-size:9px">branża</span>')
    def rs_dir_b(d):
        if d=="up":   return '<span style="color:#26ff7f;font-weight:700">↑</span>'
        if d=="dn":   return '<span style="color:#e84545;font-weight:700">↓</span>'
        return '<span style="color:#7a8299">→</span>'

    sec_cols=["#","Sektor","ETF","TV","Kat.","Sektor-matka","RS","RS↕","1D%","3D%","5D%","20D%","60D%","52W High","RVOL50","SMA50","Kwadrant"]
    head=f'<thead><tr>{"".join(f"<th style=\"{TH}\">{c}</th>" for c in sec_cols)}</tr></thead>'
    body=""
    for i,r in enumerate(rows,1):
        if r["c5d"]>=0 and r["c20d"]>=0: ql,qc="Strong","#26a65b"
        elif r["c5d"]>=0:                 ql,qc="Improving","#6c8eff"
        elif r["c20d"]>=0:                ql,qc="Weakening","#f0c040"
        else:                             ql,qc="Weak","#e84545"
        rv=r["rvol"]; rvc="#60a5fa" if rv>=2 else "#a5f3fc" if rv>=1.5 else "#7a8299"
        etf=r["etf"]
        tv_lnk=f'<a href="https://www.tradingview.com/chart/?symbol={etf}" target="_blank" style="color:#6c8eff;font-size:10px;font-weight:700;text-decoration:none">TV↗</a>'
        kat=r.get("kat","branza"); parent=r.get("parent","—")
        rs_d=r.get("rs_dir","flat")
        abv=r.get("abv50",0)
        abv_badge=('<span style="color:#26a65b;font-size:9px;font-weight:700">▲ SMA50</span>'
                   if abv else '<span style="color:#e84545;font-size:9px">▼ SMA50</span>')
        # 52W High distance
        d52v=r.get("dist52_sec",None)
        d52_html_str=(dist52_html(d52v) if d52v is not None else '<span style="color:#555;font-size:10px">—</span>')
        body+=(f'<tr style="border-bottom:1px solid #1a1e2a">'
              +f'<td style="{TD};color:#7a8299;font-size:10px">{i}</td>'
              +f'<td style="{TD};font-weight:600">{r["name"]}</td>'
              +f'<td style="{TD};color:#6c8eff;font-weight:700">{etf}</td>'
              +f'<td style="{TD}">{tv_lnk}</td>'
              +f'<td style="{TD}">{kat_badge(kat)}</td>'
              +f'<td style="{TD};font-size:10px;color:#7a8299">{parent}</td>'
              +f'<td style="{TD}">{rs_bar_html(r["rs"])}</td>'
              +f'<td style="{TD}">{rs_dir_b(rs_d)}</td>'
              +f'<td style="{TD}">{chg_tag(r["c1d"])}</td>'
              +f'<td style="{TD}">{chg_tag(r["c3d"])}</td>'
              +f'<td style="{TD}">{chg_tag(r["c5d"])}</td>'
              +f'<td style="{TD}">{chg_tag(r["c20d"])}</td>'
              +f'<td style="{TD}">{chg_tag(r["c60d"])}</td>'
              +f'<td style="{TD}">{d52_html_str}</td>'
              +f'<td style="{TD};color:{rvc};font-weight:{"700" if rv>=1.5 else "400"}">{rv:.1f}x{"🔵" if rv>=2 else ""}</td>'
              +f'<td style="{TD}">{abv_badge}</td>'
              +f'<td style="{TD}"><span style="color:{qc};font-size:10px;font-weight:700">{ql}</span></td>'
              +f'</tr>')
    st.markdown(tbl_wrap(f'<table style="width:100%;border-collapse:collapse;min-width:1200px"><thead>{head}</thead><tbody>{body}</tbody></table>'),unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 2: STOCK RADAR
# ═══════════════════════════════════════════════════════════════
elif page == "🔬  Stock Radar":
    st.markdown("# 🔬 Stock Radar")
    st.markdown("---")

    # ── IMPORT ────────────────────────────────────────────────
    st.markdown("### 📥 Importuj listę spółek")
    # Czytelne przyciski zamiast radio
    if "imp_tab" not in st.session_state: st.session_state["imp_tab"]="wl"
    ib1,ib2,ib3=st.columns(3)
    with ib1:
        if st.button("📋  Wybierz watchlistę", use_container_width=True,
                     type="primary" if st.session_state["imp_tab"]=="wl" else "secondary"):
            st.session_state["imp_tab"]="wl"
    with ib2:
        if st.button("✏️  Wpisz ręcznie", use_container_width=True,
                     type="primary" if st.session_state["imp_tab"]=="manual" else "secondary"):
            st.session_state["imp_tab"]="manual"
    with ib3:
        if st.button("📁  Wgraj plik TXT/CSV", use_container_width=True,
                     type="primary" if st.session_state["imp_tab"]=="file" else "secondary"):
            st.session_state["imp_tab"]="file"

    tickers=[]
    tab=st.session_state["imp_tab"]
    if tab=="manual":
        raw=st.text_area("Tickery — jeden per linia lub oddzielone przecinkiem",height=90,
                         placeholder="NVDA, AMD, TSLA\nAAPL MSFT\nVAL",label_visibility="visible")
        if raw.strip(): tickers=parse_tickers(raw)
        if tickers: st.success(f"✅ {len(tickers)} tickerów: {', '.join(tickers[:8])}{'...' if len(tickers)>8 else ''}")
    elif tab=="file":
        up=st.file_uploader("Plik TXT lub CSV z tickerami",type=["txt","csv"],label_visibility="visible")
        if up:
            content=up.read().decode("utf-8",errors="ignore")
            tickers=parse_tickers(content)
            st.success(f"✅ {len(tickers)} tickerów z **{up.name}**")
            with st.expander("Podgląd listy"): st.write("  ·  ".join(tickers))
    else:
        wl_names=list(all_wl().keys())
        sel_wl=st.selectbox("Wybierz watchlistę",wl_names,label_visibility="visible")
        tickers=all_wl()[sel_wl]
        st.caption(f"📋 {len(tickers)} spółek w {sel_wl}")

    if not tickers: tickers=list(BUILTIN_WL.values())[0]

    c_run,c_log=st.columns([5,1])
    with c_run: run_scan=st.button("🚀 Uruchom skanowanie",use_container_width=True)
    with c_log: show_log=st.checkbox("Log",False)

    st.markdown("---")

    if run_scan:
        log=[]
        prog=st.progress(0); stxt=st.empty(); results=[]
        for i,t in enumerate(tickers):
            prog.progress((i+1)/len(tickers))
            stxt.markdown(f"Analizuję `{t}` — {i+1}/{len(tickers)} | ✅ **{len(results)}**")
            r=get_stock(t)
            if r: results.append(r); log.append(f"✅ {t}: {r['cls']} RS={r['rs']:.0f}")
            else: log.append(f"SKIP {t}")
            time.sleep(0.15)
        prog.empty(); stxt.empty()
        if show_log:
            with st.expander(f"Log ({len(log)})"): st.code("\n".join(log))
        if not results: st.error("Brak wyników — zmień watchlistę lub spróbuj ponownie")
        else:
            st.session_state["scan_results"]=results
            st.session_state["scan_time"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state["stbl_sort"]="rs"
            st.session_state["stbl_asc"]=False

    if "scan_results" in st.session_state:
        rows=st.session_state["scan_results"]
        scan_time=st.session_state.get("scan_time","")

        # ── STAT CARDS ──
        c1,c2,c3,c4,c5,c6=st.columns(6)
        c1.metric("Wszystkich",len(rows))
        c2.metric("A+ Super",sum(1 for r in rows if r["cls"]=="A+"))
        c3.metric("A Leads",sum(1 for r in rows if r["cls"].startswith("A")))
        c4.metric("+ Ready",sum(1 for r in rows if r["sign"]=="+"))
        c5.metric("RVOL 1.5x+",sum(1 for r in rows if r["rvol"]>=1.5))
        c6.metric("Stage 2A/B",sum(1 for r in rows if r["stage"] in ("2A","2B")))

        # ── FILTRY ──
        st.markdown("""<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;
        padding:12px 16px;margin-bottom:10px">
        <div style="font-size:11px;font-weight:700;color:#6c8eff;margin-bottom:10px">🔍 Filtry</div>
        </div>""", unsafe_allow_html=True)

        f1,f2,f3,f4=st.columns(4)
        with f1: fcls=st.selectbox("Klasa (A-F)",["Wszystkie","A+","A","A-","B+","B","B-","C","D","E"])
        with f2: fstg=st.selectbox("Stage (Weinstein)",["Wszystkie","2A","2B","2C","1B","3A","4A"])
        with f3: fsgn=st.selectbox("Sygnał",["Wszystkie","+ Ready","Neutral","− Extended"])
        with f4: frvol=st.selectbox("RVOL (50D)",["Wszystkie","≥ 1.5x","≥ 2.0x"])

        f5,f6,f7,f8=st.columns(4)
        with f5: frs=st.number_input("Min RS Score",0,99,0,key="frs")
        with f6: fadr=st.number_input("Min ADR%",0.0,20.0,0.0,0.5,key="fadr")
        with f7: fext_max=st.number_input("Max ATR Ext (0=wył.)",0.0,10.0,0.0,0.5,key="fext",
                                           help="Wyklucza spółki overextended. Np. 3.0")
        with f8: flod_max=st.number_input("Max LoD Dist% (0=wył.)",0.0,100.0,0.0,5.0,key="flod",
                                           help="Jeff Sun: wejście gdy LoD < 60% ATR")

        f9,f10,f11,f12=st.columns(4)
        with f9:  favgdv=st.number_input("Min Avg$Vol w mln (0=wył.)",0.0,500.0,0.0,5.0,key="favgdv",
                                          help="Avg Dollar Volume 50D. Min $10M = dobra płynność")
        with f10: finside=st.selectbox("Inside Day (VCP)",["Wszystkie","Tak","Nie"],key="finside")
        with f11: fsect=st.text_input("Sektor (fragment)",key="fsect",placeholder="np. Technology").strip()
        with f12: fshort=st.number_input("Max Short Float%",0.0,100.0,0.0,5.0,key="fshort",
                                          help="Wysoki short float = potencjalny squeeze")

        filtered=rows[:]
        if fcls!="Wszystkie":    filtered=[r for r in filtered if r["cls"].startswith(fcls)]
        if fstg!="Wszystkie":    filtered=[r for r in filtered if r["stage"]==fstg]
        if fsgn=="+ Ready":      filtered=[r for r in filtered if r["sign"]=="+"]
        if fsgn=="− Extended":   filtered=[r for r in filtered if r["sign"]=="-"]
        if frvol=="≥ 1.5x":      filtered=[r for r in filtered if r["rvol"]>=1.5]
        if frvol=="≥ 2.0x":      filtered=[r for r in filtered if r["rvol"]>=2.0]
        if frs>0:                 filtered=[r for r in filtered if r["rs"]>=frs]
        if fadr>0:                filtered=[r for r in filtered if r["adr"]>=fadr]
        if fext_max>0:            filtered=[r for r in filtered if r["atr_ext"]<=fext_max]
        if flod_max>0:            filtered=[r for r in filtered if (r.get("lod_dist") or 999)<=flod_max]
        if favgdv>0:              filtered=[r for r in filtered if (r.get("avg_dv") or 0)>=favgdv]
        if finside=="Tak":        filtered=[r for r in filtered if r.get("inside_day")]
        if finside=="Nie":        filtered=[r for r in filtered if not r.get("inside_day")]
        if fsect:                 filtered=[r for r in filtered if fsect.lower() in (r.get("sector","") or "").lower()]
        if fshort>0:              filtered=[r for r in filtered if 0<(r.get("short_float") or 0)<=fshort]

        # ── SORT STATE ──
        if "stbl_sort" not in st.session_state:
            st.session_state["stbl_sort"]="rs"; st.session_state["stbl_asc"]=False
        sk=st.session_state["stbl_sort"]; sa=st.session_state["stbl_asc"]
        filtered.sort(key=lambda x:(x.get(sk) or 0),reverse=not sa)

        st.caption(f"Wyświetlane: **{len(filtered)}** spółek · skan: `{scan_time}` · Sortowanie: **{sk}** {'↑' if sa else '↓'} · kliknij nagłówek kolumny aby zmienić")

        # ── SORTOWANIE — przyciski nad tabelą ──
        SORT_MAP={
            "RS ▼":"rs","Score":"score","ADR%":"adr","RVOL":"rvol",
            "Cena":"price","1D%":"chg1d","ATR Ext":"atr_ext","R-R":"rr",
            "1M%":"ret1m","3M%":"ret3m","52W":"dist52","Vol $M":"vol_m",
        }
        srt_cols=st.columns(len(SORT_MAP)+1)
        for i,(lbl,key) in enumerate(SORT_MAP.items()):
            with srt_cols[i]:
                active=(sk==key)
                arrow=(" ↑" if sa else " ↓") if active else ""
                if st.button(f"{lbl}{arrow}",key=f"srt_{key}",
                             use_container_width=True,
                             type="primary" if active else "secondary"):
                    if sk==key: st.session_state["stbl_asc"]=not sa
                    else: st.session_state["stbl_sort"]=key; st.session_state["stbl_asc"]=False
                    st.rerun()
        with srt_cols[-1]:
            st.caption(f"{len(filtered)} spółek")

        # Re-sort after button click
        sk=st.session_state.get("stbl_sort","rs")
        sa=st.session_state.get("stbl_asc",False)
        filtered.sort(key=lambda x:(x.get(sk) or 0),reverse=not sa)

        # ── TABELA ──
        TH_A=TH+";color:#6c8eff;border-bottom:2px solid #6c8eff"
        def th_s(label,key=None):
            s=TH_A if key and sk==key else TH
            return f'<th style="{s}">{label}</th>'

        all_cols=[("TICKER",None),("KLASA",None),("SCORE","score"),("SYGNAŁ",None),
                  ("STAGE",None),("RS","rs"),("ADR%","adr"),("RVOL50","rvol"),
                  ("CENA $","price"),("1D%","chg1d"),("ATR EXT","atr_ext"),
                  ("LoD%","lod_dist"),("ID",None),("VARS",None),("VARS★","vars_score"),
                  ("R-R","rr"),("1M%","ret1m"),("3M%","ret3m"),("52W","dist52"),
                  ("MA",None),("AVG$V","avg_dv"),("FLOAT%","float_pct"),
                  ("SHORT%","short_float"),("SEKTOR",None),
                  ("SL","sl1"),("T2","t2"),("TV",None)]
        thead="<thead><tr>"+"".join(th_s(l,k) for l,k in all_cols)+"</tr></thead>"
        body=""
        for r in filtered:
            tv=f'<a href="https://www.tradingview.com/chart/?symbol={r["ticker"]}" target="_blank" style="color:#555;font-size:11px;text-decoration:none">TV</a>'
            tk=f'<a href="https://finance.yahoo.com/quote/{r["ticker"]}" target="_blank" style="color:#6c8eff;font-weight:700;text-decoration:none;font-size:12px">{r["ticker"]}</a>'
            sec_txt=r.get("sector","—") or "—"; sec_short=sec_txt[:12]
            vs=r.get("vars_score",0) or 0; vs_c="#26ff7f" if vs>=8 else "#f0c040" if vs>=5 else "#7a8299"
            avd=r.get("avg_dv") or 0; avd_c="#4ade80" if avd>=10 else "#e84545"
            body+=(f'<tr style="border-bottom:1px solid #161920">'
                  +f'<td style="{TD}">{tk}</td>'
                  +f'<td style="{TD}">{cls_pill(r["cls"])}</td>'
                  +f'<td style="{TD}">{score_bar(r["score"])}</td>'
                  +f'<td style="{TD}">{sgn_pill(r["sign"])}</td>'
                  +f'<td style="{TD}">{stg_pill(r["stage"])}</td>'
                  +f'<td style="{TD}">{rs_bar_html(r["rs"])}</td>'
                  +f'<td style="{TD};font-weight:600">{r["adr"]:.1f}%</td>'
                  +f'<td style="{TD}">{rvol_html(r["rvol"])}</td>'
                  +f'<td style="{TD}"><strong>${r["price"]:.2f}</strong></td>'
                  +f'<td style="{TD}">{pct_html(r["chg1d"])}</td>'
                  +f'<td style="{TD}">{atr_bar_html(r["atr_ext"])}</td>'
                  +f'<td style="{TD}">{lod_dist_html(r.get("lod_dist"))}</td>'
                  +f'<td style="{TD}">{inside_day_html(r.get("inside_day"))}</td>'
                  +f'<td style="{TD}">{vars_html(r["vars"])}</td>'
                  +f'<td style="{TD}"><span style="color:{vs_c};font-weight:700;font-size:10px">{vs:.1f}</span></td>'
                  +f'<td style="{TD}">{rr_html(r["rr"])}</td>'
                  +f'<td style="{TD}">{pct_html(r["ret1m"])}</td>'
                  +f'<td style="{TD}">{pct_html(r["ret3m"])}</td>'
                  +f'<td style="{TD}">{dist52_html(r["dist52"])}</td>'
                  +f'<td style="{TD}">{ma_html(r["ma_e10"],r["ma_s20"],r["ma_s50"],r["ma_s200"])}</td>'
                  +f'<td style="{TD};color:{avd_c};font-size:10px">{avd:.0f}M</td>'
                  +f'<td style="{TD}">{float_pct_html(r.get("float_pct"))}</td>'
                  +f'<td style="{TD}">{float_pct_html(r.get("short_float"))}</td>'
                  +f'<td style="{TD};color:#7a8299;font-size:10px">{sec_short}</td>'
                  +f'<td style="{TD};color:#e84545;font-size:10px">${r["sl1"]:.2f}</td>'
                  +f'<td style="{TD};color:#26a65b;font-size:10px">${r["t2"]:.2f}</td>'
                  +f'<td style="{TD}">{tv}</td></tr>')

        st.markdown(tbl_wrap(f'<table style="width:100%;border-collapse:collapse;min-width:1600px">{thead}<tbody>{body}</tbody></table>'),unsafe_allow_html=True)
        st.markdown("---")
        csv=pd.DataFrame(filtered).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Eksportuj CSV",csv,f"scan_{datetime.date.today()}.csv","text/csv")
    else:
        st.info("Wybierz watchlistę lub wpisz tickery i kliknij **🚀 Uruchom skanowanie**")

# ═══════════════════════════════════════════════════════════════
# PAGE 3: PLAYBOOK
# ═══════════════════════════════════════════════════════════════
elif page == "📚  Playbook":
    st.markdown("# 📚 Playbook & Strategy")
    st.markdown("*Rutyna · Checklista · Kalkulator · Definicje · System A-F · Stage · Focus List*")
    st.markdown("---")

    tab1,tab2,tab3,tab4,tab5,tab6,tab7=st.tabs([
        "📋 Rutyna pracy","✅ Checklista","💰 Kalkulator",
        "🏷️ System A-F","📐 Wskaźniki","📊 Stage","🎯 Focus List"
    ])

    # ══════ TAB 1: RUTYNA ══════
    with tab1:
        st.markdown("### Rutyna pracy ze skanerem — krok po kroku")

        def step_card(num, title, color, items, note=""):
            items_html = "".join(
                f'<div style="font-size:11px;color:#b0b8cc;padding:3px 0;border-bottom:1px solid #1e2230">{x}</div>'
                for x in items
            )
            note_html = f'<div style="font-size:10px;color:#7a8299;margin-top:6px;font-style:italic">{note}</div>' if note else ""
            html = (
                '<div style="background:#161920;border-left:4px solid ' + color + ';border-radius:8px;padding:12px 16px;margin-bottom:10px">'
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
                '<div style="background:' + color + ';color:#000;width:24px;height:24px;border-radius:50%;'
                'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;flex-shrink:0">' + str(num) + '</div>'
                '<div style="font-size:13px;font-weight:700;color:' + color + '">' + title + '</div>'
                '</div>' + items_html + note_html + '</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

        st.markdown("#### 🌅 PRZED SESJĄ (pre-market)")
        step_card(1,"Page 1 — Market Radar: Kontekst rynku","#6c8eff",[
            "Risk-On czy Risk-Off? → jeśli RISK-OFF = nie szukasz nowych wejść",
            "Breadth: ile sektorów nad SMA50? → <40% = gotówka, 40-60% = małe pozycje, >60% = normalnie",
            "RS Line Direction: ile sektorów ma ↑ vs ↓ → chcesz przewagi rosnących",
            "Quadrant chart: które sektory w STRONG? → zapisujesz 2-3 do dalszej pracy",
        ],"Jeff Sun i Franczesko: zawsze zacznij od kontekstu rynku, nie od spółek")

        step_card(2,"Page 2 — Stock Radar: Załaduj watchlistę","#4ade80",[
            "Wybierz watchlistę (wczoraj przygotowaną post-market)",
            "Kliknij Uruchom skanowanie — w tym czasie obserwuj Page 1",
            "Watchlista to lista pre-filtrowana — nie skanujesz całego rynku rano",
        ],"Watchlista = praca post-market z poprzedniego dnia. Rano tylko weryfikujesz.")

        step_card(3,"Filtry — eliminacja słabych spółek","#f0c040",[
            "Klasa: A lub B | Stage: 2A lub 2B",
            "Min RS: 70 | Min ADR%: 3.0 | Min Avg$Vol: 10M",
            "Max ATR Ext: 3.0 (eliminuje overextended)",
            "Sygnał: + Ready | Max LoD Dist%: 60",
        ],"Po tych filtrach zostajesz z 20-40% listy = Twoja Focus List")

        step_card(4,"Analiza tabeli — wybór kandydatów","#26ff7f",[
            "Sortuj po Score malejąco — najsilniejsze na górze",
            "Dla top 5: KLASA → RS → ATR EXT → LoD% → VARS → ID → R-R → RVOL → SEKTOR → MA",
            "Spółka która przejdzie wszystkie punkty = prime setup",
            "Kliknij TV przy spółce → potwierdź setup na wykresie TradingView",
        ],"Skaner = lista kandydatów. Wykres = ostateczne potwierdzenie.")

        st.markdown("#### 📈 W TRAKCIE SESJI")
        step_card(5,"Execution — czekasz na sygnał wejścia","#c084fc",[
            "Wariant 1: Cena wybija ORH + RVOL >= 1.5x → wchodzisz",
            "Wariant 2: M30 Re-ORH (reclaim po 30 min) + RVOL >= 1.0x → wchodzisz",
            "Wariant 3: Pullback do EMA10 na niskim RVOL → wchodzisz",
            "Jeśli do 30 min żadna spółka nie spełnia warunków → NIE WCHODZISZ",
            "Sprawdź LoD Dist% W MOMENCIE WEJŚCIA — musi nadal być < 60%",
        ],'Jeff Sun: "Patience is the edge." Lepszy brak transakcji niż zły entry.')

        step_card(6,"Trade Management — T+3","#fb923c",[
            "T = dzień wejścia | T+1, T+2, T+3 = kolejne sesje (bez weekendów)",
            "T+3 brak ruchu → rozważ wyjście (setup nie pracuje)",
            "T+3 cena > entry + 1R → przesuń SL na breakeven",
            "T1 (2R osiągnięty) → sprzedaj 33%, przesuń SL na BE",
            "T2 (3R osiągnięty) → sprzedaj kolejne 33%, trzymaj resztę na EMA10",
        ])

        st.markdown("#### 🌙 PO SESJI (post-market)")
        step_card(7,"Aktualizuj watchlisty — przygotowanie na jutro","#26a65b",[
            "Spółki które wybiły dziś ale nie weszłeś → zostają na watchliście",
            "Spółki które złamały strukturę → usuwasz",
            "Nowe spółki ze skanerów Finviz/TradingView → dodajesz",
            "Sprawdź kalendarz wyników na najbliższe 14 dni → unikasz earnings zone",
        ],"Jeff Sun: 14 skanerów post-market każdego wieczoru.")

        st.markdown("---")
        st.markdown(
            '<div style="background:#0f3320;border:1px solid #166534;border-radius:8px;padding:12px 16px">'
            '<div style="font-size:12px;font-weight:700;color:#4ade80;margin-bottom:6px">Złota zasada całego procesu</div>'
            '<div style="font-size:11px;color:#b0b8cc">'
            '<b style="color:#e2e6f0">Market Radar</b> (kontekst) → '
            '<b style="color:#e2e6f0">Stock Radar</b> (kandydaci) → '
            '<b style="color:#e2e6f0">TradingView</b> (potwierdzenie) → '
            '<b style="color:#e2e6f0">Execution</b> (ORH + RVOL) → '
            '<b style="color:#e2e6f0">T+3 Management</b>'
            '</div></div>',
            unsafe_allow_html=True
        )

    # ══════ TAB 2: CHECKLISTA ══════
    with tab2:
        st.markdown("### Checklista przed wejściem w pozycję")
        st.caption("Zaznacz wszystkie punkty zanim wejdziesz w pozycję")
        checks=[
            "SPY/QQQ powyżej SMA50 (trend rynku wzrostowy)",
            "Breadth: >60% sektorów nad SMA50 (Risk-On potwierdzony)",
            "Sektor spółki w kwadrancie STRONG z rosnącym RS",
            "Spółka klasy A lub B (ADR > 3%, RS > 70)",
            "Stage 2A lub 2B (Weinstein trend wzrostowy)",
            "ATR Extension < 1.5x od SMA50 (nie overextended)",
            "VARS 4/5 LUB Inside Day (VCP — ciasna baza)",
            "LoD Dist < 60% ATR (wejście blisko Low dnia)",
            "RVOL >= 1.0 na otwarciu (wolumen potwierdza ruch)",
            "Avg Dollar Vol >= $10M (płynność — bez slippage)",
            "R-R >= 2.0 (min. 2x zysk do ryzyka)",
            "Stop loss zdefiniowany PRZED wejściem w pozycję",
        ]
        if "checks" not in st.session_state: st.session_state["checks"]=[False]*len(checks)
        for i,c in enumerate(checks):
            st.session_state["checks"][i]=st.checkbox(c,value=st.session_state["checks"][i],key=f"ck_{i}")
        done=sum(st.session_state["checks"]); total=len(checks)
        if done==total:
            st.success(f"Wszystkie {done}/{total} warunki spełnione. Możesz szukać setupów!")
        elif done>=8:
            st.warning(f"{done}/{total} — Prawie gotowy. Uzupełnij brakujące punkty.")
        else:
            st.error(f"{done}/{total} — Za mało warunków. Poczekaj na lepsze warunki rynkowe.")

    # ══════ TAB 3: KALKULATOR ══════
    with tab3:
        st.markdown("### Kalkulator wielkości pozycji")
        st.caption("Ryzykuj max 1-2% kapitału na jedną transakcję")
        c1,c2=st.columns(2)
        with c1:
            cap=st.number_input("Kapital ($)",100,10000000,50000,1000)
            price=st.number_input("Cena wejscia ($)",0.01,100000.0,100.0,1.0)
        with c2:
            risk_pct=st.number_input("Max ryzyko %",0.1,10.0,1.0,0.1)
            sl_price=st.number_input("Stop Loss ($)",0.01,100000.0,94.0,0.5)
        risk_amt=cap*risk_pct/100; risk_per_sh=price-sl_price
        if risk_per_sh>0:
            shares=int(risk_amt/risk_per_sh)
            st.markdown("---")
            r1,r2,r3,r4=st.columns(4)
            r1.metric("Liczba akcji",f"{shares:,}")
            r2.metric("Wartosc pozycji",f"${shares*price:,.0f}")
            r3.metric("Max strata (1R)",f"${risk_amt:,.0f}")
            r4.metric("Cel T1 (2R)",f"${price+2*risk_per_sh:.2f}")
            st.markdown("---")
            t1c,t2c,t3c=st.columns(3)
            t1c.metric("T1 — cel 2R",f"${price+2*risk_per_sh:.2f}",delta="Sprzedaj 33%, SL na BE")
            t2c.metric("T2 — cel 3R",f"${price+3*risk_per_sh:.2f}",delta="Sprzedaj kolejne 33%")
            t3c.metric("SL",f"${sl_price:.2f}",delta=f"-{risk_per_sh:.2f} na akcje")
        else:
            st.error("Stop Loss musi byc ponizej ceny wejscia")

    # ══════ TAB 4: SYSTEM A-F ══════
    with tab4:
        st.markdown("### System klasyfikacji A-F")
        classes=[
            ("A+ Super-Lead","#c084fc","#1a0a4a","ADR>5% · RS>90 · Vol>$50M",
             "Najsilniejsze liderki rynku. Potencjal multibagger. Najwyzszy priorytet."),
            ("A Lead","#4ade80","#0f3320","ADR>5% · RS>85",
             "Bardzo silne. Duzy zasieg ruchu. Zazwyczaj tech/biotech/space."),
            ("B Quality Growth","#6ee7b7","#0a2820","ADR 3-5% · RS>70",
             "Solidne trendy. Mniejszy potencjal niz A, ale bardziej przewidywalne."),
            ("C Standard Momentum","#fb923c","#2e1a06","ADR 2.5-4% · RS>55",
             "Wolniejsze spolki. Dluzsze trzymanie. Mniejszy dzienny zasieg."),
            ("D Slow Movers","#9ca3af","#1e1e28","ADR<2.5% · RS<70",
             "Blue chipy — zbyt wolne dla strategii momentum. Pomijamy."),
            ("E Broken Chart","#f87171","#2e0a0a","Cena < SMA200",
             "Trend spadkowy lub po crashu. Omijamy."),
            ("F Junk/Illiquid","#fca5a5","#300606","Cena<$5 lub vol<$5M",
             "Ryzyko manipulacji. Penny stocks. Zawsze omijamy."),
        ]
        for name,fg,bg,crit,desc in classes:
            st.markdown(
                f'<div style="background:{bg};border-left:4px solid {fg};border-radius:8px;padding:10px 14px;margin-bottom:7px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">'
                f'<span style="font-size:13px;font-weight:700;color:{fg}">Klasa {name}</span>'
                f'<span style="font-size:10px;color:{fg};background:{fg}22;padding:2px 8px;border-radius:3px">{crit}</span>'
                f'</div><p style="color:#b0b8cc;font-size:12px;margin:0">{desc}</p></div>',
                unsafe_allow_html=True
            )
        st.markdown("---")
        st.markdown("### Sygnal — jakosc setupu")
        signals=[
            ("+ Ready","#26ff7f","#0f3320","ATR Ext < 1.5 · VARS >= 4/5 · R-R >= 2.0",
             "Spolka gotowa do ruchu. Ciasna baza, mala rozciagnietosoc, dobry R-R. Priorytet."),
            ("Neutral","#6b7280","#1e1e28","Brak sygnalu",
             "Spolka w trendzie ale buduje baze. Czekaj."),
            ("Extended","#ff6b6b","#2e0a0a","ATR Ext > 3.0",
             "Za daleko od SMA50. Nie kupuj — czekaj na pullback do EMA10."),
        ]
        for name,fg,bg,crit,desc in signals:
            st.markdown(
                f'<div style="background:{bg};border-left:4px solid {fg};border-radius:8px;padding:10px 14px;margin-bottom:7px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">'
                f'<span style="font-size:13px;font-weight:700;color:{fg}">{name}</span>'
                f'<span style="font-size:10px;color:{fg};background:{fg}22;padding:2px 8px;border-radius:3px">{crit}</span>'
                f'</div><p style="color:#b0b8cc;font-size:12px;margin:0">{desc}</p></div>',
                unsafe_allow_html=True
            )

    # ══════ TAB 5: WSKAZNIKI ══════
    with tab5:
        st.markdown("### Definicje wskaznikow — wzory i przyklady")

        def ind_box(title, formula, interp, quote=""):
            q = (
                '<div style="font-size:10px;color:#6c8eff;font-style:italic;margin-top:6px;'
                'border-left:2px solid #6c8eff;padding-left:8px">' + quote + '</div>'
            ) if quote else ""
            st.markdown(
                '<div style="background:#161920;border:1px solid #252a3a;border-radius:8px;padding:12px 16px;margin-bottom:8px">'
                '<div style="font-size:12px;font-weight:700;color:#6c8eff;margin-bottom:6px">📐 ' + title + '</div>'
                '<div style="background:#0f1218;border-radius:5px;padding:8px 10px;font-family:monospace;'
                'font-size:11px;color:#4ade80;margin-bottom:6px;white-space:pre-wrap">' + formula + '</div>'
                '<div style="font-size:11px;color:#b0b8cc;line-height:1.6">' + interp + '</div>' + q + '</div>',
                unsafe_allow_html=True
            )

        ind_box(
            "Score — Composite Score (0-100)",
            "Score = RS x 0.4 + Stage_score + min(RVOL x 7.5, 15) + VARS x 3 + min(R-R x 5, 10)\nStage: 2A=20, 2B=18, 2C=12, 1B=8, 3A=4, 4A=0",
            "Laczy 5 wskaznikow w jeden numer. RS ma najwieksza wage (40%). 80+ = elite · 60-80 = dobry · <40 = slaby."
        )
        ind_box(
            "ADR% — Average Daily Range",
            "ADR% = avg(|High - Low| / Close) x 100  (za ostatnie 20 sesji)",
            "Przecietny dzienny ruch ceny. ADR>5% = Super-Lead · 3-5% = Quality · <2.5% = Slow Mover.\nPrzyklad: ADR 8% → spolka moze dac 40% zwrotu w 5 dniach.",
            'Jeff Sun: "High ADR% securities allow you to achieve significant returns with smaller position sizes"'
        )
        ind_box(
            "ATR Extension — odleglosc od SMA50",
            "ATR_Ext = (Cena - SMA50) / ATR(14)\nPrzyklad: Cena=$100, SMA50=$90, ATR=$5 → ATR_Ext = 2.0x",
            "<1.0 = Bezpieczne | 1-2 = OK | 2-3 = Uwaga | >3.0 = Overextended — NIE KUPUJ.",
            'Jeff Sun: "One core trading philosophy is all it takes to make your first million from swing trading"'
        )
        ind_box(
            "RVOL — Relative Volume (50-dniowy)",
            "RVOL = Wolumen_dzis / Sredni_wolumen_50D\nPrzyklad: Dzis 2M akcji, avg 50D = 1M → RVOL = 2.0x",
            ">2.0x = atak instytucji | >1.5x = ponadnorma | 1.0x = normalny | <0.8x = ponizej normy.\nJeff Sun: baza 50D, nie 20D jak wiekszosc.",
            'Jeff Sun: "RVOL based entry on ORH have proven statistical edge in the market"'
        )
        ind_box(
            "LoD Dist% — Low of Day Distance",
            "LoD_Dist% = (Cena - Low_dnia) / ATR x 100\nPrzyklad: Cena=$100, Low=$98, ATR=$5 → LoD = 40% (dobry entry)",
            "< 60% = DOBRY ENTRY — kupujesz blisko Low, maly drawdown do stopu.\n> 60% = ZLY ENTRY — za daleko od Low, duze ryzyko cofniecia.\nKolory: zielony <60%, czerwony >60%.",
            'Jeff Sun: "Perks of <60% LoD Execution — trading tight"'
        )
        ind_box(
            "VARS — Volatility Contraction Score (5 kropek)",
            "5 warunkow ciastosci (kazdy = 1 kropka):\n1. H-L ostatnich 5D < 50% sredniej 20D\n2. Malejace zakresy swiec\n3. Cena blisko EMA10 (odchylenie <1%)\n4. Wolumen spada w konsolidacji\n5. Cena nad EMA20",
            "4-5/5 = TIGHT | 2-3/5 = normalna | 0-1/5 = luzna baza.\nVARS 4/5 + ATR Ext <1.5 = idealny setup przed wyciem.",
            'Minervini: "The tighter the base, the bigger the breakout"'
        )
        ind_box(
            "R-R Ratio — Risk/Reward",
            "R-R = (Szczyt_20D - Cena) / (Cena - EMA10)\nPrzyklad: Cena=$100, Szczyt20D=$120, EMA10=$95 → R-R = 4.0x",
            ">=2.0x = dobry | 1.5-2.0x = akceptowalny | <1.5x = slaby.\nLicznik = potencjalny zysk. Mianownik = ryzyko (stop)."
        )
        ind_box(
            "Inside Day (ID) — sygnal VCP",
            "ID = True gdy: (High_dzis - Low_dzis) < (High_wczoraj - Low_wczoraj)",
            "Zakres dzis mniejszy niz wczoraj = kompresja zmiennosci = spolka oddycha przed wybiciem.\nSygnal VCP. Jeff Sun ma osobny skaner ID + ADR%.",
            'Jeff Sun: "I will NEVER enter a stock with prior loose price action"'
        )
        ind_box(
            "Float% i Short Float%",
            "Float% = Akcje_float / Akcje_outstanding x 100\nShort% = Akcje_shortowane / Float x 100",
            "Float% <20% = low float = duze ruchy przy malym wolumenie.\nShort% >20% = potencjalny short squeeze.",
            'Jeff Sun: "Best % performers almost always have: low float, high short, high ADR%"'
        )
        ind_box(
            "Avg $ Volume — plynnosc 50D",
            "Avg_DV = Sredni_wolumen_50D x Cena  (wynik w $M)",
            "Min $10M = akceptowalna plynnosc. $50M+ = dobra. $100M+ = swietna.\nCzerwony <$10M = ryzyko slippage.",
            'Jeff Sun: "Slippage cost me 6-7% of my 2021 total equity"'
        )
        ind_box(
            "T+3 — Trade Management",
            "T = dzien wejscia\nT+1/T+2/T+3 = kolejne sesje (bez weekendow i swiat)",
            "T+3 bez ruchu → rozwazt wyjscie.\nT+3 cena > entry+1R → przesun SL na breakeven.\nSilny ruch do T+3 → trailing EMA10."
        )
        ind_box(
            "ORH i M30 Re-ORH",
            "ORH = High z pierwszych 15-30 minut sesji\nM30 Re-ORH = powrot ceny powyzej ORH po 30 minutach",
            "Wybicie ORH + RVOL >=1.5x = sygnal wejscia.\nM30 Re-ORH = silniejszy sygnal (falstart wyeliminowany).",
            'Jeff Sun: "RVOL based entry on ORH have proven statistical edge"'
        )
        ind_box(
            "PEAD — Post-Earnings Announcement Drift",
            "PEAD = kontynuacja ruchu po zaskoczeniu wynikowym przez tygodnie\nWarunki EP: Luka >10% + RVOL >3.0x w dniu wynikow",
            "Naukowo udokumentowana anomalia rynkowa.\nRozni sie od EP (jednorazowy skok) — PEAD = drift 2-8 tygodni.\nNajlepsze okazje: 3-10 dni po pozytywnym zaskoczeniu.",
            'Jeff Sun: "PEAD provides traders an opportunity to exploit the delayed market response"'
        )

    # ══════ TAB 6: STAGE ══════
    with tab6:
        st.markdown("### Stage Analysis — Cykl zycia spolki (Weinstein)")
        stages=[
            ("Stage 1A/1B — Basing","#9ca3af","#252535",
             "Konsolidacja po trendzie spadkowym. EMA splecione. Wolumen spada. Czekaj."),
            ("Stage 2A — Breakout","#4ade80","#0f3320",
             "Wybicie z bazy. Cena > EMA10 > EMA20 > SMA50 > SMA200. RVOL wysoki. NAJLEPSZY moment wejscia."),
            ("Stage 2B — Advancing","#86efac","#172a18",
             "Silny trend wzrostowy. Pullbacki do EMA10/20 na niskim wolumenie. Trzymaj pozycje."),
            ("Stage 2C — Late Stage","#bbf7d0","#1a2c1a",
             "Trend wzrostowy ale spolka rozciagnieta. ATR Ext >2.5. Zmniejszaj pozycje."),
            ("Stage 3A — Distribution","#fb923c","#2e1a06",
             "EMA10 tnie EMA20. Instytucje sprzedaja. Zamknij pozycje."),
            ("Stage 4A — Declining","#f87171","#2e0a0a",
             "Cena pod SMA50 i SMA200. Trend spadkowy. Omijaj."),
        ]
        for name,fg,bg,desc in stages:
            st.markdown(
                f'<div style="background:{bg};border-left:5px solid {fg};border-radius:8px;padding:10px 14px;margin-bottom:8px">'
                f'<span style="font-size:13px;font-weight:700;color:{fg}">{name}</span>'
                f'<p style="color:#b0b8cc;font-size:11px;margin:5px 0 0">{desc}</p></div>',
                unsafe_allow_html=True
            )

    # ══════ TAB 7: FOCUS LIST ══════
    with tab7:
        st.markdown("### From Watchlist to Focus List — Jeff Sun Process")
        cols_fl=st.columns(3)
        stages_fl=[
            ("WATCHLIST","#1e2a4a","#6c8eff",
             ["Klasa A lub B","Stage 2A/2B lub late 1B","Avg $Vol >= $10M","Sektor w STRONG/IMPROVING","Brak earnings w 14 dniach"]),
            ("FOCUS LIST","#0f3320","#4ade80",
             ["ATR Ext < 1.5x od SMA50","VARS 4/5 LUB Inside Day","LoD Dist < 60% ATR","RVOL >= 1.0","R-R >= 2.0","RS Line rosnie"]),
            ("EXECUTION","#1a0a4a","#c084fc",
             ["Cena wybija ORH na RVOL >= 1.5x","LUB M30 Re-ORH + RVOL >= 1.0x","LUB pullback do EMA10","LoD Dist < 60% W MOMENCIE WEJSCIA","Stop loss ustawiony PRZED wejsciem"]),
        ]
        for (title,bg,fg,items),col in zip(stages_fl,cols_fl):
            with col:
                items_html="".join(
                    f'<div style="font-size:11px;color:#b0b8cc;padding:3px 0;border-bottom:1px solid #1e2230">+ {x}</div>'
                    for x in items
                )
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {fg}44;border-top:3px solid {fg};border-radius:8px;padding:12px 14px">'
                    f'<div style="font-size:13px;font-weight:700;color:{fg};margin-bottom:8px">{title}</div>'
                    f'{items_html}</div>',
                    unsafe_allow_html=True
                )
        st.markdown("---")
        st.markdown("**Klucz Jeff Suna:** *Every sustainable price expansion rally will always be preceded by a phase of price contraction/tightening. I will NEVER enter a stock with prior loose price action.*")
        st.markdown("**Sekwencja:** Market Radar → Stock Radar (A/B, VARS, LoD<60%) → Focus List → ORH + RVOL → T+3 management")


# ═══════════════════════════════════════════════════════════════
# PAGE 4: WATCHLIST MANAGER
# ═══════════════════════════════════════════════════════════════
elif page == "📋  Watchlisty":
    st.markdown("# 📋 Menedżer Watchlist")
    st.markdown("*Twórz, edytuj i zapisuj własne listy spółek*")
    st.markdown("---")

    custom=load_custom_wl()
    ICONS=["📋","🔥","📈","⚡","🛢️","🤖","💊","🏗️","🚀","💰","🌍","⭐","🎯","💎"]

    col_l,col_r=st.columns([1,2])

    with col_l:
        st.markdown("### Wbudowane")
        for name,tickers in BUILTIN_WL.items():
            if st.button(f"{name} ({len(tickers)})",key=f"b_{name}",use_container_width=True):
                st.session_state["sel_wl"]=name; st.session_state["edit_wl"]=False

        if custom:
            st.markdown("### Własne")
            for name,meta in custom.items():
                ca,cb=st.columns([5,1])
                with ca:
                    if st.button(f"{meta.get('icon','📋')} {name} ({len(meta.get('tickers',[]))})",key=f"c_{name}",use_container_width=True):
                        st.session_state["sel_wl"]=name; st.session_state["edit_wl"]=False
                with cb:
                    if st.button("✏️",key=f"e_{name}"):
                        st.session_state["sel_wl"]=name; st.session_state["edit_wl"]=True

        st.markdown("---")
        if st.button("➕ Nowa watchlista",use_container_width=True,type="primary"):
            st.session_state["sel_wl"]=None; st.session_state["edit_wl"]=True; st.session_state["new_wl"]=True

    with col_r:
        sel=st.session_state.get("sel_wl"); edit=st.session_state.get("edit_wl",False); is_new=st.session_state.get("new_wl",False)

        if edit or is_new:
            meta=custom.get(sel,{}) if sel else {}
            existing=meta.get("tickers",[])
            st.markdown(f"### {'Nowa watchlista' if is_new or not sel else f'Edytuj: {sel}'}")
            f_name=st.text_input("Nazwa *",value="" if is_new else (sel or ""),placeholder="np. Moje Oil & Gas...")
            f_icon=st.selectbox("Ikona",ICONS,index=ICONS.index(meta.get("icon","📋")) if meta.get("icon","📋") in ICONS else 0)
            imp=st.radio("Dodaj tickery",["✏️ Ręcznie","📁 Plik"],horizontal=True,key="wl_imp")
            f_tickers=[]
            if imp=="✏️ Ręcznie":
                raw=st.text_area("Tickery",value=", ".join(existing),height=100,placeholder="NVDA, AMD, TSLA\nVAL RIG")
                if raw.strip(): f_tickers=parse_tickers(raw)
            else:
                up=st.file_uploader("Plik TXT/CSV",type=["txt","csv"],key="wl_up")
                if up:
                    f_tickers=parse_tickers(up.read().decode("utf-8",errors="ignore"))
                    st.success(f"✅ {len(f_tickers)} tickerów z {up.name}")
                else: f_tickers=existing
            if f_tickers: st.caption(f"Podgląd ({len(f_tickers)}): {' · '.join(f_tickers[:10])}{'...' if len(f_tickers)>10 else ''}")
            cs,cc=st.columns(2)
            with cs:
                if st.button("💾 Zapisz",type="primary",use_container_width=True):
                    if not f_name.strip(): st.error("Podaj nazwę")
                    elif not f_tickers: st.error("Dodaj tickery")
                    else:
                        if sel and sel!=f_name.strip() and sel in custom: del custom[sel]
                        custom[f_name.strip()]={"icon":f_icon,"tickers":f_tickers,"updated":int(time.time()*1000)}
                        save_custom_wl(custom)
                        st.session_state["sel_wl"]=f_name.strip(); st.session_state["edit_wl"]=False; st.session_state["new_wl"]=False
                        st.success(f"✅ Zapisano '{f_name}' ({len(f_tickers)} spółek)"); st.rerun()
            with cc:
                if st.button("Anuluj",use_container_width=True):
                    st.session_state["edit_wl"]=False; st.session_state["new_wl"]=False; st.rerun()

        elif sel:
            all_lists=all_wl(); tickers=all_lists.get(sel,[])
            is_c=sel in custom; meta=custom.get(sel,{})
            st.markdown(f"### {meta.get('icon','📋') if is_c else ''} {sel}")
            m1,m2,m3=st.columns(3)
            m1.metric("Spółek",len(tickers)); m2.metric("Typ","Własna" if is_c else "Wbudowana")
            if is_c and meta.get("updated"):
                try: m3.metric("Zaktualizowano",datetime.datetime.fromtimestamp(meta["updated"]/1000).strftime("%d.%m.%Y"))
                except: pass
            st.markdown("**Spółki:**")
            for chunk in [tickers[i:i+10] for i in range(0,len(tickers),10)]:
                st.markdown("  ".join([f"`{t}`" for t in chunk]))
            st.markdown("---")
            ca,cb,cc=st.columns(3)
            with ca:
                if st.button("🚀 Użyj w skanerze",type="primary",use_container_width=True):
                    st.session_state["scanner_wl"]=sel; st.success(f"✅ Przejdź do Stock Radar")
            with cb:
                if st.button("📋 Duplikuj",use_container_width=True):
                    new_n=f"{sel} (kopia)"; i=2
                    while new_n in custom or new_n in BUILTIN_WL: new_n=f"{sel} (kopia {i})"; i+=1
                    custom[new_n]={"icon":"📋","tickers":list(tickers),"updated":int(time.time()*1000)}
                    save_custom_wl(custom); st.success(f"✅ Zduplikowano jako '{new_n}'"); st.rerun()
            with cc:
                if is_c and st.button("🗑️ Usuń",use_container_width=True):
                    del custom[sel]; save_custom_wl(custom)
                    st.session_state["sel_wl"]=None; st.rerun()
        else:
            st.info("Wybierz watchlistę z listy po lewej lub utwórz nową klikając **➕ Nowa watchlista**")
