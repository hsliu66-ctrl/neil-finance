#!/usr/bin/env python3
"""Official U.S. Treasury and ECB reference rates. Never fabricate missing observations."""
import argparse, datetime as dt, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
TENORS={"1M":"BC_1MONTH","2M":"BC_2MONTH","3M":"BC_3MONTH","6M":"BC_6MONTH","1Y":"BC_1YEAR","2Y":"BC_2YEAR","3Y":"BC_3YEAR","5Y":"BC_5YEAR","7Y":"BC_7YEAR","10Y":"BC_10YEAR","20Y":"BC_20YEAR","30Y":"BC_30YEAR"}
SRC_T="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
SRC_E="https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
def lname(tag): return tag.rsplit("}",1)[-1].upper()
def xml(url):
    req=urllib.request.Request(url,headers={"User-Agent":"NeilFinancialDesk/2.0","Accept":"application/xml,text/xml,*/*"})
    with urllib.request.urlopen(req,timeout=35) as f: return ET.fromstring(f.read())
def get(path,default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if not path.exists() or path.read_text(encoding="utf-8")!=text:
        path.write_text(text,encoding="utf-8")
def n(value,lower,upper):
    v=float(value)
    if not lower<=v<=upper: raise ValueError("outlier")
    return round(v,6)
def treasury():
    out={}
    year=dt.datetime.now(dt.timezone.utc).year
    for yr in (year-1,year):
        try:
            root=xml(SRC_T+"?data=daily_treasury_yield_curve&field_tdr_date_value="+str(yr))
            for entry in root.iter():
                if lname(entry.tag)!="ENTRY": continue
                props={lname(e.tag):(e.text or "").strip() for e in entry.iter() if e.text}
                raw=props.get("NEW_DATE","").split("T")[0]
                try:
                    date=dt.datetime.strptime(raw,"%Y-%m-%d").date().isoformat() if "-" in raw else dt.datetime.strptime(raw,"%m/%d/%Y").date().isoformat()
                except ValueError: continue
                vals={}
                for name,tag in TENORS.items():
                    try: vals[name]=n(props[tag],0,25)
                    except (KeyError,ValueError,TypeError): continue
                if len(vals)>=10 and "2Y" in vals and "10Y" in vals: out[date]=vals
        except Exception as exc: print("Treasury feed unavailable",yr,str(exc))
    return out
def ecb():
    out={}
    try:
        root=xml(SRC_E)
        for el in root.iter():
            if lname(el.tag)!="CUBE" or "time" not in el.attrib: continue
            day=el.attrib["time"]
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",day): continue
            rates={}
            for child in el:
                if "currency" in child.attrib:
                    try: rates[child.attrib["currency"]]=n(child.attrib["rate"],.000001,10000)
                    except (ValueError,KeyError): continue
            if "USD" not in rates: continue
            vals={"ECB_EURUSD":rates["USD"]}
            for cc in ("JPY","CNY"):
                if cc in rates: vals["ECB_USD"+cc]=round(rates[cc]/rates["USD"],6)
            out[day]=vals
    except Exception as exc: print("ECB feed unavailable",str(exc))
    return out
def daily():
    history=get(DATA/"history.json",{"schema":1,"series":{}})
    store=history.setdefault("series",{})
    t,f=treasury(),ecb()
    for src,records in (("U.S. Treasury",t),("ECB",f)):
        for date,values in records.items():
            for key,value in values.items():
                series=("UST_"+key) if src=="U.S. Treasury" else key
                existing={(r["date"],r["source"]):r for r in store.get(series,[])}
                existing[(date,src)]={"date":date,"value":value,"source":src}
                store[series]=sorted(existing.values(),key=lambda r:r["date"])
    if not store:
        print("No official data. Empty placeholders remain; no fake market observations.")
        return
    latest={"schema":1,"series":{},"sources":{"treasury":SRC_T,"ecb":SRC_E},"notes":["U.S. Treasury par yields: percent, official observation date; publication lag possible.","ECB EUR/USD reference; USD/JPY and USD/CNY are derived cross-rates, NOT spot closing prices.","No automatic USD/TWD Taipei close, USD/CNH or US equity prices."]}
    for key,rows in sorted(store.items()):
        if rows: latest["series"][key]=rows[-1]
    save(DATA/"history.json",history)
    save(DATA/"latest.json",latest)
    print("Verified history updated:",len(store),"series",len(t),"Treasury dates",len(f),"ECB dates")
def articles():
    file=(ROOT/"reports.js").read_text(encoding="utf-8")
    m=re.search(r"window\.NEIL_REPORTS\s*=\s*(\[[\s\S]*\])\s*;\s*$",file)
    if not m: raise ValueError("Unknown article schema")
    return json.loads(m.group(1))
def archive():
    today=dt.datetime.now(dt.timezone.utc).date()
    sunday=today-dt.timedelta(days=today.weekday()+1)
    monday=sunday-dt.timedelta(days=6)
    key=monday.strftime("%G-W%V")
    first,last=monday.isoformat(),sunday.isoformat()
    h=get(DATA/"history.json",{"series":{}})
    metrics={}
    for name,rows in h.get("series",{}).items():
        subset=[r for r in rows if first<=r.get("date","")<=last]
        if subset: metrics[name]={"first":subset[0],"last":subset[-1],"observations":len(subset)}
    links=[{"id":r["id"],"title":r.get("title",""),"date":r.get("date",""),"category":r.get("category",""),"sample":bool(r.get("sample",True))} for r in articles() if first<=r.get("date","")<=last]
    rel="data/weekly/"+key+".json"
    save(ROOT/rel,{"schema":1,"week":key,"from":first,"to":last,"market":metrics,"articles":links})
    idx=get(DATA/"weekly-index.json",{"weeks":[]})
    rows={w["week"]:w for w in idx.get("weeks",[])}
    rows[key]={"week":key,"from":first,"to":last,"dataFile":rel,"articleCount":len(links),"seriesCount":len(metrics)}
    save(DATA/"weekly-index.json",{"weeks":sorted(rows.values(),key=lambda r:r["week"],reverse=True)})
    print("Completed week archived:",key,len(links),"reports",len(metrics),"series")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--daily",action="store_true");p.add_argument("--weekly",action="store_true")
    a=p.parse_args()
    if not a.daily and not a.weekly: p.error("Choose --daily or --weekly")
    if a.daily: daily()
    if a.weekly: archive()
