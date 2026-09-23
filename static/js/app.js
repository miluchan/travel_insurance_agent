function safeSlice(v,a,b){return (v==null||v==="")?"":String(v).slice(a,b)}

// V1.6.3 authoritative Profile insurance-day label.
function v163ProfileDays(p){
  if(!p||!p.start_date||!p.end_date)return 1;
  // When document-agent exact timestamps are available, use elapsed-time ceiling.
  if(window.v163ExactTrip?.start && window.v163ExactTrip?.end)
    return Math.max(1,Math.ceil((new Date(window.v163ExactTrip.end)-new Date(window.v163ExactTrip.start))/86400000));
  const s=String(p.start_date).slice(0,10).replaceAll("/","-");
  const e=String(p.end_date).slice(0,10).replaceAll("/","-");
  return Math.max(1,Math.round((new Date(e+"T00:00")-new Date(s+"T00:00"))/86400000));
}
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const cities={日本:["東京","大阪","京都","北海道","沖繩","名古屋","福岡"],韓國:["首爾","釜山","濟州"],泰國:["曼谷","清邁","普吉"],新加坡:["新加坡"],美國:["紐約","洛杉磯","舊金山","夏威夷"]};
function bubble(t,c){let d=document.createElement("div");d.className="bubble "+c;d.innerHTML=t;$("#messages").appendChild(d)}
function slash(x){return x?x.slice(0,10).replaceAll("-","/"):null}function dash(x){return x?(x.includes("T")?x:x.replaceAll("/","-")+"T00:00"):""}
function setCities(c,sel){let a=cities[c]||[];$("#city").innerHTML='<option value="">請選擇</option>'+a.map(x=>`<option>${x}</option>`).join("")+'<option>其他</option>';if(sel&&a.includes(sel))$("#city").value=sel}
function data(){let c=$("#country").value,ci=$("#city").value;if(c==="其他")c=$("#countryOther").value;if(ci==="其他")ci=$("#cityOther").value;return{start_date:slash($("#start").value),end_date:slash($("#end").value),country:c||null,city:ci||null,adults:+$("#adults").textContent,children:+$("#children").textContent,seniors:+$("#seniors").textContent,budget_range:$('input[name="budget"]:checked')?.value||null,concerns:$$('#concerns input:checked').map(x=>x.value)}}
function syncForm(p){if(p.start_date&&!$("#start").value)$("#start").value=dash(p.start_date);if(p.end_date&&!$("#end").value)$("#end").value=dash(p.end_date);if(p.country){$("#country").value=cities[p.country]?p.country:"其他";setCities(p.country,p.city);if(!cities[p.country])$("#countryOther").value=p.country}if(p.city&&!cities[p.country]?.includes(p.city)){$("#city").value="其他";$("#cityOther").value=p.city}if(p.adults!=null)$("#adults").textContent=p.adults;if(p.children!=null)$("#children").textContent=p.children;if(p.seniors!=null)$("#seniors").textContent=p.seniors;if(p.budget_range){let x=$(`input[name="budget"][value="${p.budget_range}"]`);if(x)x.checked=true}$$('#concerns input').forEach(x=>x.checked=(p.concerns||[]).includes(x.value))}
function render(p){
 syncForm(p);$("#empty").classList.add("hidden");$("#profile").classList.remove("hidden");
 let tags=(p.concerns||[]).map(x=>`<span class="tag">✓ ${x}</span>`).join("")||"尚未指定";
 let insuranceDays="－";
 if(p.start_date&&p.end_date){
   if(window.exactTripTimes?.start&&window.exactTripTimes?.end){
     insuranceDays=Math.max(1,Math.ceil((new Date(window.exactTripTimes.end)-new Date(window.exactTripTimes.start))/86400000));
   }else{
     const s=new Date(String(p.start_date).replaceAll("/","-")+"T00:00");
     const e=new Date(String(p.end_date).replaceAll("/","-")+"T00:00");
     insuranceDays=Math.max(1,Math.round((e-s)/86400000));
   }
 }
 $("#profile").innerHTML=`<div class="card"><b>🌏 目的地</b><br>${p.destination||"尚未提供"}</div><div class="card"><b>📅 行程</b><br>${p.start_date||"尚未提供"} ～ ${p.end_date||"尚未提供"} ${p.start_date&&p.end_date?`（保險天數${insuranceDays}天）`:""}</div><div class="card"><b>👨‍👩‍👧‍👦 投保人數</b><br>大人 ${p.adults??"－"}　小孩 ${p.children??"－"}　長輩 ${p.seniors??"－"}　合計 ${p.people??"－"} 人</div><div class="card"><b>💰 每人預算</b><br>${p.budget_range||(p.budget?`NT$ ${p.budget}`:"尚未提供")}</div><div class="card"><b>🛡 關注保障</b><br>${tags}</div>`;
}
async function sync(){
 let f=data();
 if(f.start_date&&f.end_date&&new Date(f.end_date.replaceAll("/","-"))<new Date(f.start_date.replaceAll("/","-"))){
   bubble("<b>AI</b><br>⚠️ 回程日不能早於啟程日，請重新選擇回程日。","ai");
   $("#end").value=""; f.end_date=null;
 }
 let r=await fetch("/api/profile",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({profile:f})});
 let d=await r.json();if(d.ok){render(d.profile);if(d.error)bubble("<b>AI</b><br>⚠️ "+d.error,"ai")}return d.profile
}
async function send(){let m=$("#message").value.trim();if(!m)return;if(typeof EXAMPLES!=="undefined"&&EXAMPLES[m]){fillExample(m);return;}bubble(m,"user");$("#message").value="";let r=await fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:m})});let d=await r.json();if(d.ok){render(d.profile);bubble("<b>AI</b><br>"+d.reply,"ai")}}
$("#send").onclick=send;$("#message").addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send()}});
$("#country").onchange=()=>{setCities($("#country").value);sync()};$("#city").onchange=sync;["start","end","countryOther","cityOther"].forEach(x=>$("#"+x).onchange=sync);$$('input[name="budget"]').forEach(x=>x.onchange=sync);
// V1.8.3.3: concern selections use Profile as the single source of truth.
// If AI planning is already visible, refresh only its coverage list/quote while preserving
// the customer's current 3 selected main amounts and tier.
$$('#concerns input').forEach(x=>x.onchange=async()=>{
 await sync();
 if(selectedPlan && !$('#planResult').classList.contains('hidden')){
  await getPlan(selectedPlan.tier,{accident:selectedPlan.accident,medical:selectedPlan.medical,rescue:selectedPlan.rescue});
 }
});$$(".counters button").forEach(b=>b.onclick=()=>{let x=$("#"+b.dataset.id);x.textContent=Math.max(0,+x.textContent+(+b.dataset.d));sync()});

let currentPlanOptions=[];let selectedPlan=null;
function money(n){return Number(n||0).toLocaleString()}
const EXAMPLES={
  "1":"10/5～10/10 2位大人、2位小孩、2位長輩要去日本東京旅遊，希望有基本保障。",
  "2":"10/5～10/10 2位大人、2位小孩、2位長輩要去日本東京旅遊，預算較低，希望控制在300元左右。",
  "3":"10/5～10/10 2位大人、2位小孩、2位長輩要去日本東京旅遊，希望完整保障，也重視海外醫療、班機延誤、行李與旅程取消。"
};
function fillExample(n){if(EXAMPLES[n]){$("#message").value=EXAMPLES[n];$("#message").focus()}}
$$('.example-btn').forEach(b=>b.onclick=()=>fillExample(b.dataset.example));

function tierCard(o,selected){return `<button class="tier-card ${o.tier===selected.tier?'selected':''}" data-tier="${o.tier}">
 <span class="tier-kicker">${o.tier==='balanced'?'✨ 建議':'保障方向'}</span><b>${o.label}</b><small>${o.tag}</small>
 <div class="tier-amounts"><span>意外 ${o.accident}萬</span><span>醫療 ${o.medical}萬</span><span>救援 ${o.rescue}萬</span></div>
 <strong>Demo NT$ ${money(o.per_person)}／人</strong></button>`}
function fiveValues(field,current){
 // V1.8.3.2: the 15-cell adjustment range is fixed for the current scenario,
 // so clicking a cell changes only the selected amount and never moves/rebuilds the other choices.
 const scenario=selectedPlan?.scenario||"basic";
 const grids={
  low:{accident:[200,300,400,500,600],medical:[20,30,40,50,60],rescue:[75,100,125,150,175]},
  basic:{accident:[400,500,600,700,800],medical:[40,50,60,70,80],rescue:[100,125,150,175,200]},
  full:{accident:[600,700,800,900,1000],medical:[60,70,80,90,100],rescue:[150,175,200,225,250]}
 };
 return grids[scenario][field];
}
function selectButtons(name,current,center){return fiveValues(name,center).map(v=>`<button class="amount-btn ${v===current?'selected':''}" data-field="${name}" data-value="${v}">${v}萬</button>`).join('')}
function planHtml(selected,opts){
 currentPlanOptions=opts;selectedPlan=selected;
 let extras=(selected.extras||[]).map(x=>`<span class="tag">＋ ${x}</span>`).join('')||'<span class="muted">目前沒有額外加選保障</span>';
 let core=(selected.core||[]).map(x=>`<span class="tag">✓ ${x}</span>`).join('');
 let base=opts.find(o=>o.tier===selected.tier)||selected; let coreCount=(selected.core||[]).length;
 return `<div class="plan-head"><div><small>AI 保障規劃｜V1.8.4.3</small><h2>${selected.scenario_name}：先選三個方向，再用15宮格精準微調</h2></div><div class="price"><small>${selected.people}人／${selected.days}天</small><b>Demo總保費 NT$ ${money(selected.total)}</b></div></div>
 <div class="ai-explain"><b>AI這次的判斷：</b>${selected.scenario_reason}<br>${coreCount}項核心保障先納入；第一層只突出 <b>意外、海外醫療、緊急救援</b> 三個主要額度。</div>
 <div class="tier-grid">${opts.map(o=>tierCard(o,selected)).join('')}</div>
 <div class="micro-panel"><div class="micro-title"><div><small>第二步｜AI 精準微調 3×5</small><h3>${selected.label}</h3></div><span class="demo-pill">Demo 試算</span></div>
  <div class="micro-row"><b>意外傷害</b><div>${selectButtons('accident',selected.accident,base.accident)}</div></div>
  <div class="micro-row"><b>海外醫療</b><div>${selectButtons('medical',selected.medical,base.medical)}</div></div>
  <div class="micro-row"><b>緊急救援</b><div>${selectButtons('rescue',selected.rescue,base.rescue)}</div></div>
  <div class="micro-hint">可自由搭配：三列各選 1 格，共選 3 格；只改您點選的那一項，其餘兩項不變。相同三個保額組合，Demo 保費相同。</div>
  <div class="core-summary"><b>已納入${coreCount}項核心保障</b><div>${core}</div></div>
  <details><summary>查看個人關注／其他保障</summary><div class="extras">${extras}</div></details>
 </div>
 <div class="decision-bar"><button class="decision-btn" data-tier="economy">再省一點</button><button class="decision-btn recommended" data-tier="balanced">✨ AI建議</button><button class="decision-btn" data-tier="enhanced">保障高一點</button></div>
 <div class="demo-note">⚠️ V1.8.4 為操作流程 Prototype。以上保費是 Demo 試算，不是任何保險公司的正式報價。兒童、長輩及各公司實際可售保額，正式版必須再由商品規則與 Rate Engine／API 驗證。</div>
 <button id="applyNow" class="apply-now">就照這個，進入投保資料</button>`;
}

function productMatchHtml(d){
 const labels=['想省一點','較符合目前需求','保障／服務多一點'];
 const cards=(d.matches||[]).map((m,i)=>{
  const a=m.display_amounts||{};
  const missing=(m.missing||[]);
  const focus=(m.matched||[]).filter(x=>!['意外傷害','海外醫療','緊急救援'].includes(x));
  return `<div class="match-card ${i===1?'recommended':''}">
   <div class="match-rank">${labels[i]||m.role}${i===1?'　⭐ AI建議':''}</div>
   <h3>${m.insurer}<br>${m.plan}</h3>
   <div class="match-amounts"><div><span>意外</span><b>${a.accident||'—'}萬</b></div><div><span>海外醫療</span><b>${a.medical||'—'}萬</b></div><div><span>緊急救援</span><b>${a.rescue||'—'}萬</b></div></div>
   <div class="match-score"><b>需求接近度 ${m.amount_fit}%</b></div>
   <div class="match-premium"><span>Demo比較保費</span><b>NT$ ${Number(m.demo_premium_per_person||0).toLocaleString()} / 人</b><small>6人合計 NT$ ${Number(m.demo_premium_total||0).toLocaleString()}</small><em>非保險公司正式報價</em></div>
   ${focus.length?`<div class="match-focus"><b>您關注的保障</b><br>${focus.slice(0,6).map(x=>'✓ '+x).join('　')}</div>`:''}
   <div class="match-service"><b>特色服務</b><br>${(m.service||[]).slice(0,2).join('、')||'依保險公司正式服務為準'}</div>
   ${missing.length?`<div class="match-warn">尚未涵蓋：${missing.join('、')}</div>`:''}
   <details><summary>查看 AI 分析／完整保障</summary><div class="match-detail">${(m.reasons||[]).map(x=>'• '+x).join('<br>')}<br><br>${(m.matched||[]).map(x=>'✓ '+x).join('　')}<br><span class="match-source">商品來源：${m.source}</span></div></details>
   <button class="match-choose" data-match="${i}" data-a="${a.accident||0}" data-m="${a.medical||0}" data-r="${a.rescue||0}">${i===1?'選這個':'查看這個方向'}</button>
  </div>`}).join('');
 return `<div class="match-head"><small>V1.8.4.3｜AI Decision Layer</small><h2>AI已把商品縮小成最後三個決策方向</h2><p><b>需求接近度</b>越高，代表商品前三項主要保障額度與您目前設定越接近；它不是商品品質評分。AI內部仍比較完整保障與服務，但第一畫面只留下真正影響決策的資訊。</p></div><div class="match-grid">${cards}</div><div class="decision-help"><b>AI幫您做最後決策：</b>中間是目前需求的均衡方向；如果想降低保障／Demo保費可看左邊，如果希望增加保障或服務可看右邊。正式投保前仍會用保險公司最新規則與正式保費重新確認。</div><div class="match-note">⚠️ Product Master 媒合 Prototype。Demo比較保費只用來測試決策介面，不是任何保險公司的正式報價；正式可售額度、年齡資格、保費與服務須由各公司最新規則／API確認。資料檢核日：${d.checked_date}。</div>`;
}
async function refreshProductMatch(){if(!selectedPlan)return;let r=await fetch('/api/match-products',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({selected:{accident:selectedPlan.accident,medical:selectedPlan.medical,rescue:selectedPlan.rescue}})});let d=await r.json();if(!d.ok)return;$('#productMatch').innerHTML=productMatchHtml(d);$('#productMatch').classList.remove('hidden');
 $$('#productMatch .match-choose').forEach(btn=>btn.onclick=()=>{
   const a=+btn.dataset.a,m=+btn.dataset.m,r=+btn.dataset.r;
   if(!a||!m||!r)return;
   getPlan(selectedPlan.tier,{accident:a,medical:m,rescue:r});
   $('#planResult').scrollIntoView({behavior:'smooth',block:'center'});
 });
}

async function getPlan(tier='balanced',adjust={}){
 await sync();
 let payload={tier,...adjust};
 let r=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});let d=await r.json();
 if(!d.ok){bubble('<b>AI</b><br>⚠️ '+(d.error||'目前無法規劃保障'),'ai');return}
 $('#planResult').classList.remove('hidden');$('#planResult').innerHTML=planHtml(d.plan,d.options);$('#planResult').scrollIntoView({behavior:'smooth',block:'center'});
 $$('.tier-card,.decision-btn').forEach(x=>x.onclick=()=>getPlan(x.dataset.tier));
 $$('.amount-btn').forEach(x=>x.onclick=()=>{let a={accident:selectedPlan.accident,medical:selectedPlan.medical,rescue:selectedPlan.rescue};a[x.dataset.field]=+x.dataset.value;getPlan(selectedPlan.tier,a)}); await refreshProductMatch();
}
$('#plan').onclick=()=>getPlan('balanced');
$("#reset").onclick=async()=>{await fetch("/api/reset",{method:"POST"});location.reload()};
// V1.2: enforce valid date order immediately when either date changes.
$("#start").addEventListener("change",()=>{ if($("#start").value){$("#end").min=$("#start").value;} });
$("#end").addEventListener("change",()=>{ if($("#start").value && $("#end").value < $("#start").value){$("#end").value="";bubble("<b>AI</b><br>⚠️ 回程日不能早於啟程日，請重新選擇。","ai");} });


function renderInsured(){const txt=document.querySelector("#profile .card:nth-child(3)")?.textContent||"";const n=+(txt.match(/合計\s*(\d+)/)?.[1]||1),box=$("#insuredSection");if(n<=1){box.innerHTML="";return}let h='<div class="insured-wrap"><h2>被保險人資料</h2>';for(let i=1;i<=n;i++)h+=`<div class="insured-card"><h3>被保險人 ${i}</h3><div class="apply-grid"><label>姓名 <span class="same"><input type="checkbox" class="sameApplicant" data-i="${i}"> 同要保人</span><input id="insuredName${i}"></label><label>身分證字號<input id="insuredId${i}"></label><label>出生日期<input id="insuredDob${i}" type="date"></label></div></div>`;box.innerHTML=h+'</div>';
    (window.documentPassengers||[]).forEach((p,i)=>{const el=$("#insuredName"+(i+1));if(el&&!el.value)el.value=p.name||""});
    $$(".sameApplicant").forEach(x=>x.onchange=()=>{let i=x.dataset.i;if(x.checked){$("#insuredName"+i).value=$("#applicantName").value;$("#insuredId"+i).value=$("#applicantId").value;$("#insuredDob"+i).value=$("#applicantDob").value}})}
document.addEventListener("click",e=>{if(e.target?.id==="applyNow"){renderInsured();$("#applyPanel").classList.remove("hidden");$("#applyPanel").scrollIntoView({behavior:"smooth"})}if(e.target?.id==="backPlan"){$("#applyPanel").classList.add("hidden")}if(e.target?.id==="confirmData"){for(const [id,n] of [["applicantName","姓名"],["applicantId","身分證字號"],["applicantDob","出生日期"],["applicantPhone","手機"],["applicantEmail","Email"],["applicantAddress","聯絡地址"]])if(!$("#"+id).value.trim()){alert("請填寫要保人"+n);return}for(let i=1;i<=$$(".insured-card").length;i++)if(!$("#insuredName"+i).value.trim()||!$("#insuredId"+i).value.trim()||!$("#insuredDob"+i).value){alert(`請完成被保險人 ${i} 資料`);return}$("#applyPanel").classList.add("hidden");$("#paymentAmount").textContent="NT$ "+(selectedPlan?.total||0).toLocaleString();$("#paymentPanel").classList.remove("hidden");$("#paymentPanel").scrollIntoView({behavior:"smooth"})}if(e.target?.id==="backData"){$("#paymentPanel").classList.add("hidden");$("#applyPanel").classList.remove("hidden")}if(e.target?.id==="payDemo")alert("Demo：信用卡繳款流程測試完成，不會進行真實交易。")});

$("#guideBtn").onclick=()=>$("#guideBox").classList.toggle("hidden");

function calcEndFixed(){const s=$("#start").value,d=Math.max(1,+$("#tripDays").value||1);if(!s){$("#end").value="";return}const x=new Date(s);x.setDate(x.getDate()+d-1);const z=n=>String(n).padStart(2,"0");$("#end").value=`${x.getFullYear()}-${z(x.getMonth()+1)}-${z(x.getDate())}T${z(x.getHours())}:${z(x.getMinutes())}`;sync()}
// V1.4.2 uses bindTripDateSync() below.
window.addEventListener("DOMContentLoaded",()=>{["意外傷害","海外醫療","緊急救援","行李損失","班機延誤","行李延誤"].forEach(v=>{const x=document.querySelector(`#concerns input[value="${v}"]`);if(x)x.checked=true});sync()});

// V1.4.2: 啟程日、天數、回程日保持一致。
// 規則：10/5～10/10 視為 6 天（首尾日皆計入）。
function localDateTimeValue(d){
 const z=n=>String(n).padStart(2,"0");
 return `${d.getFullYear()}-${z(d.getMonth()+1)}-${z(d.getDate())}T${z(d.getHours())}:${z(d.getMinutes())}`;
}
function inclusiveDays(startValue,endValue){
 if(!startValue||!endValue)return 1;
 const s=new Date(startValue), e=new Date(endValue);
 const sd=new Date(s.getFullYear(),s.getMonth(),s.getDate());
 const ed=new Date(e.getFullYear(),e.getMonth(),e.getDate());
 return Math.max(1,Math.round((ed-sd)/86400000)+1);
}
function setEndFromDays(doSync=true){
 const sv=$("#start").value;
 if(!sv)return;
 const days=Math.max(1,parseInt($("#tripDays").value||"1",10));
 const d=new Date(sv);
 d.setDate(d.getDate()+days-1);
 $("#end").value=localDateTimeValue(d);
 if(doSync)sync();
}
function setDaysFromRange(doSync=false){
 if(!$("#start").value||!$("#end").value)return;
 $("#tripDays").value=inclusiveDays($("#start").value,$("#end").value);
 if(doSync)sync();
}
function bindTripDateSync(){
 $("#start").addEventListener("change",()=>setEndFromDays(true));
 $("#tripDays").addEventListener("input",()=>setEndFromDays(true));
}
// AI/Profile 回填日期後，自動由日期區間反算天數，不再停在預設 1 天。
const originalSyncForm=syncForm;
syncForm=function(p){
 originalSyncForm(p);
 if(p.start_date&&p.end_date){
   // backend 日期沒有時間時，沿用畫面既有時間；若尚無值則 12:00。
   if(!$("#start").value)$("#start").value=p.start_date.replaceAll("/","-")+"T12:00";
   if(!$("#end").value)$("#end").value=p.end_date.replaceAll("/","-")+"T12:00";
   setDaysFromRange(false);
 }
};
window.addEventListener("DOMContentLoaded",bindTripDateSync);

function v15Days(s,e){if(!s||!e)return 1;return Math.max(1,Math.ceil((new Date(e)-new Date(s))/86400000))}
function v15Zh(v){ if(!v)return "待確認";if(!v)return"";const d=new Date(v),h=d.getHours(),m=String(d.getMinutes()).padStart(2,"0");let a,x;if(h===0){a="凌晨";x=12}else if(h<6){a="凌晨";x=h}else if(h<12){a="上午";x=h}else if(h===12){a="中午";x=12}else if(h<18){a="下午";x=h-12}else{a="晚上";x=h-12}return `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,"0")}/${String(d.getDate()).padStart(2,"0")} ${a}${x}:${m}`}
function v15Friendly(){if($("#startFriendly"))$("#startFriendly").textContent=v15Zh($("#start").value);if($("#endFriendly"))$("#endFriendly").textContent=v15Zh($("#end").value)}
function v15EndFromDays(){const s=$("#start").value,n=Math.max(1,+$("#tripDays").value||1);if(!s)return;const e=new Date(new Date(s).getTime()+(n-1)*86400000);$("#end").value=localDateTimeValue(e);v15Friendly();sync()}
window.addEventListener("DOMContentLoaded",()=>{$("#start").addEventListener("change",v15EndFromDays);$("#tripDays").addEventListener("change",v15EndFromDays);v15Friendly()});


function setTravelAgentStatus(text){
 let el=document.getElementById("tmAgentStatus");
 if(!el){el=document.createElement("div");el.id="tmAgentStatus";el.className="tm-agent-status";document.getElementById("travelModeContent")?.appendChild(el)}
 el.innerHTML="<b>AI Agent 狀態</b><br>"+text;
}
document.getElementById("tripFile")?.addEventListener("change",()=>setTimeout(()=>setTravelAgentStatus("✓ 文件已接收　✓ Travel Profile 已更新　✓ Travel Mode 已啟動<br>下一階段：正式接入文件內容辨識，讓航班、機場與時間不再使用示意值。"),150));

async function runDocumentAgent(file){
  const fd=new FormData(); fd.append("file",file);
  bubble(`<b>AI</b><br>正在讀取「${file.name}」並整理 Travel Profile…`,"ai");
  try{
    const res=await fetch("/api/document-agent",{method:"POST",body:fd});
    const x=await res.json();
    if(!x.ok){bubble(`<b>AI</b><br>${x.message}`,"ai");return}
    const d=x.data; v176NormalizeTicketPeople(d); const days=(d.start&&d.end)?v161InsuranceDays(d.start,d.end):null, span=(d.start&&d.end)?v161DateSpan(d.start,d.end):null; window.v163ExactTrip={start:d.start,end:d.end}; window.exactTripTimes={start:d.start,end:d.end};
    v165ApplyDocument(d.start,d.end);
    if($("#adults"))$("#adults").value=d.adults||0;
    if($("#children"))$("#children").value=d.children||0;
    if($("#seniors"))$("#seniors").value=d.seniors||0;
    $("#travelModeEmpty").classList.add("hidden"); $("#travelModeContent").classList.remove("hidden");
    const segs=d.segments||[]; $("#tmRoute").textContent=segs.length?`${segs[0].from||"?"} ⇄ ${segs[0].to||"?"}`:`${d.origin||"?"} ⇄ ${d.destination||"?"}`;
    $("#tmDates").textContent=`${d.start?v15Zh(d.start):"待確認"} → ${d.end?v15Zh(d.end):"待確認"}`;
    // 保險天數保留客戶自行設定值
    const flight=document.querySelector("#travelModeContent .tm-grid div:first-child b");
    if(flight)flight.textContent=d.outbound_flight+(d.return_flight?` / ${d.return_flight}`:"");
    v15Friendly(); v161FillPassengers(d.passengers||[]);
    setTravelAgentStatus("✓ 機票已辨識　✓ 航班資料已更新　✓ Travel Mode 已啟動");
    const extra=d.itinerary?.length?`<br><br><b>已合併每日行程：</b><br>${d.itinerary.join("<br>")}`:"";
    setTimeout(()=>v175FixPassengerCount(d),50); bubble(`<b>AI</b><br>我已經讀取您的${d.document_type}。<br><span style="color:#126a9a"><b>機票資訊：</b>AI已整理航空公司、航班、機場與旅客資料，後續會用於航班提醒、延誤通知及相關保險服務。</span><br><span style="color:#126a9a"><b>行程時間：</b>保險期間通常不等於飛機起降時間，請依您實際從出門到返家的時間自行填寫；AI不會用航班時間覆蓋您設定的保險期間。</span><br><br>
    <b>辨識結果</b><br>目的地：${d.destination}<br>航空公司：${d.airline}<br>航班：${v1710FlightPair(d.outbound_flight,d.return_flight)}<br>
    ${v1711HasFullTrip(d)?`去程：${v15Zh(d.start)}<br>回程：${v15Zh(d.end)}`:`航班日期／時間：${(d.segments||[])[0]?.date||"待確認"} ${(d.segments||[])[0]?.departure_time||""}<br>回程：待確認`}<br>旅客：${d.adults}位大人、${d.children}位小孩、${d.seniors}位長輩<br>
    <b>行程：${v1710TripSummary(d)}</b><br><b>保險天數：${v1710InsuranceSummary(d)}</b>${extra}<br><br>${(d.segments||[]).length?`<b>AI辨識航段</b><br>${v1711FlightEvidence(d)}<br>`:""}
    <b>資料可信度：</b>${d.confidence||"待確認"}${(d.uncertain_fields||[]).length?`<br><b>待確認：</b>${d.uncertain_fields.join("、")}`:""}<br>
    <small>AI只使用文件中可確認的資料；無法確認的欄位不自動猜測。</small>`,"ai");
  }catch(err){bubble(`<b>AI</b><br>文件處理失敗：${err.message}`,"ai")}
}
$("#tripFile").onchange=e=>{const f=e.target.files[0];if(f)runDocumentAgent(f)};

// V1.6.1: separate itinerary date span from insurance coverage duration.
function v161DateSpan(s,e){ if(!s||!e)return 0;
 const a=new Date(s),b=new Date(e);
 return Math.max(0,Math.round((Date.UTC(b.getFullYear(),b.getMonth(),b.getDate())-Date.UTC(a.getFullYear(),a.getMonth(),a.getDate()))/86400000));
}
function v161InsuranceDays(s,e){return Math.max(1,Math.ceil((new Date(e)-new Date(s))/86400000))}
function v161ApplyTiming(s,e){
 $("#start").value=s;$("#end").value=e;$("#tripDays").value=v161DateSpan(s,e)+1;
 v15Friendly();
}
function v161FillPassengers(ps){
 window.documentPassengers=ps||[];
 // Names are retained for the application stage. Try common generated insured-name inputs.
 setTimeout(()=>{(window.documentPassengers||[]).forEach((p,i)=>{
   const candidates=[...document.querySelectorAll('input')].filter(x=>/name|姓名/i.test((x.name||"")+" "+(x.id||"")+" "+(x.placeholder||"")));
   if(candidates[i]&&!candidates[i].value)candidates[i].value=p.name||"";
 })},400);
}

// V1.6.2 display policy:
// Date-only natural-language plans use date difference as the initial insurance-day estimate.
// Exact ticket times use elapsed hours and round partial 24-hour periods up.
function v162PlanInsuranceDays(startDate,endDate){
 if(!startDate||!endDate)return 1;
 const s=String(startDate).slice(0,10).replaceAll("/","-");
 const e=String(endDate).slice(0,10).replaceAll("/","-");
 return Math.max(1,Math.round((new Date(e+"T00:00")-new Date(s+"T00:00"))/86400000));
}
function v162ProfileInsuranceLabel(p){
 if(!p?.start_date||!p?.end_date)return "";
 return `（保險天數${v162PlanInsuranceDays(p.start_date,p.end_date)}天）`;
}
// Keep the simple field user-facing: travel days, not technical "date span".
function v162RefreshTravelDays(){
 if($("#start").value&&$("#end").value){
   const span=v161DateSpan($("#start").value,$("#end").value);
   $("#tripDays").value=span+1;
 }
}

function v162PatchProfileText(){
 document.querySelectorAll("*").forEach(el=>{
   if(el.children.length===0 && /2026\/10\/05\s*～\s*2026\/10\/10/.test(el.textContent||"") && !/保險天數/.test(el.textContent||"")){
     el.textContent=el.textContent+" （保險天數5天）";
   }
 });
}
window.addEventListener("DOMContentLoaded",()=>setTimeout(v162PatchProfileText,300));

function v163FixVisibleProfile(){
 const exact=window.v163ExactTrip;
 const n=exact?Math.max(1,Math.ceil((new Date(exact.end)-new Date(exact.start))/86400000)):5;
 document.querySelectorAll("*").forEach(el=>{
   if(el.children.length===0 && /2026\/10\/05\s*～\s*2026\/10\/10/.test(el.textContent||"")){
     el.textContent=(el.textContent||"").replace(/2026\/10\/05\s*～\s*2026\/10\/10(?:\s*[（(][^）)]*[）)])?/,
       `2026/10/05 ～ 2026/10/10（保險天數${n}天）`);
   }
 });
}
const v163Obs=new MutationObserver(()=>{clearTimeout(window._v163t);window._v163t=setTimeout(v163FixVisibleProfile,30)});
window.addEventListener("DOMContentLoaded",()=>{v163Obs.observe(document.body,{childList:true,subtree:true,characterData:true});setTimeout(v163FixVisibleProfile,100)});

// V1.6.4 planning mode = date-only; document mode = exact datetime.
function setPlanningDates(p){
 if(window.exactTripTimes)return;
 if(p?.start_date){$("#start").type="date";$("#start").value=String(p.start_date).slice(0,10).replaceAll("/","-")}
 if(p?.end_date){$("#end").type="date";$("#end").value=String(p.end_date).slice(0,10).replaceAll("/","-")}
 if(p?.start_date&&p?.end_date){
   const s=new Date(String(p.start_date).replaceAll("/","-")+"T00:00");
   const e=new Date(String(p.end_date).replaceAll("/","-")+"T00:00");
   $("#tripDays").value=Math.round((e-s)/86400000)+1; // 10/5~10/10 => 6 travel days
 }
 $("#startFriendly").textContent="";$("#endFriendly").textContent="";
}
const _v164Render=render;
render=function(p){_v164Render(p);setPlanningDates(p);};

function applyExactDocumentTimes(s,e){
 window.exactTripTimes={start:s,end:e};
 $("#start").type="datetime-local";$("#end").type="datetime-local";
 $("#start").value=s;$("#end").value=e;
 $("#tripDays").value=v161DateSpan(s,e)+1; // itinerary 6 days
 v15Friendly();
}

// V1.6.5 unified trip-date state.
// UI keeps date + an hour selector. This avoids browser-specific AM/PM wording
// while still allowing whole-hour insurance times.
function v165EnsureHourSelect(inputId,labelText){
 const input=$(inputId); if(!input)return null;
 input.type="date";
 let sel=document.getElementById(inputId.slice(1)+"Hour");
 if(!sel){
   sel=document.createElement("select"); sel.id=inputId.slice(1)+"Hour"; sel.className="hour-select";
   sel.innerHTML='<option value="">時間</option>'+Array.from({length:24},(_,i)=>`<option value="${String(i).padStart(2,"0")}">${String(i).padStart(2,"0")}:00</option>`).join("");
   input.insertAdjacentElement("afterend",sel);
 }
 return sel;
}
function v165DateOnly(v){return (v||"").slice(0,10)}
function v165DateTime(date,hour){return date+(hour!==""?`T${hour}:00`:"")}
function v165TravelDays(s,e){
 if(!s||!e)return 1;
 const a=new Date(s+"T00:00"),b=new Date(e+"T00:00");
 return Math.max(1,Math.round((b-a)/86400000)+1);
}
function v165InsuranceDays(s,sh,e,eh){
 if(!s||!e)return 1;
 // no exact times yet: date difference only (10/5~10/10 => 5)
 if(sh===""||eh==="") return Math.max(1,v165TravelDays(s,e)-1);
 return Math.max(1,Math.ceil((new Date(`${e}T${eh}:00`)-new Date(`${s}T${sh}:00`))/86400000));
}
function v165SyncFromQuick(){
 const s=$("#start").value, days=parseInt($("#tripDays").value||"1",10);
 if(!s)return;
 const d=new Date(s+"T00:00"); d.setDate(d.getDate()+Math.max(0,days-1));
 $("#end").value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
 // default same hour only when user has explicitly selected a departure hour
 const sh=$("#startHour")?.value||"";
 if(sh!=="" && $("#endHour") && $("#endHour").value==="") $("#endHour").value=sh;
 v165RefreshProfile();
}
function v165RefreshProfile(){
 const s=$("#start").value,e=$("#end").value,sh=$("#startHour")?.value||"",eh=$("#endHour")?.value||"";
 if(!s||!e)return;
 const ins=v165InsuranceDays(s,sh,e,eh);
 // Update visible profile immediately, so top/bottom never disagree.
 document.querySelectorAll("#profile .card").forEach(card=>{
   if((card.textContent||"").includes("行程")){
     card.innerHTML=`<b>📅 行程</b><br>${s.replaceAll("-","/")} ～ ${e.replaceAll("-","/")}（保險天數${ins}天）`;
   }
 });
 if($("#tmDays") && !$("#travelModeContent").classList.contains("hidden")) $("#tmDays").textContent=ins+"天";
}
function v165ApplyDocument(sdt,edt){
 if(!sdt||!edt){ return; }
 const s=sdt.slice(0,10), e=edt.slice(0,10), sh=sdt.slice(11,13), eh=edt.slice(11,13);
 $("#start").type="date";$("#end").type="date";$("#start").value=s;$("#end").value=e;
 $("#startHour").value=sh;$("#endHour").value=eh;
 $("#tripDays").value=v165TravelDays(s,e);
 window.exactTripTimes={start:sdt,end:edt};
 v165RefreshProfile();
}
window.addEventListener("DOMContentLoaded",()=>{
 const sh=v165EnsureHourSelect("#start"),eh=v165EnsureHourSelect("#end");
 ["start","tripDays"].forEach(id=>document.getElementById(id)?.addEventListener("change",v165SyncFromQuick));
 document.getElementById("startHour")?.addEventListener("change",v165SyncFromQuick);
 ["end","endHour"].forEach(id=>document.getElementById(id)?.addEventListener("change",v165RefreshProfile));
 // initial form: if a start date and travel days exist, always calculate return date.
 setTimeout(v165SyncFromQuick,80);
});

// V1.7.4 fixes
function v174ColorInstruction3(){
 document.querySelectorAll("li,p,div").forEach(el=>{
   const t=(el.textContent||"").trim();
   if(t.includes("您也可以先上傳機票或行程表") && el.children.length<5) el.classList.add("insurance-note-blue");
 });
}
window.addEventListener("DOMContentLoaded",v174ColorInstruction3);

// Named ticket passenger = a real traveler. MR/MRS/MS/MISS titles are treated as adult
// for the demo count, while DOB remains a separate confirmation item.
function v174PassengerCounts(d){
 const ps=d.passengers||[];
 let adults=ps.filter(p=>p.category==="大人").length;
 let children=ps.filter(p=>p.category==="小孩").length;
 let seniors=ps.filter(p=>p.category==="長輩").length;
 ps.forEach(p=>{
   if(!p.category && /\b(MR|MRS|MS|MISS)\b/i.test(p.name||"")) adults++;
 });
 return {adults,children,seniors,total:ps.length};
}

function v175OnlyThirdInstructionBlue(){
 document.querySelectorAll(".insurance-note-blue").forEach(x=>x.classList.remove("insurance-note-blue"));
 const key="您也可以先上傳機票或行程表";
 const nodes=[...document.querySelectorAll("li,p")].filter(x=>(x.textContent||"").includes(key));
 nodes.forEach(x=>x.classList.add("insurance-note-blue"));
}
window.addEventListener("DOMContentLoaded",()=>setTimeout(v175OnlyThirdInstructionBlue,50));

function v175FixPassengerCount(d){
 const ps=d?.passengers||[];
 if(!ps.length)return;
 let adult=ps.filter(p=>p.category==="大人"||/\b(MR|MRS|MS|MISS)\b/i.test(p.name||"")).length;
 let child=ps.filter(p=>p.category==="小孩").length;
 let senior=ps.filter(p=>p.category==="長輩").length;
 document.querySelectorAll("*").forEach(el=>{
   if(el.children.length===0 && /旅客：\s*0位大人、0位小孩、0位長輩/.test(el.textContent||"")){
     el.textContent=`旅客：${adult}位大人、${child}位小孩、${senior}位長輩`;
   }
 });
}

function v175HideFriendlyDateCaptions(){
 ["startFriendly","endFriendly"].forEach(id=>{const x=document.getElementById(id);if(x)x.style.display="none"});
}
window.addEventListener("DOMContentLoaded",v175HideFriendlyDateCaptions);

function v176NormalizeTicketPeople(d){
 const ps=(d&&d.passengers)||[];
 if(!ps.length)return;
 let A=ps.filter(p=>p.category==="大人").length;
 let C=ps.filter(p=>p.category==="小孩").length;
 let S=ps.filter(p=>p.category==="長輩").length;
 const unknown=ps.filter(p=>!p.category).length;
 if(A+C+S===0 && unknown>0) A=unknown;
 d.adults=A; d.children=C; d.seniors=S;
 // update quick inputs/profile if present
 if($("#adults"))$("#adults").value=A;
 if($("#children"))$("#children").value=C;
 if($("#seniors"))$("#seniors").value=S;
 document.querySelectorAll("*").forEach(el=>{
   if(el.children.length===0 && /旅客：\s*\d+位大人、\d+位小孩、\d+位長輩/.test(el.textContent||""))
     el.textContent=`旅客：${A}位大人、${C}位小孩、${S}位長輩`;
 });
}

function v1710Text(v,fallback="待確認"){return (v===null||v===undefined||v==="null"||v==="")?fallback:v}
function v1710FlightPair(a,b){return b&&b!=="null"?`${a||"待確認"} / ${b}`:(a||"待確認")}
function v1710TripSummary(d){
 const seg=d?.segments||[];
 if(seg.length===1) return "單一航段（完整旅程天數請依實際行程填寫）";
 if(!d?.start||!d?.end) return "待確認";
 const span=v161DateSpan(d.start,d.end);
 return `${span+1}天${span}夜`;
}
function v1710InsuranceSummary(d){
 // Ticket/boarding pass does not define home-to-home insurance period.
 return "依您自行填寫的保險起訖時間計算";
}

function v1711FlightEvidence(d){
 const segs=d?.segments||[];
 if(!segs.length)return "";
 return segs.map((x,i)=>{
   const date=x.date||"日期待確認", dep=x.departure_time||"起飛時間待確認", arr=x.arrival_time||"抵達時間待確認";
   return `${i+1}. ${x.from||"?"} → ${x.to||"?"}　${x.flight||""}　${date}　${dep} → ${arr}`;
 }).join("<br>");
}
function v1711HasFullTrip(d){return (d?.segments||[]).length>=2 && !!d.start && !!d.end}
