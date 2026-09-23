"""V1.8.4 Product Master prototype.
Public product facts checked 2026-09-22. Formal saleability/premium must be revalidated by insurer rules/API.
"""
PRODUCTS = [
 {"insurer":"富邦產險","plan":"A 小資旅遊","accident_min":200,"accident_max":1500,"medical_max":150,"illness_max":120,"rescue":180,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒","手機遭竊"],"service":["SOS海外緊急救援服務"],"age":"15歲～未滿80歲","source":"https://www.fubon.com/insurance/b2c/content/prod_travel/index.html"},
 {"insurer":"富邦產險","plan":"C 人氣首選","accident_min":600,"accident_max":1500,"medical_max":150,"illness_max":120,"rescue":180,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒","手機遭竊"],"service":["SOS海外緊急救援服務"],"age":"18歲～未滿70歲","source":"https://www.fubon.com/insurance/b2c/content/prod_travel/index.html"},
 {"insurer":"國泰產險","plan":"安心型 T5","accident_min":200,"accident_max":1500,"medical_max":200,"illness_max":120,"rescue":200,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["官方LINE保單查詢／理賠服務"],"age":"依投保系統規則","source":"https://www.cathay-ins.com.tw/cathayins/personal/travel/oversea/"},
 {"insurer":"國泰產險","plan":"海外豪華型 U3","accident_min":200,"accident_max":1500,"medical_max":200,"illness_max":120,"rescue":300,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["官方LINE保單查詢／理賠服務"],"age":"依投保系統規則","source":"https://www.cathay-ins.com.tw/cathayins/personal/travel/oversea/"},
 {"insurer":"新安東京海上","plan":"A 旅平險","accident_min":200,"accident_max":1500,"medical_max":150,"illness_max":0,"rescue":0,"coverages":["意外傷害","個人責任"],"service":["線上投保"],"age":"15歲以上主保額範圍依官網","source":"https://www.tmnewa.com.tw/ec/contents/travel/travel-insurance.html"},
 {"insurer":"新安東京海上","plan":"B 旅平險＋定額不便險","accident_min":200,"accident_max":1500,"medical_max":150,"illness_max":0,"rescue":0,"coverages":["意外傷害","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["定額型旅遊不便保障"],"age":"依投保系統規則","source":"https://www.tmnewa.com.tw/ec/contents/travel/travel-insurance.html"},
 {"insurer":"新安東京海上","plan":"C 旅平險＋限額不便險＋海外疾病","accident_min":200,"accident_max":1500,"medical_max":150,"illness_max":10,"rescue":0,"coverages":["意外傷害","海外醫療","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["限額型旅遊不便保障"],"age":"依投保系統規則","source":"https://www.tmnewa.com.tw/ec/contents/travel/travel-insurance.html"},
 {"insurer":"明台產險","plan":"經濟入門版","accident_min":200,"accident_max":900,"medical_max":100,"illness_max":60,"rescue":90,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["班機延誤快速理賠","24小時海外緊急救援"],"age":"依投保系統規則","source":"https://www.msig-mingtai.com.tw/ec/foreign-travel.html"},
 {"insurer":"明台產險","plan":"商務經典版","accident_min":200,"accident_max":900,"medical_max":100,"illness_max":80,"rescue":100,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["班機延誤快速理賠","24小時海外緊急救援"],"age":"依投保系統規則","source":"https://www.msig-mingtai.com.tw/ec/foreign-travel.html"},
 {"insurer":"明台產險","plan":"頭等晶鑽版","accident_min":200,"accident_max":900,"medical_max":100,"illness_max":100,"rescue":150,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["班機延誤快速理賠","24小時海外緊急救援","日本華語門診預約安排"],"age":"依投保系統規則","source":"https://www.msig-mingtai.com.tw/ec/foreign-travel.html"},
 {"insurer":"臺灣產物","plan":"安心遊","accident_min":200,"accident_max":1000,"medical_max":100,"illness_max":50,"rescue":30,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["安心Care 24小時醫療諮詢（活動資格依官網）"],"age":"依投保系統規則","source":"https://ec.tfmi.com.tw/Content/TravelAccident/"},
 {"insurer":"臺灣產物","plan":"豪華遊","accident_min":200,"accident_max":1000,"medical_max":100,"illness_max":100,"rescue":50,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["安心Care 24小時醫療諮詢（活動資格依官網）"],"age":"依投保系統規則","source":"https://ec.tfmi.com.tw/Content/TravelAccident/"},
 {"insurer":"臺灣產物","plan":"尊榮遊","accident_min":1200,"accident_max":1200,"medical_max":120,"illness_max":120,"rescue":150,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["安心Care 24小時醫療諮詢（活動資格依官網）"],"age":"依投保系統規則","source":"https://ec.tfmi.com.tw/Content/TravelAccident/"},
 {"insurer":"臺灣產物","plan":"環球遊","accident_min":1200,"accident_max":1200,"medical_max":150,"illness_max":120,"rescue":150,"coverages":["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任","食品中毒"],"service":["安心Care 24小時醫療諮詢（活動資格依官網）","日本韓國海外疾病額度依地區係數提升"],"age":"依投保系統規則","source":"https://ec.tfmi.com.tw/Content/TravelAccident/"},
 {"insurer":"泰安產險","plan":"海外套餐 A","accident_min":200,"accident_max":200,"medical_max":20,"illness_max":6,"rescue":0,"coverages":["意外傷害","海外醫療","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["海外套餐式投保"],"age":"成人／青少年／兒童額度分級","source":"https://www.taian.com.tw/Travel/TravelProduct"},
 {"insurer":"泰安產險","plan":"海外套餐 B","accident_min":500,"accident_max":500,"medical_max":50,"illness_max":15,"rescue":0,"coverages":["意外傷害","海外醫療","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["海外套餐式投保"],"age":"成人／青少年／兒童額度分級","source":"https://www.taian.com.tw/Travel/TravelProduct"},
 {"insurer":"泰安產險","plan":"海外套餐 C","accident_min":1000,"accident_max":1000,"medical_max":100,"illness_max":30,"rescue":0,"coverages":["意外傷害","海外醫療","行李損失","班機延誤","行李延誤","旅程取消","旅行文件損失","個人責任"],"service":["海外套餐式投保"],"age":"成人／青少年／兒童額度分級","source":"https://www.taian.com.tw/Travel/TravelProduct"},
]

def _amount_fit(target, lo, hi):
    """0..1. Shortfall is penalized more than modest excess."""
    target=max(float(target or 0),1.0); lo=float(lo or 0); hi=float(hi or 0)
    if lo <= target <= hi: return 1.0
    if target > hi: return max(0.0, 1.0 - ((target-hi)/target)*1.35)
    return max(0.0, 1.0 - ((lo-target)/target)*0.70)

def _ratio_fit(target, actual):
    target=max(float(target or 0),1.0); actual=float(actual or 0)
    if actual <= 0: return 0.0
    if actual < target: return max(0.0, 1.0-((target-actual)/target)*1.35)
    return max(0.0, 1.0-((actual-target)/target)*0.55)

def _facts(p, concerns, a, m, r):
    covered=concerns.intersection(p['coverages']); missing=concerns.difference(p['coverages'])
    extra=set(p['coverages']).difference(concerns)
    af=_amount_fit(a,p['accident_min'],p['accident_max'])
    mf=_ratio_fit(m,p['illness_max'])
    rf=_ratio_fit(r,p['rescue']) if r else 1.0
    return covered,missing,extra,af,mf,rf

def _card(p, role, score, concerns, a, m, r, why):
    covered,missing,extra,af,mf,rf=_facts(p,concerns,a,m,r)
    # Decision Layer display amounts are deliberately different by direction.
    # They are configurable comparison targets inside the product's known public limits,
    # NOT an assertion that every insurer sells this exact combination as a fixed package.
    delta = {'精簡取向':-1, '均衡取向':0, '完整／服務取向':1}.get(role, 0)
    ta=max(200, min(1000, int(a)+delta*100))
    tm=max(20, min(100, int(m)+delta*10))
    tr=max(75, min(250, int(r)+delta*25))
    da=int(min(max(ta, p['accident_min']), p['accident_max'])) if p['accident_max'] else 0
    dm=int(min(tm, p.get('illness_max') or 0)) if p.get('illness_max') else 0
    dr=int(min(tr, p.get('rescue') or 0)) if p.get('rescue') else 0
    # The closeness shown to the customer must describe the displayed comparison amounts,
    # not the product's broad min/max range.
    daf=_ratio_fit(a,da); dmf=_ratio_fit(m,dm); drf=_ratio_fit(r,dr) if r else 1.0
    return {**p,'role':role,'score':round(score,1),'matched':sorted(covered),'missing':sorted(missing),
            'extra_count':len(extra),'amount_fit':round((daf+dmf+drf)/3*100),
            'display_amounts':{'accident':da,'medical':dm,'rescue':dr},
            'reasons':why[:4]}

def match_products(profile, selected, limit=3):
    """V1.8.4.1 differentiated matching.
    Returns one candidate for each *decision lens*, rather than top-3 of one global score.
    Product price is deliberately NOT inferred: formal premium needs insurer Rate Engine/API.
    """
    concerns=set(profile.get('concerns') or [])
    if not concerns: concerns={'意外傷害','海外醫療','緊急救援','行李損失','班機延誤','行李延誤'}
    a=int(selected.get('accident') or 600); m=int(selected.get('medical') or 60); r=int(selected.get('rescue') or 150)
    budget=profile.get('budget_range') or ''
    rows=[]
    for p in PRODUCTS:
        covered,missing,extra,af,mf,rf=_facts(p,concerns,a,m,r)
        cov=len(covered)/max(1,len(concerns)); amt=(af+mf+rf)/3
        # Need-specific coverages have strong value; unrequested extras matter mainly to the lean lens.
        missing_pen=len(missing)/max(1,len(concerns))
        extra_pen=min(len(extra),8)/8
        service=min(len(p.get('service') or []),3)/3

        lean=46*amt + 42*cov - 18*extra_pen - 14*missing_pen
        # Low-budget intent increases preference for a lean product structure, but is NOT a premium claim.
        if budget=='300元以下': lean += 7*(1-extra_pen)
        balanced=50*amt + 48*cov - 16*missing_pen + 2*service
        complete=34*amt + 48*cov + 14*service - 20*missing_pen + 4*(1-extra_pen if len(concerns)<=6 else 0)
        if len(concerns)>=8: complete += 8*cov
        rows.append((p,lean,balanced,complete,cov,amt))

    lenses=[('精簡取向','lean'),('均衡取向','balanced'),('完整／服務取向','complete')]
    chosen=[]; used_plans=set(); used_insurers=set()
    for role,key in lenses:
        idx={'lean':1,'balanced':2,'complete':3}[key]
        ranked=sorted(rows,key=lambda x:x[idx],reverse=True)
        pick=None
        # Prefer market diversity when the score is still close to the best candidate.
        best=ranked[0][idx]
        for row in ranked:
            p=row[0]
            if (p['insurer'],p['plan']) in used_plans: continue
            if p['insurer'] not in used_insurers and row[idx] >= best-8:
                pick=row; break
        if pick is None:
            pick=next(row for row in ranked if (row[0]['insurer'],row[0]['plan']) not in used_plans)
        p=pick[0]; covered,missing,extra,af,mf,rf=_facts(p,concerns,a,m,r)
        if role=='精簡取向':
            why=[f'以目前 {len(concerns)} 項需求為主，避免單純因保障項目多就加分',
                 f'目前需求涵蓋 {len(covered)}/{len(concerns)} 項']
        elif role=='均衡取向':
            why=[f'同時衡量前三項保額與目前 {len(concerns)} 項保障需求',
                 f'目前需求涵蓋 {len(covered)}/{len(concerns)} 項']
        else:
            why=[f'提高客戶主動關注保障與服務能力的權重',
                 f'目前需求涵蓋 {len(covered)}/{len(concerns)} 項',
                 ('服務特色：'+'、'.join(p.get('service',[])[:2])) if p.get('service') else '服務內容仍須依官方最新資訊確認']
        chosen.append(_card(p,role,pick[idx],concerns,a,m,r,why)); used_plans.add((p['insurer'],p['plan'])); used_insurers.add(p['insurer'])
    return chosen[:limit]
