#!/usr/bin/env python3
"""Render editable diagrams.net pages and standalone SVG/PNG video slides.
Icons: official AWS Architecture Icons, July 2026. PNG export requires cairosvg.
"""
from pathlib import Path
from html import escape
import base64
import xml.etree.ElementTree as ET
import argparse
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/week-4/phuc/architecture'
ASSETS = OUT / 'assets'
GREEN='#194d42'; INK='#203a39'; MUTED='#637b7b'; BLUE='#36769a'; ORANGE='#bc7436'; PURPLE='#8667ac'

class Slide:
    def __init__(self,name,slug):
        self.name,self.slug=name,slug;self.svg=[]
        self.model=ET.Element('mxGraphModel',dx='1920',dy='1080',grid='1',gridSize='10',page='1',pageScale='1',pageWidth='1920',pageHeight='1080',background='#f7faf8')
        self.root=ET.SubElement(self.model,'root');ET.SubElement(self.root,'mxCell',id='0');ET.SubElement(self.root,'mxCell',id='1',parent='0');self.count=1
        self.box(0,0,1920,1080,'#f7faf8','none',0)
    def cell(self,value,style,x,y,w,h):
        self.count+=1
        c=ET.SubElement(self.root,'mxCell',id=str(self.count),value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        return str(self.count)
    def box(self,x,y,w,h,fill='#fff',stroke='#d5e2dc',radius=12,dashed=False):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"'+(' stroke-dasharray="8 6"' if dashed else '')+'/>')
        return self.cell('',f'rounded={int(bool(radius))};arcSize=8;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};dashed={int(dashed)};',x,y,w,h)
    def text(self,x,y,text,size=20,color=INK,weight=400,anchor='start',width=700):
        lines=text.split('\n');self.svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="DejaVu Sans,Arial,sans-serif">'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else size*1.4}">{escape(line)}</tspan>' for i,line in enumerate(lines))+'</text>')
        left=x-width/2 if anchor=='middle' else x
        self.cell('<br>'.join(escape(v) for v in lines),f'text;html=1;whiteSpace=wrap;align={"center" if anchor=="middle" else "left"};verticalAlign=top;fontFamily=DejaVu Sans;fontSize={size};fontStyle={int(weight>=600)};fontColor={color};strokeColor=none;fillColor=none;spacing=0;',left,y-size,width,len(lines)*size*1.4+5)
    def icon(self,name,x,y,size=42):
        data=(ASSETS/(name+'.svg')).read_bytes();url='data:image/svg+xml;base64,'+base64.b64encode(data).decode()
        self.svg.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{url}"/>')
        drawio_url = 'data:image/svg+xml,' + quote(data.decode(), safe='')
        self.cell('',f'shape=image;imageAspect=0;aspect=fixed;image={drawio_url};',x,y,size,size)
    def arrow(self,points,color=GREEN,dashed=False):
        d='M '+' L '.join(f'{x},{y}' for x,y in points)
        self.svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2" marker-end="url(#{color[1:]})"'+(' stroke-dasharray="7 5"' if dashed else '')+'/>')
        self.count+=1;c=ET.SubElement(self.root,'mxCell',id=str(self.count),value='',style=f'edgeStyle=none;rounded=0;html=1;endArrow=block;strokeWidth=2;strokeColor={color};dashed={int(dashed)};',edge='1',parent='1')
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        for label,(x,y) in zip(['sourcePoint','targetPoint'],[points[0],points[-1]]):ET.SubElement(g,'mxPoint',x=str(x),y=str(y),attrib={'as':label})
        if len(points)>2:
            a=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in points[1:-1]:ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
    def card(self,x,y,w,h,title,lines,icon=None,fill='#fff',accent=GREEN,title_size=22,body_size=18):
        self.box(x,y,w,h,fill); offset=70 if icon else 20
        if icon:self.icon(icon,x+18,y+18,38)
        self.text(x+offset,y+38,title,title_size,accent,600,width=w-offset-10)
        self.text(x+20,y+76,'\n'.join(lines),body_size,MUTED,width=w-35)
    def heading(self,kicker,title,subtitle):
        self.text(45,38,kicker,14,GREEN,700)
        self.text(45,81,title,34,INK,700)
        self.text(45,114,subtitle,18,MUTED)
    def footer(self,number):
        self.text(45,1053,'HOTEL BOOKING MICROSERVICES · TUẦN 4 · 30/10/2026',14,MUTED)
        self.text(1335,1053,'AWS account 055652951832 · us-east-1',14,MUTED,width=500)
        self.text(1860,1053,f'{number:02}',18,GREEN,700,width=50)
    def save(self):
        colors=[GREEN,BLUE,ORANGE,PURPLE,MUTED]
        defs='<defs>'+''.join(f'<marker id="{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>' for c in colors)+'</defs>'
        path=OUT/(self.slug+'.svg');path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" role="img"><title>'+escape(self.name)+'</title>'+defs+''.join(self.svg)+'</svg>')
        try:
            import cairosvg
            cairosvg.svg2png(url=str(path),write_to=str(OUT/(self.slug+'.png')),output_width=3840,output_height=2160)
        except ImportError: print('cairosvg unavailable; SVG and drawio preserved.')


def architecture(discovery):
    s=Slide('01 · Kiến trúc AWS tuần 4','01-aws-architecture-week4')
    s.heading('KIẾN TRÚC TRIỂN KHAI','Từ giao diện đến hạ tầng AWS','UI phục vụ trong room-service · 3 microservices trên ECS Fargate · 2 Availability Zones')
    s.box(300,145,1575,855,'#fff','#b9c9cb',16)
    s.text(323,175,'AWS REGION · us-east-1',17,BLUE,700)
    s.box(325,195,1080,575,'#fbfdfb','#78a98d',10)
    s.text(345,222,'VPC 10.0.0.0/16 · vpc-025a0fd949a26f610',18,GREEN,700)
    s.box(345,240,500,125,'#f0f6e8','#bed2aa',8);s.box(865,240,520,125,'#f0f6e8','#bed2aa',8)
    s.text(360,265,'PUBLIC · us-east-1a · 10.0.0.0/20',15,GREEN,600)
    s.text(885,265,'PUBLIC · us-east-1b · 10.0.16.0/20',15,GREEN,600)
    s.icon('NAT-Gateway',365,292,38);s.text(415,310,'NAT Gateway',19,GREEN,600);s.text(415,336,'Private egress → IGW',15,MUTED,width=250)
    s.box(705,281,510,69,'#fff','#a9c3b6',8);s.icon('Elastic-Load-Balancing',721,294,39)
    s.text(775,310,'Application Load Balancer',21,GREEN,600,width=420);s.text(775,336,'HTTP :80 · health /actuator/health',16,MUTED,width=430)
    s.card(45,270,225,140,'Khách / Lễ tân',['Maison UI','Postman / curl'],'Users',title_size=18)
    s.arrow([(270,310),(315,310),(315,278),(960,278),(960,281)]);s.icon('Internet-Gateway',300,264,32)
    s.box(345,385,500,365,'#edf5fa','#adcadb',8);s.box(865,385,520,365,'#edf5fa','#adcadb',8)
    s.text(360,412,'PRIVATE · us-east-1a · 10.0.128.0/20',15,BLUE,600)
    s.text(885,412,'PRIVATE · us-east-1b · 10.0.144.0/20',15,BLUE,600)
    s.box(365,430,1000,155,'#fbfcfd','#a4bfd0',8,True)
    s.text(385,455,'ECS FARGATE · hotel-cluster · vị trí task do scheduler chọn trong 2 AZ',16,BLUE,600,width=970)
    s.card(385,473,280,96,'room-service',['UI + /api/rooms*'],'AWS-Fargate',title_size=19,body_size=16)
    s.card(725,473,280,96,'booking-service',['/api/bookings*'],'AWS-Fargate',title_size=19,body_size=16)
    s.card(1060,473,285,96,'notification-service',['/api/notifications*'],'AWS-Fargate',title_size=17,body_size=16)
    s.arrow([(960,350),(960,373),(525,373),(525,473)]);s.arrow([(960,373),(865,373),(865,473)]);s.arrow([(960,373),(1200,373),(1200,473)])
    s.text(45,455,'ALB path routing',17,GREEN,600,width=220)
    s.text(45,486,'/ → UI\n/ui/* → room\n/api/rooms* → room\n/api/bookings* → booking\n/api/notifications* → notify',15,MUTED,width=250)
    if discovery == 'alb':
        s.arrow([(740,473),(690,473),(690,320),(705,320)],BLUE,True)
        s.text(45,646,'REST: booking → ALB → room',13,BLUE,width=260)
    else:
        s.arrow([(725,530),(665,530)],BLUE);s.text(671,512,'REST',13,BLUE,width=60)
    if discovery=='cloudmap':
        s.card(365,625,375,105,'Private service discovery',['room-service.hotel.internal:8080','ECS cập nhật DNS theo task'],'AWS-Cloud-Map',title_size=18,body_size=15)
    elif discovery=='alb':
        s.card(365,625,375,105,'REST ổn định qua ALB',['Booking → ALB → room target group','Không phụ thuộc IP task / Cloud Map'],'Elastic-Load-Balancing',title_size=18,body_size=15)
    else:
        s.card(365,625,375,105,'Route 53 private DNS',['room-service.hotel.local:8080','Bản ghi A cần theo IP task'],'Amazon-Route-53',title_size=18,body_size=15)
    s.card(1000,625,365,105,'RDS PostgreSQL',['room_db · booking_db','Single-AZ: us-east-1b · private'],'Amazon-RDS',title_size=20,body_size=16)
    s.arrow([(525,569),(525,603),(1115,603),(1115,625)],BLUE)
    s.arrow([(865,569),(865,592),(1245,592),(1245,625)],BLUE)
    s.text(760,677,'JDBC :5432',16,BLUE,width=230)
    s.text(760,705,'Tách DB / user',15,MUTED,width=230)
    s.text(1440,222,'DỊCH VỤ AWS CẤP REGION',16,PURPLE,700,width=400)
    s.card(1450,245,400,103,'Amazon SNS',['hotel-booking-events'],'Amazon-Simple-Notification-Service',title_size=20,body_size=16)
    s.card(1450,385,400,103,'Amazon SQS',['booking-notification-queue'],'Amazon-Simple-Queue-Service',title_size=20,body_size=16)
    s.card(1450,525,400,103,'Dead Letter Queue',['booking-notification-dlq'],'Amazon-Simple-Queue-Service',title_size=20,body_size=16)
    s.card(1450,665,400,103,'DynamoDB · audit',['hotel-booking-audit-logs'],'Amazon-DynamoDB',title_size=20,body_size=16)
    s.arrow([(1005,494),(1030,494),(1030,465),(1420,465),(1420,296),(1450,296)],ORANGE)
    s.arrow([(1650,348),(1650,385)],ORANGE);s.text(1670,372,'subscription',14,ORANGE,width=175)
    s.arrow([(1345,548),(1434,548),(1434,435),(1450,435)],ORANGE);s.text(45,615,'Cam: publish / poll SQS',14,ORANGE,width=250)
    s.arrow([(1650,488),(1650,525)],ORANGE);s.text(1670,511,'maxReceiveCount = 3',13,ORANGE,width=190)
    s.arrow([(950,569),(950,612),(1417,612),(1417,715),(1450,715)],PURPLE)
    s.text(1150,610,'Audit (best effort)',14,PURPLE,width=240)
    s.card(325,800,325,170,'CloudShell → ECR',['3 image repositories','Tag theo Git commit','ECS tải image khi deploy'],'Amazon-Elastic-Container-Registry',title_size=19,body_size=17)
    s.card(675,800,325,170,'SSM Parameter Store',['/hotel/database/*','6 tham số SecureString','Inject qua task secrets'],'AWS-Systems-Manager',title_size=17,body_size=17)
    s.card(1025,800,450,170,'Amazon CloudWatch',['Logs 3 ngày · X-Correlation-Id','Dashboard CPU / RAM / ALB / SQS','4 alarms + target-tracking alarms'],'Amazon-CloudWatch',title_size=21,body_size=17)
    s.card(1500,800,350,170,'IAM + Security Groups',['LabRole: task / execution','Internet → ALB:80 → ECS:8080','ECS → RDS:5432'],'AWS-Identity-and-Access-Management',title_size=17,body_size=16)
    s.text(45,685,'KHẢ NĂNG PHỤC HỒI',15,GREEN,700,width=240)
    s.text(45,717,'ECS thay task lỗi\nALB health check\nScale room / booking: 0–3\nMột NAT, một RDS instance',14,MUTED,width=250)
    s.footer(1);return s


def table(s,x,y,w,title,subtitle,fields,color):
    height=107+len(fields)*35
    s.box(x,y,w,height,'#fff','#ccd9d5',10)
    s.box(x,y,w,90,color,color,8)
    s.text(x+20,y+34,title,25,'#fff',700,width=w-40);s.text(x+20,y+66,subtitle,17,'#e5eeeb',width=w-40)
    for i,(field,kind) in enumerate(fields):
        yy=y+120+i*35
        s.text(x+20,yy,field,17,INK,600 if 'PK' in field or 'UK' in field else 400,width=w-170)
        s.text(x+w-165,yy,kind,15,MUTED,width=160)
    return height


def erd():
    s=Slide('02 · ERD triển khai tuần 4','02-erd-week4')
    s.heading('MÔ HÌNH DỮ LIỆU TRIỂN KHAI','ERD tuần 4: đúng với entity và dữ liệu ứng dụng','2 logical databases trên cùng RDS PostgreSQL · quan hệ xuyên service là tham chiếu logic, không có FK liên database')
    table(s,45,215,500,'rooms','room_db · owner: room-service',[
        ('PK  id','BIGINT / identity'),('UK  room_number','VARCHAR(20) NN'),('type','VARCHAR(50) NN'),('price_per_night','NUMERIC(10,2) NN'),('status','VARCHAR(30) NN'),('description','TEXT NULL'),('created_at','TIMESTAMP NN'),('updated_at','TIMESTAMP NN')],GREEN)
    table(s,680,175,545,'bookings','booking_db · owner: booking-service',[
        ('PK  id','VARCHAR(36) NN'),('UK  booking_code','VARCHAR(30) NN'),('customer_id','VARCHAR(50) NN'),('customer_name','VARCHAR(100) NN'),('customer_email','VARCHAR(150) NN'),('customer_phone','VARCHAR(20) NULL'),('room_id  [logical ref]','BIGINT NN'),('check_in_date','DATE NN'),('check_out_date','DATE NN'),('total_price','NUMERIC(12,2) NN'),('status','VARCHAR(30) NN'),('created_at','TIMESTAMP NN'),('updated_at','TIMESTAMP NN')],BLUE)
    s.arrow([(545,370),(600,370),(600,505),(680,505)],BLUE,True)
    s.text(560,337,'1 → 0..N',17,BLUE,600,width=130)
    s.text(558,556,'rooms.id\n↔ room_id\nTham chiếu\nqua REST',13,MUTED,width=130)
    s.card(1350,175,525,472,'hotel-booking-audit-logs',[
        'DynamoDB · owner: booking-service','',
        'PK: bookingId   (String)','SK: timestamp   (String / ISO instant)',
        'auditId · action · actor','previousStatus · newStatus','details (Map): roomId, totalPrice,', 'customerEmail','',
        'bookingId lưu booking_code (BK-…),','không phải UUID bookings.id.'
    ],'Amazon-DynamoDB',title_size=19,body_size=19)
    s.arrow([(1225,320),(1280,320),(1280,350),(1350,350)],PURPLE,True)
    s.text(1240,287,'1 → 0..N',17,PURPLE,600,width=130)
    s.text(1239,388,'booking_code\n→ bookingId',14,PURPLE,width=120)
    s.card(1350,680,525,290,'NotificationRecord · RAM',[
        'notification-service không có database.',
        'History: CopyOnWriteArrayList',
        'Dedup: Set<eventId> trong bộ nhớ task',
        'notificationId, eventId, bookingId,',
        'customerName/email, roomNumber,',
        'totalPrice, channel, status, sentAt',
        'Dữ liệu mất khi restart; không chia sẻ task.'
    ],'AWS-Fargate',title_size=22,body_size=18)
    s.card(45,675,500,295,'Đọc đúng mô hình tuần 4',[
        'NN = NOT NULL · UK = UNIQUE',
        'Không có bảng customers, room_types,',
        'payments hay notifications trong JPA.',
        'type được lưu trực tiếp trong rooms.',
        'Thông tin khách là snapshot trong booking.',
        'Không có FK / join xuyên room_db ↔ booking_db.'
    ],None,title_size=22,body_size=19)
    s.card(680,800,545,170,'Trạng thái và phạm vi hiện có',[
        'Room: AVAILABLE → RESERVED; UI hỗ trợ đổi trạng thái.',
        'Booking được tạo CONFIRMED; chưa có API hủy.',
        'Không có kiểm tra lịch trống theo khoảng ngày.'
    ],None,title_size=22,body_size=18)
    s.text(680,765,'Khóa / kiểu / độ dài đối chiếu entity JPA; khóa audit đối chiếu AWS.',16,MUTED,width=700)
    s.footer(2);return s


def strategy():
    s=Slide('03 · Chiến lược database tuần 4','03-db-strategy-week4')
    s.heading('QUYỀN SỞ HỮU DỮ LIỆU & TÍNH NHẤT QUÁN','Database strategy: tách service, chia sẻ hạ tầng','Một RDS instance cho Learner Lab · mỗi service sở hữu dữ liệu của mình · không có distributed ACID transaction')
    cards=[(45,'room-service',['room_db · rooms','room_user','Chỉ sở hữu dữ liệu phòng'],'Amazon-RDS',GREEN),
           (510,'booking-service',['booking_db · bookings','booking_user','Lưu đơn và snapshot khách'],'Amazon-RDS',BLUE),
           (975,'booking-service / audit',['DynamoDB audit trail','bookingId + timestamp','Ghi best effort qua AWS SDK'],'Amazon-DynamoDB',PURPLE),
           (1440,'notification-service',['SQS consumer + RAM history','Không có PostgreSQL riêng','Idempotency chỉ trong từng task'],'AWS-Fargate',ORANGE)]
    for x,title,lines,icon,color in cards:s.card(x,175,435,185,title,lines,icon,title_size=21,body_size=19,accent=color)
    s.text(45,411,'LUỒNG TẠO BOOKING',18,GREEN,700)
    steps=[(45,'1 · Nhận request',['Validate khách / ngày','GET room qua REST']),
           (420,'2 · Khóa phòng',['PUT status=RESERVED','room_db commit riêng']),
           (795,'3 · Lưu booking',['@Transactional local','booking_db → CONFIRMED']),
           (1170,'4 · Side effects',['DynamoDB audit + SNS','Gọi trước DB commit']),
           (1545,'5 · Consumer',['SNS → SQS → notify','Xử lý + xóa message'])]
    for x,title,lines in steps:s.card(x,445,330,137,title,lines,None,title_size=22,body_size=18)
    for x in [375,750,1125,1500]:s.arrow([(x,513),(x+45,513)],ORANGE if x>=1125 else GREEN)
    s.arrow([(960,582),(960,605),(585,605),(585,582)],BLUE,True)
    s.text(45,655,'Lỗi trong khối try sau khi khóa → gọi releaseRoom để đưa phòng về AVAILABLE (bồi hoàn best effort).',19,BLUE,width=1800)
    s.card(45,690,570,280,'Bảo mật & vận hành',[
        'RDS private; SG chỉ nhận :5432 từ ECS SG.',
        'URL / username / password trong SSM SecureString.',
        'ECS inject secrets; không đưa secret xuống UI.',
        'Hibernate ddl-auto=update; chưa có migration tool.',
        'RDS Single-AZ; chưa triển khai replica / failover.'
    ],'AWS-Systems-Manager',title_size=23,body_size=19)
    s.card(675,690,570,280,'Tính nhất quán hiện tại',[
        'Không có transaction chung giữa 2 DB / AWS.',
        'Audit và SNS bắt lỗi rồi tiếp tục luồng chính.',
        'Commit DB lỗi sau publish có thể lệch trạng thái.',
        'Bồi hoàn không bảo đảm nếu REST release thất bại.',
        'Chưa có transactional outbox / durable dedup.'
    ],'Amazon-DynamoDB',title_size=23,body_size=19)
    s.card(1305,690,570,280,'Minh chứng cho video demo',[
        '201 + RDS booking + phòng RESERVED.',
        'Audit item + SNS/SQS + notification log.',
        'Lỗi đặt phòng → kiểm tra phòng AVAILABLE.',
        'Poison message → DLQ sau 3 lần nhận.',
        'X-Correlation-Id đối chiếu CloudWatch Logs.'
    ],'Amazon-CloudWatch',title_size=23,body_size=19)
    s.footer(3);return s


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--discovery',choices=['static','cloudmap','alb'],default='alb');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    slides=[architecture(args.discovery),erd(),strategy()]
    mx=ET.Element('mxfile',host='app.diagrams.net',agent='Codex',version='24.7.17',type='device')
    for i,s in enumerate(slides):
        s.save();d=ET.SubElement(mx,'diagram',id=f'week4-{i+1}',name=s.name);d.append(s.model)
    ET.indent(mx)
    ET.ElementTree(mx).write(OUT/'hotel-week4-architecture-erd-db-strategy.drawio',encoding='utf-8',xml_declaration=True)
    print('Rendered 3 SVG slides, 4K PNGs, and editable 3-page drawio.')

if __name__=='__main__':main()
