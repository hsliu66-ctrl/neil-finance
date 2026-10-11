(function(){
"use strict";
var status=document.getElementById("week-status"),grid=document.getElementById("week-grid"),detail=document.getElementById("week-detail");
function esc(x){return String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function date(x){return esc(x||"")}
function reportLink(id){return "article.html?id="+encodeURIComponent(id)}
function show(w){
 var path=String(w.dataFile||"");
 if(!/^data\/weekly\/\d{4}-W\d{2}\.json$/.test(path)){status.textContent="歸檔檔案路徑異常";return}
 status.textContent="讀取 "+w.week+" 內容中…";
 fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("找不到歸檔資料");return r.json()}).then(a=>{
 if(a.week!==w.week)throw Error("歸檔週別不一致");
 var rows=Object.entries(a.market||{}).sort((x,y)=>x[0].localeCompare(y[0]));
 var articleRows=a.articles||[];
 detail.hidden=false;
 detail.innerHTML='<h2>'+esc(w.week)+'｜'+esc(w.from)+' – '+esc(w.to)+'</h2>'
 +'<h3>市場指標｜週內首末觀測值</h3>'
 +(rows.length?'<table><thead><tr><th>系列</th><th>期初日期與數值</th><th>期末日期與數值</th><th>筆數</th></tr></thead><tbody>'+
 rows.map(([id,x])=>'<tr><td>'+esc(id)+'</td><td>'+esc(x.first.date)+'：'+Number(x.first.value).toFixed(4)+'</td><td>'+esc(x.last.date)+'：'+Number(x.last.value).toFixed(4)+'</td><td>'+Number(x.observations)+'</td></tr>').join('')+'</tbody></table>':'<p>此週沒有可核對的官方觀測值。</p>')
 +'<h3>研究文章｜'+articleRows.length+' 篇</h3>'+
 (articleRows.length?'<ul>'+articleRows.map(r=>'<li>'+date(r.date)+'｜<a href="'+reportLink(String(r.id||""))+'">'+esc(r.title)+'</a>'+(r.sample?'（示範）':'')+'</li>').join('')+'</ul>':'<p>此週沒有已登錄的研究文章。</p>')
 +'<p style="margin-top:20px;font-size:12px;color:#627780">僅保存已發表文章的 ID 與標題。請點文章查看來源及完整內容。</p>';
 status.textContent="顯示 "+w.week+" 歸檔";
 detail.scrollIntoView({behavior:"smooth",block:"start"});
 }).catch(e=>{status.textContent="讀取歸檔失敗："+e.message});
}
fetch("data/weekly-index.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("索引尚未建立");return r.json()}).then(data=>{
 var weeks=(data.weeks||[]).sort((a,b)=>b.week.localeCompare(a.week));
 if(!weeks.length){status.textContent="等待首次每週自動歸檔執行，尚未產生歷史週報。";return}
 status.textContent="共 "+weeks.length+" 週歷史資料";
 grid.innerHTML=weeks.map((w,i)=>'<article class="week-card"><div style="font-size:11px;letter-spacing:2px;color:#285b4d">ARCHIVE / '+esc(w.week)+'</div><h2>'+date(w.from)+' – '+date(w.to)+'</h2><p>文章：'+Number(w.articleCount||0)+' 篇｜市場數據系列：'+Number(w.seriesCount||0)+' 組</p><button type="button" data-week="'+esc(w.week)+'" style="padding:10px 15px;background:#142b36;color:#fff;border:0;cursor:pointer">查看本週歸檔 ↗</button></article>').join('');
 grid.addEventListener("click",e=>{var b=e.target.closest("button[data-week]");if(b){var w=weeks.find(x=>x.week===b.dataset.week);if(w)show(w)}});
 }).catch(e=>{status.textContent="歸檔資料尚不可用："+e.message});
})();