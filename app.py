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
    c="#60a5fa" if v>=2 else "#a5f3fc" if v>=1.5 else "#7a8299"
    return f'<span style="color:{c};font-weight:{"700" if v>=1.5 else "400"}">{v:.2f}x</span>'

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

# ═══════════════════════════════════════════════════════════════
# PAGE 1: MARKET RADAR
# ═══════════════════════════════════════════════════════════════
if page == "🌍  Market Radar":
    st.markdown("# 🌍 Market & Sector Radar")
    st.markdown("*Ranking 51 sektorów — RS Score, zmiany %, RVOL, Quadrant Chart*")
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
    # Breadth widgets
    abv50_n=sum(r["abv50"] for r in rows); tot_r=max(1,len(rows)); pct50=round(abv50_n/tot_r*100)
    rs_up=sum(1 for r in rows if r["rs_dir"]=="up")
    rs_dn=sum(1 for r in rows if r["rs_dir"]=="dn")
    rs_fl=sum(1 for r in rows if r["rs_dir"]=="flat")
    bc1,bc2=st.columns(2)
    with bc1:
        bc=("#26ff7f" if pct50>=60 else "#f0c040" if pct50>=40 else "#e84545")
        st.markdown(f"""<div style="background:#161920;border:1px solid #252a3a;border-radius:7px;padding:10px 14px;margin-bottom:8px">
<div style="font-size:10px;color:#7a8299;font-weight:600;margin-bottom:5px">MARKET BREADTH — sektory ETF powyżej SMA50</div>
<div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:4px">
  <span style="color:#26ff7f">{abv50_n} above</span>
  <span style="font-weight:700;color:{bc}">{pct50}%</span>
  <span style="color:#e84545">{tot_r-abv50_n} below</span>
</div>
<div style="height:8px;background:#252a3a;border-radius:4px"><div style="width:{pct50}%;height:8px;background:{bc};border-radius:4px"></div></div>
</div>""",unsafe_allow_html=True)
    with bc2:
        st.markdown(f"""<div style="background:#161920;border:1px solid #252a3a;border-radius:7px;padding:10px 14px;margin-bottom:8px">
<div style="font-size:10px;color:#7a8299;font-weight:600;margin-bottom:5px">RS LINE DIRECTION vs SPY (5D)</div>
<div style="display:flex;gap:14px;font-size:12px;margin-top:6px">
  <span style="color:#26ff7f;font-weight:700">↑ {rs_up}</span>
  <span style="color:#7a8299">→ {rs_fl}</span>
  <span style="color:#e84545;font-weight:700">↓ {rs_dn}</span>
</div></div>""",unsafe_allow_html=True)
    # Apply category filters
    if kat_filter=="🏛️ Główne sektory S&P500": rows=[r for r in rows if r["kat"]=="sektor"]
    elif kat_filter=="🔬 Branże / Nisze": rows=[r for r in rows if r["kat"]=="branza"]
    if parent_filter!="Wszystkie": rows=[r for r in rows if r["parent"]==parent_filter]
    # default sort by RS
    if "sec_sort" not in st.session_state:
        st.session_state["sec_sort"]="rs"
        st.session_state["sec_asc"]=False
    rows.sort(key=lambda x:x.get(st.session_state["sec_sort"],0),reverse=not st.session_state["sec_asc"])

    # Risk-On/Off
    abv=sum(1 for r in rows if r["rs"]>=50)
    tot=len(rows); pct=round(abv/tot*100) if tot else 0
    ron=pct>=50
    risk_col="#0f3320" if ron else "#2e0a0a"
    risk_border="#166534" if ron else "#7f1d1d"
    risk_txt_col="#4ade80" if ron else "#f87171"
    risk_label="RISK-ON ✅" if ron else "RISK-OFF 🔴"
    st.markdown(f'<div style="background:{risk_col};border:1px solid {risk_border};border-radius:8px;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;margin-bottom:12px"><div><div style="font-size:15px;font-weight:800;color:{risk_txt_col}">{risk_label}</div><div style="font-size:10px;color:{risk_txt_col}88;margin-top:2px">{abv}/{tot} sektorów powyżej RS 50 ({pct}%)</div></div><div style="font-size:26px">{"🟢" if ron else "🔴"}</div></div>', unsafe_allow_html=True)

    # Metrics
    strong=sum(1 for r in rows if r["c5d"]>=0 and r["c20d"]>=0)
    improv=sum(1 for r in rows if r["c5d"]>=0 and r["c20d"]<0)
    weakn =sum(1 for r in rows if r["c5d"]<0  and r["c20d"]>=0)
    weak  =sum(1 for r in rows if r["c5d"]<0  and r["c20d"]<0)
    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Śr. RS Score",round(np.mean([r["rs"] for r in rows]),1))
    m2.metric("Strong ↑↑",strong); m3.metric("Improving ↑↓",improv)
    m4.metric("Weakening ↓↑",weakn); m5.metric("Weak ↓↓",weak)

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
    st.markdown("*Checklista · Kalkulator pozycji · System A-F · Wskaźniki · Stage Analysis*")
    st.markdown("---")

    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["✅ Checklista","💰 Kalkulator","🏷️ System A-F","📐 Wskaźniki","📊 Stage","🎯 Focus List"])

    with tab1:
        st.markdown("### Checklista przed wejściem w pozycję")
        checks=[
            "SPY/QQQ powyżej SMA50 (trend rynku wzrostowy)",
            "Breadth: >60% sektorów nad SMA50 (Risk-On)",
            "Sektor spółki w kwadrancie STRONG (RS Line rośnie ↑)",
            "Spółka klasy A lub B (ADR > 3%, RS > 70)",
            "Stage 2A lub 2B (Weinstein trend wzrostowy)",
            "ATR Extension < 1.5× od SMA50 (nie overextended)",
            "VARS 4/5 LUB Inside Day (VCP — ciasna baza)",
            "LoD Dist < 60% ATR (wejście blisko Low dnia)",
            "RVOL >= 1.0 na otwarciu (wolumen potwierdza ruch)",
            "Avg $Vol >= $10M (płynność, bez slippage)",
            "R-R >= 2.0 (min. 2x zysk do ryzyka)",
            "Stop loss zdefiniowany PRZED wejściem",
        ]
        if "checks" not in st.session_state: st.session_state["checks"]=[False]*len(checks)
        for i,c in enumerate(checks):
            st.session_state["checks"][i]=st.checkbox(c,value=st.session_state["checks"][i],key=f"ck_{i}")
        done=sum(st.session_state["checks"]); total=len(checks)
        if done==total: st.success(f"✅ {done}/{total} — Możesz szukać setupów!")
        else: st.warning(f"⚠️ {done}/{total} — Uzupełnij checklistę przed wejściem")

    with tab2:
        st.markdown("### Kalkulator wielkości pozycji")
        c1,c2=st.columns(2)
        with c1:
            cap=st.number_input("Kapitał ($)",100,10000000,50000,1000)
            price=st.number_input("Cena wejścia ($)",0.01,100000.0,100.0,1.0)
        with c2:
            risk_pct=st.number_input("Max ryzyko %",0.1,10.0,1.0,0.1)
            sl_price=st.number_input("Stop Loss ($)",0.01,100000.0,94.0,0.5)
        risk_amt=cap*risk_pct/100; risk_per_sh=price-sl_price
        if risk_per_sh>0:
            shares=int(risk_amt/risk_per_sh)
            st.markdown("---")
            r1,r2,r3,r4=st.columns(4)
            r1.metric("Liczba akcji",f"{shares:,}")
            r2.metric("Wartość pozycji",f"${shares*price:,.0f}")
            r3.metric("Max strata",f"${risk_amt:,.0f}")
            r4.metric("Cel T1 (2R)",f"${price+2*risk_per_sh:.2f}")
        else: st.error("Stop Loss musi być poniżej ceny wejścia")

    with tab3:
        classes=[("A+ Super-Lead","#c084fc","#1a0a4a","ADR>5% · RS>90 · Vol>$50M","Najsilniejsze liderki. Potencjał multibagger."),
                 ("A Lead","#4ade80","#0f3320","ADR>5% · RS>85","Bardzo silne. Duży zasięg ruchu."),
                 ("B Quality Growth","#6ee7b7","#0a2820","ADR 3-5% · RS>70","Solidne trendy tech/healthcare."),
                 ("C Standard Momentum","#fb923c","#2e1a06","ADR 2.5-4% · RS>55","Wolniejsze. Dłuższe trzymanie."),
                 ("D Slow Movers","#9ca3af","#1e1e28","ADR<2.5% · RS<70","Blue chipy. Zbyt wolne dla momentum."),
                 ("E Broken Chart","#f87171","#2e0a0a","Cena < SMA200","Trend spadkowy. Omijamy."),
                 ("F Junk/Illiquid","#fca5a5","#300606","Cena<$5 lub vol<$5M","Ryzyko manipulacji. Zawsze omijamy.")]
        for name,fg,bg,crit,desc in classes:
            st.markdown(f'<div style="background:{bg};border-left:4px solid {fg};border-radius:8px;padding:10px 14px;margin-bottom:7px"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px"><span style="font-size:13px;font-weight:700;color:{fg}">Klasa {name}</span><span style="font-size:10px;color:{fg};background:{fg}22;padding:2px 8px;border-radius:3px">{crit}</span></div><p style="color:#b0b8cc;font-size:12px;margin:0">{desc}</p></div>',unsafe_allow_html=True)

    with tab4:
        _inds=[
            ("ADR% — Average Daily Range",
             "avg(High-Low)/Close x100 za 20 sesji. ADR>5% = Super-Lead, 3-5% = Quality, <2.5% = Slow Mover. "
             "Jeff Sun: High ADR pozwala osiagac duze zwroty przy malych pozycjach."),
            ("ATR Extension — X x ATR od SMA50",
             "(Cena - SMA50) / ATR(14). Podstawowy wskaznik Jeff Suna. "
             "<1.0 = Bezpieczne, 1-2 = OK, 2-3 = Uwaga, >3.0 = Overextended - NIE KUPUJ. "
             "Jeff Sun: Jeden wskaznik wystarczy do pierwszego miliona ze swing tradingu."),
            ("VARS — Volatility Adjusted Relative Strength",
             "Ulepszenie klasycznego RS przez Jeff Suna. Uwzglednia zmiennosc spolki. "
             "VARS Score = RS x ciastosc konsolidacji. Spolka z ADR 8% i RS 85 jest lepsza od spolki z ADR 2% i RS 85. "
             "Wskaznik TradingView: tradingview.com/script/nbgyYwu1"),
            ("RVOL — Relative Volume (50D)",
             "Wolumen dzis / avg 50 sesji (Jeff Sun standard, nie 20!). "
             ">2.0x = atak instytucji, >1.5x = ponadnorma, <1.0 = brak zainteresowania. "
             "Jeff Sun: RVOL based entry on ORH have proven statistical edge."),
            ("LoD Dist% — Low of Day Distance",
             "(Cena - Low dnia) / ATR x 100. "
             "< 60% = DOBRY ENTRY (blisko Low, maly drawdown do stopu). "
             "> 60% = zly entry (za daleko od Low). "
             "Jeff Sun: Perks of <60% LoD Execution — klucz do ciasnych wejsc."),
            ("Inside Day — VCP sygnal",
             "Zakres dzis (High-Low) < zakres wczoraj. "
             "Sygnal kompresji zmiennosci. Poprzedza wybicia (VCP). "
             "Jeff Sun ma osobny skaner Inside Day + ADR% na TradingView. "
             "Jeff Sun: I will NEVER enter a stock with prior loose price action."),
            ("T+3 — Trade Management",
             "T = dzien wejscia. T+3 = 3 sesje pozniej (bez weekendow/swiat). "
             "Do T+3 brak ruchu = rozwazt wyjscie. "
             "Do T+3 cena > entry + 1R = przesun SL na breakeven. "
             "Do T+3 silny ruch = trailing EMA10."),
            ("ORH / M30 Re-ORH",
             "ORH = Opening Range High — szczyt z pierwszych minut sesji. "
             "M30 Re-ORH = spolka spada ponizej ORH, ale po 30 minutach go odzyskuje. "
             "Bardzo silny sygnal kontynuacji przy wysokim RVOL."),
            ("PEAD — Post-Earnings Drift",
             "Cena kontynuuje ruch w kierunku niespodzianki wynikowej przez tygodnie. "
             "Rozni sie od EP (jednorazowy skok) — PEAD = dlugotrwaly drift. "
             "Jeff Sun: PEAD provides traders opportunity to exploit the delayed market response."),
            ("Float% i Short Float%",
             "Float% = akcje w wolnym obrocie / wszystkie akcje. "
             "Niski Float% (<20%) = kazdy duzy zakup mocno przesuwa cene. "
             "Short Float% = ile % float jest shortowane. Wysoki (>20%) = potencjalny short squeeze. "
             "Jeff Sun: Best % performers almost always have: low float, high short, high ADR%."),
            ("Avg $ Volume — plynnosc",
             "Sredni dzienny obrot w dolarach (50 sesji). "
             "Jeff Sun stracil 6-7% equity przez slippage w 2021. "
             "Min $10M/dzien = akceptowalna plynnosc. $50M+ = dobra. $100M+ = swietna."),
            ("Composite Score (0-100)",
             "RS x0.4 + Stage + RVOL + VARS + R-R. "
             "80+ = elite setup, 60-80 = dobry, <40 = slaby."),
        ]
        for title,body in _inds:
            with st.expander(f"📐 {title}"):
                st.markdown(body)

    with tab5:
        stages=[("2A — Breakout","#4ade80","#0f3320","NAJLEPSZY moment wejścia. Wybicie z bazy, RVOL wysoki."),
                ("2B — Advancing","#86efac","#172a18","Silny trend wzrostowy. Pullbacki do EMA10/20. Trzymaj."),
                ("2C — Late Stage","#bbf7d0","#1a2c1a","Rozciągnięta. Zmniejszaj pozycję. Nie dokupuj."),
                ("1B — Basing","#93c5fd","#1a2030","Buduje bazę po Stage 1A. Czekaj na wybicie."),
                ("3A — Distribution","#fb923c","#2e1a06","EMA10 tnie EMA20. Instytucje sprzedają. Zamknij."),
                ("4A — Declining","#f87171","#2e0a0a","Trend spadkowy. Omijaj. Szukaj shorta lub stój z boku.")]
        for name,fg,bg,desc in stages:
            st.markdown(f'<div style="background:{bg};border-left:4px solid {fg};border-radius:8px;padding:10px 14px;margin-bottom:7px"><span style="font-size:13px;font-weight:700;color:{fg}">{name}</span><p style="color:#b0b8cc;font-size:12px;margin:5px 0 0">{desc}</p></div>',unsafe_allow_html=True)

    with tab6:
        st.markdown("### 🎯 From Watchlist to Focus List — Jeff Sun Process")
        cols_fl=st.columns(3)
        stages_fl=[
            ("📋 WATCHLIST","#1e2a4a","#6c8eff",
             ["Klasa A lub B (ADR>3%, RS>70)","Stage 2A/2B lub late 1B","Avg $Vol >= $10M","Sektor w STRONG/IMPROVING","Brak earnings w 14 dniach"]),
            ("🎯 FOCUS LIST","#0f3320","#4ade80",
             ["ATR Ext < 1.5x od SMA50","VARS 4/5 LUB Inside Day","LoD Dist < 60% ATR","RVOL >= 1.0","R-R >= 2.0","RS Line rośnie ↑"]),
            ("🚀 EXECUTION","#1a0a4a","#c084fc",
             ["Cena wybija ORH na RVOL >= 1.5x","LUB M30 Re-ORH (reclaim po 30 min)","LUB pullback do EMA10 (niski vol)","LoD Dist < 60% W MOMENCIE WEJŚCIA","Stop loss ustawiony PRZED wejściem"]),
        ]
        for (title,bg,fg,items),col in zip(stages_fl,cols_fl):
            with col:
                items_html="".join(f'<div style="font-size:11px;color:#b0b8cc;padding:3px 0;border-bottom:1px solid #252a3a22">✓ {x}</div>' for x in items)
                st.markdown(f'<div style="background:{bg};border:1px solid {fg}44;border-top:3px solid {fg};border-radius:8px;padding:12px 14px"><div style="font-size:13px;font-weight:700;color:{fg};margin-bottom:8px">{title}</div>{items_html}</div>',unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""**Klucz Jeff Suna:** *"Every sustainable price expansion rally will always be preceded by a phase of price contraction/tightening. I will NEVER enter a stock with prior loose price action."*

**Sekwencja:**  
`Market Radar` → `STRONG sektor` → `Stock Radar` (A/B, VARS, LoD<60%) → `Focus List` → `ORH + RVOL` → `T+3 management`""")

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
