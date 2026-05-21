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
SECTORS = [
    ("Półprzewodniki","SOXX"),("Cyberbezpieczeństwo","CIBR"),("Technologia","XLK"),
    ("Motoryzacja","CARZ"),("Energia Odnawialna","ICLN"),("Ochrona Zdrowia","IHF"),
    ("Oprogramowanie","IGV"),("Usługi Naftowe","OIH"),("Ropa i Gaz","XLE"),
    ("Internet i Media","FDN"),("Surowce","DJP"),("Metale Szlachetne","DBB"),
    ("Ropa i Gaz E&P","XOP"),("Telekomunikacja","IYZ"),("Nieruchomości","XLRE"),
    ("Energia Słoneczna","TAN"),("Górnicy / Metale","PICK"),("REIT","VNQ"),
    ("Transport i Logistyka","IYT"),("Lit i Baterie","LIT"),("Biotechnologia","XBI"),
    ("Dobra Podstawowe","XLP"),("Stal","SLX"),("Ubezpieczenia","KIE"),
    ("AI i Robotyka","ROBT"),("Kasyna i Hazard","BETZ"),("Dobra Uznaniowe","XLY"),
    ("Chmura Obliczeniowa","WCLD"),("Bankowość","KBE"),("Usługi Biznesowe","VFH"),
    ("Rynki Wschodzące","EEM"),("Finanse","XLF"),("Genomika","ARKG"),
    ("Komunikacja","XLC"),("Małe Spółki","IWM"),("Przemysł","XLI"),
    ("Użytk. Publiczna","XLU"),("Farmacja","PPH"),("Fintech","FINX"),
    ("Podróże i Hotele","PEJ"),("Żywność","MOO"),("Materiały","XLB"),
    ("Infrastruktura","PAVE"),("Lotnictwo i Obrona","ITA"),("Detaliczny","XRT"),
    ("Linie Lotnicze","JETS"),("Górnictwo Złoto","GDX"),("Budownictwo","XHB"),
    ("Urządzenia Medyczne","IHI"),("Energia Uran","URA"),("Data Center","SRVR"),
]

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
def calc_rvol(vol,n=20):
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
        h=yf.Ticker(etf).history(period="6mo",interval="1d",auto_adjust=True)
        if h is None or len(h)<22: return None
        c,v=h["Close"].dropna(),h["Volume"].dropna()
        spy=get_spy(); ret=c.pct_change().dropna(); ret.index=ret.index.normalize()
        common=ret.index.intersection(spy.index)
        rs=calc_rs(ret.loc[common],spy.loc[common]) if len(common)>=20 else 50.0
        return {"rs":rs,"c1d":safe_pct(c,2),"c3d":safe_pct(c,4),"c5d":safe_pct(c,6),
                "c20d":safe_pct(c,21),"c60d":safe_pct(c,61),"rvol":calc_rvol(v)}
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
        rv=calc_rvol(v); vol_m=round(float(v.tail(20).mean())*p/1e6,1)
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
        return dict(ticker=ticker,cls=cls,sign=sign,stage=stage,rs=rs,adr=adr,rvol=rv,
                    price=round(p,2),chg1d=safe_pct(c,2),atr_ext=ext,vars=vars_v,rr=rr,
                    score=sc,ret1m=rn(21),ret3m=rn(63),vol_m=vol_m,
                    dist52=round((p/h52-1)*100,1),
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

    col_a,col_b = st.columns([3,1])
    with col_a: show_n=st.slider("Liczba sektorów w tabeli",10,51,30,5)
    with col_b:
        st.markdown("<br>",unsafe_allow_html=True)
        run_sec=st.button("🔄 Odśwież sektory",use_container_width=True)

    if run_sec: st.cache_data.clear()

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
    rows=[{"name":n,"etf":v["etf"],"rs":v.get("rs",50),"c1d":v.get("c1d",0),
           "c3d":v.get("c3d",0),"c5d":v.get("c5d",0),"c20d":v.get("c20d",0),
           "c60d":v.get("c60d",0),"rvol":v.get("rvol",1)} for n,v in raw.items()]
    rows.sort(key=lambda x:x["rs"],reverse=True)

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
    st.markdown(f"### Pełny ranking sektorów (top {show_n})")
    display=rows[:show_n]
    head=f'<thead><tr>{"".join(f"<th style=\"{TH}\">{c}</th>" for c in ["#","Sektor","ETF","RS","1D%","3D%","5D%","20D%","60D%","RVOL","Kwadrant"])}</tr></thead>'
    body=""
    for i,r in enumerate(display,1):
        if r["c5d"]>=0 and r["c20d"]>=0: ql,qc="Strong","#26a65b"
        elif r["c5d"]>=0:                 ql,qc="Improving","#6c8eff"
        elif r["c20d"]>=0:                ql,qc="Weakening","#f0c040"
        else:                              ql,qc="Weak","#e84545"
        rv=r["rvol"]; rvc="#60a5fa" if rv>=2 else "#a5f3fc" if rv>=1.5 else "#7a8299"
        body+=f'<tr style="border-bottom:1px solid #1a1e2a"><td style="{TD};color:#7a8299;font-size:10px">{i}</td><td style="{TD};font-weight:600">{r["name"]}</td><td style="{TD};color:#6c8eff;font-weight:700">{r["etf"]}</td><td style="{TD}">{rs_bar_html(r["rs"])}</td><td style="{TD}">{chg_tag(r["c1d"])}</td><td style="{TD}">{chg_tag(r["c3d"])}</td><td style="{TD}">{chg_tag(r["c5d"])}</td><td style="{TD}">{chg_tag(r["c20d"])}</td><td style="{TD}">{chg_tag(r["c60d"])}</td><td style="{TD};color:{rvc};font-weight:{"700" if rv>=1.5 else "400"}">{rv:.1f}x{" 🔵" if rv>=2 else ""}</td><td style="{TD}"><span style="color:{qc};font-size:10px;font-weight:700">{ql}</span></td></tr>'
    st.markdown(tbl_wrap(f'<table style="width:100%;border-collapse:collapse;min-width:900px"><thead>{head}</thead><tbody>{body}</tbody></table>'),unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 2: STOCK RADAR
# ═══════════════════════════════════════════════════════════════
elif page == "🔬  Stock Radar":
    st.markdown("# 🔬 Stock Radar")
    st.markdown("*Klasyfikacja A-F · Composite Score · ATR Bar · EP Timer · RVOL*")
    st.markdown("---")

    st.markdown("### 📥 Importuj listę spółek")
    imp_method=st.radio("",["✏️ Wpisz ręcznie","📁 Wgraj plik TXT/CSV","📋 Wybierz watchlistę"],horizontal=True,label_visibility="collapsed")
    tickers=[]
    if imp_method=="✏️ Wpisz ręcznie":
        raw=st.text_area("Tickery",height=80,placeholder="NVDA, AMD, TSLA\nAAPL MSFT\nVAL",label_visibility="collapsed")
        if raw.strip(): tickers=parse_tickers(raw)
        if tickers: st.success(f"✅ {len(tickers)} tickerów: {', '.join(tickers[:8])}{'...' if len(tickers)>8 else ''}")
    elif imp_method=="📁 Wgraj plik TXT/CSV":
        up=st.file_uploader("Plik z tickerami",type=["txt","csv"],label_visibility="collapsed")
        if up:
            content=up.read().decode("utf-8",errors="ignore")
            tickers=parse_tickers(content)
            st.success(f"✅ {len(tickers)} tickerów z **{up.name}**")
            with st.expander("Podgląd"): st.write("  ·  ".join(tickers))
    else:
        wl_names=list(all_wl().keys())
        sel_wl=st.selectbox("Watchlista",wl_names,label_visibility="collapsed")
        tickers=all_wl()[sel_wl]
        st.info(f"📋 **{sel_wl}** — {len(tickers)} spółek")

    if not tickers: tickers=list(BUILTIN_WL.values())[0]

    c_run,c_log=st.columns([3,1])
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
        if not results: st.error("Brak wyników — zmień filtry lub watchlistę")
        else:
            st.session_state["scan_results"]=results
            st.session_state["scan_time"]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if "scan_results" in st.session_state:
        rows=st.session_state["scan_results"]
        scan_time=st.session_state.get("scan_time","")

        c1,c2,c3,c4,c5,c6=st.columns(6)
        c1.metric("Wszystkich",len(rows))
        c2.metric("A+ Super",sum(1 for r in rows if r["cls"]=="A+"))
        c3.metric("A Leads",sum(1 for r in rows if r["cls"].startswith("A")))
        c4.metric("+ Ready",sum(1 for r in rows if r["sign"]=="+"))
        c5.metric("RVOL 1.5x+",sum(1 for r in rows if r["rvol"]>=1.5))
        c6.metric("Stage 2A/B",sum(1 for r in rows if r["stage"] in ("2A","2B")))

        f1,f2,f3,f4,f5=st.columns([2,2,2,2,2])
        with f1: fcls=st.selectbox("Klasa",["Wszystkie","A+","A","B+","B","C","D","E"])
        with f2: fstg=st.selectbox("Stage",["Wszystkie","2A","2B","2C","1B","3A","4A"])
        with f3: fsgn=st.selectbox("Sygnał",["Wszystkie","+ Ready","Neutral","− Extended"])
        with f4: frvol=st.selectbox("RVOL",["Wszystkie","≥ 1.5x","≥ 2.0x"])
        with f5: frs=st.number_input("Min RS",0,99,0,key="frs")

        filtered=rows[:]
        if fcls!="Wszystkie": filtered=[r for r in filtered if r["cls"].startswith(fcls)]
        if fstg!="Wszystkie": filtered=[r for r in filtered if r["stage"]==fstg]
        if fsgn=="+ Ready":   filtered=[r for r in filtered if r["sign"]=="+"]
        if fsgn=="− Extended":filtered=[r for r in filtered if r["sign"]=="-"]
        if frvol=="≥ 1.5x":   filtered=[r for r in filtered if r["rvol"]>=1.5]
        if frvol=="≥ 2.0x":   filtered=[r for r in filtered if r["rvol"]>=2.0]
        if frs>0:              filtered=[r for r in filtered if r["rs"]>=frs]
        filtered.sort(key=lambda x:x["rs"],reverse=True)

        st.caption(f"Wyświetlane: **{len(filtered)}** spółek · skan: `{scan_time}`")

        cols=["TICKER","KLASA","SCORE","SYGNAŁ","STAGE","RS","ADR%","RVOL","CENA $","1D%","ATR EXT","VARS","R-R","1M%","3M%","52W","MA CHECK","SL","T2","TV"]
        head=f'<thead><tr>{"".join(f"<th style=\"{TH}\">{c}</th>" for c in cols)}</tr></thead>'
        body=""
        for r in filtered:
            tv=f'<a href="https://www.tradingview.com/chart/?symbol={r["ticker"]}" target="_blank" style="color:#555;font-size:11px;text-decoration:none">TV</a>'
            tk=f'<a href="https://finance.yahoo.com/quote/{r["ticker"]}" target="_blank" style="color:#6c8eff;font-weight:700;text-decoration:none;font-size:12px">{r["ticker"]}</a>'
            body+=f'<tr style="border-bottom:1px solid #161920"><td style="{TD}">{tk}</td><td style="{TD}">{cls_pill(r["cls"])}</td><td style="{TD}">{score_bar(r["score"])}</td><td style="{TD}">{sgn_pill(r["sign"])}</td><td style="{TD}">{stg_pill(r["stage"])}</td><td style="{TD}">{rs_bar_html(r["rs"])}</td><td style="{TD};font-weight:600">{r["adr"]:.1f}%</td><td style="{TD}">{rvol_html(r["rvol"])}</td><td style="{TD}"><strong>${r["price"]:.2f}</strong></td><td style="{TD}">{pct_html(r["chg1d"])}</td><td style="{TD}">{atr_bar_html(r["atr_ext"])}</td><td style="{TD}">{vars_html(r["vars"])}</td><td style="{TD}">{rr_html(r["rr"])}</td><td style="{TD}">{pct_html(r["ret1m"])}</td><td style="{TD}">{pct_html(r["ret3m"])}</td><td style="{TD}">{dist52_html(r["dist52"])}</td><td style="{TD}">{ma_html(r["ma_e10"],r["ma_s20"],r["ma_s50"],r["ma_s200"])}</td><td style="{TD};color:#e84545;font-size:10px">${r["sl1"]:.2f}</td><td style="{TD};color:#26a65b;font-size:10px">${r["t2"]:.2f}</td><td style="{TD}">{tv}</td></tr>'
        st.markdown(tbl_wrap(f'<table style="width:100%;border-collapse:collapse;min-width:1500px"><thead>{head}</thead><tbody>{body}</tbody></table>'),unsafe_allow_html=True)
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

    tab1,tab2,tab3,tab4,tab5=st.tabs(["✅ Checklista","💰 Kalkulator","🏷️ System A-F","📐 Wskaźniki","📊 Stage"])

    with tab1:
        st.markdown("### Checklista przed wejściem w pozycję")
        checks=["SPY/QQQ powyżej SMA20","Risk-On — >50% sektorów nad SMA20","Sektor w kwadrancie STRONG lub IMPROVING","Spółka klasy A lub B (nie C/D/E/F)","Stage 2A lub 2B","ATR Extension < 1.5 (nie overextended)","VARS ≥ 4/5 (ciasna konsolidacja)","R-R ≥ 2.0 (dobry stosunek zysk/ryzyko)","Stop loss zdefiniowany przed wejściem"]
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
        for title,body in [
            ("ADR% — Average Daily Range","avg(|High−Low| / Close) × 100 za 20 sesji. ADR>5% = Super-Lead · 3-5% = Quality · <2.5% = Slow Mover"),
            ("ATR Extension","(Cena − SMA50) / ATR(14). Zielony <1.0 · Żółty 1-3 · Czerwony >3.0 = Overextended. NIE kupuj powyżej 3!"),
            ("VARS — 5 kropek ciasności","TIGHT = VARS 4/5 + ATR Ext <1.5 = cisza przed burzą. Sprawdza malejące zakresy H-L i bliskość EMA10."),
            ("RVOL — Relative Volume","Wolumen dziś / avg 20D. Niebieski >1.5x = ponadnorma · Jasnoniebieski >2x = atak instytucji."),
            ("Composite Score (0–100)","RS×0.4 + Stage + RVOL + VARS + R-R. Jednym spojrzeniem widzisz jakość spółki."),
            ("R-R Ratio","(Szczyt 20D − Cena) / (Cena − EMA10). Zielony ≥2.0 · Żółty 1.5-2.0 · Czerwony <1.5"),
        ]:
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
