import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QSpinBox, QDoubleSpinBox,
    QMessageBox, QComboBox, QScrollArea,
    QDialog, QFormLayout, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QCursor, QPalette
from crm_sistemi import (
    Musteri, Satis, CRMSistemi, MusteriTipi, SatisKategorisi, SadakatSeviyesi,
    Operator, OperatorRol, TalepDurumu
)

# ========== RENK PALETİ (Modern Dark Mode) ==========
C = {
    "bg":         "#0F172A",
    "card":       "#1E293B",
    "border":     "#334155",
    "accent":     "#3B82F6",
    "accent_dark":"#1D4ED8",
    "success":    "#10B981",
    "warning":    "#F59E0B",
    "danger":     "#EF4444",
    "text":       "#F1F5F9",
    "text_dim":   "#94A3B8",
    "sidebar":    "#0F172A",
}

def card_ss():
    return f"QFrame {{ background: {C['card']}; border: 1px solid {C['border']}; border-radius: 12px; }}"

def btn_primary_ss():
    return f"""QPushButton{{ background-color: {C['accent']}; color: {C['text']}; border: none; border-radius: 8px; 
        padding: 12px; font-weight: bold; font-size: 13px; }} QPushButton:hover{{ background-color: {C['accent_dark']}; }}"""

def input_ss():
    return (
        f"QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{ "
        f"  background: {C['sidebar']}; color: #FFFFFF; "
        f"  border: 1px solid {C['border']}; border-radius: 6px; "
        f"  padding: 10px; font-size: 14px; font-weight: 500; "
        f"  selection-background-color: {C['accent']}; selection-color: #FFFFFF; "
        f"}} "
        f"QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {{ "
        f"  color: #FFFFFF; background: #1a202c; "
        f"  border: 2px solid {C['accent']}; "
        f"}} "
        f"QLineEdit {{ placeholder-text-color: {C['text_dim']}; }} "
        f"QComboBox {{ placeholder-text-color: {C['text_dim']}; }}"
    )

def make_label(text: str, ss: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(ss)
    return lbl

def optimize_columns(tbl: QTableWidget, stretch_cols: list[int]) -> None:
    """Tüm sütunları içeriğe göre daraltır, sadece belirtilen indekslerdeki sütunları esnetir."""
    header = tbl.horizontalHeader()
    if header is not None:
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for col in stretch_cols:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

def stretch_columns(tbl: QTableWidget) -> None:
    header = tbl.horizontalHeader()
    if header is not None:
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

def trigger_global_refresh(widget: QWidget) -> None:
    """Arayüzde bir veri silinip/eklendiğinde tüm sayfaların eşzamanlı güncellenmesini sağlar."""
    win = widget.window()
    if hasattr(win, "refresh_all"):
        win.refresh_all()

class StatCard(QFrame):
    def __init__(self, baslik: str, deger: str | int, renk: str = "#3B82F6") -> None:
        super().__init__()
        self.setStyleSheet(f"QFrame {{ background: {C['card']}; border-left: 4px solid {renk}; border-radius: 8px; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 15, 20, 15)
        
        lbl_title = QLabel(baslik.upper())
        lbl_title.setStyleSheet(f"color: #FFFFFF; font-size: 13px; font-weight: bold; letter-spacing: 1px;")
        
        self.lbl_val = QLabel(str(deger))
        self.lbl_val.setStyleSheet(f"color: #FFFFFF; font-size: 40px; font-weight: 900;")
        
        lay.addWidget(lbl_title)
        lay.addWidget(self.lbl_val)
        lay.addStretch()

class NavBtn(QPushButton):
    def __init__(self, ikon: str, metin: str) -> None:
        super().__init__(f"{ikon}  {metin}")
        self.setCheckable(True)
        self.setFixedHeight(45)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggled.connect(self._refresh)
        self._refresh(False)

    def _refresh(self, aktif: bool) -> None:
        if aktif:
            self.setStyleSheet(f"""QPushButton {{ background-color: {C['accent']}; color: {C['text']};
                border: none; text-align: left; padding-left: 20px; font-size: 13px; font-weight: bold;
                border-radius: 6px; margin: 2px 12px; }}""")
        else:
            self.setStyleSheet(f"""QPushButton {{ background-color: transparent; color: {C['text_dim']};
                border: none; text-align: left; padding-left: 20px; font-size: 13px; font-weight: 600;
                margin: 2px 12px; }} QPushButton:hover {{ color: {C['text']}; background-color: {C['card']};
                border-radius: 6px; }}""")

class MusteriDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, musteri: Musteri | None = None) -> None:
        super().__init__(parent)
        self.musteri = musteri
        self.setWindowTitle("Müşteri Bilgisi" if musteri else "Yeni Müşteri")
        self.setGeometry(100, 100, 500, 450)
        self.setStyleSheet(f"QDialog {{ background: {C['card']}; }}")
        
        lay = QFormLayout(self)
        lay.setSpacing(12)
        
        self.id_inp = QSpinBox()
        self.id_inp.setRange(1, 9999)
        self.id_inp.setStyleSheet(input_ss())
        if musteri:
            self.id_inp.setValue(musteri.musteri_id)
            self.id_inp.setEnabled(False)
        
        self.ad_inp = QLineEdit()
        self.ad_inp.setPlaceholderText("Müşteri adı veya şirket ünvanı")
        self.ad_inp.setStyleSheet(input_ss())
        if musteri:
            self.ad_inp.setText(musteri.ad)
        
        self.tel_inp = QLineEdit()
        self.tel_inp.setPlaceholderText("0532 123 45 67")
        self.tel_inp.setStyleSheet(input_ss())
        if musteri:
            self.tel_inp.setText(musteri.telefon)
        
        self.email_inp = QLineEdit()
        self.email_inp.setPlaceholderText("ornek@email.com")
        self.email_inp.setStyleSheet(input_ss())
        if musteri:
            self.email_inp.setText(musteri.email)
        
        self.sehir_inp = QLineEdit()
        self.sehir_inp.setPlaceholderText("İstanbul")
        self.sehir_inp.setStyleSheet(input_ss())
        if musteri:
            self.sehir_inp.setText(musteri.sehir)
        
        self.tip_combo = QComboBox()
        self.tip_combo.addItems([t.value for t in MusteriTipi])
        self.tip_combo.setStyleSheet(input_ss())
        if musteri:
            self.tip_combo.setCurrentText(musteri.tip.value)
        
        self.notlar_inp = QTextEdit()
        self.notlar_inp.setPlaceholderText("Müşteri hakkında notlar...")
        self.notlar_inp.setStyleSheet(input_ss())
        self.notlar_inp.setMaximumHeight(80)
        if musteri:
            self.notlar_inp.setText(musteri.notlar)
        
        form_ss = f"color: #FFFFFF; font-size: 14px;"
        lay.addRow(make_label("Müşteri ID:", form_ss), self.id_inp)
        lay.addRow(make_label("Müşteri Adı:", form_ss), self.ad_inp)
        lay.addRow(make_label("Telefon:", form_ss), self.tel_inp)
        lay.addRow(make_label("E-mail:", form_ss), self.email_inp)
        lay.addRow(make_label("Şehir:", form_ss), self.sehir_inp)
        lay.addRow(make_label("Müşteri Tipi:", form_ss), self.tip_combo)
        lay.addRow(make_label("Notlar:", form_ss), self.notlar_inp)
        
        btn_lay = QHBoxLayout()
        btn_save = QPushButton("✓ Kaydet")
        btn_save.setStyleSheet(btn_primary_ss())
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("✕ İptal")
        btn_cancel.setStyleSheet(f"QPushButton{{ background-color: {C['card']}; color: {C['text']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 10px; }}")
        btn_cancel.clicked.connect(self.reject)
        
        btn_lay.addWidget(btn_save)
        btn_lay.addWidget(btn_cancel)
        lay.addRow(btn_lay)

    def accept(self) -> None:
        """Kaydet butonuna basıldığında zorunlu alanları kontrol eder."""
        eksikler = []
        
        if not self.ad_inp.text().strip():
            eksikler.append("• Müşteri Adı")
        if not self.tel_inp.text().strip():
            eksikler.append("• Telefon")
        if not self.email_inp.text().strip():
            eksikler.append("• E-mail")
        if not self.sehir_inp.text().strip():
            eksikler.append("• Şehir")
            
        if eksikler:
            hata_mesaji = "Lütfen aşağıdaki zorunlu alanları doldurun:\n\n" + "\n".join(eksikler)
            QMessageBox.warning(self, "Eksik Bilgi", hata_mesaji)
            return
            
        super().accept()

class TalepGuncelleDialog(QDialog):
    def __init__(self, parent: QWidget, talep, musteri_ad: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Talep Güncelle - {musteri_ad}")
        self.setFixedSize(400, 250)
        self.setStyleSheet(f"QDialog {{ background: {C['card']}; }}")
        
        lay = QFormLayout(self)
        lay.setSpacing(15)
        form_ss = "color: #FFFFFF; font-size: 14px; font-weight: bold;"
        
        aciklama_lbl = QLabel(talep.aciklama)
        aciklama_lbl.setWordWrap(True)
        aciklama_lbl.setStyleSheet(f"color: {C['text_dim']}; font-size: 13px; padding-bottom: 10px;")
        lay.addRow(make_label("Müşteri Sorunu:", form_ss), aciklama_lbl)
        
        self.durum_combo = QComboBox()
        for d in TalepDurumu:
            self.durum_combo.addItem(d.value, userData=d)
        self.durum_combo.setStyleSheet(input_ss())
        self.durum_combo.setCurrentText(talep.durum.value)
        lay.addRow(make_label("Yeni Durum:", form_ss), self.durum_combo)
        
        btn_lay = QHBoxLayout()
        btn_save = QPushButton("✓ Güncelle")
        btn_save.setStyleSheet(btn_primary_ss())
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("✕ İptal")
        btn_cancel.setStyleSheet(
            f"QPushButton{{ background-color: transparent; color: {C['text']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; padding: 10px; }}")
        btn_cancel.clicked.connect(self.reject)
        
        btn_lay.addWidget(btn_save)
        btn_lay.addWidget(btn_cancel)
        lay.addRow(btn_lay)

class DashboardPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)
        
        title = QLabel("📊 Yönetim Panosu")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)
        
        stat_lay = QHBoxLayout()
        self.stat_musteri = StatCard("Toplam Müşteri", 0)
        self.stat_satis = StatCard("Toplam Satış", "₺0", C['success'])
        self.stat_gelir = StatCard("Ort. Müşteri Değeri", "₺0", C['warning'])
        self.stat_talep = StatCard("Açık Talepler", 0, C['danger'])
        
        stat_lay.addWidget(self.stat_musteri)
        stat_lay.addWidget(self.stat_satis)
        stat_lay.addWidget(self.stat_gelir)
        stat_lay.addWidget(self.stat_talep)
        lay.addLayout(stat_lay)
        
        tbl_frame = QFrame()
        tbl_frame.setStyleSheet(card_ss())
        tbl_lay = QVBoxLayout(tbl_frame)
        
        tbl_title = QLabel("👥 Müşteri Portföyü")
        tbl_title.setStyleSheet(f"color: #FFFFFF; font-size: 18px; font-weight: bold;")
        tbl_lay.addWidget(tbl_title)
        
        search_lay = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Müşteri ara...")
        self.search.setMaximumWidth(300)
        self.search.setStyleSheet(input_ss())
        self.search.textChanged.connect(self.refresh)
        search_lay.addWidget(self.search)
        search_lay.addStretch()
        tbl_lay.addLayout(search_lay)
        
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(7)
        self.tbl.setHorizontalHeaderLabels(["ID", "Adı", "Telefon", "E-mail", "Harcama", "Segment", "Açık"])
        optimize_columns(self.tbl, [1, 3])
        self.tbl.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; border: none; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        tbl_lay.addWidget(self.tbl)
        lay.addWidget(tbl_frame)
        lay.addStretch()
        
        self.refresh()
    
    def refresh(self) -> None:
        stats = self.sistem.get_istatistikler()
        self.stat_musteri.lbl_val.setText(str(stats['toplam_musteri']))
        self.stat_satis.lbl_val.setText(f"₺{stats['toplam_gelir']:,.0f}")
        self.stat_gelir.lbl_val.setText(f"₺{stats['ortalama_musteri_degeri']:,.0f}")
        self.stat_talep.lbl_val.setText(str(stats['acik_talepler']))
        
        musteriler = self.sistem.get_tum_musteriler()
        arama = self.search.text().lower()
        
        self.tbl.setRowCount(0)
        for m in musteriler.values():
            if arama and arama not in m.ad.lower() and arama not in str(m.musteri_id):
                continue
            
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            
            items = [
                str(m.musteri_id), m.ad, m.telefon, m.email,
                f"₺{m.toplam_harcama():,.0f}", m.get_segment(),
                f"🔴 {m.acik_talep_sayisi()}" if m.acik_talep_sayisi() > 0 else "✓"
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl.setItem(r, col, item)

class MusteriPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(15)
        
        title = QLabel("👥 Müşteri Yönetimi")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)
        
        btn_lay = QHBoxLayout()
        btn_new = QPushButton("➕ Yeni Müşteri")
        btn_new.setStyleSheet(btn_primary_ss())
        btn_new.clicked.connect(self._new_musteri)
        
        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setStyleSheet(btn_primary_ss())
        btn_refresh.clicked.connect(self.refresh)
        
        btn_lay.addWidget(btn_new)
        btn_lay.addWidget(btn_refresh)
        btn_lay.addStretch()
        lay.addLayout(btn_lay)
        
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(10)
        self.tbl.setHorizontalHeaderLabels(["ID", "Adı", "Telefon", "E-mail", "Şehir", "Tip", "Katılım", "Seviye", "Puan", "İşlem"])
        optimize_columns(self.tbl, [1, 3, 4])
        self.tbl.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        lay.addWidget(self.tbl)
        
        self.refresh()
    
    def _new_musteri(self) -> None:
        dialog = MusteriDialog(self)
        if dialog.exec():
            tip_text = dialog.tip_combo.currentText()
            tip = next((t for t in MusteriTipi if t.value == tip_text), MusteriTipi.BIREYSEL)
            musteri = Musteri(
                dialog.id_inp.value(),
                dialog.ad_inp.text(),
                dialog.tel_inp.text(),
                dialog.email_inp.text(),
                dialog.sehir_inp.text(),
                tip,
            )
            musteri.notlar = dialog.notlar_inp.toPlainText()

            ok, msg = self.sistem.musteri_ekle(musteri)
            if ok:
                QMessageBox.information(self, "✓ Başarılı", msg)
                trigger_global_refresh(self)
            else:
                QMessageBox.critical(self, "✗ Hata", msg)
    
    def refresh(self) -> None:
        self.tbl.setRowCount(0)
        aktif_op = self.sistem.get_aktif_operator()
        is_admin = aktif_op and aktif_op.rol == OperatorRol.ADMIN

        for m in self.sistem.get_tum_musteriler().values():
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)

            seviye_metni = f"{m.seviye.rozet} {m.seviye.ad} (%{m.indirim_orani_al()*100:.0f})"
            items_data = [
                str(m.musteri_id), m.ad, m.telefon, m.email,
                m.sehir, m.tip.value, m.kayit_tarihi.strftime("%d/%m/%Y"),
                seviye_metni, f"{m.puan:,}"
            ]

            for col, text in enumerate(items_data):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl.setItem(r, col, item)

            btn_frame = QFrame()
            btn_frame.setStyleSheet("background: transparent;")
            btn_h = QHBoxLayout(btn_frame)
            btn_h.setContentsMargins(0, 0, 0, 0)
            btn_h.setSpacing(4)

            btn_edit = QPushButton("✏️")
            btn_edit.setMaximumWidth(40)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setToolTip("Düzenle")
            btn_edit.setStyleSheet(
                f"QPushButton {{ background: {C['accent']}; color: white; border: none; border-radius: 4px; }} "
                f"QPushButton:hover {{ background: {C['accent_dark']}; }}")
            btn_edit.clicked.connect(lambda checked, mid=m.musteri_id: self._edit(mid))
            btn_h.addWidget(btn_edit)

            if is_admin:
                btn_del = QPushButton("🗑️")
                btn_del.setMaximumWidth(40)
                btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_del.setToolTip("Sil")
                btn_del.setStyleSheet(f"QPushButton {{ background: {C['danger']}; color: white; border: none; border-radius: 4px; }}")
                btn_del.clicked.connect(lambda checked, mid=m.musteri_id: self._delete(mid))
                btn_h.addWidget(btn_del)

            self.tbl.setCellWidget(r, 9, btn_frame)

    def _edit(self, m_id: int) -> None:
        musteri = self.sistem.musteriler.get(m_id)
        if not musteri:
            QMessageBox.critical(self, "✗ Hata", "Müşteri bulunamadı!")
            return

        dialog = MusteriDialog(self, musteri=musteri)
        if dialog.exec():
            tip_text = dialog.tip_combo.currentText()
            tip = next((t for t in MusteriTipi if t.value == tip_text), musteri.tip)
            ok, msg = self.sistem.musteri_guncelle(
                m_id,
                ad=dialog.ad_inp.text(),
                telefon=dialog.tel_inp.text(),
                email=dialog.email_inp.text(),
                sehir=dialog.sehir_inp.text(),
                tip=tip,
                notlar=dialog.notlar_inp.toPlainText(),
            )
            if ok:
                QMessageBox.information(self, "✓ Başarılı", msg)
                trigger_global_refresh(self)
            else:
                QMessageBox.critical(self, "✗ Hata", msg)

    def _delete(self, m_id: int) -> None:
        aktif_op = self.sistem.get_aktif_operator()
        if not aktif_op or aktif_op.rol != OperatorRol.ADMIN:
            QMessageBox.warning(self, "Yetki Hatası", "Müşteri silme işlemi için Yönetici yetkisi gereklidir.")
            return

        StdBtn = QMessageBox.StandardButton
        reply = QMessageBox.question(
            self, "Onay", f"Müşteri {m_id} silinecektir.",
            StdBtn.Yes | StdBtn.No,
        )
        if reply == StdBtn.Yes:
            _, msg = self.sistem.musteri_sil(m_id)
            QMessageBox.information(self, "Bilgi", msg)
            trigger_global_refresh(self)

class IslemPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        icerik = QWidget()
        icerik.setStyleSheet(f"background: {C['bg']};")
        lay = QVBoxLayout(icerik)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)
        
        title = QLabel("⚙️ İşlemler")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)
        
        # SATIŞ KARTI
        satis_frame = QFrame()
        satis_frame.setStyleSheet(card_ss())
        satis_lay = QVBoxLayout(satis_frame)
        satis_lay.addWidget(make_label("💰 Satış Kaydı", f"color: #FFFFFF; font-weight: bold; font-size: 16px;"))

        form_lay = QFormLayout()
        self.s_id = QSpinBox()
        self.s_id.setRange(1, 9999)
        self.s_id.setStyleSheet(input_ss())
        form_lay.addRow(make_label("Müşteri ID:", f"color: #FFFFFF; font-size: 14px;"), self.s_id)

        self.s_urun = QLineEdit()
        self.s_urun.setPlaceholderText("Ürün/Hizmet adı")
        self.s_urun.setStyleSheet(input_ss())
        form_lay.addRow(make_label("Ürün:", f"color: #FFFFFF; font-size: 14px;"), self.s_urun)

        self.s_fiyat = QDoubleSpinBox()
        self.s_fiyat.setRange(0.01, 999999999)
        self.s_fiyat.setStyleSheet(input_ss())
        form_lay.addRow(make_label("Fiyat (₺):", f"color: #FFFFFF; font-size: 14px;"), self.s_fiyat)

        self.s_kat = QComboBox()
        self.s_kat.addItems([k.value for k in SatisKategorisi])
        self.s_kat.setStyleSheet(input_ss())
        form_lay.addRow(make_label("Kategori:", f"color: #FFFFFF; font-size: 14px;"), self.s_kat)

        satis_lay.addLayout(form_lay)

        self.sadakat_lbl = QLabel("Müşteri ID girin: sadakat seviyesi ve sepet indirimi burada görünür.")
        self.sadakat_lbl.setStyleSheet(
            f"color: {C['text_dim']}; background: {C['sidebar']}; border: 1px solid {C['border']}; "
            f"border-radius: 6px; padding: 10px; font-size: 13px; font-weight: 600;")
        self.sadakat_lbl.setWordWrap(True)
        satis_lay.addWidget(self.sadakat_lbl)

        self.s_id.valueChanged.connect(self._sadakat_onizleme)
        self.s_fiyat.valueChanged.connect(self._sadakat_onizleme)

        btn = QPushButton("✓ Satışı Kaydet")
        btn.setStyleSheet(btn_primary_ss())
        btn.clicked.connect(self._satis)
        satis_lay.addWidget(btn)
        lay.addWidget(satis_frame)
        
        # TALEP KARTI
        talep_frame = QFrame()
        talep_frame.setStyleSheet(card_ss())
        talep_lay = QVBoxLayout(talep_frame)
        talep_lay.addWidget(make_label("📋 Destek Talebi", f"color: #FFFFFF; font-weight: bold; font-size: 16px;"))
        
        form_lay2 = QFormLayout()
        self.t_id = QSpinBox()
        self.t_id.setRange(1, 9999)
        self.t_id.setStyleSheet(input_ss())
        form_lay2.addRow(make_label("Müşteri ID:", f"color: #FFFFFF; font-size: 14px;"), self.t_id)
        
        self.t_acik = QLineEdit()
        self.t_acik.setPlaceholderText("Sorun veya talep açıklaması")
        self.t_acik.setStyleSheet(input_ss())
        form_lay2.addRow(make_label("Açıklama:", f"color: #FFFFFF; font-size: 14px;"), self.t_acik)
        
        talep_lay.addLayout(form_lay2)
        btn2 = QPushButton("✓ Talebi Oluştur")
        btn2.setStyleSheet(btn_primary_ss())
        btn2.clicked.connect(self._talep)
        talep_lay.addWidget(btn2)
        lay.addWidget(talep_frame)
        
        lay.addStretch()
        scroll.setWidget(icerik)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.addWidget(scroll)
    
    def _sadakat_onizleme(self) -> None:
        m_id = self.s_id.value()
        m = self.sistem.musteriler.get(m_id)
        if not m:
            self.sadakat_lbl.setText(f"⚠ {m_id} ID'li müşteri bulunamadı.")
            self.sadakat_lbl.setStyleSheet(
                f"color: {C['warning']}; background: {C['sidebar']}; border: 1px solid {C['border']}; "
                f"border-radius: 6px; padding: 10px; font-size: 13px; font-weight: 600;")
            return

        sepet = self.s_fiyat.value()
        odenecek = m.indirimli_fiyat_hesapla(sepet)
        indirim = sepet - odenecek
        kazanilacak = int(odenecek * 0.10)
        kalan = m.sonraki_seviyeye_kalan()
        kalan_metni = f" • Sonraki seviyeye {kalan:,} puan" if kalan > 0 else " • En üst seviyede"

        metin = (
            f"{m.seviye.rozet} {m.ad} — {m.seviye.ad} ({m.puan:,} puan){kalan_metni}\n"
            f"Sepet: ₺{sepet:,.2f}  •  İndirim: −₺{indirim:,.2f} (%{m.indirim_orani_al()*100:.0f})  "
            f"•  Ödenecek: ₺{odenecek:,.2f}  •  Kazanılacak: +{kazanilacak} puan"
        )
        self.sadakat_lbl.setText(metin)
        self.sadakat_lbl.setStyleSheet(
            f"color: {C['text']}; background: {C['sidebar']}; border: 1px solid {C['accent']}; "
            f"border-radius: 6px; padding: 10px; font-size: 13px; font-weight: 600;")

    def _satis(self) -> None:
        if not self.s_urun.text().strip():
            QMessageBox.warning(self, "Uyarı", "Ürün adı gerekli!")
            return

        kat_text = self.s_kat.currentText()
        kategori = next((k for k in SatisKategorisi if k.value == kat_text), SatisKategorisi.URUN_SATISI)
        ok, msg = self.sistem.satis_yap(
            self.s_id.value(),
            self.s_urun.text(),
            self.s_fiyat.value(),
            kategori,
        )

        if ok:
            self.s_urun.clear()
            self.s_fiyat.setValue(0.01)
            self._sadakat_onizleme()
            QMessageBox.information(self, "✓ Başarılı", msg)
            trigger_global_refresh(self)
        else:
            QMessageBox.critical(self, "✗ Hata", msg)
    
    def _talep(self) -> None:
        if not self.t_acik.text().strip():
            QMessageBox.warning(self, "Uyarı", "Açıklama gerekli!")
            return
        
        ok, msg = self.sistem.destek_talebi_olustur(self.t_id.value(), self.t_acik.text())
        if ok:
            self.t_acik.clear()
            QMessageBox.information(self, "✓ Başarılı", msg)
            trigger_global_refresh(self)
        else:
            QMessageBox.critical(self, "✗ Hata", msg)

class TaleplerPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(15)

        title = QLabel("📋 Destek Talepleri")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)

        ust_lay = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Müşteri Adı veya ID ara...")
        self.search.setMaximumWidth(360)
        self.search.setStyleSheet(input_ss())
        self.search.textChanged.connect(self.refresh)

        self.durum_filter = QComboBox()
        self.durum_filter.addItem("Tüm Durumlar", userData=None)
        for d in TalepDurumu:
            self.durum_filter.addItem(d.value, userData=d)
        self.durum_filter.setStyleSheet(input_ss())
        self.durum_filter.setMaximumWidth(220)
        self.durum_filter.currentIndexChanged.connect(self.refresh)

        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setStyleSheet(btn_primary_ss())
        btn_refresh.clicked.connect(self.refresh)

        ust_lay.addWidget(self.search)
        ust_lay.addWidget(self.durum_filter)
        ust_lay.addStretch()
        ust_lay.addWidget(btn_refresh)
        lay.addLayout(ust_lay)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(6)
        self.tbl.setHorizontalHeaderLabels(
            ["Tarih", "Müşteri", "Açıklama", "Durum", "Operatör", "İşlem"])
        optimize_columns(self.tbl, [1, 2])
        self.tbl.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; border: none; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        lay.addWidget(self.tbl)

        self.refresh()

    def refresh(self) -> None:
        tum_talepler = []
        for m in self.sistem.musteriler.values():
            for t in m.talepler:
                tum_talepler.append((m, t))
        
        tum_talepler.sort(key=lambda x: x[1].olusturma_tarihi, reverse=True)

        arama = self.search.text().strip().lower()
        durum_secili = self.durum_filter.currentData()

        self.tbl.setRowCount(0)
        for m, t in tum_talepler:
            if durum_secili is not None and t.durum != durum_secili:
                continue
            if arama and (arama not in m.ad.lower() and arama not in str(m.musteri_id)):
                continue

            r = self.tbl.rowCount()
            self.tbl.insertRow(r)

            op = self.sistem.operatorler.get(t.operator_id) if t.operator_id else None
            op_ad = op.ad_soyad if op else "—"
            
            satirlar = [
                t.olusturma_tarihi.strftime("%d/%m/%Y %H:%M"),
                f"#{m.musteri_id} {m.ad}",
                t.aciklama[:40] + ("..." if len(t.aciklama) > 40 else ""),
                t.get_status_badge(),
                op_ad
            ]
            
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl.setItem(r, col, item)

            btn_frame = QFrame()
            btn_frame.setStyleSheet("background: transparent;")
            btn_h = QHBoxLayout(btn_frame)
            btn_h.setContentsMargins(0, 0, 0, 0)

            btn_edit = QPushButton("Güncelle")
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            renk = C['accent'] if t.durum != TalepDurumu.KAPALI else C['border']
            btn_edit.setStyleSheet(
                f"QPushButton {{ background: {renk}; color: white; border: none; border-radius: 4px; padding: 4px 10px; font-weight: bold; }}")
            btn_edit.clicked.connect(
                lambda checked, t_obj=t, m_id=m.musteri_id, m_ad=m.ad: self._durum_degistir(t_obj, m_id, m_ad))
            btn_h.addWidget(btn_edit)

            self.tbl.setCellWidget(r, 5, btn_frame)

    def _durum_degistir(self, talep, m_id: int, m_ad: str) -> None:
        dialog = TalepGuncelleDialog(self, talep, m_ad)
        if dialog.exec():
            yeni_durum = dialog.durum_combo.currentData()
            if yeni_durum != talep.durum:
                ok, msg = self.sistem.talep_durumu_degistir(talep.talep_id, m_id, yeni_durum)
                if ok:
                    QMessageBox.information(self, "✓ Başarılı", msg)
                    trigger_global_refresh(self)
                else:
                    QMessageBox.critical(self, "✗ Hata", msg)

class SatislarPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(15)

        title = QLabel("💰 Satış Kayıtları")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)

        stat_lay = QHBoxLayout()
        self.stat_adet = StatCard("Toplam Satış", 0)
        self.stat_ciro = StatCard("Toplam Ciro", "₺0", C['success'])
        self.stat_ort = StatCard("Ort. Sepet", "₺0", C['warning'])
        stat_lay.addWidget(self.stat_adet)
        stat_lay.addWidget(self.stat_ciro)
        stat_lay.addWidget(self.stat_ort)
        lay.addLayout(stat_lay)

        ust_lay = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Müşteri, ürün veya kategori ara...")
        self.search.setMaximumWidth(360)
        self.search.setStyleSheet(input_ss())
        self.search.textChanged.connect(self.refresh)

        self.kat_filter = QComboBox()
        self.kat_filter.addItem("Tüm kategoriler")
        for k in SatisKategorisi:
            self.kat_filter.addItem(k.value)
        self.kat_filter.setStyleSheet(input_ss())
        self.kat_filter.setMaximumWidth(220)
        self.kat_filter.currentIndexChanged.connect(self.refresh)

        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.setStyleSheet(btn_primary_ss())
        btn_refresh.clicked.connect(self.refresh)

        ust_lay.addWidget(self.search)
        ust_lay.addWidget(self.kat_filter)
        ust_lay.addStretch()
        ust_lay.addWidget(btn_refresh)
        lay.addLayout(ust_lay)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(8)
        self.tbl.setHorizontalHeaderLabels(
            ["Tarih", "Müşteri", "Ürün / Hizmet", "Kategori", "Tutar (₺)", "Operatör", "Notlar", "İşlem"])
        optimize_columns(self.tbl, [1, 2, 6])
        self.tbl.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        lay.addWidget(self.tbl)

        self.refresh()

    def refresh(self) -> None:
        kayitlar = self.sistem.get_tum_satislar()
        arama = self.search.text().strip().lower()
        kat_text = self.kat_filter.currentText()
        kat_secili = (
            None if self.kat_filter.currentIndex() == 0
            else next((k for k in SatisKategorisi if k.value == kat_text), None)
        )

        aktif_op = self.sistem.get_aktif_operator()
        is_admin = aktif_op and aktif_op.rol == OperatorRol.ADMIN

        gosterilenler: list[tuple[Musteri, Satis]] = []
        for m, s in kayitlar:
            if kat_secili is not None and s.kategori != kat_secili:
                continue
            if arama:
                havuz = f"{m.ad} {s.urun} {s.kategori.value}".lower()
                if arama not in havuz:
                    continue
            gosterilenler.append((m, s))

        adet = len(gosterilenler)
        ciro = sum(s.fiyat for _, s in gosterilenler)
        ort = ciro / adet if adet else 0.0
        self.stat_adet.lbl_val.setText(f"{adet}")
        self.stat_ciro.lbl_val.setText(f"₺{ciro:,.0f}")
        self.stat_ort.lbl_val.setText(f"₺{ort:,.0f}")

        self.tbl.setRowCount(0)
        for m, s in gosterilenler:
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)

            op = self.sistem.operatorler.get(s.operator_id) if s.operator_id is not None else None
            op_ad = op.ad_soyad if op else "—"
            satirlar = [
                s.tarih.strftime("%d/%m/%Y %H:%M"),
                f"#{m.musteri_id} {m.ad}",
                s.urun,
                s.kategori.value,
                f"{s.fiyat:,.2f}",
                op_ad,
                s.notlar or "—",
            ]
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl.setItem(r, col, item)

            btn_frame = QFrame()
            btn_frame.setStyleSheet("background: transparent;")
            btn_h = QHBoxLayout(btn_frame)
            btn_h.setContentsMargins(0, 0, 0, 0)

            if is_admin:
                btn_del = QPushButton("🗑️")
                btn_del.setMaximumWidth(40)
                btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_del.setToolTip("Satışı sil")
                btn_del.setStyleSheet(
                    f"QPushButton {{ background: {C['danger']}; color: white; border: none; border-radius: 4px; }}")
                btn_del.clicked.connect(
                    lambda checked, sid=s.satis_id, mid=m.musteri_id: self._delete(sid, mid))
                btn_h.addWidget(btn_del)

            self.tbl.setCellWidget(r, 7, btn_frame)

    def _delete(self, satis_id: int, m_id: int) -> None:
        aktif_op = self.sistem.get_aktif_operator()
        if not aktif_op or aktif_op.rol != OperatorRol.ADMIN:
            QMessageBox.warning(self, "Yetki Hatası", "Satış kaydı silme işlemi için Yönetici yetkisi gereklidir.")
            return

        StdBtn = QMessageBox.StandardButton
        reply = QMessageBox.question(
            self, "Onay", f"#{satis_id} satış kaydı silinecektir.",
            StdBtn.Yes | StdBtn.No,
        )
        if reply != StdBtn.Yes:
            return
        ok, msg = self.sistem.satis_sil(satis_id, m_id)
        if ok:
            QMessageBox.information(self, "✓ Başarılı", msg)
            trigger_global_refresh(self)
        else:
            QMessageBox.critical(self, "✗ Hata", msg)


class RaporlarPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)
        
        title = QLabel("📈 Raporlar & Analiz")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)
        
        top_frame = QFrame()
        top_frame.setStyleSheet(card_ss())
        top_lay = QVBoxLayout(top_frame)
        top_lay.addWidget(make_label("🏆 Top 10 Müşteri", f"color: #FFFFFF; font-weight: bold; font-size: 18px;"))
        
        self.tbl_top = QTableWidget()
        self.tbl_top.setColumnCount(4)
        self.tbl_top.setHorizontalHeaderLabels(["Rank", "Müşteri", "Toplam Satış", "İşlem"])
        self.tbl_top.setMaximumHeight(300)
        optimize_columns(self.tbl_top, [1])
        self.tbl_top.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        top_lay.addWidget(self.tbl_top)
        lay.addWidget(top_frame)
        
        sehir_frame = QFrame()
        sehir_frame.setStyleSheet(card_ss())
        sehir_lay = QVBoxLayout(sehir_frame)
        sehir_lay.addWidget(make_label("🌍 Şehir Bazlı Dağılım", f"color: #FFFFFF; font-weight: bold; font-size: 18px;"))
        
        self.tbl_sehir = QTableWidget()
        self.tbl_sehir.setColumnCount(2)
        self.tbl_sehir.setHorizontalHeaderLabels(["Şehir", "Müşteri Sayısı"])
        self.tbl_sehir.setMaximumHeight(250)
        optimize_columns(self.tbl_sehir, [0])
        self.tbl_sehir.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        sehir_lay.addWidget(self.tbl_sehir)
        lay.addWidget(sehir_frame)
        
        lay.addStretch()
        self.refresh()
    
    def refresh(self) -> None:
        self.tbl_top.setRowCount(0)
        for idx, m in enumerate(self.sistem.musteri_raporlari(), 1):
            r = self.tbl_top.rowCount()
            self.tbl_top.insertRow(r)
            
            items_data = [f"#{idx}", m.ad, f"₺{m.toplam_harcama():,.0f}", f"📊 {m.satis_sayisi()}"]
            for col, text in enumerate(items_data):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl_top.setItem(r, col, item)
        
        self.tbl_sehir.setRowCount(0)
        for sehir, sayi in sorted(self.sistem.sehir_bazli_istatistik().items(), key=lambda x: x[1], reverse=True):
            r = self.tbl_sehir.rowCount()
            self.tbl_sehir.insertRow(r)
            
            item1 = QTableWidgetItem(sehir)
            item1.setForeground(QColor("#FFFFFF"))
            item1.setFont(QFont("Segoe UI", 13))
            self.tbl_sehir.setItem(r, 0, item1)
            
            item2 = QTableWidgetItem(str(sayi))
            item2.setForeground(QColor("#FFFFFF"))
            item2.setFont(QFont("Segoe UI", 13))
            self.tbl_sehir.setItem(r, 1, item2)

class SadakatPage(QWidget):
    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        icerik = QWidget()
        icerik.setStyleSheet(f"background: {C['bg']};")
        lay = QVBoxLayout(icerik)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        title = QLabel("🎁 Ödül & Sadakat Programı")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)

        metrik_lay = QHBoxLayout()
        self.stat_toplam_puan = StatCard("Toplam Puan", "0", C['accent'])
        self.stat_ort_puan = StatCard("Ort. Puan / Müşteri", "0", C['warning'])
        self.stat_tasarruf = StatCard("Toplam İndirim", "₺0", C['success'])
        metrik_lay.addWidget(self.stat_toplam_puan)
        metrik_lay.addWidget(self.stat_ort_puan)
        metrik_lay.addWidget(self.stat_tasarruf)
        lay.addLayout(metrik_lay)

        sev_frame = QFrame()
        sev_frame.setStyleSheet(card_ss())
        sev_lay = QVBoxLayout(sev_frame)
        sev_baslik = QLabel("📊 Seviye Dağılımı & Kurallar")
        sev_baslik.setStyleSheet(f"color: #FFFFFF; font-weight: bold; font-size: 18px;")
        sev_lay.addWidget(sev_baslik)

        self.tbl_sev = QTableWidget()
        self.tbl_sev.setColumnCount(5)
        self.tbl_sev.setHorizontalHeaderLabels(
            ["Seviye", "Eşik (Puan)", "Sepet İndirimi", "Müşteri Sayısı", "Toplam İndirim"])
        optimize_columns(self.tbl_sev, [0])
        self.tbl_sev.setMaximumHeight(220)
        self.tbl_sev.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        sev_lay.addWidget(self.tbl_sev)
        lay.addWidget(sev_frame)

        top_frame = QFrame()
        top_frame.setStyleSheet(card_ss())
        top_lay = QVBoxLayout(top_frame)
        top_baslik = QLabel("🏆 En Yüksek Puanlı Müşteriler")
        top_baslik.setStyleSheet(f"color: #FFFFFF; font-weight: bold; font-size: 18px;")
        top_lay.addWidget(top_baslik)

        self.tbl_top = QTableWidget()
        self.tbl_top.setColumnCount(5)
        self.tbl_top.setHorizontalHeaderLabels(
            ["Müşteri", "Seviye", "Puan", "Sepet İndirimi", "Sonraki Seviyeye"])
        optimize_columns(self.tbl_top, [0, 1])
        self.tbl_top.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        top_lay.addWidget(self.tbl_top)
        lay.addWidget(top_frame)

        lay.addStretch()
        scroll.setWidget(icerik)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.addWidget(scroll)

        self.refresh()

    def refresh(self) -> None:
        sad = self.sistem.sadakat_istatistikleri()
        ind = self.sistem.indirim_analizi()
        toplam_puan = int(sad['toplam_puan'])
        ortalama_puan = float(sad['ortalama_puan'])
        toplam_tasarruf = float(ind['toplam_tasarruf'])
        seviye_dagitimi: dict[str, int] = sad['seviye_dagitimi']  # type: ignore[assignment]
        seviye_tasarruflari: dict[str, float] = ind['seviye_tasarruflari']  # type: ignore[assignment]

        self.stat_toplam_puan.lbl_val.setText(f"{toplam_puan:,}")
        self.stat_ort_puan.lbl_val.setText(f"{ortalama_puan:,.0f}")
        self.stat_tasarruf.lbl_val.setText(f"₺{toplam_tasarruf:,.0f}")

        self.tbl_sev.setRowCount(0)
        for seviye in SadakatSeviyesi:
            r = self.tbl_sev.rowCount()
            self.tbl_sev.insertRow(r)
            satirlar = [
                f"{seviye.rozet} {seviye.ad}",
                f"{seviye.esik:,}+",
                f"%{seviye.indirim_orani*100:.0f}",
                str(seviye_dagitimi.get(seviye.name, 0)),
                f"₺{seviye_tasarruflari.get(seviye.name, 0):,.0f}",
            ]
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl_sev.setItem(r, col, item)

        self.tbl_top.setRowCount(0)
        siralanmis = sorted(self.sistem.musteriler.values(), key=lambda x: x.puan, reverse=True)[:10]
        for m in siralanmis:
            r = self.tbl_top.rowCount()
            self.tbl_top.insertRow(r)
            kalan = m.sonraki_seviyeye_kalan()
            kalan_metni = f"{kalan:,} puan" if kalan > 0 else "—"
            satirlar = [
                m.ad,
                f"{m.seviye.rozet} {m.seviye.ad}",
                f"{m.puan:,}",
                f"%{m.indirim_orani_al()*100:.0f}",
                kalan_metni,
            ]
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl_top.setItem(r, col, item)

class LoginDialog(QDialog):
    def __init__(self, sistem: CRMSistemi, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.sistem = sistem
        self.dogrulanan: Operator | None = None

        self.setWindowTitle("ProCRM — Giriş")
        self.setFixedSize(440, 360)
        self.setStyleSheet(f"QDialog {{ background: {C['card']}; }}")
        self.setModal(True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 28, 36, 28)
        lay.setSpacing(12)

        baslik = QLabel("⚡ ProCRM Girişi")
        baslik.setStyleSheet(f"color: {C['accent']}; font-size: 24px; font-weight: 900;")
        lay.addWidget(baslik)

        bilgi = QLabel("Kullanıcı adınız ve parolanızla oturum açın.")
        bilgi.setStyleSheet(f"color: {C['text_dim']}; font-size: 12px;")
        lay.addWidget(bilgi)

        form_ss = "color: #FFFFFF; font-size: 13px; font-weight: 700;"
        lay.addWidget(make_label("Kullanıcı Adı", form_ss))
        self.kadi_inp = self._mk_input("admin", password=False)
        lay.addWidget(self.kadi_inp)

        lay.addWidget(make_label("Parola", form_ss))
        self.parola_inp = self._mk_input("", password=True)
        self.parola_inp.returnPressed.connect(self._giris_dene)
        lay.addWidget(self.parola_inp)

        self.hata_lbl = QLabel("")
        self.hata_lbl.setStyleSheet(f"color: {C['danger']}; font-size: 12px; font-weight: 700;")
        lay.addWidget(self.hata_lbl)

        btn_lay = QHBoxLayout()
        btn_giris = self._mk_button("→ Giriş Yap", primary=True)
        btn_giris.clicked.connect(self._giris_dene)
        btn_iptal = self._mk_button("✕ İptal", primary=False)
        btn_iptal.clicked.connect(self.reject)
        btn_lay.addWidget(btn_giris)
        btn_lay.addWidget(btn_iptal)
        lay.addLayout(btn_lay)

        ipucu = QLabel("İlk kurulumda varsayılan: admin / admin")
        ipucu.setStyleSheet(f"color: {C['text_dim']}; font-size: 10px; padding-top: 6px;")
        lay.addWidget(ipucu)

    def _mk_input(self, placeholder: str, password: bool) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setMinimumHeight(40)
        inp.setStyleSheet(
            f"QLineEdit {{ border: 1px solid {C['border']}; border-radius: 6px; padding: 8px; }} "
            f"QLineEdit:focus {{ border: 2px solid {C['accent']}; }}"
        )
        f = inp.font()
        f.setPointSize(11)
        f.setBold(True)
        inp.setFont(f)
        pal = inp.palette()
        pal.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(C['text_dim']))
        pal.setColor(QPalette.ColorRole.Base, QColor(C['sidebar']))
        pal.setColor(QPalette.ColorRole.Window, QColor(C['sidebar']))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(C['accent']))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        inp.setPalette(pal)
        inp.setAutoFillBackground(True)
        return inp

    def _mk_button(self, metin: str, primary: bool) -> QPushButton:
        btn = QPushButton(metin)
        btn.setMinimumHeight(44)
        if primary:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {C['accent']}; "
                f" border: none; border-radius: 8px; padding: 10px; }} "
                f"QPushButton:hover {{ background-color: {C['accent_dark']}; }}"
            )
        else:
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {C['card']}; "
                f" border: 1px solid {C['border']}; border-radius: 8px; padding: 10px; }} "
                f"QPushButton:hover {{ border-color: {C['accent']}; }}"
            )
        f = btn.font()
        f.setPointSize(11)
        f.setBold(True)
        btn.setFont(f)
        pal = btn.palette()
        pal.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
        pal.setColor(QPalette.ColorRole.Button,
                     QColor(C['accent'] if primary else C['card']))
        btn.setPalette(pal)
        return btn

    def _giris_dene(self) -> None:
        op = self.sistem.operator_dogrula(self.kadi_inp.text().strip(), self.parola_inp.text())
        if op is None:
            self.hata_lbl.setText("✗ Kullanıcı adı veya parola hatalı.")
            self.parola_inp.clear()
            self.parola_inp.setFocus()
            return
        self.dogrulanan = op
        self.sistem.aktif_operator_ata(op.operator_id)
        self.accept()

class OperatorDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, op: Operator | None = None) -> None:
        super().__init__(parent)
        self.op = op
        self.setWindowTitle("Operatör Bilgisi" if op else "Yeni Operatör")
        self.setGeometry(100, 100, 460, 280)
        self.setStyleSheet(f"QDialog {{ background: {C['card']}; }}")

        lay = QFormLayout(self)
        lay.setSpacing(12)
        form_ss = "color: #FFFFFF; font-size: 14px;"

        self.kadi_inp = QLineEdit()
        self.kadi_inp.setPlaceholderText("kullanici_adi")
        self.kadi_inp.setStyleSheet(input_ss())
        if op:
            self.kadi_inp.setText(op.kullanici_adi)
            self.kadi_inp.setEnabled(False)

        self.ad_inp = QLineEdit()
        self.ad_inp.setPlaceholderText("Ad Soyad")
        self.ad_inp.setStyleSheet(input_ss())
        if op:
            self.ad_inp.setText(op.ad_soyad)

        self.rol_combo = QComboBox()
        for r in OperatorRol:
            self.rol_combo.addItem(r.value)
        self.rol_combo.setStyleSheet(input_ss())
        if op:
            self.rol_combo.setCurrentText(op.rol.value)

        self.parola_inp = QLineEdit()
        self.parola_inp.setEchoMode(QLineEdit.EchoMode.Password)
        self.parola_inp.setStyleSheet(input_ss())
        if op:
            self.parola_inp.setPlaceholderText("Boş bırakırsanız değişmez")
            parola_etiketi = "Yeni Parola:"
        else:
            self.parola_inp.setPlaceholderText("En az 4 karakter")
            parola_etiketi = "Parola:"

        lay.addRow(make_label("Kullanıcı Adı:", form_ss), self.kadi_inp)
        lay.addRow(make_label("Ad Soyad:", form_ss), self.ad_inp)
        lay.addRow(make_label("Rol:", form_ss), self.rol_combo)
        lay.addRow(make_label(parola_etiketi, form_ss), self.parola_inp)

        btn_lay = QHBoxLayout()
        btn_save = QPushButton("✓ Kaydet")
        btn_save.setStyleSheet(btn_primary_ss())
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("✕ İptal")
        btn_cancel.setStyleSheet(
            f"QPushButton{{ background-color: {C['card']}; color: {C['text']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; padding: 10px; }}")
        btn_cancel.clicked.connect(self.reject)
        btn_lay.addWidget(btn_save)
        btn_lay.addWidget(btn_cancel)
        lay.addRow(btn_lay)

class YoneticiPage(QWidget):
    ISLEM_ETIKETLERI = {
        "MUSTERI_EKLE":      "Müşteri Eklendi",
        "MUSTERI_GUNCELLE":  "Müşteri Güncellendi",
        "MUSTERI_SIL":       "Müşteri Silindi",
        "SATIS":             "Satış",
        "SATIS_SIL":         "Satış Silindi",
        "TALEP_OLUSTUR":     "Talep Açıldı",
        "TALEP_DURUMU":      "Talep Durumu",
        "OPERATOR_EKLE":     "Operatör Eklendi",
        "OPERATOR_GUNCELLE": "Operatör Güncellendi",
        "OPERATOR_SIL":      "Operatör Silindi",
    }

    def __init__(self, sistem: CRMSistemi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setStyleSheet(f"background: {C['bg']};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        icerik = QWidget()
        icerik.setStyleSheet(f"background: {C['bg']};")
        lay = QVBoxLayout(icerik)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        title = QLabel("👤 Yönetici Paneli")
        title.setStyleSheet(f"color: #FFFFFF; font-size: 32px; font-weight: 900;")
        lay.addWidget(title)

        op_frame = QFrame()
        op_frame.setStyleSheet(card_ss())
        op_lay = QVBoxLayout(op_frame)
        op_lay.addWidget(make_label("👥 Operatörler", "color: #FFFFFF; font-weight: bold; font-size: 18px;"))

        ust = QHBoxLayout()
        btn_yeni = QPushButton("➕ Yeni Operatör")
        btn_yeni.setStyleSheet(btn_primary_ss())
        btn_yeni.clicked.connect(self._yeni_operator)
        ust.addWidget(btn_yeni)
        ust.addStretch()
        op_lay.addLayout(ust)

        self.tbl_op = QTableWidget()
        self.tbl_op.setColumnCount(6)
        self.tbl_op.setHorizontalHeaderLabels(
            ["ID", "Kullanıcı Adı", "Ad Soyad", "Rol", "Durum", "İşlem"])
        optimize_columns(self.tbl_op, [1, 2])
        self.tbl_op.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        op_lay.addWidget(self.tbl_op)
        lay.addWidget(op_frame)

        log_frame = QFrame()
        log_frame.setStyleSheet(card_ss())
        log_lay = QVBoxLayout(log_frame)
        log_lay.addWidget(make_label("📜 İşlem Geçmişi", "color: #FFFFFF; font-weight: bold; font-size: 18px;"))

        filtre = QHBoxLayout()
        self.op_filter = QComboBox()
        self.op_filter.setStyleSheet(input_ss())
        self.op_filter.setMaximumWidth(260)
        self.op_filter.currentIndexChanged.connect(self.refresh_log)

        self.tip_filter = QComboBox()
        self.tip_filter.addItem("Tüm işlemler")
        for tip, etiket in self.ISLEM_ETIKETLERI.items():
            self.tip_filter.addItem(etiket, userData=tip)
        self.tip_filter.setStyleSheet(input_ss())
        self.tip_filter.setMaximumWidth(260)
        self.tip_filter.currentIndexChanged.connect(self.refresh_log)

        btn_yenile = QPushButton("🔄 Yenile")
        btn_yenile.setStyleSheet(btn_primary_ss())
        btn_yenile.clicked.connect(self.refresh)

        filtre.addWidget(self.op_filter)
        filtre.addWidget(self.tip_filter)
        filtre.addStretch()
        filtre.addWidget(btn_yenile)
        log_lay.addLayout(filtre)

        self.tbl_log = QTableWidget()
        self.tbl_log.setColumnCount(5)
        self.tbl_log.setHorizontalHeaderLabels(
            ["Tarih", "Operatör", "İşlem", "Hedef", "Detay"])
        optimize_columns(self.tbl_log, [3, 4])
        self.tbl_log.setStyleSheet(f"""QTableWidget {{ background: {C['bg']}; gridline-color: {C['border']}; }}
            QHeaderView::section {{ background: {C['card']}; color: #FFFFFF; padding: 8px; font-size: 14px; font-weight: bold; }}
            QTableWidgetItem {{ padding: 8px; color: #FFFFFF; }}""")
        log_lay.addWidget(self.tbl_log)
        lay.addWidget(log_frame)

        lay.addStretch()
        scroll.setWidget(icerik)
        ana = QVBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.addWidget(scroll)

        self.refresh()

    def refresh(self) -> None:
        self._refresh_op_filter()
        self._refresh_op_tablo()
        self.refresh_log()

    def _refresh_op_filter(self) -> None:
        prev = self.op_filter.currentData()
        self.op_filter.blockSignals(True)
        self.op_filter.clear()
        self.op_filter.addItem("Tüm operatörler", userData=None)
        for op in self.sistem.operatorler.values():
            etiket = f"{op.ad_soyad} ({op.kullanici_adi})"
            if not op.aktif:
                etiket += " [pasif]"
            self.op_filter.addItem(etiket, userData=op.operator_id)
        if prev is not None:
            for i in range(self.op_filter.count()):
                if self.op_filter.itemData(i) == prev:
                    self.op_filter.setCurrentIndex(i)
                    break
        self.op_filter.blockSignals(False)

    def _refresh_op_tablo(self) -> None:
        self.tbl_op.setRowCount(0)
        aktif_id = self.sistem.aktif_operator_id
        for op in self.sistem.operatorler.values():
            r = self.tbl_op.rowCount()
            self.tbl_op.insertRow(r)
            durum = "🟢 Aktif" if op.aktif else "⚪ Pasif"
            if op.operator_id == aktif_id:
                durum += " (Şu an)"
            satirlar = [
                str(op.operator_id), op.kullanici_adi, op.ad_soyad,
                op.rol.value, durum,
            ]
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl_op.setItem(r, col, item)

            btn_frame = QFrame()
            btn_frame.setStyleSheet("background: transparent;")
            btn_h = QHBoxLayout(btn_frame)
            btn_h.setContentsMargins(0, 0, 0, 0)
            btn_h.setSpacing(4)

            btn_edit = QPushButton("✏️")
            btn_edit.setMaximumWidth(36)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.setToolTip("Düzenle")
            btn_edit.setStyleSheet(
                f"QPushButton {{ background: {C['accent']}; color: white; border: none; border-radius: 4px; }}")
            btn_edit.clicked.connect(lambda checked, oid=op.operator_id: self._edit_op(oid))

            btn_del = QPushButton("🗑️")
            btn_del.setMaximumWidth(36)
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.setToolTip("Pasifleştir")
            btn_del.setStyleSheet(
                f"QPushButton {{ background: {C['danger']}; color: white; border: none; border-radius: 4px; }}")
            btn_del.clicked.connect(lambda checked, oid=op.operator_id: self._sil_op(oid))

            btn_h.addWidget(btn_edit)
            btn_h.addWidget(btn_del)
            self.tbl_op.setCellWidget(r, 5, btn_frame)

    def refresh_log(self) -> None:
        op_id = self.op_filter.currentData()
        tip = self.tip_filter.currentData() if self.tip_filter.currentIndex() > 0 else None
        loglar = self.sistem.get_islem_gecmisi(op_id=op_id, islem_tipi=tip, limit=300)

        self.tbl_log.setRowCount(0)
        for log in loglar:
            r = self.tbl_log.rowCount()
            self.tbl_log.insertRow(r)
            log_op_id = log['operator_id']
            op = self.sistem.operatorler.get(log_op_id) if isinstance(log_op_id, int) else None
            op_ad = op.ad_soyad if op else "—"
            tarih_str = str(log['tarih'])[:19].replace("T", " ")
            tip_etiket = self.ISLEM_ETIKETLERI.get(str(log['tip']), str(log['tip']))
            satirlar = [tarih_str, op_ad, tip_etiket, str(log['hedef']), str(log['detay'])]
            for col, text in enumerate(satirlar):
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#FFFFFF"))
                item.setFont(QFont("Segoe UI", 13))
                self.tbl_log.setItem(r, col, item)

    def _yeni_operator(self) -> None:
        dialog = OperatorDialog(self)
        if dialog.exec():
            rol_text = dialog.rol_combo.currentText()
            rol = next((r for r in OperatorRol if r.value == rol_text), OperatorRol.SATICI)
            ok, msg = self.sistem.operator_ekle(
                dialog.kadi_inp.text(), dialog.ad_inp.text(),
                dialog.parola_inp.text(), rol)
            if ok:
                QMessageBox.information(self, "✓ Başarılı", msg)
                trigger_global_refresh(self)
            else:
                QMessageBox.critical(self, "✗ Hata", msg)

    def _edit_op(self, op_id: int) -> None:
        op = self.sistem.operatorler.get(op_id)
        if not op:
            return
        dialog = OperatorDialog(self, op=op)
        if dialog.exec():
            rol_text = dialog.rol_combo.currentText()
            rol = next((r for r in OperatorRol if r.value == rol_text), op.rol)
            ok, msg = self.sistem.operator_guncelle(
                op_id, ad_soyad=dialog.ad_inp.text(), rol=rol)
            yeni_parola = dialog.parola_inp.text()
            if ok and yeni_parola:
                ok2, msg2 = self.sistem.operator_parola_ayarla(op_id, yeni_parola)
                if not ok2:
                    QMessageBox.warning(self, "Parola güncellenmedi", msg2)
                else:
                    msg = msg + " " + msg2
            if ok:
                QMessageBox.information(self, "✓ Başarılı", msg)
                trigger_global_refresh(self)
            else:
                QMessageBox.critical(self, "✗ Hata", msg)

    def _sil_op(self, op_id: int) -> None:
        StdBtn = QMessageBox.StandardButton
        reply = QMessageBox.question(
            self, "Onay", f"Operatör #{op_id} pasifleştirilecek (geçmiş kayıtlar korunur).",
            StdBtn.Yes | StdBtn.No,
        )
        if reply != StdBtn.Yes:
            return
        ok, msg = self.sistem.operator_sil(op_id)
        if ok:
            QMessageBox.information(self, "✓ Başarılı", msg)
            trigger_global_refresh(self)
        else:
            QMessageBox.critical(self, "✗ Hata", msg)

class MainWindow(QMainWindow):
    def __init__(self, sistem: CRMSistemi | None = None) -> None:
        super().__init__()
        self.setWindowTitle("ProCRM Enterprise 2.0")
        self.setGeometry(0, 0, 1700, 950)
        self.setStyleSheet(f"QMainWindow {{ background: {C['bg']}; }}")

        self.sistem = sistem if sistem is not None else CRMSistemi()
        
        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana = QHBoxLayout(merkez)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)
        
        # SIDEBAR
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"background: {C['sidebar']}; border-right: 1px solid {C['border']};")
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 20, 0, 20)
        sb_lay.setSpacing(8)
        
        logo = QLabel("⚡ ProCRM 2.0")
        logo.setStyleSheet(f"color: {C['accent']}; font-size: 22px; font-weight: 900; padding: 0 20px 14px 20px;")
        sb_lay.addWidget(logo)

        op_lbl = QLabel("AKTİF KULLANICI")
        op_lbl.setStyleSheet(f"color: {C['text_dim']}; font-size: 10px; font-weight: bold; "
                             f"letter-spacing: 1px; padding: 0 20px;")
        sb_lay.addWidget(op_lbl)

        self.op_isim_lbl = QLabel("—")
        self.op_isim_lbl.setStyleSheet(
            f"color: {C['text']}; font-size: 14px; font-weight: bold; padding: 4px 20px 0 20px;")
        sb_lay.addWidget(self.op_isim_lbl)

        self.op_rol_lbl = QLabel("")
        self.op_rol_lbl.setStyleSheet(
            f"color: {C['text_dim']}; font-size: 11px; padding: 0 20px 6px 20px;")
        sb_lay.addWidget(self.op_rol_lbl)

        self.btn_logout = QPushButton("⎋  Çıkış / Hesap Değiştir")
        self.btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_logout.setStyleSheet(
            f"QPushButton {{ background: {C['card']}; color: {C['text_dim']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; "
            f"padding: 8px; margin: 4px 16px 18px 16px; font-size: 12px; font-weight: 600; }}"
            f"QPushButton:hover {{ color: {C['text']}; border-color: {C['accent']}; }}")
        self.btn_logout.clicked.connect(self._logout)
        sb_lay.addWidget(self.btn_logout)

        self.btn_dash = NavBtn("📊", "Pano")
        self.btn_musteri = NavBtn("👥", "Müşteriler")
        self.btn_islem = NavBtn("⚙️", "İşlemler")
        self.btn_talep = NavBtn("📋", "Talepler") 
        self.btn_satis = NavBtn("💰", "Satışlar")
        self.btn_rapor = NavBtn("📈", "Raporlar")
        self.btn_sadakat = NavBtn("🎁", "Sadakat")
        self.btn_yonetici = NavBtn("👤", "Yönetici")

        sb_lay.addWidget(self.btn_dash)
        sb_lay.addWidget(self.btn_musteri)
        sb_lay.addWidget(self.btn_islem)
        sb_lay.addWidget(self.btn_talep)
        sb_lay.addWidget(self.btn_satis)
        sb_lay.addWidget(self.btn_rapor)
        sb_lay.addWidget(self.btn_sadakat)
        sb_lay.addWidget(self.btn_yonetici)
        sb_lay.addStretch()
        
        footer = QLabel("v2.0 Modern")
        footer.setStyleSheet(f"color: #FFFFFF; font-size: 11px; text-align: center; padding: 0 20px;")
        sb_lay.addWidget(footer)
        
        ana.addWidget(sidebar)
        
        # SAYFA STACK
        self.stack = QStackedWidget()
        
        self.p_dash = DashboardPage(self.sistem)
        self.p_musteri = MusteriPage(self.sistem)
        self.p_islem = IslemPage(self.sistem)
        self.p_talep = TaleplerPage(self.sistem) 
        self.p_satis = SatislarPage(self.sistem)
        self.p_rapor = RaporlarPage(self.sistem)
        self.p_sadakat = SadakatPage(self.sistem)
        self.p_yonetici = YoneticiPage(self.sistem)

        self.stack.addWidget(self.p_dash)     # 0
        self.stack.addWidget(self.p_musteri)  # 1
        self.stack.addWidget(self.p_islem)    # 2
        self.stack.addWidget(self.p_talep)    # 3
        self.stack.addWidget(self.p_satis)    # 4
        self.stack.addWidget(self.p_rapor)    # 5
        self.stack.addWidget(self.p_sadakat)  # 6
        self.stack.addWidget(self.p_yonetici) # 7

        ana.addWidget(self.stack)

        self.btn_dash.clicked.connect(lambda: self._switch(0))
        self.btn_musteri.clicked.connect(lambda: self._switch(1))
        self.btn_islem.clicked.connect(lambda: self._switch(2))
        self.btn_talep.clicked.connect(lambda: self._switch(3))
        self.btn_satis.clicked.connect(lambda: self._switch(4))
        self.btn_rapor.clicked.connect(lambda: self._switch(5))
        self.btn_sadakat.clicked.connect(lambda: self._switch(6))
        self.btn_yonetici.clicked.connect(lambda: self._switch(7))

        self._load_operatorler()
        self._switch(0)

    def refresh_all(self) -> None:
        """Sistemdeki değişikliklerden sonra tüm sekmelerin yeniden verileri çekmesini sağlar."""
        self.p_dash.refresh()
        self.p_musteri.refresh()
        self.p_talep.refresh()
        self.p_satis.refresh()
        self.p_rapor.refresh()
        self.p_sadakat.refresh()
        self.p_yonetici.refresh()

    def _load_operatorler(self) -> None:
        op = self.sistem.get_aktif_operator()
        if op is None:
            self.op_isim_lbl.setText("—")
            self.op_rol_lbl.setText("")
            self.btn_yonetici.hide()
        else:
            self.op_isim_lbl.setText(op.ad_soyad)
            self.op_rol_lbl.setText(f"{op.rol.value} • @{op.kullanici_adi}")
            
            if op.rol == OperatorRol.ADMIN:
                self.btn_yonetici.show()
            else:
                self.btn_yonetici.hide()

    def _logout(self) -> None:
        self.hide()
        login = LoginDialog(self.sistem, self)
        if login.exec():
            self._load_operatorler()
            self.show()
            
            if self.stack.currentIndex() == 7 and self.sistem.get_aktif_operator().rol != OperatorRol.ADMIN:
                self._switch(0)
            else:
                self._switch(self.stack.currentIndex())
        else:
            QApplication.quit()

    def _switch(self, idx: int) -> None:
        aktif_op = self.sistem.get_aktif_operator()
        if idx == 7 and aktif_op and aktif_op.rol != OperatorRol.ADMIN:
            QMessageBox.warning(self, "Yetkisiz İşlem", "Bu sayfaya sadece yöneticiler erişebilir.")
            return

        self.stack.setCurrentIndex(idx)
        self.btn_dash.setChecked(idx == 0)
        self.btn_musteri.setChecked(idx == 1)
        self.btn_islem.setChecked(idx == 2)
        self.btn_talep.setChecked(idx == 3)
        self.btn_satis.setChecked(idx == 4)
        self.btn_rapor.setChecked(idx == 5)
        self.btn_sadakat.setChecked(idx == 6)
        self.btn_yonetici.setChecked(idx == 7)

        self._load_operatorler()

        if idx == 0:
            self.p_dash.refresh()
        elif idx == 1:
            self.p_musteri.refresh()
        elif idx == 3:
            self.p_talep.refresh()
        elif idx == 4:
            self.p_satis.refresh()
        elif idx == 5:
            self.p_rapor.refresh()
        elif idx == 6:
            self.p_sadakat.refresh()
        elif idx == 7:
            self.p_yonetici.refresh()

def _koyu_palette() -> QPalette:
    pal = QPalette()
    beyaz = QColor("#FFFFFF")
    dim = QColor(C['text_dim'])
    pal.setColor(QPalette.ColorRole.Window, QColor(C['bg']))
    pal.setColor(QPalette.ColorRole.WindowText, beyaz)
    pal.setColor(QPalette.ColorRole.Base, QColor(C['sidebar']))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(C['card']))
    pal.setColor(QPalette.ColorRole.Text, beyaz)
    pal.setColor(QPalette.ColorRole.PlaceholderText, dim)
    pal.setColor(QPalette.ColorRole.Button, QColor(C['card']))
    pal.setColor(QPalette.ColorRole.ButtonText, beyaz)
    pal.setColor(QPalette.ColorRole.Highlight, QColor(C['accent']))
    pal.setColor(QPalette.ColorRole.HighlightedText, beyaz)
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(C['card']))
    pal.setColor(QPalette.ColorRole.ToolTipText, beyaz)
    return pal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_koyu_palette())
    sistem = CRMSistemi()
    login = LoginDialog(sistem)
    if not login.exec():
        sys.exit(0)
    win = MainWindow(sistem)
    win.show()
    sys.exit(app.exec())