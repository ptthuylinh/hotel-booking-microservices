#!/usr/bin/env python3
"""Smoke test deployed UI/API using a previously created, clearly labelled test booking.
Negative POST tests are opt-in and require its room to remain RESERVED.
"""
import argparse
import datetime
import json
import urllib.error
import urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--base-url',required=True)
parser.add_argument('--booking-code',required=True)
parser.add_argument('--negative-writes',action='store_true')
args=parser.parse_args()
base=args.base_url.rstrip('/')
checks=[]
def expect(path,status=200,body=None):
    method='POST' if body is not None else 'GET'
    request=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,
        headers={'Content-Type':'application/json','X-Correlation-Id':'cloud-smoke-verify-week4'},method=method)
    try:
        response=urllib.request.urlopen(request,timeout=30)
    except urllib.error.HTTPError as error:
        response=error
    text=response.read().decode()
    assert response.status==status,f'{method} {path}: expected {status}, got {response.status}'
    checks.append({'method':method,'path':path,'status':response.status})
    try:return json.loads(text)
    except json.JSONDecodeError:return text

assert 'Maison' in expect('/ui/index.html')
assert 'createCorrelationId' in expect('/ui/app.js')
assert '@media' in expect('/ui/styles.css')
assert '/ui/index.html' in expect('/')
rooms=expect('/api/rooms');assert isinstance(rooms,list)
booking=expect('/api/bookings/code/'+args.booking_code)
assert booking['bookingCode']==args.booking_code
assert expect('/api/bookings/'+booking['id'])['bookingCode']==args.booking_code
assert any(b['id']==booking['id'] for b in expect('/api/bookings'))
room=expect('/api/rooms/'+str(booking['roomId']));assert room['status']=='RESERVED'
assert any(r['id']==room['id'] for r in expect('/api/rooms?status=RESERVED'))
notifications=expect('/api/notifications')['notifications']
assert any(n['bookingId']==args.booking_code for n in notifications),'Notification not found in current task memory'
expect('/api/rooms/999999999',404)
expect('/api/bookings/not-found-ui-smoke',404)
if args.negative_writes:
    check_in=datetime.date.today()+datetime.timedelta(days=30)
    payload={'customerName':'UI Negative Test','customerEmail':'ui-negative@example.com','roomId':room['id'],
             'checkInDate':str(check_in),'checkOutDate':str(check_in+datetime.timedelta(days=2))}
    expect('/api/bookings',400,{**payload,'customerEmail':'invalid-email'})
    expect('/api/bookings',409,payload)
print(json.dumps({'result':'PASS','bookingCode':args.booking_code,'bookingId':booking['id'],
                  'roomId':room['id'],'roomStatus':room['status'],'notificationVerified':True,
                  'checksPassed':len(checks),'checks':checks},ensure_ascii=False,indent=2))
