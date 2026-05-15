import sqlite3
import os
import sys
import hashlib
import secrets
from datetime import datetime
from enum import Enum

# ========== PAROLA YARDIMCILARI ==========
_VARSAYILAN_PAROLA = "admin"

def _hash_parola(parola: str) -> str:
    """salt$hash biçiminde PBKDF2-HMAC-SHA256 hash'i üretir."""
    salt = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", parola.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}${h.hex()}"

def _parola_dogrula(parola: str, hash_str: str) -> bool:
    if not hash_str or "$" not in hash_str:
        return False
    salt_hex, h_hex = hash_str.split("$", 1)
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    h = hashlib.pbkdf2_hmac("sha256", parola.encode("utf-8"), salt, 120_000)
    return secrets.compare_digest(h.hex(), h_hex)

# ========== ENUM TANILARI (SABIT DEĞERLER) ==========
class TalepDurumu(Enum):
    ACIK = "Açık"
    ESLEME = "Eşleştirme"
    COZUMLENDI = "Çözümlendi"
    KAPALI = "Kapalı"

class MusteriTipi(Enum):
    BIREYSEL = "Bireysel"
    KURUMSAL = "Kurumsal"
    OZEL = "Özel"

class SatisKategorisi(Enum):
    DANISMANLIK = "Danışmanlık"
    URUN_SATISI = "Ürün Satışı"
    HIZMET = "Hizmet"
    LISANS = "Lisans"
    DESTEK = "Destek"

class OperatorRol(Enum):
    ADMIN = "Yönetici"
    SATICI = "Satıcı"

class Operator:
    def __init__(self, operator_id: int, kullanici_adi: str, ad_soyad: str,
                 rol: OperatorRol = OperatorRol.SATICI) -> None:
        self.operator_id: int = operator_id
        self.kullanici_adi: str = kullanici_adi
        self.ad_soyad: str = ad_soyad
        self.rol: OperatorRol = rol
        self.aktif: bool = True
        self.olusturma_tarihi: datetime = datetime.now()
        self.parola_hash: str = ""

class SadakatSeviyesi(Enum):
    STANDART = ("Standart", 0.00, 0,     "⚪")
    GUMUSH   = ("Gümüş",    0.02, 1000,  "🥈")
    ALTIN    = ("Altın",    0.05, 5000,  "🥇")
    PLATIN   = ("Platin",   0.10, 10000, "💎")

    @property
    def ad(self):
        return self.value[0]

    @property
    def indirim_orani(self):
        return self.value[1]

    @property
    def esik(self):
        return self.value[2]

    @property
    def rozet(self):
        return self.value[3]

    @classmethod
    def puana_gore(cls, puan: int) -> "SadakatSeviyesi":
        seviye = cls.STANDART
        for s in cls:
            if puan >= s.esik:
                seviye = s
        return seviye

    @classmethod
    def sonraki(cls, mevcut: "SadakatSeviyesi") -> "SadakatSeviyesi | None":
        sirali = list(cls)
        idx = sirali.index(mevcut)
        return sirali[idx + 1] if idx + 1 < len(sirali) else None

# ========== SINIF: SATIS ==========
class Satis:
    def __init__(self, satis_id: int, urun: str, fiyat: float,
                 kategori: SatisKategorisi = SatisKategorisi.URUN_SATISI,
                 notlar: str = "", operator_id: int | None = None) -> None:
        self.satis_id: int = satis_id
        self.urun: str = urun
        self.fiyat: float = fiyat
        self.kategori: SatisKategorisi = kategori
        self.notlar: str = notlar
        self.tarih: datetime = datetime.now()
        self.operator_id: int | None = operator_id

# ========== SINIF: DESTEK TALEBİ ==========
class DestekTalebi:
    def __init__(self, talep_id: int, aciklama: str,
                 durum: TalepDurumu = TalepDurumu.ACIK,
                 operator_id: int | None = None) -> None:
        self.talep_id: int = talep_id
        self.aciklama: str = aciklama
        self.durum: TalepDurumu = durum
        self.olusturma_tarihi: datetime = datetime.now()
        self.kapanma_tarihi: datetime | None = None
        self.notlar: str = ""
        self.operator_id: int | None = operator_id

    def durum_degistir(self, yeni_durum: TalepDurumu) -> None:
        self.durum = yeni_durum
        if yeni_durum == TalepDurumu.KAPALI or yeni_durum == TalepDurumu.COZUMLENDI:
            self.kapanma_tarihi = datetime.now()
            
    def get_status_badge(self):
        renk_map = {
            TalepDurumu.ACIK: "🔴",
            TalepDurumu.ESLEME: "🟡",
            TalepDurumu.COZUMLENDI: "🟢",
            TalepDurumu.KAPALI: "⚫"
        }
        return f"{renk_map.get(self.durum, '⚪')} {self.durum.value}"

# ========== SINIF: MÜŞTERİ ==========
class Musteri:
    def __init__(self, musteri_id: int, ad: str, telefon: str,
                 email: str = "", sehir: str = "",
                 tip: MusteriTipi = MusteriTipi.BIREYSEL) -> None:
        self.musteri_id: int = musteri_id
        self.ad: str = ad
        self.telefon: str = telefon
        self.email: str = email
        self.sehir: str = sehir
        self.tip: MusteriTipi = tip
        self.satislar: list[Satis] = []
        self.talepler: list[DestekTalebi] = []
        self.kayit_tarihi: datetime = datetime.now()
        self.notlar: str = ""

        self.puan: int = 0
        self.seviye: SadakatSeviyesi = SadakatSeviyesi.STANDART
        
    def toplam_harcama(self):
        return sum(s.fiyat for s in self.satislar)
    
    def satis_sayisi(self):
        return len(self.satislar)
    
    def ortalama_satis_tutari(self):
        if len(self.satislar) == 0:
            return 0
        return self.toplam_harcama() / len(self.satislar)
    
    def acik_talep_sayisi(self):
        return sum(1 for t in self.talepler if t.durum == TalepDurumu.ACIK)
    
    def get_segment(self):
        if self.toplam_harcama() > 50000:
            return "💎 VIP"
        elif self.toplam_harcama() > 10000:
            return "⭐ Normal"
        else:
            return "🆕 Yeni"
    
    def puan_ekle(self, tutar: float) -> int:
        yeni_puan = int(tutar * 0.10)
        self.puan += yeni_puan
        self.seviye_hesapla()
        return yeni_puan

    def seviye_hesapla(self) -> None:
        self.seviye = SadakatSeviyesi.puana_gore(self.puan)

    def indirim_orani_al(self) -> float:
        return self.seviye.indirim_orani

    def indirimli_fiyat_hesapla(self, tutar: float) -> float:
        return tutar - tutar * self.indirim_orani_al()

    def sonraki_seviyeye_kalan(self) -> int:
        sonraki = SadakatSeviyesi.sonraki(self.seviye)
        return max(sonraki.esik - self.puan, 0) if sonraki else 0

    def get_sadakat_bilgisi(self) -> str:
        return f"{self.seviye.rozet} {self.seviye.ad} • {self.puan} puan • %{self.indirim_orani_al()*100:.0f} indirim"

# ========== SINIF: CRM SİSTEMİ ==========
class CRMSistemi:
    def __init__(self):
        self.musteriler: dict[int, Musteri] = {}
        self.operatorler: dict[int, Operator] = {}
        self.aktif_operator_id: int | None = None
        self._son_satis_id = 1
        self._son_talep_id = 1
        self._son_operator_id = 1

        exe_yolu = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.db_path = os.path.join(exe_yolu, "crm_veritabani.db")

        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        self._tablolari_kur()
        self._eski_kayitlari_yukle()
        self._varsayilan_operator_olustur()

    def _tablolari_kur(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS musteriler (
            id INTEGER PRIMARY KEY,
            ad TEXT,
            telefon TEXT,
            email TEXT,
            sehir TEXT,
            tip TEXT,
            kayit_tarihi TEXT,
            notlar TEXT,
            puan INTEGER DEFAULT 0,
            seviye TEXT DEFAULT 'STANDART'
        )""")
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY,
            musteri_id INTEGER,
            urun TEXT,
            fiyat REAL,
            kategori TEXT,
            notlar TEXT,
            tarih TEXT,
            operator_id INTEGER
        )""")
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS talepler (
            id INTEGER PRIMARY KEY,
            musteri_id INTEGER,
            aciklama TEXT,
            durum TEXT,
            olusturma_tarihi TEXT,
            kapanma_tarihi TEXT,
            notlar TEXT,
            operator_id INTEGER
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS operatorler (
            id INTEGER PRIMARY KEY,
            kullanici_adi TEXT UNIQUE,
            ad_soyad TEXT,
            rol TEXT,
            aktif INTEGER DEFAULT 1,
            olusturma_tarihi TEXT,
            parola_hash TEXT
        )""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS islem_logu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            operator_id INTEGER,
            islem_tipi TEXT,
            hedef TEXT,
            detay TEXT
        )""")

        self._sema_gocu()
        self.db.commit()

    def _sema_gocu(self) -> None:
        eksikler: dict[str, list[tuple[str, str]]] = {
            "musteriler": [
                ("email",        "TEXT"),
                ("sehir",        "TEXT"),
                ("tip",          "TEXT"),
                ("kayit_tarihi", "TEXT"),
                ("notlar",       "TEXT"),
                ("puan",         "INTEGER DEFAULT 0"),
                ("seviye",       "TEXT DEFAULT 'STANDART'"),
            ],
            "satislar": [
                ("kategori",    "TEXT"),
                ("notlar",      "TEXT"),
                ("tarih",       "TEXT"),
                ("operator_id", "INTEGER"),
            ],
            "talepler": [
                ("durum",            "TEXT"),
                ("olusturma_tarihi", "TEXT"),
                ("kapanma_tarihi",   "TEXT"),
                ("notlar",           "TEXT"),
                ("operator_id",      "INTEGER"),
            ],
            "operatorler": [
                ("parola_hash", "TEXT"),
            ],
        }
        for tablo, kolonlar in eksikler.items():
            self.cursor.execute(f"PRAGMA table_info({tablo})")
            mevcut = {row[1] for row in self.cursor.fetchall()}
            for kolon, tip in kolonlar:
                if kolon not in mevcut:
                    self.cursor.execute(f"ALTER TABLE {tablo} ADD COLUMN {kolon} {tip}")
        self.db.commit()

    def _eski_kayitlari_yukle(self):
        # Müşterileri Yükle
        try:
            self.cursor.execute("SELECT id, ad, telefon, email, sehir, tip, kayit_tarihi, notlar, puan, seviye FROM musteriler")
        except:
            self.cursor.execute("SELECT id, ad, telefon FROM musteriler")
            for r in self.cursor.fetchall():
                m = Musteri(r[0], r[1], r[2], "", "", MusteriTipi.BIREYSEL)
                self.musteriler[r[0]] = m
            return
            
        for r in self.cursor.fetchall():
            m = Musteri(r[0], r[1], r[2], r[3] or "", r[4] or "", MusteriTipi[r[5]] if r[5] else MusteriTipi.BIREYSEL)
            m.kayit_tarihi = datetime.fromisoformat(r[6]) if r[6] else datetime.now()
            m.notlar = r[7] or ""
            if len(r) > 8:
                m.puan = r[8] or 0
            if len(r) > 9:
                m.seviye = SadakatSeviyesi[r[9]] if r[9] else SadakatSeviyesi.STANDART
            m.seviye_hesapla()
            self.musteriler[r[0]] = m
            
        # SATIŞLARI YÜKLE (BUG BURADAYDI - operator_id EKLENDİ VE TİP KONTROLÜ YAPILDI)
        try:
            self.cursor.execute("SELECT id, musteri_id, urun, fiyat, kategori, notlar, tarih, operator_id FROM satislar")
        except sqlite3.OperationalError:
            self.cursor.execute("SELECT id, musteri_id, urun, fiyat FROM satislar")
            for r in self.cursor.fetchall():
                if r[1] in self.musteriler:
                    s = Satis(r[0], r[2], r[3], SatisKategorisi.URUN_SATISI, "")
                    self.musteriler[r[1]].satislar.append(s)
            return
                
        for r in self.cursor.fetchall():
            if r[1] in self.musteriler:
                s = Satis(r[0], r[2], r[3], SatisKategorisi[r[4]] if r[4] else SatisKategorisi.URUN_SATISI, r[5] or "")
                s.tarih = datetime.fromisoformat(r[6]) if r[6] else datetime.now()
                # 8. Sütun (r[7]) operator_id
                if len(r) > 7 and r[7] is not None:
                    try:
                        s.operator_id = int(r[7])
                    except ValueError:
                        pass
                self.musteriler[r[1]].satislar.append(s)

        # Talepleri Yükle
        try:
            self.cursor.execute("SELECT id, musteri_id, aciklama, durum, olusturma_tarihi, kapanma_tarihi, notlar, operator_id FROM talepler")
        except sqlite3.OperationalError:
            self.cursor.execute("SELECT id, musteri_id, aciklama FROM talepler")
            for r in self.cursor.fetchall():
                if r[1] in self.musteriler:
                    t = DestekTalebi(r[0], r[2], TalepDurumu.ACIK)
                    self.musteriler[r[1]].talepler.append(t)
            return

        for r in self.cursor.fetchall():
            if r[1] in self.musteriler:
                t = DestekTalebi(r[0], r[2], TalepDurumu[r[3]] if r[3] else TalepDurumu.ACIK)
                t.olusturma_tarihi = datetime.fromisoformat(r[4]) if r[4] else datetime.now()
                t.kapanma_tarihi = datetime.fromisoformat(r[5]) if r[5] else None
                t.notlar = r[6] or ""
                if len(r) > 7 and r[7] is not None:
                    try:
                        t.operator_id = int(r[7])
                    except ValueError:
                        pass
                self.musteriler[r[1]].talepler.append(t)

        # Operatörleri Yükle (Tip kontrolleri eklendi)
        try:
            self.cursor.execute(
                "SELECT id, kullanici_adi, ad_soyad, rol, aktif, olusturma_tarihi, parola_hash FROM operatorler")
            for r in self.cursor.fetchall():
                rol = OperatorRol[r[3]] if r[3] in OperatorRol.__members__ else OperatorRol.SATICI
                op_id = int(r[0])
                op = Operator(op_id, r[1], r[2] or r[1], rol)
                op.aktif = bool(r[4]) if r[4] is not None else True
                op.olusturma_tarihi = datetime.fromisoformat(r[5]) if r[5] else datetime.now()
                op.parola_hash = r[6] or ""
                self.operatorler[op_id] = op
        except sqlite3.OperationalError:
            pass

        # Numaratörleri Güncelle
        self.cursor.execute("SELECT MAX(id) FROM satislar")
        res_s = self.cursor.fetchone()[0]
        self._son_satis_id = (res_s + 1) if res_s else 1

        self.cursor.execute("SELECT MAX(id) FROM talepler")
        res_t = self.cursor.fetchone()[0]
        self._son_talep_id = (res_t + 1) if res_t else 1

        self.cursor.execute("SELECT MAX(id) FROM operatorler")
        res_o = self.cursor.fetchone()[0]
        self._son_operator_id = (res_o + 1) if res_o else 1

    # ========== OPERATÖR YÖNETİMİ ==========
    def _varsayilan_operator_olustur(self) -> None:
        for op in self.operatorler.values():
            if not op.parola_hash:
                op.parola_hash = _hash_parola(_VARSAYILAN_PAROLA)
                self.cursor.execute(
                    "UPDATE operatorler SET parola_hash=? WHERE id=?",
                    (op.parola_hash, op.operator_id))
        if self.operatorler:
            self.db.commit()
            self.aktif_operator_id = next(
                (op.operator_id for op in self.operatorler.values() if op.aktif),
                next(iter(self.operatorler), None),
            )
            return

        op = Operator(self._son_operator_id, "admin", "Yönetici", OperatorRol.ADMIN)
        op.parola_hash = _hash_parola(_VARSAYILAN_PAROLA)
        self.operatorler[op.operator_id] = op
        self._son_operator_id += 1
        self.cursor.execute(
            "INSERT INTO operatorler (id, kullanici_adi, ad_soyad, rol, aktif, olusturma_tarihi, parola_hash) "
            "VALUES (?,?,?,?,?,?,?)",
            (op.operator_id, op.kullanici_adi, op.ad_soyad, op.rol.name, 1,
             op.olusturma_tarihi.isoformat(), op.parola_hash))
        self.db.commit()
        self.aktif_operator_id = op.operator_id

    def operator_ekle(self, kullanici_adi: str, ad_soyad: str, parola: str,
                      rol: OperatorRol = OperatorRol.SATICI) -> tuple[bool, str]:
        if not kullanici_adi.strip():
            return False, "Kullanıcı adı boş olamaz!"
        if not ad_soyad.strip():
            return False, "Ad-Soyad boş olamaz!"
        if not parola or len(parola) < 4:
            return False, "Parola en az 4 karakter olmalı!"
        if any(o.kullanici_adi.lower() == kullanici_adi.lower() for o in self.operatorler.values()):
            return False, "Bu kullanıcı adı zaten kayıtlı!"

        op = Operator(self._son_operator_id, kullanici_adi.strip(), ad_soyad.strip(), rol)
        op.parola_hash = _hash_parola(parola)
        self.operatorler[op.operator_id] = op
        self.cursor.execute(
            "INSERT INTO operatorler (id, kullanici_adi, ad_soyad, rol, aktif, olusturma_tarihi, parola_hash) "
            "VALUES (?,?,?,?,?,?,?)",
            (op.operator_id, op.kullanici_adi, op.ad_soyad, op.rol.name, 1,
             op.olusturma_tarihi.isoformat(), op.parola_hash))
        self.db.commit()
        self._son_operator_id += 1
        self._log_islem("OPERATOR_EKLE", op.kullanici_adi, op.rol.value)
        return True, f"✓ {op.ad_soyad} eklendi."

    def operator_parola_ayarla(self, op_id: int, yeni_parola: str) -> tuple[bool, str]:
        op = self.operatorler.get(op_id)
        if not op:
            return False, "Operatör bulunamadı!"
        if not yeni_parola or len(yeni_parola) < 4:
            return False, "Parola en az 4 karakter olmalı!"
        op.parola_hash = _hash_parola(yeni_parola)
        self.cursor.execute("UPDATE operatorler SET parola_hash=? WHERE id=?",
                            (op.parola_hash, op_id))
        self.db.commit()
        self._log_islem("OPERATOR_PAROLA", op.kullanici_adi)
        return True, "✓ Parola güncellendi."

    def operator_dogrula(self, kullanici_adi: str, parola: str) -> Operator | None:
        if not kullanici_adi or not parola:
            return None
        for op in self.operatorler.values():
            if op.kullanici_adi.lower() == kullanici_adi.lower() and op.aktif:
                if _parola_dogrula(parola, op.parola_hash):
                    return op
                return None
        return None

    def operator_guncelle(self, op_id: int, ad_soyad: str | None = None,
                          rol: OperatorRol | None = None,
                          aktif: bool | None = None) -> tuple[bool, str]:
        op = self.operatorler.get(op_id)
        if not op:
            return False, "Operatör bulunamadı!"
        if ad_soyad is not None:
            if not ad_soyad.strip():
                return False, "Ad-Soyad boş olamaz!"
            op.ad_soyad = ad_soyad.strip()
        if rol is not None:
            op.rol = rol
        if aktif is not None:
            op.aktif = aktif
        self.cursor.execute(
            "UPDATE operatorler SET ad_soyad=?, rol=?, aktif=? WHERE id=?",
            (op.ad_soyad, op.rol.name, 1 if op.aktif else 0, op_id))
        self.db.commit()
        self._log_islem("OPERATOR_GUNCELLE", op.kullanici_adi, op.rol.value)
        return True, f"✓ {op.ad_soyad} güncellendi."

    def operator_sil(self, op_id: int) -> tuple[bool, str]:
        op = self.operatorler.get(op_id)
        if not op:
            return False, "Operatör bulunamadı!"
        if op.operator_id == self.aktif_operator_id:
            return False, "Şu an aktif olan operatörü silemezsiniz."
        op.aktif = False
        self.cursor.execute("UPDATE operatorler SET aktif=0 WHERE id=?", (op_id,))
        self.db.commit()
        self._log_islem("OPERATOR_SIL", op.kullanici_adi)
        return True, f"✓ {op.ad_soyad} pasifleştirildi."

    def aktif_operator_ata(self, op_id: int) -> tuple[bool, str]:
        op = self.operatorler.get(op_id)
        if not op or not op.aktif:
            return False, "Geçersiz veya pasif operatör."
        self.aktif_operator_id = op_id
        return True, f"Aktif operatör: {op.ad_soyad}"

    def get_aktif_operator(self) -> Operator | None:
        if self.aktif_operator_id is None:
            return None
        return self.operatorler.get(self.aktif_operator_id)

    def get_tum_operatorler(self) -> dict[int, Operator]:
        return self.operatorler

    # ========== DENETİM KAYDI ==========
    def _log_islem(self, islem_tipi: str, hedef: str, detay: str = "") -> None:
        self.cursor.execute(
            "INSERT INTO islem_logu (tarih, operator_id, islem_tipi, hedef, detay) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), self.aktif_operator_id, islem_tipi, hedef, detay))
        self.db.commit()

    def get_islem_gecmisi(self, op_id: int | None = None,
                          islem_tipi: str | None = None,
                          limit: int = 500) -> list[dict[str, object]]:
        sql = "SELECT id, tarih, operator_id, islem_tipi, hedef, detay FROM islem_logu"
        kosullar: list[str] = []
        params: list[object] = []
        if op_id is not None:
            kosullar.append("operator_id = ?")
            params.append(op_id)
        if islem_tipi:
            kosullar.append("islem_tipi = ?")
            params.append(islem_tipi)
        if kosullar:
            sql += " WHERE " + " AND ".join(kosullar)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        self.cursor.execute(sql, tuple(params))
        return [
            {"id": r[0], "tarih": r[1], "operator_id": r[2],
             "tip": r[3], "hedef": r[4], "detay": r[5] or ""}
            for r in self.cursor.fetchall()
        ]

    # ========== MÜŞTERİ YÖNETİMİ ==========
    def musteri_ekle(self, musteri: Musteri):
        if musteri.musteri_id in self.musteriler:
            return False, "Bu müşteri ID zaten sistemde kayıtlı!"
        if not musteri.ad or not musteri.ad.strip():
            return False, "Müşteri adı boş olamaz!"
        if not musteri.telefon or not musteri.telefon.strip():
            return False, "Telefon numarası boş olamaz!"
        
        self.musteriler[musteri.musteri_id] = musteri
        self.cursor.execute(
            """INSERT INTO musteriler
               (id, ad, telefon, email, sehir, tip, kayit_tarihi, notlar, puan, seviye)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (musteri.musteri_id, musteri.ad, musteri.telefon, musteri.email, musteri.sehir,
             musteri.tip.name, musteri.kayit_tarihi.isoformat(), musteri.notlar,
             musteri.puan, musteri.seviye.name))
        self.db.commit()
        self._log_islem("MUSTERI_EKLE", f"#{musteri.musteri_id} {musteri.ad}", musteri.tip.value)
        return True, f"✓ {musteri.ad} başarıyla eklendi."

    def musteri_guncelle(self, m_id: int, ad: str | None = None, telefon: str | None = None,
                         email: str | None = None, sehir: str | None = None,
                         tip: MusteriTipi | None = None, notlar: str | None = None):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"
        if ad is not None and not ad.strip():
            return False, "Müşteri adı boş olamaz!"
        if telefon is not None and not telefon.strip():
            return False, "Telefon numarası boş olamaz!"

        m = self.musteriler[m_id]
        if ad is not None:
            m.ad = ad
        if telefon is not None:
            m.telefon = telefon
        if email is not None:
            m.email = email
        if sehir is not None:
            m.sehir = sehir
        if tip is not None:
            m.tip = tip
        if notlar is not None:
            m.notlar = notlar

        self.cursor.execute(
            """UPDATE musteriler SET ad=?, telefon=?, email=?, sehir=?, tip=?, notlar=? WHERE id=?""",
            (m.ad, m.telefon, m.email, m.sehir, m.tip.name, m.notlar, m_id))
        self.db.commit()
        self._log_islem("MUSTERI_GUNCELLE", f"#{m_id} {m.ad}")
        return True, f"✓ {m.ad} bilgileri güncellendi."

    def musteri_sil(self, m_id: int):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"

        ad = self.musteriler[m_id].ad
        self.cursor.execute("DELETE FROM satislar WHERE musteri_id = ?", (m_id,))
        self.cursor.execute("DELETE FROM talepler WHERE musteri_id = ?", (m_id,))
        self.cursor.execute("DELETE FROM musteriler WHERE id = ?", (m_id,))
        self.db.commit()
        del self.musteriler[m_id]
        self._log_islem("MUSTERI_SIL", f"#{m_id} {ad}")
        return True, "Müşteri başarıyla silindi."

    # ========== SATIŞ YÖNETİMİ ==========
    def satis_yap(self, m_id: int, urun: str, fiyat: float, kategori: SatisKategorisi = SatisKategorisi.URUN_SATISI, notlar: str = ""):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"
        if not urun or not urun.strip():
            return False, "Ürün adı boş olamaz!"
        if fiyat <= 0:
            return False, "Fiyat sıfırdan büyük olmalıdır!"

        musteri = self.musteriler[m_id]
        eski_seviye = musteri.seviye

        indirim_orani = musteri.indirim_orani_al()
        odenen = round(musteri.indirimli_fiyat_hesapla(fiyat), 2)
        indirim_tutari = round(fiyat - odenen, 2)

        satis = Satis(self._son_satis_id, urun, odenen, kategori, notlar,
                      operator_id=self.aktif_operator_id)
        self.cursor.execute(
            """INSERT INTO satislar
               (id, musteri_id, urun, fiyat, kategori, notlar, tarih, operator_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (self._son_satis_id, m_id, urun, odenen, kategori.name, notlar,
             satis.tarih.isoformat(), self.aktif_operator_id))
        musteri.satislar.append(satis)

        kazanilan = musteri.puan_ekle(odenen)
        self.cursor.execute("""UPDATE musteriler SET puan=?, seviye=? WHERE id=?""",
            (musteri.puan, musteri.seviye.name, m_id))
        self.db.commit()

        self._son_satis_id += 1

        parcalar = [f"✓ Satış kaydedildi."]
        if indirim_orani > 0:
            parcalar.append(
                f"{eski_seviye.ad} indirimi: −₺{indirim_tutari:,.2f} (%{indirim_orani*100:.0f})"
            )
        parcalar.append(f"Ödenen: ₺{odenen:,.2f}")
        parcalar.append(f"+{kazanilan} puan (toplam {musteri.puan})")
        if musteri.seviye != eski_seviye:
            parcalar.append(f"🎉 Yeni seviye: {musteri.seviye.rozet} {musteri.seviye.ad}!")
        self._log_islem(
            "SATIS",
            f"#{musteri.musteri_id} {musteri.ad} → {urun}",
            f"₺{odenen:,.2f} ({kategori.value})",
        )
        return True, " | ".join(parcalar)

    def satis_sil(self, satis_id: int, m_id: int):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"

        satis = next((s for s in self.musteriler[m_id].satislar if s.satis_id == satis_id), None)
        if not satis:
            return False, "Satış bulunamadı!"

        self.musteriler[m_id].satislar.remove(satis)
        self.cursor.execute("DELETE FROM satislar WHERE id = ?", (satis_id,))
        self.db.commit()
        self._log_islem(
            "SATIS_SIL",
            f"#{satis_id} {self.musteriler[m_id].ad} → {satis.urun}",
            f"₺{satis.fiyat:,.2f}",
        )
        return True, "Satış silindi."

    # ========== DESTEK TALEBİ YÖNETİMİ ==========
    def destek_talebi_olustur(self, m_id: int, aciklama: str):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"
        if not aciklama or not aciklama.strip():
            return False, "Talep açıklaması boş olamaz!"

        talep = DestekTalebi(self._son_talep_id, aciklama, operator_id=self.aktif_operator_id)
        self.cursor.execute(
            """INSERT INTO talepler
               (id, musteri_id, aciklama, durum, olusturma_tarihi, kapanma_tarihi, notlar, operator_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (self._son_talep_id, m_id, aciklama, talep.durum.name,
             talep.olusturma_tarihi.isoformat(), None, talep.notlar, self.aktif_operator_id))
        self.db.commit()
        self.musteriler[m_id].talepler.append(talep)
        self._log_islem(
            "TALEP_OLUSTUR",
            f"#{self._son_talep_id} {self.musteriler[m_id].ad}",
            aciklama[:80],
        )
        self._son_talep_id += 1
        return True, "✓ Destek talebi oluşturuldu."

    def talep_durumu_degistir(self, talep_id: int, m_id: int, yeni_durum: TalepDurumu):
        if m_id not in self.musteriler:
            return False, "Müşteri bulunamadı!"

        talep = next((t for t in self.musteriler[m_id].talepler if t.talep_id == talep_id), None)
        if not talep:
            return False, "Talep bulunamadı!"

        talep.durum_degistir(yeni_durum)
        self.cursor.execute("""UPDATE talepler SET durum=?, kapanma_tarihi=? WHERE id=?""",
            (talep.durum.name, talep.kapanma_tarihi.isoformat() if talep.kapanma_tarihi else None, talep_id))
        self.db.commit()
        self._log_islem(
            "TALEP_DURUMU",
            f"#{talep_id} {self.musteriler[m_id].ad}",
            yeni_durum.value,
        )
        return True, f"✓ Talep durumu '{yeni_durum.value}' olarak güncellendi."

    # ========== İSTATİSTİKLER & RAPORLAR ==========
    def get_istatistikler(self) -> dict[str, float]:
        toplam_musteri = len(self.musteriler)
        toplam_satis = sum(m.satis_sayisi() for m in self.musteriler.values())
        toplam_gelir = sum(m.toplam_harcama() for m in self.musteriler.values())
        acik_talepler = sum(m.acik_talep_sayisi() for m in self.musteriler.values())
        
        return {
            "toplam_musteri": toplam_musteri,
            "toplam_satis": toplam_satis,
            "toplam_gelir": toplam_gelir,
            "acik_talepler": acik_talepler,
            "ortalama_satis": toplam_gelir / toplam_satis if toplam_satis > 0 else 0,
            "ortalama_musteri_degeri": toplam_gelir / toplam_musteri if toplam_musteri > 0 else 0
        }
    
    def sadakat_istatistikleri(self) -> dict[str, float | dict[str, int]]:
        seviye_sayilari: dict[str, int] = {s.name: 0 for s in SadakatSeviyesi}
        toplam_puan: int = 0

        for m in self.musteriler.values():
            seviye_sayilari[m.seviye.name] += 1
            toplam_puan += m.puan

        return {
            "toplam_puan": float(toplam_puan),
            "ortalama_puan": toplam_puan / len(self.musteriler) if len(self.musteriler) > 0 else 0.0,
            "seviye_dagitimi": seviye_sayilari
        }
    
    def indirim_analizi(self) -> dict[str, float | dict[str, float]]:
        toplam_tasarruf: float = 0.0
        seviye_tasarruflari: dict[str, float] = {s.name: 0.0 for s in SadakatSeviyesi}

        for m in self.musteriler.values():
            tasarruf = m.toplam_harcama() * m.indirim_orani_al()
            toplam_tasarruf += tasarruf
            seviye_tasarruflari[m.seviye.name] += tasarruf

        return {
            "toplam_tasarruf": toplam_tasarruf,
            "seviye_tasarruflari": seviye_tasarruflari
        }

    def musteri_raporlari(self) -> list[Musteri]:
        siralanmis = sorted(self.musteriler.values(), key=lambda x: x.toplam_harcama(), reverse=True)
        return siralanmis[:10]

    def get_tum_satislar(self) -> list[tuple[Musteri, Satis]]:
        kayitlar: list[tuple[Musteri, Satis]] = []
        for m in self.musteriler.values():
            for s in m.satislar:
                kayitlar.append((m, s))
        kayitlar.sort(key=lambda ms: ms[1].tarih, reverse=True)
        return kayitlar

    def en_cok_talep_alan_aylar(self) -> dict[str, int]:
        aylar: dict[str, int] = {}
        for m in self.musteriler.values():
            for t in m.talepler:
                ay_anahtar = t.olusturma_tarihi.strftime("%Y-%m")
                aylar[ay_anahtar] = aylar.get(ay_anahtar, 0) + 1
        return aylar

    def sehir_bazli_istatistik(self) -> dict[str, int]:
        sehirler: dict[str, int] = {}
        for m in self.musteriler.values():
            sehir = m.sehir or "Belirtilmemiş"
            sehirler[sehir] = sehirler.get(sehir, 0) + 1
        return sehirler

    def get_tum_musteriler(self) -> dict[int, Musteri]:
        return self.musteriler