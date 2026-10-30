const $ = (selector) => document.querySelector(selector);
const state = { rooms: [], bookings: [], notifications: [], requests: [], failures: {}, loaded: false, generation: 0 };
const titles = { overview: ['Tổng quan khách sạn', 'Mọi hoạt động của khách sạn, trong một không gian.'], rooms: ['Quản lý phòng', 'Theo dõi tình trạng phòng và sẵn sàng đón khách.'], 'new-booking': ['Đặt phòng mới', 'Một kỳ nghỉ trọn vẹn bắt đầu từ đây.'], bookings: ['Đơn đặt phòng', 'Tra cứu và theo dõi mọi lượt đặt phòng.'], notifications: ['Thông báo', 'Lịch sử xử lý thông báo từ notification-service.'] };
const statusNames = { AVAILABLE: 'Sẵn sàng', RESERVED: 'Đã đặt', MAINTENANCE: 'Bảo trì', OCCUPIED: 'Đang ở', CONFIRMED: 'Đã xác nhận', SENT: 'Đã xử lý' };
export const escapeHtml = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const e = escapeHtml;
const money = (v) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'USD' }).format(Number(v) || 0);
const date = (v) => v ? new Date(v).toLocaleString('vi-VN') : '—';
const badge = (s) => `<span class="badge ${e(/^[A-Z_]+$/.test(s || '') ? s : '')}">${e(statusNames[s] || s || 'Chưa rõ')}</span>`;
const page = () => Object.hasOwn(titles, location.hash.slice(1).split('?')[0]) ? location.hash.slice(1).split('?')[0] : 'overview';
const today = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
export function bookingPayload(values) {
  const p = { customerName: values.customerName.trim(), customerEmail: values.customerEmail.trim(), customerPhone: values.customerPhone.trim(), roomId: Number(values.roomId), checkInDate: values.checkInDate, checkOutDate: values.checkOutDate };
  if (!p.customerName || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.customerEmail)) throw new Error('Vui lòng nhập họ tên và email hợp lệ.');
  if (!Number.isSafeInteger(p.roomId) || p.roomId <= 0) throw new Error('Vui lòng chọn phòng.');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.checkInDate) || p.checkInDate < today()) throw new Error('Ngày nhận phòng không được ở trong quá khứ.');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.checkOutDate) || p.checkOutDate <= p.checkInDate) throw new Error('Ngày trả phòng phải sau ngày nhận phòng.');
  if (p.customerName.length > 100 || p.customerEmail.length > 150 || p.customerPhone.length > 20 || (values.customerId?.trim().length || 0) > 50) throw new Error('Thông tin khách hàng vượt quá độ dài cho phép.');
  if (values.customerId?.trim()) p.customerId = values.customerId.trim();
  return p;
}
function notify(message, error = false) { const el = $('#notice'); el.textContent = message; el.className = error ? 'error' : 'success'; el.hidden = false; }
function logRequests() {
  $('#request-count').textContent = `${state.requests.length} yêu cầu`;
  $('#requests').innerHTML = state.requests.map(r => `<div class="request-row">${e(r.method)} ${e(r.path)} · HTTP ${e(r.status)} · ${r.ms} ms<small>Correlation: ${e(r.correlation || 'Không có header trả về')} · ${e(r.time)}</small>${r.error ? `<small>${e(r.error)}</small>` : ''}</div>`).join('');
}
async function api(path, options = {}) {
  const started = performance.now(), correlation = crypto.randomUUID(); let status = 'NETWORK', returnedCorrelation = '', failure = '';
  try {
    const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', 'X-Correlation-Id': correlation, ...options.headers }, signal: AbortSignal.timeout(20000) });
    status = response.status; returnedCorrelation = response.headers.get('X-Correlation-Id') || correlation;
    const text = await response.text(); let data;
    try { data = text ? JSON.parse(text) : null; } catch { throw new Error(`HTTP ${status}: Phản hồi không phải JSON. Kiểm tra định tuyến ALB.`); }
    if (!response.ok) {
      const fields = data?.errors ? ` · ${JSON.stringify(data.errors)}` : '';
      throw new Error(`HTTP ${status}: ${data?.detail || data?.message || data?.title || data?.error || response.statusText}${fields}`);
    }
    return data;
  } catch (err) { failure = err.name === 'TimeoutError' ? 'Yêu cầu quá thời gian chờ. Kiểm tra dịch vụ và thử lại.' : err.message; throw new Error(failure); }
  finally { state.requests.unshift({ method: options.method || 'GET', path, status, correlation: returnedCorrelation || correlation, ms: Math.round(performance.now() - started), time: new Date().toLocaleTimeString('vi-VN'), error: failure }); state.requests = state.requests.slice(0, 30); logRequests(); }
}
async function loadData() {
  const generation = ++state.generation;
  const results = await Promise.allSettled([api('/api/rooms'), api('/api/bookings'), api('/api/notifications')]);
  if (generation !== state.generation) return;
  ['rooms', 'bookings', 'notifications'].forEach((key, i) => {
    const result = results[i]; delete state.failures[key];
    if (result.status === 'fulfilled') {
      const data = key === 'notifications' ? result.value?.notifications : result.value;
      if (Array.isArray(data)) state[key] = data;
      else { state[key] = []; state.failures[key] = 'Cấu trúc dữ liệu không hợp lệ.'; }
    } else { state[key] = []; state.failures[key] = result.reason.message; }
  });
  state.loaded = true;
}
function failure(key) { return state.failures[key] ? `<div class="error-state" role="alert">Không tải được ${e({ rooms: 'danh sách phòng', bookings: 'đơn đặt phòng', notifications: 'thông báo' }[key])}: ${e(state.failures[key])}. Bấm “Làm mới dữ liệu” để thử lại.</div>` : ''; }
function empty(text) { return `<div class="empty">${e(text)}</div>`; }
function bookingRows(rows) {
  if (!rows.length) return empty('Chưa có đơn đặt phòng phù hợp.');
  return `<div class="table-wrap"><table><thead><tr><th>MÃ ĐẶT PHÒNG</th><th>KHÁCH HÀNG</th><th>PHÒNG</th><th>NHẬN / TRẢ PHÒNG</th><th>TỔNG TIỀN</th><th>TRẠNG THÁI</th><th></th></tr></thead><tbody>${rows.map(b => `<tr><td><strong>${e(b.bookingCode)}</strong></td><td>${e(b.customerName)}<small>${e(b.customerEmail)}</small></td><td>${e(state.rooms.find(r => r.id === b.roomId)?.roomNumber || b.roomId)}</td><td>${e(b.checkInDate)}<small>${e(b.checkOutDate)}</small></td><td>${money(b.totalPrice)}</td><td>${badge(b.status)}</td><td><button class="text-button" data-booking-id="${e(b.id)}">Chi tiết ↗</button></td></tr>`).join('')}</tbody></table></div>`;
}
function overview() {
  const available = state.rooms.filter(r => r.status === 'AVAILABLE').length;
  const stat = (label, value, desc, symbol) => `<div class="stat"><div class="stat-label">${label}<span class="stat-symbol">${symbol}</span></div><strong>${value}</strong><small>${desc}</small></div>`;
  return `<section class="hero"><div><p class="eyebrow">CHÀO MỪNG ĐẾN MAISON</p><h2>Sẵn sàng cho những<br>kỳ nghỉ đáng nhớ.</h2><p>Kiểm tra phòng trống, đón tiếp khách hàng và quản lý đặt phòng dễ dàng mỗi ngày.</p><a class="button" href="#new-booking">＋ Tạo đơn đặt phòng</a></div><div class="hero-art" aria-hidden="true"><div class="building"><span></span><span></span><span></span><span></span></div><div class="building tall"><span></span><span></span><span></span><span></span></div></div></section><div class="stats">${stat('Tổng số phòng', state.failures.rooms ? '—' : state.rooms.length, 'Danh mục phòng khách sạn', '▦')}${stat('Phòng sẵn sàng', state.failures.rooms ? '—' : available, 'Có thể đặt ngay', '◉')}${stat('Đơn đặt phòng', state.failures.bookings ? '—' : state.bookings.length, 'Tổng số đơn đã ghi nhận', '▤')}${stat('Thông báo đã xử lý', state.failures.notifications ? '—' : state.notifications.length, 'Trong bộ nhớ task hiện tại', '♧')}</div><section class="panel"><div class="panel-title"><div><h2>Đơn đặt phòng gần đây</h2><p>Những vị khách tiếp theo của Maison</p></div><a class="text-button" href="#bookings">Xem tất cả ↗</a></div>${failure('bookings') || bookingRows([...state.bookings].sort((a,b) => String(b.createdAt).localeCompare(String(a.createdAt))).slice(0,5))}</section><section class="panel"><div class="panel-title"><h2>Kết nối dịch vụ</h2><small class="muted">Kết quả lần tải gần nhất</small></div><div class="service-status">${['rooms','bookings','notifications'].map((key,i) => `<span class="service-chip ${state.failures[key] ? 'fail' : 'ok'}">${state.failures[key] ? '○' : '●'} ${['Room service','Booking service','Notification service'][i]} · ${state.failures[key] ? 'Không kết nối' : 'Đã kết nối'}</span>`).join('')}</div></section>`;
}
function rooms() {
 return `${failure('rooms')}<div class="toolbar"><label>Tìm phòng<input id="room-search" type="search" placeholder="Số phòng hoặc loại phòng"></label><label>Trạng thái<select id="room-status"><option value="">Tất cả trạng thái</option><option value="AVAILABLE">Sẵn sàng</option><option value="RESERVED">Đã đặt</option><option value="OCCUPIED">Đang ở</option><option value="MAINTENANCE">Bảo trì</option></select></label><button id="filter-rooms" class="secondary">Áp dụng bộ lọc</button></div><div id="room-list" class="room-grid"></div>`;
}
function renderRoomCards(rows) {
 $('#room-list').innerHTML = rows.length ? rows.map(r => `<article class="room-card"><div class="room-visual" aria-hidden="true"></div><div class="room-body"><div class="room-top"><h3>Phòng ${e(r.roomNumber)}</h3>${badge(r.status)}</div><p>${e(r.type)} · ${e(r.description || 'Không gian nghỉ ngơi tại Maison')}</p><div class="room-bottom"><div><strong>${money(r.pricePerNight)}</strong><small> / đêm</small></div><button class="text-button" data-room-id="${e(r.id)}">Chi tiết ↗</button></div>${r.status === 'AVAILABLE' ? `<a class="button" style="width:100%;margin-top:15px" href="#new-booking?room=${e(r.id)}">Đặt phòng này</a>` : ''}</div></article>`).join('') : empty('Không có phòng phù hợp.');
}
function bookingForm() {
 return `<div class="form-layout"><section class="panel">${failure('rooms')}<form id="booking-form"><div class="form-grid"><h2 class="form-section full">01 · Thông tin khách hàng</h2><label>Họ và tên *<input name="customerName" autocomplete="name" maxlength="100" required placeholder="Nguyễn Hoàng An"></label><label>Email *<input name="customerEmail" type="email" autocomplete="email" maxlength="150" required placeholder="khach@example.com"></label><label>Số điện thoại<input name="customerPhone" type="tel" autocomplete="tel" maxlength="20" placeholder="090 123 4567"></label><label>Mã khách hàng (tùy chọn)<input name="customerId" maxlength="50" placeholder="Tự tạo nếu bỏ trống"></label><h2 class="form-section full">02 · Thông tin kỳ nghỉ</h2><label class="full">Chọn phòng *<select name="roomId" id="booking-room" required><option value="">Chọn phòng sẵn sàng</option>${state.rooms.filter(r => r.status === 'AVAILABLE').map(r => `<option value="${e(r.id)}">Phòng ${e(r.roomNumber)} · ${e(r.type)} · ${money(r.pricePerNight)}/đêm</option>`).join('')}</select></label><label>Ngày nhận phòng *<input name="checkInDate" type="date" min="${today()}" required></label><label>Ngày trả phòng *<input name="checkOutDate" type="date" min="${today()}" required></label></div><div class="form-actions"><button type="submit" ${state.failures.rooms ? 'disabled' : ''}>Xác nhận đặt phòng →</button><a class="text-button" href="#rooms">Xem danh sách phòng</a></div><p class="muted">Giá chính thức do máy chủ tính theo giá phòng và số đêm.</p></form></section><aside class="estimate"><p class="eyebrow">THÔNG TIN ĐẶT PHÒNG</p><h2>Kỳ nghỉ của bạn</h2><div id="estimate-content"><p class="muted">Chọn phòng và ngày lưu trú để xem giá dự kiến.</p></div><hr><p class="muted">Sau khi đặt thành công, phòng được giữ chỗ và hệ thống tiếp nhận sự kiện thông báo. Bạn có thể theo dõi ở mục Thông báo.</p></aside></div>`;
}
function bookings() { return `<section class="panel"><div class="panel-title"><div><h2>Tất cả đơn đặt phòng</h2><p>Tra cứu chính xác bằng mã booking hoặc ID</p></div><a class="button" href="#new-booking">＋ Đặt phòng mới</a></div><form id="lookup-form" class="toolbar"><label>Tra cứu đơn<input id="booking-query" required placeholder="BK-123456 hoặc UUID"></label><label>Tìm theo<select id="lookup-type"><option value="code">Mã đặt phòng</option><option value="id">ID đơn đặt phòng</option></select></label><button type="submit">Tra cứu</button><button id="show-all" type="button" class="secondary">Hiện tất cả</button></form>${failure('bookings')}<div id="booking-list">${bookingRows(state.bookings)}</div></section>`; }
function notifications() {
 return `<section class="panel"><div class="panel-title"><div><h2>Lịch sử thông báo</h2><p>Dữ liệu trong bộ nhớ của notification-service; có thể khác giữa các task và mất khi task khởi động lại.</p></div><button id="refresh-notifications" class="secondary">↻ Tải thông báo</button></div>${failure('notifications')}${state.notifications.length ? `<div class="table-wrap"><table><thead><tr><th>KHÁCH HÀNG</th><th>BOOKING</th><th>PHÒNG</th><th>KÊNH</th><th>TRẠNG THÁI</th><th>THỜI GIAN</th><th></th></tr></thead><tbody>${state.notifications.map((n,i) => `<tr><td>${e(n.customerName)}<small>${e(n.customerEmail)}</small></td><td>${e(n.bookingId)}</td><td>${e(n.roomNumber)}</td><td>${e(n.channel)}</td><td>${badge(n.status)}</td><td>${e(date(n.sentAt))}</td><td><button class="text-button" data-notification="${i}">Chi tiết ↗</button></td></tr>`).join('')}</tbody></table></div>` : empty('Chưa có thông báo trong task hiện tại. Sau khi đặt phòng, bấm tải lại để kiểm tra.')}</section>`;
}
function showDetail(title, data, extra = '') { $('#detail-title').textContent = title; $('#detail-content').innerHTML = `<dl class="details-list">${Object.entries(data).filter(([,v]) => v !== null && typeof v !== 'object').map(([k,v]) => `<dt>${e(k)}</dt><dd>${e(v)}</dd>`).join('')}</dl>${extra}<details><summary class="muted">Dữ liệu JSON</summary><pre>${e(JSON.stringify(data,null,2))}</pre></details>`; if (!$('#detail-dialog').open) $('#detail-dialog').showModal(); }
async function showBooking(id) { try { showDetail('Chi tiết đơn đặt phòng', await api(`/api/bookings/${encodeURIComponent(id)}`)); } catch(err) { notify(err.message,true); } }
async function showRoom(id) {
 try {
  const room = await api(`/api/rooms/${encodeURIComponent(id)}`);
  showDetail(`Phòng ${room.roomNumber}`,room,`<form id="room-status-form"><h3>Cập nhật trạng thái phòng</h3><p class="muted">Thao tác này chỉ đổi trạng thái phòng, không hủy hay sửa đơn đặt phòng.</p><label>Trạng thái mới<select name="status">${['AVAILABLE','RESERVED','OCCUPIED','MAINTENANCE'].map(s => `<option value="${s}" ${s === room.status ? 'selected' : ''}>${statusNames[s]}</option>`).join('')}</select></label><label>Mã tham chiếu booking<input name="bookingId" placeholder="Tùy chọn"></label><label>Lý do thay đổi<textarea name="reason" required maxlength="500" placeholder="Nhập lý do cập nhật"></textarea></label><button style="margin:16px 0" type="submit">Lưu trạng thái</button></form>`);
  $('#room-status-form').onsubmit = async event => { event.preventDefault(); const form = event.currentTarget, button = form.querySelector('button'); button.disabled = true;
   try { const values = Object.fromEntries(new FormData(form)); await api(`/api/rooms/${encodeURIComponent(id)}/status`, {method:'PUT',body:JSON.stringify(values)}); $('#detail-dialog').close(); notify('Đã cập nhật trạng thái phòng.'); await refresh(); } catch(err) { let error = $('#room-save-error'); if (!error) { error = document.createElement('p'); error.id='room-save-error'; error.setAttribute('role','alert'); form.append(error); } error.textContent=err.message; } finally {button.disabled=false;} };
 } catch(err) { notify(err.message,true); }
}
function estimate() {
 const form = $('#booking-form'), values = Object.fromEntries(new FormData(form)); const room = state.rooms.find(r => r.id === Number(values.roomId));
 const nights = Math.round((new Date(values.checkOutDate) - new Date(values.checkInDate))/86400000);
 $('#estimate-content').innerHTML = room ? `<dl><dt>Phòng</dt><dd>${e(room.roomNumber)} · ${e(room.type)}</dd><dt>Giá mỗi đêm</dt><dd>${money(room.pricePerNight)}</dd><dt>Số đêm</dt><dd>${nights > 0 ? nights : '—'}</dd></dl><div class="total">${nights > 0 ? money(nights * Number(room.pricePerNight)) : '—'}</div><small class="muted">Tổng tiền dự kiến · USD</small>` : '<p class="muted">Chọn phòng và ngày lưu trú để xem giá dự kiến.</p>';
 if (values.checkInDate) form.elements.checkOutDate.min = values.checkInDate;
}
function bind() {
 $('#content').onclick = event => { const b=event.target.closest('[data-booking-id]'), r=event.target.closest('[data-room-id]'), n=event.target.closest('[data-notification]'); if(b) showBooking(b.dataset.bookingId); if(r) showRoom(r.dataset.roomId); if(n) showDetail('Chi tiết thông báo',state.notifications[Number(n.dataset.notification)]); };
 if(page() === 'rooms') {
  renderRoomCards(state.rooms);
  $('#room-search').oninput = () => { const term = $('#room-search').value.toLowerCase(); renderRoomCards(state.rooms.filter(r => (!$('#room-status').value || r.status === $('#room-status').value) && `${r.roomNumber} ${r.type}`.toLowerCase().includes(term))); };
  $('#filter-rooms').onclick = async () => { const button = $('#filter-rooms'); button.disabled=true; try { const rows=await api('/api/rooms'+($('#room-status').value ? `?status=${encodeURIComponent($('#room-status').value)}` : '')); if(!Array.isArray(rows)) throw new Error('Cấu trúc dữ liệu phòng không hợp lệ.'); const term=$('#room-search').value.toLowerCase(); renderRoomCards(rows.filter(r => `${r.roomNumber} ${r.type}`.toLowerCase().includes(term))); } catch(err){notify(err.message,true);} finally{button.disabled=false;} };
 }
 if(page() === 'new-booking') {
  const form=$('#booking-form'); const selected=new URLSearchParams(location.hash.split('?')[1]).get('room'); if(selected) form.elements.roomId.value=selected;
  form.oninput=estimate; form.onchange=estimate; estimate();
  form.onsubmit=async event => {event.preventDefault(); const button=form.querySelector('[type=submit]'); button.disabled=true; let created;
   try { const payload=bookingPayload(Object.fromEntries(new FormData(form))); created=await api('/api/bookings',{method:'POST',body:JSON.stringify(payload)}); }
   catch(err){notify(err.message,true);button.disabled=false;return;}
   form.reset(); notify(`Đặt phòng thành công! Mã đơn: ${created.bookingCode}.`); await loadData(); location.hash='bookings'; render(); showDetail('Đặt phòng thành công',created);
  };
 }
 if(page() === 'bookings') {
  $('#show-all').onclick=()=>{$('#booking-query').value='';$('#booking-list').innerHTML=bookingRows(state.bookings);};
  $('#lookup-form').onsubmit=async event => {event.preventDefault(); const button=event.currentTarget.querySelector('[type=submit]');button.disabled=true;try { const query=$('#booking-query').value.trim();if(!query)throw new Error('Nhập mã hoặc ID đơn đặt phòng.'); const b=await api(`/api/bookings/${$('#lookup-type').value === 'code' ? 'code/' : ''}${encodeURIComponent(query)}`);$('#booking-list').innerHTML=bookingRows([b]);showDetail('Kết quả tra cứu',b);}catch(err){$('#booking-list').innerHTML=empty(err.message);notify(err.message,true);}finally{button.disabled=false;} };
 }
 if(page() === 'notifications') $('#refresh-notifications').onclick=refresh;
}
function render() {
 // Accept an optional room query without treating it as a separate route.
 const route = location.hash.slice(1).split('?')[0];
 const active = Object.hasOwn(titles,route) ? route : 'overview';
 const [title,subtitle]=titles[active]; $('#page-title').textContent=title;$('#page-subtitle').textContent=subtitle;$('#breadcrumb').textContent=title;
 document.querySelectorAll('nav a').forEach(a=>{a.classList.toggle('active',a.dataset.page===active);if(a.dataset.page===active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 $('#content').innerHTML=({overview,rooms,'new-booking':bookingForm,bookings,notifications}[active])(); bind();
}
async function refresh() { $('#refresh').disabled=true;$('#content').setAttribute('aria-busy','true');try{await loadData();render();}finally{$('#refresh').disabled=false;$('#content').setAttribute('aria-busy','false');} }
if (typeof document !== 'undefined') {
 $('#today').textContent=new Date().toLocaleDateString('vi-VN',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
 $('#close-dialog').onclick=()=>$('#detail-dialog').close(); $('#refresh').onclick=refresh;
 window.addEventListener('hashchange',()=>{if(state.loaded)render();});
 $('#content').innerHTML='<div class="loading">Đang kết nối với khách sạn…</div>';refresh();
}
