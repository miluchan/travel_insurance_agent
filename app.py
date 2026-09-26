from openai import OpenAI
import mimetypes
import base64
import json
import os, re
from ai.document_vision_agent import recognize_document
from flask import Flask,render_template,request,jsonify,session

from io import BytesIO
from datetime import datetime, date
from openpyxl import load_workbook
from ai.travel_agent import update_profile,empty_profile
from ai.rate_engine import quote, tier_options, scenario_for
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


# ---------------- V1.9.3 Product Selection -> Quote Engine ----------------
DEMO_PRODUCTS = [
 {"id":"FUBON-A","company":"富邦產險","name":"A 小資旅遊","direction":"economy","ages":"15～未滿80歲",
  "features":["旅平險","海外醫療","旅遊不便保障"],"service":"公開商品資料 Demo；正式內容依官方投保系統"},
 {"id":"TMNEWA-A","company":"新安東京海上","name":"A 旅平險","direction":"economy","ages":"依正式網投規則",
  "features":["意外傷害","傷害醫療","個人責任"],"service":"保障結構較精簡"},
 {"id":"TAIAN-A","company":"泰安產險","name":"海外套餐 A","direction":"economy","ages":"分成人／15～18／未滿15歲",
  "features":["旅平險","緊急救援"],"service":"已有公開年齡層參考資料"},
 {"id":"CATHAY-T5","company":"國泰產險","name":"T5 安心型","direction":"balanced","ages":"依正式投保系統",
  "features":["班機延誤","行李延誤","行李損失","旅程取消"],"service":"定額型旅遊不便保障"},
 {"id":"TMNEWA-C","company":"新安東京海上","name":"C 完整型","direction":"balanced","ages":"依正式網投規則",
  "features":["意外傷害","海外突發疾病","班機延誤","旅遊不便"],"service":"含限額型不便保障"},
 {"id":"TFMI-SAFE","company":"臺灣產物","name":"安心遊","direction":"balanced","ages":"依正式投保系統",
  "features":["旅平險","海外突發疾病","班機延誤","旅程取消"],"service":"可再銜接旅遊服務能力"},
 {"id":"TAIAN-C","company":"泰安產險","name":"海外套餐 C","direction":"enhanced","ages":"分成人／15～18／未滿15歲",
  "features":["旅平險","傷害醫療","海外突發疾病","班機延誤","行李","緊急救援"],"service":"已有公開年齡層差異資料"},
 {"id":"MSIG-DIAMOND","company":"明台產險","name":"頭等晶鑽版","direction":"enhanced","ages":"依正式投保系統",
  "features":["意外","醫療","班機延誤","緊急醫療運送"],"service":"可延伸24H海外緊急救援／理賠服務"},
 {"id":"TFMI-GLOBAL","company":"臺灣產物","name":"環球遊","direction":"enhanced","ages":"依正式投保系統",
  "features":["高額旅平險","傷害醫療","海外突發疾病","旅程取消","個人責任"],"service":"高保障方向 Demo"}
]

def _age_on(dob_text, ref_text):
    from datetime import date, datetime
    try:
        dob=datetime.strptime(dob_text,"%Y-%m-%d").date()
        ref=datetime.strptime((ref_text or "")[:10],"%Y-%m-%d").date()
        return ref.year-dob.year-((ref.month,ref.day)<(dob.month,dob.day))
    except Exception:
        return None

def _travelers(p):
    # V1.9.3.1: DOB is collected before Product Engine.
    # If names are not known yet, AI uses neutral labels; legal identity remains later.
    saved=session.get("traveler_dobs") or []
    a=int(p.get("adults") or 0); c=int(p.get("children") or 0); s=int(p.get("seniors") or 0)
    total=max(int(p.get("people") or 0), a+c+s, len(saved))
    labels=[]
    labels += [f"大人{i+1}" for i in range(a)]
    labels += [f"小孩{i+1}" for i in range(c)]
    labels += [f"長輩{i+1}" for i in range(s)]
    while len(labels)<total: labels.append(f"旅客{len(labels)+1}")
    out=[]
    for i in range(total):
        dob=saved[i] if i < len(saved) else ""
        age=_age_on(dob,p.get("start_date"))
        out.append({"label":labels[i],"dob":dob,"age":age})
    return out

def _precheck(product, p):
    travelers=_travelers(p)
    blocked=[]; pending=[]
    for t in travelers:
        age=t["age"]
        if age is None:
            pending.append(f'{t["label"]}尚缺生日')
            continue
        if product["id"]=="FUBON-A" and not (15 <= age < 80):
            blocked.append(f'{t["label"]}（{age}歲）不符合公開年齡15～未滿80歲')
        elif product["id"]=="FUBON-D" and not (18 <= age < 70):
            blocked.append(f'{t["label"]}（{age}歲）不符合公開年齡18～未滿70歲')
    if product["id"] in {"TAIAN-A","TAIAN-C"} and not blocked:
        pending.append("正式保額／費率仍須依各旅客年齡層套官方規則")
    if product["id"] not in {"FUBON-A","FUBON-D","TAIAN-A","TAIAN-C"} and not blocked:
        pending.append("公開資料尚不足以完成正式年齡資格判定，需官方完整規則")
    status="BLOCKED" if blocked else ("NEED_OFFICIAL_RULE" if pending else "ELIGIBLE")
    return status, blocked, pending, travelers

@app.post("/api/traveler-dobs")
def traveler_dobs():
    d=request.get_json(silent=True) or {}
    dobs=d.get("dobs") or []
    p=session.get("profile") or empty_profile()
    # V1.9.3.1.1: the browser may have changed adults/children/seniors
    # immediately before this request, while session.profile still has the old total.
    # DOB count is therefore validated against the current submitted traveler labels,
    # not a stale session total. Profile sync follows before Product Engine.
    expected = int(p.get("adults") or 0) + int(p.get("children") or 0) + int(p.get("seniors") or 0)
    if expected and len(dobs) != expected:
        # Accept the current DOB list as source-of-truth for this transition instead
        # of blocking the customer with an internal synchronization error.
        p["people"] = len(dobs)
        session["profile"] = p
    if any(not x for x in dobs):
        return jsonify(ok=False,error="請先補齊每位旅客生日"),400
    session["traveler_dobs"]=dobs
    return jsonify(ok=True,travelers=_travelers(p))

@app.post("/api/product-match")
def product_match():
    p=session.get("profile") or empty_profile()
    d=request.get_json(silent=True) or {}
    desired=d.get("desired") or {}
    tier=d.get("tier") or session.get("plan_tier") or "balanced"
    concerns=set(p.get("concerns") or [])
    budget=p.get("budget_range") or ""
    # Scenario controls the shortlist, but not formal saleability or price.
    if "300元以下" in budget: tier="economy"
    elif "500元以上" in budget: tier="enhanced"
    candidates=[x for x in DEMO_PRODUCTS if x["direction"]==tier]
    results=[]
    for x in candidates:
        st,blocked,pending,travelers=_precheck(x,p)
        overlap=sum(1 for f in x["features"] if any(k in f for k in ["班機延誤","行李","海外","醫療","救援"]) and
                    any(c in " ".join(x["features"]) for c in concerns))
        if st=="BLOCKED":
            continue
        requested=set(p.get("concerns") or [])
        feature_text="、".join(x["features"])
        extra=[]
        # Customer-facing "海外醫療／海外生病醫療" already represents
        # 傷害醫療 + 生病醫療（含海外突發疾病概念）.
        # Do not mislabel 海外突發疾病 as an extra coverage.
        medical_need = any(v in requested for v in ["海外醫療","海外生病/醫療","海外生病醫療"])
        for label in ["旅程取消","行李損失","個人責任","班機延誤","行李延誤","緊急救援"]:
            if label in feature_text and label not in requested:
                extra.append(label)
        if "海外突發疾病" in feature_text and not medical_need:
            extra.append("海外突發疾病")
        results.append({**x,"precheck":st,"blocked":blocked,"pending":pending,
                        "desired":desired,"extra_coverages":extra,
                        "travelers":travelers,
                        "match_note":"15宮格是需求；本卡顯示商品與需求的差異。",
                        "rate_status":"WAIT_OFFICIAL_RATE"})
    session["product_candidates"]=results
    return jsonify(ok=True,products=results,profile=p,tier=tier)

@app.post("/api/product-select")
def product_select():
    d=request.get_json(silent=True) or {}
    pid=d.get("product_id")
    desired=d.get("desired") or {}
    p=session.get("profile") or empty_profile()
    product=next((x for x in DEMO_PRODUCTS if x["id"]==pid),None)
    if not product:return jsonify(ok=False,error="找不到商品"),404
    st,blocked,pending,travelers=_precheck(product,p)
    if blocked:
        return jsonify(ok=False,error="此商品目前不適用全部旅客，請重新選擇商品"),400

    # V1.9.4.1 Demo Quote:
    # Reuse the stable V1.8.3.3 demo rate engine only to test the purchase flow.
    # This is NOT an insurer/product official premium and is never called a formal quote.
    demo=quote(
        p,
        session.get("plan_tier") or "balanced",
        desired.get("accident"),desired.get("medical"),desired.get("rescue"),
        scenario=scenario_for(p)
    )
    per_person=demo["per_person"]
    person_rows=[]
    for t in travelers:
        person_rows.append({
            "group":t["label"],"dob":t["dob"],"age":t["age"],
            "status":"可進入 Demo 投保流程",
            "demo_premium":per_person
        })
    q={
      "quote_id":"DEMO-"+pid,
      "product":product,
      "people":len(person_rows),
      "desired":desired,
      "eligibility_status":st,
      "person_rows":person_rows,
      "demo_per_person":per_person,
      "demo_total":per_person*len(person_rows),
      "quote_status":"DEMO_QUOTE_READY",
      "can_apply_demo":True,
      "official_ready":False,
      "rate_notice":"Demo 試算保費｜非正式報價。僅用於測試商品選定 → Quote → 投保流程；正式版必須改接官方 Rate Engine／費率表。"
    }
    session["selected_product"]=pid
    session["quote_snapshot"]=q
    return jsonify(ok=True,quote=q)



ID_VISION_PROMPT = """你是保險投保證件文件理解 Agent。請直接閱讀使用者提供的證件影像。
安全規則：
1. 只能抄錄影像中清楚可見的資料，不可猜測、補字、推算或從檔名推斷。
2. 本 Prototype 只擷取：姓名、身分證字號/證件號碼、出生日期。
3. 若欄位不存在、遮罩、模糊或不確定，value 必須是 null。
4. 出生日期盡量標準化為 YYYY-MM-DD；若無法確定完整年月日，value=null，raw_text 保留看見的原文。
5. 每欄回傳 confidence 0~1。只有非常清楚時才給 >=0.90。
6. 不要回傳地址、照片、生物特徵或其他不需要的敏感資料。
7. 只回傳 JSON，不要 Markdown：
{
  "document_type":"identity_document|passport|unknown",
  "name":{"value":null,"raw_text":null,"confidence":0.0},
  "id_no":{"value":null,"raw_text":null,"confidence":0.0},
  "dob":{"value":null,"raw_text":null,"confidence":0.0},
  "notes":[]
}
"""

def _json_from_model(text):
    s=(text or "").strip()
    s=re.sub(r"^```(?:json)?\s*|\s*```$","",s)
    return json.loads(s)

def _trust_field(field, threshold=0.90):
    field=field if isinstance(field,dict) else {}
    value=field.get("value")
    try: conf=float(field.get("confidence") or 0)
    except: conf=0.0
    # Trust Gate is deterministic: AI proposes evidence; code decides acceptance.
    if value and conf >= threshold:
        status="accepted"
    elif value:
        status="needs_confirmation"
    else:
        status="needs_confirmation"
    return {
      "value":value or None,
      "raw_text":field.get("raw_text") or value or None,
      "confidence":round(conf,2),
      "status":status
    }

@app.post("/api/id-document-upload")
def id_document_upload():
    f=request.files.get("file")
    if not f or not f.filename:
        return jsonify(ok=False,error="請先選擇證件圖片。"),400
    ext=(f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else "")
    if ext not in {"png","jpg","jpeg","webp"}:
        return jsonify(ok=False,error="目前先支援 PNG、JPG、JPEG、WEBP 證件圖片。"),400
    raw=f.read()
    if not raw:
        return jsonify(ok=False,error="證件圖片是空的。"),400
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify(ok=False,error="尚未設定 OPENAI_API_KEY。請先在 Terminal 設定後重新啟動程式。"),400
    try:
        mime=mimetypes.guess_type(f.filename)[0] or "image/jpeg"
        data=base64.b64encode(raw).decode("ascii")
        client=OpenAI()
        resp=client.responses.create(
          model=os.getenv("OPENAI_VISION_MODEL","gpt-5.6-luna"),
          input=[{"role":"user","content":[
            {"type":"input_text","text":ID_VISION_PROMPT},
            {"type":"input_image","image_url":"data:"+mime+";base64,"+data}
          ]}]
        )
        result=_json_from_model(resp.output_text)
    except Exception as e:
        return jsonify(ok=False,error="AI Vision 證件辨識失敗："+str(e)),500

    evidence={
      "document_type":result.get("document_type") or "unknown",
      "name":_trust_field(result.get("name")),
      "id_no":_trust_field(result.get("id_no")),
      "dob":_trust_field(result.get("dob")),
      "notes":result.get("notes") if isinstance(result.get("notes"),list) else []
    }
    accepted=sum(1 for k in ("name","id_no","dob") if evidence[k]["status"]=="accepted")
    evidence["trust_gate_status"]="accepted" if accepted==3 else "needs_confirmation"
    evidence["accepted_count"]=accepted
    evidence["note"]="AI 已完成證件辨識；只有高信心欄位會自動帶入，其餘資料請您確認。"
    return jsonify(ok=True,evidence=evidence,filename=f.filename)

@app.post("/api/roster-upload")
def roster_upload():
    f=request.files.get("file")
    if not f or not f.filename:
        return jsonify(ok=False,error="請先選擇 Excel 旅客名單。"),400
    if not f.filename.lower().endswith(".xlsx"):
        return jsonify(ok=False,error="目前 Prototype 先支援 .xlsx 檔案。"),400
    try:
        wb=load_workbook(BytesIO(f.read()),read_only=True,data_only=True)
        ws=wb[wb.sheetnames[0]]
        rows=list(ws.iter_rows(values_only=True))
    except Exception:
        return jsonify(ok=False,error="Excel 檔案無法讀取，請確認格式是否正確。"),400
    if not rows:
        return jsonify(ok=False,error="旅客名單是空的。"),400

    def norm(v):
        return str(v).strip() if v is not None else ""
    aliases={
      "name":["姓名","旅客姓名","被保險人姓名","name"],
      "id_no":["身分證字號","身分證","證號","id","id_no"],
      "dob":["生日","出生日期","birth_date","dob"],
      "relation":["與要保人關係","關係","relation"],
      "phone":["手機","手機號碼","電話","phone"],
      "email":["email","e-mail","電子郵件"]
    }
    headers=[norm(x).lower() for x in rows[0]]
    col={}
    for key,names in aliases.items():
        for i,h in enumerate(headers):
            if h in [n.lower() for n in names]:
                col[key]=i;break
    if "name" not in col or "dob" not in col:
        return jsonify(ok=False,error="Excel 至少需要「姓名」與「生日」欄位。"),400

    def val(row,key):
        i=col.get(key)
        if i is None or i>=len(row): return ""
        v=row[i]
        if isinstance(v,(datetime,date)): return v.strftime("%Y-%m-%d")
        return norm(v)
    people=[]
    for n,row in enumerate(rows[1:],start=2):
        if not any(x not in (None,"") for x in row): continue
        item={k:val(row,k) for k in aliases}
        item["row"]=n
        item["missing"]=[label for key,label in [("name","姓名"),("id_no","身分證字號"),("dob","生日")] if not item.get(key)]
        people.append(item)
    if not people:
        return jsonify(ok=False,error="沒有讀到任何旅客資料。"),400

    profile=session.get("profile") or empty_profile()
    expected=max(int(profile.get("people") or 0),
                 int(profile.get("adults") or 0)+int(profile.get("children") or 0)+int(profile.get("seniors") or 0))
    saved_dobs=session.get("traveler_dobs") or []
    warnings=[]
    if expected and len(people)!=expected:
        warnings.append(f"名單有 {len(people)} 人，但目前行程設定為 {expected} 人，請確認。")
    dob_diff=[]
    for i,p in enumerate(people):
        if i<len(saved_dobs) and saved_dobs[i] and p["dob"] and saved_dobs[i]!=p["dob"]:
            dob_diff.append(i+1)
    if dob_diff:
        warnings.append("第 "+ "、".join(map(str,dob_diff)) +" 位旅客生日與前一步資料不同，請確認後再套用。")
    return jsonify(ok=True,people=people,count=len(people),expected=expected,warnings=warnings)

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
