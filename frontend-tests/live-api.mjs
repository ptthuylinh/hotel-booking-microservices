// Integration checks against disposable local containers only; never targets AWS.
import assert from 'node:assert/strict';
const base='http://127.0.0.1:58080';
let passed=0;
async function call(path,status=200,options={}){const response=await fetch(base+path,{...options,headers:{'Content-Type':'application/json','X-Correlation-Id':'ui-integration-local'}});assert.equal(response.status,status,path);assert.equal(response.headers.get('X-Correlation-Id'),'ui-integration-local');passed++;return response;}
const json=async(path,status=200,options={})=>(await call(path,status,options)).json();
for(const path of ['/ui/index.html','/ui/app.js','/ui/styles.css'])assert.ok((await call(path)).headers.get('content-type'));
const root=await call('/');assert.match(await root.text(),/ui\/index.html/);
for(const path of ['/ui','/ui/']){const response=await fetch(base+path,{redirect:'manual'});assert.equal(response.status,302);assert.equal(new URL(response.headers.get('location'),base).pathname,'/ui/index.html');passed++;}
const rooms=await json('/api/rooms');assert.equal(rooms.length,4);
const room=rooms.find(r=>r.status==='AVAILABLE');assert.ok(room);
assert.ok((await json('/api/rooms?status=AVAILABLE')).every(r=>r.status==='AVAILABLE'));
assert.equal((await json('/api/rooms/'+room.id)).id,room.id);
await json('/api/rooms/99999',404);
const update=async status=>json(`/api/rooms/${room.id}/status`,200,{method:'PUT',body:JSON.stringify({status,reason:'Disposable local integration test'})});
assert.equal((await update('MAINTENANCE')).status,'MAINTENANCE');await update('AVAILABLE');
const payload={customerName:'LOCAL UI Integration',customerEmail:'local-ui@example.com',customerPhone:'0900000000',roomId:room.id,checkInDate:'2099-11-01',checkOutDate:'2099-11-03'};
await json('/api/bookings',400,{method:'POST',body:JSON.stringify({...payload,customerEmail:'invalid'})});
await json('/api/bookings',400,{method:'POST',body:JSON.stringify({...payload,checkOutDate:'2099-10-01'})});
const created=await json('/api/bookings',201,{method:'POST',body:JSON.stringify(payload)});assert.equal(created.status,'CONFIRMED');assert.equal(Number(created.totalPrice),Number(room.pricePerNight)*2);
assert.equal((await json('/api/rooms/'+room.id)).status,'RESERVED');
assert.equal((await json('/api/bookings/'+created.id)).bookingCode,created.bookingCode);
assert.equal((await json('/api/bookings/code/'+created.bookingCode)).id,created.id);
assert.ok((await json('/api/bookings')).some(b=>b.id===created.id));
await json('/api/bookings/missing',404);await json('/api/bookings/code/missing',404);
await json('/api/bookings',409,{method:'POST',body:JSON.stringify(payload)});
const notifications=await json('/api/notifications');assert.ok(Array.isArray(notifications.notifications));
console.log(`${passed} local HTTP integration checks PASS (real Spring Boot + PostgreSQL; AWS publishing intentionally offline).`);
