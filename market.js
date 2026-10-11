(function(){
"use strict";
var labels={
"UST_1M":"美債 1 個月","UST_2M":"美債 2 個月","UST_3M":"美債 3 個月",
"UST_6M":"美債 6 個月","UST_1Y":"美債 1 年","UST_2Y":"美債 2 年",
"UST_3Y":"美債 3 年","UST_5Y":"美債 5 年","UST_7Y":"美債 7 年",
"UST_10Y":"美債 10 年","UST_20Y":"美債 20 年","UST_30Y":"美債 30 年",
"ECB_EURUSD":"EUR/USD（ECB 參考）",
"ECB_USDJPY":"USD/JPY（ECB 交叉換算）",
"ECB_USDCNY":"USD/CNY（ECB 交叉換算）"
};
var desired=["UST_10Y","UST_2Y","UST_30Y","UST_3M","ECB_EURUSD","ECB_USDJPY","ECB_USDCNY"];
function el(id){return document.getElementById(id)}
function escape(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function val(x){return Number(x).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:5})}
function isYield(id){return id.startsWith("UST_")}
function unit(id){return isYield(id)?"%":""}
function draw(data,id){
 if(data.length<2)return "<p>有效觀測值少於兩筆，暫無法繪製曲線。</p>";
 var W=740,H=265,L=59,R=22,T=23,B=46;
 var values=data.map(d=>Number(d.value)), low=Math.min(...values), high=Math.max(...values), diff=high-low||.05;
 low-=diff*.12;high+=diff*.12;
 var xs=values.map((v,i)=>L+i*(W-L-R)/(values.length-1));
 var ys=values.map(v=>T+(high-v)/(high-low)*(H-T-B));
 var path=xs.map((x,i)=>(i?"L":"M")+x.toFixed(2)+","+ys[i].toFixed(2)).join(" ");
 var xTicks=[0,Math.floor((data.length-1)/2),data.length-1].map(i=>'<text x="'+xs[i]+'" y="'+(H-14)+'" text-anchor="middle" font-size="12" fill="#586d75">'+escape(data[i].date)+'</text>').join("");
 var grids=Array.from({length:5},(_,i)=>{let y=T+i*(H-T-B)/4;return '<path d="M'+L+','+y+' H'+(W-R)+'" stroke="#e0e5e0"/><text x="'+(L-8)+'" y="'+(y+4)+'" text-anchor="end" font-size="11" fill="#586d75">'+val(high-i*(high-low)/4)+'</text>'}).join("");
 return '<svg class="data-chart" role="img" aria-label="'+escape(labels[id])+' 歷史折線圖" viewBox="0 0 740 265">'+grids+'<path d="'+path+'" fill="none" stroke="#285b4d" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'+xTicks+'</svg>';
}
Promise.all([
 fetch("data/history.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("資料庫狀態 "+r.status);return r.json()}),
 fetch("data/latest.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("最新資料 "+r.status);return r.json()})
]).then(function(results){
 var history=results[0],latest=results[1];
 var data=history.series||{}, keys=Object.keys(data).filter(k=>Array.isArray(data[k])&&data[k].length).sort((a,b)=>(desired.indexOf(a)<0?99:desired.indexOf(a))-(desired.indexOf(b)<0?99:desired.indexOf(b)));
 if(!keys.length){el("data-status").textContent="等待首次官方資料擷取。尚無已核實的市場數值，這裡不展示假行情。";el("data-rows").innerHTML='<tr><td colspan="3">首次 GitHub Actions 成功執行後才會顯示正式資料</td></tr>';return}
 el("data-status").textContent="已載入 "+keys.length+" 項官方觀測序列；數據日期各依來源，非即時報價。";
 el("series-select").innerHTML=keys.map(id=>'<option value="'+escape(id)+'">'+escape(labels[id]||id)+'</option>').join("");
 var featured=desired.filter(id=>keys.includes(id)).slice(0,8);
 el("data-kpis").innerHTML=featured.map(id=>{
 var last=data[id][data[id].length-1];
 return '<button class="data-kpi" type="button" data-id="'+escape(id)+'" aria-pressed="false"><span>'+escape(labels[id]||id)+'</span><strong>'+val(last.value)+unit(id)+'</strong><small>觀測日：'+escape(last.date)+'<br>'+escape(last.source)+'</small></button>';
 }).join("");
 var range=30;
 function render(){
 var id=el("series-select").value;if(!id||!data[id])return;
 var series=data[id].slice(range==="all"?0:-range);
 el("chart-heading").textContent=(labels[id]||id)+"｜"+series.length+" 筆觀測值（"+unit(id)+"）";
 el("chart-container").innerHTML=draw(series,id);
 el("data-rows").innerHTML=series.slice().reverse().slice(0,40).map(r=>'<tr><td>'+escape(r.date)+'</td><td>'+val(r.value)+unit(id)+'</td><td>'+escape(r.source)+'</td></tr>').join("");
 el("data-kpis").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.id===id)));
 }
 el("series-select").addEventListener("change",render);
 el("data-kpis").addEventListener("click",e=>{var b=e.target.closest("button[data-id]");if(b){el("series-select").value=b.dataset.id;render()}});
 el("range-controls").addEventListener("click",e=>{var b=e.target.closest("button[data-range]");if(!b)return;range=b.dataset.range==="all"?"all":Number(b.dataset.range);el("range-controls").querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));render()});
 el("series-select").value=keys.includes("UST_10Y")?"UST_10Y":keys[0];render();
}).catch(function(e){el("data-status").textContent="市場資料暫時無法載入，請稍後重試："+e.message;el("data-rows").innerHTML='<tr><td colspan="3">資料尚不可用</td></tr>'});
})();