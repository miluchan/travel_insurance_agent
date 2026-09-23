import os, re
from ai.document_vision_agent import recognize_document
from flask import Flask,render_template,request,jsonify,session
from ai.travel_agent import update_profile,empty_profile
from ai.rate_engine import quote, tier_options, scenario_for
from ai.product_master import match_products
from datetime import datetime
app=Flask(__name__);app.secret_key="v12-local"
@app.get("/")
def index():session.clear();return render_template("index.html")
@app.post("/api/analyze")
def analyze():
 d=request.get_json(silent=True) or {};m=(d.get("message") or "").strip()
 if not m:return jsonify(ok=False,error="請輸入旅行需求"),400
 p,r=update_profile(session.get("profile") or empty_profile(),m);session["profile"]=p
 return jsonify(ok=True,profile=p,reply=r)
@app.post("/api/profile")
def profile():
 d=request.get_json(silent=True) or {};p=session.get("profile") or empty_profile();f=d.get("profile") or {}
 for k in ["start_date","end_date","country","city","adults","children","seniors","budget_range","concerns","coverage_intent"]:
  if k in f:p[k]=f[k]
 p["people"]=int(p.get("adults") or 0)+int(p.get("children") or 0)+int(p.get("seniors") or 0)
 p["destination"]="／".join(x for x in [p.get("country"),p.get("city")] if x) or "尚未提供"
 error=None
 try:
  if p.get("start_date") and p.get("end_date"):
   a=datetime.strptime(p["start_date"],"%Y/%m/%d");b=datetime.strptime(p["end_date"],"%Y/%m/%d")
   if b<a:
    p["end_date"]=None;p["days"]=None;error="回程日不可早於啟程日，請重新選擇回程日。"
   else:p["days"]=(b-a).days+1
 except:
  p["days"]=None;error="日期格式不正確，請重新選擇。"
 session["profile"]=p;return jsonify(ok=True,profile=p,error=error)

@app.post("/api/plan")
def plan():
 p=session.get("profile") or empty_profile()
 required=[]
 if not p.get("country"): required.append("目的地")
 if not p.get("start_date") or not p.get("end_date"): required.append("旅行日期")
 if not p.get("people"): required.append("投保人數")
 if required:return jsonify(ok=False,error="請先完成："+"、".join(required)),400
 d=request.get_json(silent=True) or {}
 tier=d.get("tier") or session.get("plan_tier") or "balanced"
 if tier not in {"economy","balanced","enhanced"}: tier="balanced"
 session["plan_tier"]=tier
 scenario=scenario_for(p)
 plan=quote(p,tier,d.get("accident"),d.get("medical"),d.get("rescue"),scenario=scenario)
 return jsonify(ok=True,plan=plan,options=tier_options(p,scenario),profile=p)

@app.post("/api/match-products")
def match_products_api():
 d=request.get_json(silent=True) or {};p=session.get("profile") or empty_profile();selected=d.get("selected") or {}
 matches=match_products(p,selected,3)
 # V1.8.4.2 Decision Layer: Demo comparison premium is calculated only from each candidate's
 # displayed main amounts + the customer's requested coverages that the candidate actually covers.
 # It is NOT an insurer quote and never replaces an official Rate Engine/API.
 for m in matches:
  am=m.get("display_amounts") or {}
  pp=dict(p); pp["concerns"]=m.get("matched") or []
  q=quote(pp,"balanced",am.get("accident") or selected.get("accident"),am.get("medical") or selected.get("medical"),am.get("rescue") or selected.get("rescue"))
  m["demo_premium_per_person"]=q["per_person"]; m["demo_premium_total"]=q["total"]
 return jsonify(ok=True,matches=matches,checked_date="2026-09-22",formal=False)

@app.post("/api/reset")
def reset():session.clear();return jsonify(ok=True)

@app.post("/api/document-agent")
def document_agent():
    f=request.files.get("file")
    if not f:return jsonify({"ok":False,"message":"未收到檔案"}),400
    try:
        d=recognize_document(f.filename or "document.pdf",f.read())

        # V1.7.11 Trust Gate: AI extraction is evidence, not automatically trusted profile data.
        uncertain=" ".join(str(x).lower() for x in (d.get("uncertain_fields") or []))
        segs=d.get("segments") or []
        year_uncertain=("year" in uncertain) or ("年份" in uncertain)
        if year_uncertain:
            if isinstance(d.get("start"),dict): d["start"]["value"]=None; d["start"]["status"]="needs_confirmation"
            else: d["start"]=None
            if isinstance(d.get("end"),dict): d["end"]["value"]=None; d["end"]["status"]="needs_confirmation"
            else: d["end"]=None
        # A single flight segment never creates a return/end date.
        if len(segs)==1:
            if isinstance(d.get("end"),dict): d["end"]["value"]=None; d["end"]["status"]="unavailable"
            else: d["end"]=None

        def val(x):
            return x.get("value") if isinstance(x,dict) else x
        d["destination_status"]=(d.get("destination") or {}).get("status") if isinstance(d.get("destination"),dict) else "confirmed"
        d["airline_status"]=(d.get("airline") or {}).get("status") if isinstance(d.get("airline"),dict) else "confirmed"
        d["start_status"]=(d.get("start") or {}).get("status") if isinstance(d.get("start"),dict) else "confirmed"
        d["end_status"]=(d.get("end") or {}).get("status") if isinstance(d.get("end"),dict) else "confirmed"
        d["destination"]=val(d.get("destination"))
        d["airline"]=val(d.get("airline"))
        d["start"]=val(d.get("start"))
        d["end"]=val(d.get("end"))
        seg=d.get("segments") or []
        d["origin"]=seg[0].get("from") if seg else None
        d["arrival"]=seg[-1].get("to") if seg else None
        d["outbound_flight"]=seg[0].get("flight") if seg else None
        d["return_flight"]=seg[-1].get("flight") if len(seg)>1 else None
        d["adults"]=sum(x.get("category")=="大人" for x in d.get("passengers",[]))
        d["children"]=sum(x.get("category")=="小孩" for x in d.get("passengers",[]))
        d["seniors"]=sum(x.get("category")=="長輩" for x in d.get("passengers",[]))
        return jsonify({"ok":True,"mode":"real_ai_vision","data":d,
          "message":"原始文件已直接交給 AI Vision，未先做 OCR，也沒有預設答案。"})
    except Exception as e:return jsonify({"ok":False,"message":"AI 文件辨識失敗："+str(e)}),500

if __name__=="__main__":app.run(host="127.0.0.1",port=5000,debug=True)
