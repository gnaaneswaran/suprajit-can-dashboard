import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore    import Qt, QRectF, QPointF
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient


class ArcGauge(QWidget):
    def __init__(self, label, unit, min_val, max_val,
                 warn=None, danger=None, arc_start=220, arc_span=260,
                 c_normal="#22c55e", c_warn="#f59e0b", c_danger="#ef4444", parent=None):
        super().__init__(parent)
        self.label=label; self.unit=unit; self.min_val=min_val; self.max_val=max_val
        self.warn=warn or max_val*0.7; self.danger=danger or max_val*0.9
        self.arc_start=arc_start; self.arc_span=arc_span
        self.cn=QColor(c_normal); self.cw=QColor(c_warn); self.cd=QColor(c_danger)
        self._value=min_val; self.setMinimumSize(160,160)

    def set_value(self, v):
        self._value=max(self.min_val,min(self.max_val,v)); self.update()

    def _angle(self, v):
        return self.arc_start-((v-self.min_val)/max(1,self.max_val-self.min_val))*self.arc_span

    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height(); cx,cy=w/2,h/2; r=min(w,h)/2-10
        gr=QRadialGradient(cx,cy,r); gr.setColorAt(0,QColor("#0d1b2e")); gr.setColorAt(1,QColor("#060e1a"))
        p.setBrush(QBrush(gr)); p.setPen(QPen(QColor("#1e293b"),2))
        p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
        rr=r-5; rect=QRectF(cx-rr,cy-rr,rr*2,rr*2); p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#1e293b"),9,Qt.SolidLine,Qt.RoundCap))
        p.drawArc(rect,int(self.arc_start*16),int(-self.arc_span*16))
        def seg(v0,v1,col):
            a0=self._angle(v0); a1=self._angle(v1)
            p.setPen(QPen(col,7,Qt.SolidLine,Qt.RoundCap))
            p.drawArc(rect,int(a0*16),int((a1-a0)*16))
        seg(self.min_val,self.warn,self.cn); seg(self.warn,self.danger,self.cw); seg(self.danger,self.max_val,self.cd)
        for i in range(8):
            ratio=i/7; val=self.min_val+ratio*(self.max_val-self.min_val)
            ang=math.radians(self._angle(val)); ca,sa=math.cos(ang),-math.sin(ang)
            p.setPen(QPen(QColor("#334155"),1.5))
            p.drawLine(QPointF(cx+ca*(r-20),cy+sa*(r-20)),QPointF(cx+ca*(r-10),cy+sa*(r-10)))
            p.setFont(QFont("Segoe UI",max(6,int(r*0.09)))); p.setPen(QPen(QColor("#64748b")))
            p.drawText(QRectF(cx+ca*(r-34)-12,cy+sa*(r-34)-9,24,18),Qt.AlignCenter,str(int(val)))
        ang=math.radians(self._angle(self._value)); ca,sa=math.cos(ang),-math.sin(ang)
        p.setPen(QPen(QColor("white"),2,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(cx-ca*12,cy-sa*12),QPointF(cx+ca*(r-18),cy+sa*(r-18)))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor("#1e293b"))); p.drawEllipse(QRectF(cx-8,cy-8,16,16))
        p.setBrush(QBrush(QColor("#38bdf8"))); p.drawEllipse(QRectF(cx-4,cy-4,8,8))
        vcol=self.cn if self._value<self.warn else(self.cw if self._value<self.danger else self.cd)
        p.setPen(QPen(vcol)); p.setFont(QFont("Segoe UI",int(r*0.18),QFont.Bold))
        p.drawText(QRectF(cx-r*0.5,cy+r*0.15,r,r*0.3),Qt.AlignCenter,str(int(self._value)))
        p.setFont(QFont("Segoe UI",int(r*0.09))); p.setPen(QPen(QColor("#64748b")))
        p.drawText(QRectF(cx-r*0.5,cy+r*0.33,r,r*0.2),Qt.AlignCenter,self.unit)
        p.setFont(QFont("Segoe UI",int(r*0.09),QFont.Bold)); p.setPen(QPen(QColor("#334155")))
        p.drawText(QRectF(cx-r,cy-r*0.4,r*2,r*0.22),Qt.AlignCenter,self.label)
        p.end()


class DigitalCluster(QWidget):
    def __init__(self, energy_model=None):
        super().__init__()
        self.setStyleSheet("QWidget{background:#040c1a;color:white;font-family:'Segoe UI';} QLabel{background:transparent;}")
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        top=QFrame(); top.setFixedHeight(40)
        top.setStyleSheet("background:#030917;border-bottom:1px solid #0f2040;")
        tl=QHBoxLayout(top); tl.setContentsMargins(16,0,16,0)
        logo=QLabel("SUPRAJIT"); logo.setStyleSheet("color:#38bdf8;font-size:18px;font-weight:bold;letter-spacing:4px;")
        sub=QLabel("SMART DIGITAL CLUSTER"); sub.setStyleSheet("color:#1e3a5f;font-size:9px;letter-spacing:2px;")
        self.live=QLabel("● LIVE"); self.live.setStyleSheet("color:#22c55e;font-size:9px;font-weight:bold;")
        tl.addWidget(logo); tl.addSpacing(10); tl.addWidget(sub); tl.addStretch(); tl.addWidget(self.live)
        root.addWidget(top)

        body=QHBoxLayout(); body.setContentsMargins(12,10,12,10); body.setSpacing(16)
        left=QVBoxLayout(); left.setSpacing(10)
        self.bat_lbl=self._card("BATTERY","100%","#22c55e")
        self.temp_lbl=self._card("TEMP","45°C","#f59e0b")
        self.eng_lbl=self._card("ENERGY","20 Wh/km","#38bdf8")
        left.addWidget(self.bat_lbl); left.addWidget(self.temp_lbl); left.addWidget(self.eng_lbl); left.addStretch()

        self.speed_gauge=ArcGauge("SPEED","km/h",0,80,warn=50,danger=70)
        self.speed_gauge.setMinimumSize(300,300)

        right=QVBoxLayout(); right.setSpacing(10)
        self.odo_lbl=self._card("ODO","0.0 km","#e2e8f0")
        self.trip_lbl=self._card("TRIP A","0.0 km","#e2e8f0")
        self.range_lbl=self._card("RANGE","100 km","#22c55e")
        right.addWidget(self.odo_lbl); right.addWidget(self.trip_lbl); right.addWidget(self.range_lbl); right.addStretch()
        body.addLayout(left,1); body.addWidget(self.speed_gauge,3); body.addLayout(right,1)
        root.addLayout(body,1)

        bot=QFrame(); bot.setFixedHeight(40)
        bot.setStyleSheet("background:#030917;border-top:1px solid #0f2040;")
        bl=QHBoxLayout(bot); bl.setContentsMargins(16,0,16,0); bl.setSpacing(24)
        self.recharge_btn=QPushButton("⚡ RECHARGE")
        self.recharge_btn.setStyleSheet("background:#1d4ed8;border:none;border-radius:6px;color:white;padding:4px 14px;font-size:10px;font-weight:bold;")
        self.recharge_btn.setVisible(False)
        bl.addStretch(); bl.addWidget(self.recharge_btn)
        root.addWidget(bot)

    def _card(self,title,val,color):
        f=QFrame(); f.setStyleSheet("background:#070f1d;border:1px solid #0f2040;border-radius:10px;")
        lay=QVBoxLayout(f); lay.setContentsMargins(10,8,10,8); lay.setSpacing(1)
        t=QLabel(title); t.setStyleSheet("color:#475569;font-size:8px;font-weight:bold;letter-spacing:1px;")
        v=QLabel(val); v.setStyleSheet(f"color:{color};font-size:18px;font-weight:bold;"); v.setObjectName("val")
        lay.addWidget(t); lay.addWidget(v); return f

    def _set(self,frame,text):
        frame.findChild(QLabel,"val").setText(text)

    def set_data(self,speed,fuel,temp,rpm,odo,trip):
        self.speed_gauge.set_value(speed)
        self._set(self.bat_lbl,f"{int(fuel)}%")
        col="#22c55e" if temp<70 else "#ef4444"
        self.temp_lbl.findChild(QLabel,"val").setStyleSheet(f"color:{col};font-size:18px;font-weight:bold;")
        self._set(self.temp_lbl,f"{int(temp)}°C")
        self._set(self.eng_lbl,f"{int(20+speed*0.1)} Wh/km")
        self._set(self.odo_lbl,f"{odo:.1f} km")
        self._set(self.trip_lbl,f"{trip:.1f} km")
        self._set(self.range_lbl,f"{int((fuel/100)*100)} km")
        self.recharge_btn.setVisible(fuel<20)

    def update_cluster(self,speed,battery):
        self.set_data(speed,battery,45,0,0,0)


DigitalClusterWidget = DigitalCluster
