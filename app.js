(function(){
'use strict';
var reports=Array.isArray(window.NEIL_REPORTS)?window.NEIL_REPORTS:[];
var labels={market:'美股晨報',macro:'全球總經',rates:'美債殖利率',fx:'匯率週報',etf:'ETF 研究',earnings:'財報洞察'};
var ordered=reports.slice().sort(function(a,b){return (b.date||'').localeCompare(a.date||'')});
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function ymd(v){return esc((v||'').replace(/-/g,'.'))}
function isTrustedImage(src){return /^assets\/reports\/[A-Za-z0-9_./-]+\.(?:png|jpe?g|webp)$/i.test(String(src||""))&&!String(src).includes("..")&&String(src).length<260}
function articleImages(r){
var images=(Array.isArray(r.images)?r.images:[]).filter(function(i){return i&&isTrustedImage(i.src)}).slice(0,12);
if(!images.length)return "";
return '<section class="report-media"><h2>研究圖卡與視覺摘要</h2><div class="report-media-grid">'
+images.map(function(i,idx){var alt=esc(i.alt||r.title+" 圖卡 "+(idx+1));return '<figure><a href="'+esc(i.src)+'" target="_blank" rel="noopener noreferrer" title="開啟原尺寸圖卡"><img loading="lazy" src="'+esc(i.src)+'" alt="'+alt+'"></a><figcaption>'+esc(i.caption||i.alt||"圖卡 "+(idx+1))+'</figcaption></figure>'}).join("")
+'</div><p class="media-source-note">點選圖卡可檢視原始大小。引用前請查核圖表上的數字、來源及授權。</p></section>'
}

function card(r,large){
return '<a class="article-card'+(large?' article-highlight':'')+'" href="article.html?id='+encodeURIComponent(r.id)+'" aria-label="閱讀 '+esc(r.title)+'">'
+'<div class="article-top"><span class="article-category">'+esc(labels[r.category]||'研究報告')+'</span><span class="article-status">'+(r.sample?'示範樣稿':'正式報告')+'</span></div>'
+(Array.isArray(r.images)&&r.images.length&&isTrustedImage(r.images[0].src)?'<div class="article-cover"><img loading="lazy" alt="'+esc(r.images[0].alt||r.title)+'" src="'+esc(r.images[0].src)+'"></div>':'')+'<h3>'+esc(r.title)+'</h3><p class="article-summary">'+esc(r.summary)+'</p><div class="article-footer"><span>'+ymd(r.date)+' ・ '+(Number(r.readingMinutes)||4)+' MIN READ</span><b>↗</b></div></a>';
}
function clock(){var d=document.getElementById('current-date');if(d){d.textContent=new Intl.DateTimeFormat('en-CA',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:'Asia/Taipei'}).format(new Date()).replace(/-/g,'.')}}
function home(){
var grid=document.getElementById('report-grid'),filters=document.getElementById('filters'),search=document.getElementById('report-search');
if(!grid||!filters||!search)return;
var current='all';
function render(){
var q=search.value.trim().toLowerCase();
var results=ordered.filter(function(r){return (current==='all'||r.category===current)&&[r.title,r.subtitle,r.summary].concat(r.tags||[]).join(' ').toLowerCase().includes(q)});
var featured=current==='all'&&!q?results.find(function(x){return x.featured}):null;
grid.innerHTML=(featured?card(featured,true):'')+results.filter(function(r){return !featured||r.id!==featured.id}).map(function(r){return card(r,false)}).join('');
var count=document.getElementById('result-count');if(count)count.textContent='共 '+results.length+' 篇研究報告';
var empty=document.getElementById('empty-state');if(empty)empty.hidden=results.length>0;
}
filters.addEventListener('click',function(e){var b=e.target.closest('button[data-filter]');if(!b)return;current=b.dataset.filter;Array.prototype.forEach.call(filters.querySelectorAll('button'),function(x){x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b))});render()});
search.addEventListener('input',render);
Array.prototype.forEach.call(document.querySelectorAll('[data-pick]'),function(link){link.addEventListener('click',function(){var b=filters.querySelector('button[data-filter="'+link.dataset.pick+'"]');if(b)b.click()})});
var reset=document.getElementById('reset-filter');if(reset)reset.addEventListener('click',function(){search.value='';var b=filters.querySelector('button[data-filter="all"]');if(b)b.click()});
render();
}
function chartMarkup(chart){
if(!chart||!Array.isArray(chart.points)||chart.points.length<2)return '';
var p=chart.points.filter(function(x){return isFinite(Number(x.value))});if(p.length<2)return '';
var vals=p.map(function(x){return Number(x.value)}),lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals),diff=hi-lo||1;
var min=lo-diff*.25,max=hi+diff*.25,W=700,H=250,L=55,R=25,T=28,B=43;
var xs=p.map(function(_,i){return L+(W-L-R)*i/(p.length-1)}),ys=vals.map(function(v){return T+(H-T-B)*(1-(v-min)/(max-min))});
var path=xs.map(function(x,i){return (i?'L':'M')+x.toFixed(1)+' '+ys[i].toFixed(1)}).join(' ');
var floor=H-B,area=path+' L '+xs[xs.length-1]+' '+floor+' L '+xs[0]+' '+floor+' Z';
var grid=[0,1,2,3].map(function(i){var y=T+i*(H-T-B)/3;return '<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y+'" y2="'+y+'" stroke="#dce2dc"/><text x="'+(L-8)+'" y="'+(y+4)+'" fill="#61747b" font-size="12" text-anchor="end">'+(max-i*(max-min)/3).toFixed(3)+'</text>'}).join('');
var ticks=p.map(function(v,i){return '<text x="'+xs[i]+'" y="'+(H-12)+'" font-size="13" fill="#5e747c" text-anchor="middle">'+esc(v.label)+'</text>'}).join('');
var dots=p.map(function(v,i){return '<circle cx="'+xs[i]+'" cy="'+ys[i]+'" r="5" fill="#285b4d" stroke="#fff" stroke-width="2"><title>'+esc(v.label)+'：'+vals[i]+'</title></circle>'}).join('');
return '<div class="report-chart"><div class="chart-heading">'+esc(chart.label)+'<span>'+esc(chart.unit)+'</span></div><svg class="chart-svg" viewBox="0 0 700 250" role="img" aria-label="'+esc(chart.label)+'">'+grid+'<path d="'+area+'" fill="#d5e4da" opacity=".8"/><path d="'+path+'" fill="none" stroke="#285b4d" stroke-width="3"/>'+dots+ticks+'</svg><table class="chart-data-table"><thead><tr><th>日期</th><th>數據</th></tr></thead><tbody>'+p.map(function(x){return '<tr><td>'+esc(x.label)+'</td><td>'+Number(x.value).toLocaleString('en-US',{maximumFractionDigits:5})+'</td></tr>'}).join('')+'</tbody></table></div>';
}
function article(){
var root=document.getElementById('article-container');if(!root)return;
var id=new URLSearchParams(location.search).get('id'),r=reports.find(function(x){return x.id===id});
if(!r){root.innerHTML='<div class="container article-shell"><h1>找不到這篇文章</h1><p>文章可能尚未發布，或網址不正確。</p><a href="index.html#reports">← 返回研究檔案</a></div>';return}
document.title=r.title+'｜Neil Financial Desk';
var m=(r.metrics||[]).map(function(x){return '<div class="metric-item"><div><label>'+esc(x.label)+'</label><small>'+esc(x.note)+'</small></div><strong>'+esc(x.value)+'</strong></div>'}).join('');
var sections=(r.sections||[]).map(function(s){return '<section class="article-section"><h2>'+esc(s.heading)+'</h2>'+(s.paragraphs||[]).map(function(p){return '<p>'+esc(p).replace(/\n/g,'<br>')+'</p>'}).join('')+((s.bullets||[]).length?'<ul>'+s.bullets.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ul>':'')+'</section>'}).join('');
var source='<div class="article-source"><strong>資料來源｜</strong>'+esc(r.source||'尚未提供')+(r.sourceUrl&&/^https?:\/\//i.test(r.sourceUrl)?' <a target="_blank" rel="noopener noreferrer" href="'+esc(r.sourceUrl)+'">原始來源 ↗</a>':'')+'<br><strong>整理日期｜</strong>'+ymd(r.date)+'<br><strong>內容整理｜</strong>📝 Neil 整理</div>';
var related=ordered.filter(function(x){return x.id!==id}).slice(0,2);
root.innerHTML='<div class="container"><div class="article-shell"><div class="article-print-brand"><img src="neil-logo.webp" alt="Neil 整理 Logo"><small>NEIL FINANCIAL DESK · 研究報告</small></div><nav class="breadcrumb"><a href="index.html">首頁</a><span>›</span><a href="index.html#reports">研究報告</a><span>›</span>'+esc(labels[r.category])+'</nav>'
+'<header class="article-header"><div class="article-meta-row"><span class="article-category">'+esc(labels[r.category])+'</span><span>／</span><span>'+ymd(r.date)+'</span><span>／</span><span>'+(r.readingMinutes||4)+' MIN READ</span>'+(r.sample?'<span class="article-status">示範樣稿</span>':'')+'</div><h1>'+esc(r.title)+'</h1><p class="article-subtitle">'+esc(r.subtitle)+'</p><p class="article-standfirst">'+esc(r.summary)+'</p><div class="article-utility"><div class="tag-list">'+(r.tags||[]).map(function(x){return '<span class="tag"># '+esc(x)+'</span>'}).join('')+'</div><div class="utility-buttons"><button type="button" id="copy-link">複製連結 ↗</button><button type="button" id="print-article">列印 / PDF ↓</button></div></div></header>'
+'<div class="article-body">'+(r.focus?'<div class="article-keynote"><span>NEIL’S KEY TAKEAWAY</span><strong>'+esc(r.focus)+'</strong></div>':'')+(m?'<div class="metrics-row">'+m+'</div>':'') +chartMarkup(r.chart)+articleImages(r)+sections+source+'<p class="article-print-disclaimer">🚫 僅供個人學習，請勿任意轉傳他人圖片或群組散布。僅供資訊參考，非投資建議。</p>'+(r.sample?'<div class="article-warning"><strong>內容提示：</strong>這是網站示範文章，不是即時行情；對外引用前請核實數據、資料來源與授權。</div>':'')+'</div>'
+(related.length?'<aside class="article-related"><h2>延伸閱讀</h2><div class="articles-grid">'+related.map(function(x){return card(x,false)}).join('')+'</div></aside>':'')+'</div></div>';
var cp=document.getElementById('copy-link');if(cp)cp.addEventListener('click',function(){if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(location.href).then(function(){cp.textContent='已複製 ✓'}).catch(function(){window.prompt('複製連結',location.href)})}else{window.prompt('複製連結',location.href)}});
var print=document.getElementById('print-article');if(print)print.addEventListener('click',function(){window.print()});
}
clock();if(document.body.dataset.page==='home')home();if(document.body.dataset.page==='article')article();
})();