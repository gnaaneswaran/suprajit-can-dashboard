import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QProgressBar
from PyQt5.QtCore    import Qt, QRectF, QPointF, QTimer
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from datetime        import datetime


# ── Reusable needle gauge ────────────────────────────────────────
class NeedleGauge(QWidget):
    def __init__(self, label, unit, min_val, max_val,
                 warn=None, danger=None, arc_start=220, arc_span=260,
                 c_normal="#22c55e", c_warn="#f59e0b", c_danger="#ef4444", parent=None):
        super().__init__(parent)
        self.label=label; self.unit=unit; self.min_val=min_val; self.max_val=max_val
        self.warn=warn or max_val*0.7; self.danger=danger or max_val*0.9
        self.arc_start=arc_start; self.arc_span=arc_span
        self.cn=QColor(c_normal); self.cw=QColor(c_warn); self.cd=QColor(c_danger)
        self._value=min_val; self.setMinimumSize(140,140)

    def set_value(self,v):
        self._value=max(self.min_val,min(self.max_val,v)); self.update()

    def _angle(self,v):
        return self.arc_start-((v-self.min_val)/max(1,self.max_val-self.min_val))*self.arc_span

    def paintEvent(self,_):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w,h=self.width(),self.height(); cx,cy=w/2,h/2; r=min(w,h)/2-8
        gr=QRadialGradient(cx,cy,r); gr.setColorAt(0,QColor("#0d1b2e")); gr.setColorAt(1,QColor("#060e1a"))
        p.setBrush(QBrush(gr)); p.setPen(QPen(QColor("#1e293b"),2))
        p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
        rr=r-4; rect=QRectF(cx-rr,cy-rr,rr*2,rr*2); p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#1e293b"),8,Qt.SolidLine,Qt.RoundCap))
        p.drawArc(rect,int(self.arc_start*16),int(-self.arc_span*16))
        def seg(v0,v1,col):
            a0=self._angle(v0); a1=self._angle(v1)
            p.setPen(QPen(col,6,Qt.SolidLine,Qt.RoundCap))
            p.drawArc(rect,int(a0*16),int((a1-a0)*16))
        seg(self.min_val,self.warn,self.cn); seg(self.warn,self.danger,self.cw); seg(self.danger,self.max_val,self.cd)
        for i in range(6):
            ratio=i/5; val=self.min_val+ratio*(self.max_val-self.min_val)
            ang=math.radians(self._angle(val)); ca,sa=math.cos(ang),-math.sin(ang)
            p.setPen(QPen(QColor("#334155"),1.5))
            p.drawLine(QPointF(cx+ca*(r-16),cy+sa*(r-16)),QPointF(cx+ca*(r-8),cy+sa*(r-8)))
            p.setFont(QFont("Segoe UI",max(6,int(r*0.1)))); p.setPen(QPen(QColor("#64748b")))
            p.drawText(QRectF(cx+ca*(r-28)-10,cy+sa*(r-28)-8,20,16),Qt.AlignCenter,str(int(val)))
        ang=math.radians(self._angle(self._value)); ca,sa=math.cos(ang),-math.sin(ang)
        p.setPen(QPen(QColor("white"),2,Qt.SolidLine,Qt.RoundCap))
        p.drawLine(QPointF(cx-ca*10,cy-sa*10),QPointF(cx+ca*(r-15),cy+sa*(r-15)))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor("#1e293b"))); p.drawEllipse(QRectF(cx-7,cy-7,14,14))
        p.setBrush(QBrush(QColor("#38bdf8"))); p.drawEllipse(QRectF(cx-3,cy-3,6,6))
        vcol=self.cn if self._value<self.warn else(self.cw if self._value<self.danger else self.cd)
        p.setPen(QPen(vcol)); p.setFont(QFont("Segoe UI",int(r*0.2),QFont.Bold))
        p.drawText(QRectF(cx-r*0.5,cy+r*0.18,r,r*0.28),Qt.AlignCenter,str(int(self._value)))
        p.setFont(QFont("Segoe UI",int(r*0.1))); p.setPen(QPen(QColor("#64748b")))
        p.drawText(QRectF(cx-r*0.5,cy+r*0.36,r,r*0.2),Qt.AlignCenter,self.unit)
        p.setFont(QFont("Segoe UI",int(r*0.1),QFont.Bold)); p.setPen(QPen(QColor("#334155")))
        p.drawText(QRectF(cx-r,cy-r*0.42,r*2,r*0.22),Qt.AlignCenter,self.label)
        p.end()


# ── Hybrid Cluster Widget ────────────────────────────────────────
class HybridCluster(QWidget):
    def __init__(self, energy_model=None):
        super().__init__()
        self.setStyleSheet("""
            QWidget{background:#060d1a;color:white;font-family:'Segoe UI';}
            QLabel{background:transparent;}
            QFrame#divider{background:#1e293b;}
            QPushButton{background:#0f172a;border:1px solid #1e293b;border-radius:8px;
                        color:white;padding:6px 14px;font-size:10px;font-weight:bold;}
            #refuelBtn{background:#16a34a;}
            QProgressBar{border:none;background:#111827;border-radius:4px;height:8px;}
            QProgressBar::chunk{background:#22c55e;border-radius:4px;}
        """)

        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ── TOP BAR ─────────────────────────────────────────────
        top=QFrame(); top.setFixedHeight(44)
        top.setStyleSheet("background:#040b16;border-bottom:1px solid #1e293b;")
        tl=QHBoxLayout(top); tl.setContentsMargins(16,0,16,0)
        logo=QLabel("SUPRAJIT"); logo.setStyleSheet("color:#38bdf8;font-size:20px;font-weight:bold;letter-spacing:4px;")
        tag=QLabel("HYBRID CLUSTER"); tag.setStyleSheet("color:#334155;font-size:9px;letter-spacing:3px;")
        self.clock_lbl=QLabel("--:--"); self.clock_lbl.setStyleSheet("color:#e2e8f0;font-size:13px;font-weight:bold;")
        self.live_lbl=QLabel("● LIVE"); self.live_lbl.setStyleSheet("color:#22c55e;font-size:9px;font-weight:bold;")
        tl.addWidget(logo); tl.addSpacing(10); tl.addWidget(tag); tl.addStretch()
        tl.addWidget(self.clock_lbl); tl.addSpacing(20); tl.addWidget(self.live_lbl)
        root.addWidget(top)

        # ── WARNING STRIP ────────────────────────────────────────
        warn_strip=QFrame(); warn_strip.setFixedHeight(28)
        warn_strip.setStyleSheet("background:#030912;border-bottom:1px solid #0f1e35;")
        wl=QHBoxLayout(warn_strip); wl.setContentsMargins(20,0,20,0); wl.setSpacing(30)
        self.ind_left=QLabel("◄"); self.ind_left.setStyleSheet("color:#334155;font-size:14px;font-weight:bold;")
        self.ind_right=QLabel("►"); self.ind_right.setStyleSheet("color:#334155;font-size:14px;font-weight:bold;")
        self.abs_lbl=self._warn_icon("ABS","#22c55e")
        self.beam_lbl=self._warn_icon("HIGH BEAM","#334155")
        self.stand_lbl=self._warn_icon("SIDE STAND","#22c55e")
        self.eng_warn=self._warn_icon("ENGINE","#334155")
        self.mode_lbl=QLabel("ECO"); self.mode_lbl.setStyleSheet("color:#22c55e;font-size:10px;font-weight:bold;letter-spacing:1px;background:#0a2010;border:1px solid #22c55e;border-radius:4px;padding:1px 8px;")
        wl.addWidget(self.ind_left)
        for w in [self.abs_lbl,self.beam_lbl,self.stand_lbl,self.eng_warn]: wl.addWidget(w)
        wl.addStretch(); wl.addWidget(self.mode_lbl); wl.addSpacing(10); wl.addWidget(self.ind_right)
        root.addWidget(warn_strip)

        # ── MAIN BODY ────────────────────────────────────────────
        body=QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)

        # LEFT — Analog section
        analog_side=QWidget(); analog_side.setStyleSheet("background:#070f1d;")
        al=QVBoxLayout(analog_side); al.setContentsMargins(16,12,8,12); al.setSpacing(12)

        analog_title=QLabel("ANALOG"); analog_title.setStyleSheet("color:#1e3a5f;font-size:9px;font-weight:bold;letter-spacing:3px;")
        al.addWidget(analog_title)

        self.speed_gauge=NeedleGauge("SPEED","km/h",0,140,warn=60,danger=100)
        self.speed_gauge.setMinimumSize(280,280)
        al.addWidget(self.speed_gauge)

        sub_gauges=QHBoxLayout(); sub_gauges.setSpacing(10)
        self.rpm_gauge=NeedleGauge("RPM ×100","",0,80,warn=55,danger=70)
        self.rpm_gauge.setMinimumSize(120,120)
        self.fuel_gauge=NeedleGauge("FUEL","%",0,100,warn=30,danger=15,
                                     c_normal="#22c55e",c_warn="#f59e0b",c_danger="#ef4444")
        self.fuel_gauge.setMinimumSize(120,120)
        sub_gauges.addWidget(self.rpm_gauge); sub_gauges.addWidget(self.fuel_gauge)
        al.addLayout(sub_gauges)
        al.addStretch()
        body.addWidget(analog_side,5)

        # DIVIDER
        div=QFrame(); div.setObjectName("divider"); div.setFixedWidth(2)
        body.addWidget(div)

        # RIGHT — Digital section
        digital_side=QWidget(); digital_side.setStyleSheet("background:#040c1a;")
        dl=QVBoxLayout(digital_side); dl.setContentsMargins(12,12,16,12); dl.setSpacing(10)

        digital_title=QLabel("DIGITAL"); digital_title.setStyleSheet("color:#1e3a5f;font-size:9px;font-weight:bold;letter-spacing:3px;")
        dl.addWidget(digital_title)

        # Big speed number
        speed_card=QFrame(); speed_card.setStyleSheet("background:#070f1d;border:1px solid #0f2040;border-radius:12px;")
        scl=QVBoxLayout(speed_card); scl.setContentsMargins(12,8,12,8); scl.setSpacing(0)
        lbl_s=QLabel("SPEED"); lbl_s.setStyleSheet("color:#334155;font-size:8px;font-weight:bold;letter-spacing:1px;")
        self.dig_speed=QLabel("0"); self.dig_speed.setStyleSheet("color:white;font-size:52px;font-weight:bold;")
        self.dig_speed.setAlignment(Qt.AlignCenter)
        unit_s=QLabel("km/h"); unit_s.setStyleSheet("color:#475569;font-size:10px;"); unit_s.setAlignment(Qt.AlignCenter)
        scl.addWidget(lbl_s); scl.addWidget(self.dig_speed); scl.addWidget(unit_s)
        dl.addWidget(speed_card)

        # Info grid
        grid=QHBoxLayout(); grid.setSpacing(8)
        left_g=QVBoxLayout(); left_g.setSpacing(8)
        right_g=QVBoxLayout(); right_g.setSpacing(8)
        self.odo_card  =self._dcard("ODO","0.0 km","#e2e8f0")
        self.trip_card =self._dcard("TRIP A","0.0 km","#e2e8f0")
        self.range_card=self._dcard("RANGE","300 km","#22c55e")
        self.bat_card  =self._dcard("BATTERY","100%","#22c55e")
        self.temp_card =self._dcard("TEMP","45°C","#f59e0b")
        self.eng_card  =self._dcard("ENERGY","20 Wh/km","#38bdf8")
        left_g.addWidget(self.odo_card); left_g.addWidget(self.trip_card); left_g.addWidget(self.range_card)
        right_g.addWidget(self.bat_card); right_g.addWidget(self.temp_card); right_g.addWidget(self.eng_card)
        grid.addLayout(left_g); grid.addLayout(right_g)
        dl.addLayout(grid)

        # Battery bar
        bat_frame=QFrame(); bat_frame.setStyleSheet("background:#070f1d;border:1px solid #0f2040;border-radius:8px;")
        bfl=QVBoxLayout(bat_frame); bfl.setContentsMargins(10,6,10,6); bfl.setSpacing(4)
        blbl=QLabel("BATTERY LEVEL"); blbl.setStyleSheet("color:#334155;font-size:7px;font-weight:bold;letter-spacing:1px;")
        self.bat_bar=QProgressBar(); self.bat_bar.setValue(100); self.bat_bar.setTextVisible(False)
        bfl.addWidget(blbl); bfl.addWidget(self.bat_bar)
        dl.addWidget(bat_frame)

        # Service reminder
        self.service_lbl=QLabel("🔧 SERVICE IN 1520 km")
        self.service_lbl.setStyleSheet("color:#f59e0b;font-size:10px;font-weight:bold;")
        self.service_lbl.setAlignment(Qt.AlignCenter)
        dl.addWidget(self.service_lbl)

        # Refuel button
        self.refuel_btn=QPushButton("⛽  REFUEL"); self.refuel_btn.setObjectName("refuelBtn")
        self.refuel_btn.setVisible(False); dl.addWidget(self.refuel_btn)
        dl.addStretch()

        body.addWidget(digital_side,4)
        root.addLayout(body,1)

        # ── BOTTOM BAR ──────────────────────────────────────────
        bot=QFrame(); bot.setFixedHeight(36)
        bot.setStyleSheet("background:#030912;border-top:1px solid #1e293b;")
        bl=QHBoxLayout(bot); bl.setContentsMargins(20,0,20,0); bl.setSpacing(30)
        self.avg_lbl =self._bstat("AVG SPEED","-- km/h")
        self.top_lbl =self._bstat("TOP SPEED","-- km/h")
        self.co2_lbl =self._bstat("CO₂ SAVED","0.0 kg")
        self.trip_dist=self._bstat("TRIP DIST","0.0 km")
        for w in [self.avg_lbl,self.top_lbl,self.co2_lbl,self.trip_dist]: bl.addWidget(w)
        bl.addStretch()
        root.addWidget(bot)

        # Clock timer
        self._clock=QTimer(); self._clock.timeout.connect(self._update_clock); self._clock.start(1000)
        self._update_clock()

        # Stats
        self._top_speed=0.0; self._total_dist=0.0; self._speed_sum=0.0; self._ticks=0

    def _warn_icon(self,label,color):
        lbl=QLabel(label); lbl.setStyleSheet(f"color:{color};font-size:8px;font-weight:bold;letter-spacing:1px;")
        return lbl

    def _dcard(self,title,val,color):
        f=QFrame(); f.setStyleSheet("background:#070f1d;border:1px solid #0f2040;border-radius:8px;")
        lay=QVBoxLayout(f); lay.setContentsMargins(8,6,8,6); lay.setSpacing(1)
        t=QLabel(title); t.setStyleSheet("color:#334155;font-size:7px;font-weight:bold;letter-spacing:1px;")
        v=QLabel(val); v.setStyleSheet(f"color:{color};font-size:14px;font-weight:bold;"); v.setObjectName("val")
        lay.addWidget(t); lay.addWidget(v); return f

    def _bstat(self,label,val):
        f=QFrame(); lay=QHBoxLayout(f); lay.setContentsMargins(0,0,0,0); lay.setSpacing(6)
        t=QLabel(label+":"); t.setStyleSheet("color:#334155;font-size:8px;font-weight:bold;")
        v=QLabel(val); v.setStyleSheet("color:#94a3b8;font-size:10px;font-weight:bold;"); v.setObjectName("val")
        lay.addWidget(t); lay.addWidget(v); return f

    def _set(self,frame,text):
        frame.findChild(QLabel,"val").setText(text)

    def _update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%I:%M %p"))

    def set_data(self,speed,fuel,temp,rpm,odo,trip):
        # Analog side
        self.speed_gauge.set_value(speed)
        self.rpm_gauge.set_value(rpm/100.0)
        self.fuel_gauge.set_value(fuel)

        # Digital side
        self.dig_speed.setText(str(int(speed)))
        self._set(self.odo_card,  f"{odo:.1f} km")
        self._set(self.trip_card, f"{trip:.1f} km")
        self._set(self.range_card,f"{int((fuel/100)*300)} km")

        bat_col="#22c55e" if fuel>30 else("#f59e0b" if fuel>15 else "#ef4444")
        self.bat_card.findChild(QLabel,"val").setStyleSheet(f"color:{bat_col};font-size:14px;font-weight:bold;")
        self._set(self.bat_card,f"{int(fuel)}%")
        self.bat_bar.setValue(int(fuel))

        temp_col="#22c55e" if temp<70 else("#f59e0b" if temp<90 else "#ef4444")
        self.temp_card.findChild(QLabel,"val").setStyleSheet(f"color:{temp_col};font-size:14px;font-weight:bold;")
        self._set(self.temp_card,f"{int(temp)}°C")
        self._set(self.eng_card,f"{int(20+speed*0.1)} Wh/km")

        # Refuel warning
        self.refuel_btn.setVisible(fuel<50)

        # Stats
        if speed>self._top_speed: self._top_speed=speed
        self._speed_sum+=speed; self._ticks+=1
        avg=self._speed_sum/self._ticks if self._ticks>0 else 0
        self._set(self.avg_lbl,f"{int(avg)} km/h")
        self._set(self.top_lbl,f"{int(self._top_speed)} km/h")
        self._set(self.trip_dist,f"{trip:.1f} km")

        # Eco mode indicator
        if speed<40: mode,col="ECO","#22c55e"
        elif speed<70: mode,col="CITY","#38bdf8"
        else: mode,col="SPORT","#ef4444"
        self.mode_lbl.setText(mode)
        self.mode_lbl.setStyleSheet(f"color:{col};font-size:10px;font-weight:bold;letter-spacing:1px;background:{col}18;border:1px solid {col};border-radius:4px;padding:1px 8px;")


HybridClusterWidget = HybridCluster