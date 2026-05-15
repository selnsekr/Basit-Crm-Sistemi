📊 Modern CRM (Müşteri İlişkileri Yönetimi) Sistemi
Bu proje, işletmelerin müşteri verilerini, satış süreçlerini, destek taleplerini ve sadakat programlarını tek bir noktadan yönetebilmeleri için geliştirilmiş, Python & PyQt6 tabanlı bir masaüstü uygulamasıdır. Nesne Yönelimli Programlama (OOP) mimarisi üzerine inşa edilen sistem, veritabanı yönetimi ve yüksek güvenlikli parola şifreleme özellikleri sunar.

✨ Temel Özellikler
🛡️ Güvenli Giriş: PBKDF2-HMAC-SHA256 algoritması ile şifrelenmiş operatör giriş sistemi.

👥 Müşteri Yönetimi: Bireysel ve Kurumsal müşteri kategorizasyonu, detaylı profil yönetimi.

💰 Satış Takibi: Satış kategorileri (Yazılım, Donanım, Danışmanlık) ve otomatik tutar hesaplama.

💎 Sadakat Programı: Müşterilerin harcama hacmine göre otomatik seviye atlaması (Bronz, Gümüş, Altın, Platin).

🎫 Talep & Destek Sistemi: Müşteri sorunlarını ve taleplerini öncelik sırasına göre takip etme.

📈 Gelişmiş Raporlama: En çok harcama yapan müşteriler, en çok talep alınan aylar ve performans analizleri.

⚙️ Yönetici Paneli: Operatör yetkilendirme ve sistem loglarını (işlem geçmişi) izleme.

🛠️ Teknik Altyapı
Dil: Python 3.10+

Arayüz (GUI): PyQt6 (Modern Dark Mode Tema)

Veritabanı: SQLite3

Güvenlik: Hashlib & Secrets (Kriptografik Parola Hashleme)

📸 Uygulama Ekran Görüntüleri ve Detaylı İnceleme
1. Sisteme Giriş (Login)
Sistemin ilk güvenlik katmanıdır. Operatörler, yetkilerine göre (Yönetici/Personel) güvenli hash doğrulaması ile sisteme dahil olurlar.
<img width="439" height="387" alt="1" src="https://github.com/user-attachments/assets/c925585c-dbab-4142-975e-a197d5dd4c8b" />


2. Ana Kontrol Paneli (Dashboard)
Giriş yapıldığında kullanıcıyı karşılayan özet ekranıdır. Toplam müşteri sayısı, aylık satışlar ve bekleyen talepler gibi kritik metrikler burada yer alır.
<img width="1349" height="730" alt="2 - Kopya" src="https://github.com/user-attachments/assets/243de551-fb7c-4acd-a273-5c79e7ea9dbc" />

3. Müşteri Listesi ve Yönetimi
Kayıtlı tüm müşterilerin detaylı listesidir.
<img width="1340" height="432" alt="3 - Kopya" src="https://github.com/user-attachments/assets/8dc702a5-657d-4159-b478-5d9615570c71" />



4. Yeni Müşteri Kaydı
Sisteme yeni bir müşteri eklerken tipi (Bireysel/Kurumsal) ve iletişim bilgileri bu modüler form üzerinden sisteme işlenir.
<img width="499" height="502" alt="4" src="https://github.com/user-attachments/assets/8676a675-55c5-4929-b5ec-e41d73d043bb" />



5. Satış Geçmişi (Finansal Takip)
Yapılan tüm ticari işlemlerin kronolojik listesidir. Hangi müşteriye, ne zaman ve hangi kategori altında satış yapıldığı izlenebilir.
<img width="1079" height="673" alt="7" src="https://github.com/user-attachments/assets/8df2a087-b394-49e0-9946-80230b59718a" />


6. Satış Oluşturma Ekranı
Yeni bir satış kaydı oluşturulurken müşterinin mevcut sadakat indirimleri otomatik olarak hesaplanır ve son tutar belirlenir.
<img width="1080" height="669" alt="5" src="https://github.com/user-attachments/assets/7ba83c44-f166-4d8b-8542-7544094e3ccf" />


7. Müşteri Talepleri ve Destek
Müşterilerden gelen teknik veya ticari taleplerin yönetildiği paneldir. "Açık", "İşlemde" veya "Çözüldü" durumları ile iş takibi yapılır.
<img width="1081" height="407" alt="6" src="https://github.com/user-attachments/assets/718a2a49-474e-4990-abb0-fdbeff97fa52" />


8. Raporlama ve İstatistikler
Veritabanındaki verilerin analitik olarak sunulduğu kısımdır. İşletme büyümesini takip etmek için görselleştirilmiş veriler sunar.
<img width="1149" height="628" alt="8" src="https://github.com/user-attachments/assets/596d7a0c-2edd-4f2e-aae2-956c564bedf4" />


9. Sadakat ve Ödül Sistemi
Müşterilerin harcama alışkanlıklarına göre hangi segmente dahil olduğunu ve kazandıkları indirim oranlarını gösteren bölümdür.
<img width="1125" height="678" alt="9" src="https://github.com/user-attachments/assets/4abae641-eb7d-4243-8e79-cd546d6deb99" />


10. Operatör ve Yetki Yönetimi
Yöneticiler için ayrılmış olan bu ekranda yeni operatörler eklenip, mevcut personelin yetkileri ve sistemdeki aktifliği düzenlenebilir.
<img width="1084" height="678" alt="10" src="https://github.com/user-attachments/assets/94ddb33f-4b98-47b1-8e5a-c8935326996d" />


Proje Yapısı:


crm_sistemi.py: Veri modelleri (Müşteri, Satış, Operatör) ve veritabanı mantığını içeren çekirdek dosya.

crm_gui.py: PyQt6 ile hazırlanan modern arayüz bileşenleri ve sayfa yönetimleri.

crm_veritabani.db: Tüm verilerin saklandığı yerel SQLite veritabanı.
