import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton # pyright: ignore[reportMissingImports]
from PyQt5.QtCore    import Qt, QRectF, QPointF # pyright: ignore[reportMissingImports]
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient # pyright: ignore[reportMissingImports]


class GaugeWidget(QWidget):
    def __init__(self, label, unit, min_val, max_val,
                 warn=None, danger=None, arc_start=220, arc_span=260,
                 c_normal="#22c55e", c_warn="#f59e0b", c_danger="#ef4444", parent=None):
        super().__init__(parent)
        self.label=label; self.unit=unit; self.min_val=min_val; self.max_val=max_val
        self.warn=warn or max_val*0.7; self.danger=danger or max_val*0.9
        self.arc_start=arc_start; self.arc_span=arc_span
        self.cn=QColor(c_normal); self.cw=QColor(c_warn); self.cd=QColor(c_danger)
        self._value=min_val; self.setMinimumSize(160,160)

    def set_value(self,v):
        self._value=max(self.min_val,min(self.max_val,v)); self.update()

    def _angle(self,v):
        return self.arc_start-((v-self.min_val)/max(1,self.max_val-self.min_val))*self.arc_span

    def paintEvent(self,_):
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
        steps=7
        for i in range(steps+1):
            ratio=i/steps; val=self.min_val+ratio*(self.max_val-self.min_val)
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


class AnalogCluster(QWidget):
    def __init__(self, energy_model=None):
        super().__init__()
        self.setStyleSheet("QWidget{background:#070f1d;color:white;font-family:'Segoe UI';} QLabel{background:transparent;} #topBar{background:#050c18;border-bottom:1px solid #1e293b;} #infoBar{background:#050c18;border-top:1px solid #1e293b;} QPushButton{background:#0f172a;border:1px solid #1e293b;border-radius:8px;color:white;padding:6px 14px;font-size:11px;font-weight:bold;} #refuelBtn{background:#16a34a;}")
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        top=QFrame(); top.setObjectName("topBar"); top.setFixedHeight(44)
        tl=QHBoxLayout(top); tl.setContentsMargins(16,0,16,0)
        logo=QLabel("SUPRAJIT"); logo.setStyleSheet("color:#38bdf8;font-size:20px;font-weight:bold;letter-spacing:4px;")
        sub=QLabel("ANALOG CLUSTER"); sub.setStyleSheet("color:#475569;font-size:10px;letter-spacing:2px;")
        self.live=QLabel("● LIVE"); self.live.setStyleSheet("color:#22c55e;font-size:10px;font-weight:bold;")
        tl.addWidget(logo); tl.addSpacing(10); tl.addWidget(sub); tl.addStretch(); tl.addWidget(self.live)
        root.addWidget(top)

        body=QHBoxLayout(); body.setContentsMargins(16,12,16,12); body.setSpacing(20)
        self.speed_gauge=GaugeWidget("SPEED","km/h",0,140,warn=60,danger=100)
        self.speed_gauge.setMinimumSize(400,400)
        right_col=QVBoxLayout(); right_col.setSpacing(16)
        self.rpm_gauge=GaugeWidget("RPM ×100","",0,80,warn=55,danger=70)
        self.rpm_gauge.setMinimumSize(180,180)
        self.fuel_gauge=GaugeWidget("FUEL","%",0,100,warn=30,danger=15,
                                     c_normal="#22c55e",c_warn="#f59e0b",c_danger="#ef4444")
        self.fuel_gauge.setMinimumSize(180,180)
        right_col.addWidget(self.rpm_gauge,1); right_col.addWidget(self.fuel_gauge,1)
        body.addWidget(self.speed_gauge,3); body.addLayout(right_col,2)
        root.addLayout(body,1)

        info=QFrame(); info.setObjectName("infoBar"); info.setFixedHeight(48)
        il=QHBoxLayout(info); il.setContentsMargins(16,0,16,0); il.setSpacing(30)
        self.lbl_trip=self._pair("TRIP A","0.0 km")
        self.lbl_odo=self._pair("ODO","0.0 km")
        self.lbl_range=self._pair("RANGE","300 km")
        self.temp_pair=self._pair("ENG TEMP","45°C")
        self.refuel_btn=QPushButton("⛽  REFUEL"); self.refuel_btn.setObjectName("refuelBtn")
        self.refuel_btn.setFixedHeight(30); self.refuel_btn.setVisible(False)
        for w in [self.lbl_trip,self.lbl_odo,self.lbl_range,self.temp_pair]: il.addWidget(w)
        il.addStretch(); il.addWidget(self.refuel_btn)
        root.addWidget(info)

    def _pair(self,title,val):
        w=QFrame(); lay=QVBoxLayout(w); lay.setContentsMargins(0,4,0,4); lay.setSpacing(0)
        t=QLabel(title); t.setStyleSheet("color:#475569;font-size:8px;font-weight:bold;letter-spacing:1px;")
        v=QLabel(val); v.setStyleSheet("color:#e2e8f0;font-size:11px;font-weight:bold;"); v.setObjectName("val")
        lay.addWidget(t); lay.addWidget(v); return w

    def _set(self,frame,text):
        frame.findChild(QLabel,"val").setText(text)

    def set_data(self,speed,fuel,temp,rpm,odo,trip):
        self.speed_gauge.set_value(speed)
        self.rpm_gauge.set_value(rpm/100.0)
        self.fuel_gauge.set_value(fuel)
        self._set(self.lbl_trip,f"{trip:.1f} km")
        self._set(self.lbl_odo,f"{odo:.1f} km")
        self._set(self.lbl_range,f"{int((fuel/100)*300)} km")
        col="#22c55e" if temp<70 else("#f59e0b" if temp<90 else "#ef4444")
        v=self.temp_pair.findChild(QLabel,"val")
        v.setStyleSheet(f"color:{col};font-size:11px;font-weight:bold;"); v.setText(f"{int(temp)}°C")
        self.refuel_btn.setVisible(fuel<50)

    def update_cluster(self,speed,fuel):
        self.set_data(speed,fuel,45,0,0,0)


AnalogClusterWidget = AnalogCluster