SANDIQ RADARI — SERVER VERSIYASI

Bu paket saytın serverlə danışan başlanğıc versiyasıdır.

İŞƏ SALMA:
1) Faylları bir Python hosting layihəsinə yüklə.
2) Python 3.10+ seç.
3) requirements.txt paketlərini quraşdır.
4) Start command: uvicorn main:app --host 0.0.0.0 --port 8000
5) Saytın URL-ni aç.

NƏ EDİR:
- Maksimum 5 TikTok istifadəçi adını paralel izləməyə çalışır.
- LIVE bağlantı/status hadisələrini saxlayır.
- TikTokLive RoomUserSeqEvent göndərərsə izləyici məlumatını alır.
- EnvelopeEvent gələndə sandıq hadisəsini qeydə alır.
- Hadisə payload-ında açılma/bitmə vaxtı kimi açıq timestamp varsa saniyə ilə geri sayım hesablayır.
- Jeton/mükafat sahəsi payload-da yoxdursa uydurmur.

VACİB MƏHDUDİYYƏTLƏR:
- TikTok-un rəsmi açıq LIVE oxuma API-si yoxdur. TikTokLive qeyri-rəsmi reverse-engineering kitabxanasıdır; TikTok dəyişiklikləri onu poza bilər.
- Bəzi LIVE-lara qoşulma uğursuz ola bilər, bəzi event-lər ümumiyyətlə gəlməyə bilər.
- Sandıq hadisəsinin mövcudluğu onun açılma vaxtı və ya jeton sayının da ötürülməsi demək deyil. Bu məlumatlar yalnız real event payload-ında olduqda göstərilə bilər.
- Eyni anda 5 WebSocket bağlantısı hosting resurslarına və TikTok limitlərinə görə uğursuz ola bilər. Əvvəl 1-2 hesabla sınaq tövsiyə olunur.
- Bu versiya hələ mobil cihazda lokal HTML kimi işləyəndə canlı məlumat toplamır; Python serverdə işləməlidir.
- TikTok hesab şifrəsi/session cookie tələb etmir; heç bir TikTok şifrəsini daxil etmə.

API:
GET /api/status
POST /api/watchlist  JSON: {"usernames":["username1","username2"]}
GET /api/events?since=0
GET /health

TikTokLive docs: https://github.com/isaackogan/TikTokLive
Lisenziya və istifadə şərtlərini yerləşdirməzdən əvvəl yoxla.


VACIB: HTML faylını telefonda content:// və ya file:// ünvanından açmaq yalnız siyahını göstərir. Canlı server funksiyaları üçün ZIP-i Python hostinqinə yerləşdirin və verilən sayt URL-sini açın. Server internetdə yerləşdirilməyib; bu paket təkbaşına 24/7 işləyən hostinq yaratmır.


YENİLİK — LIVE LINKİ:
- Saytın giriş xanasına tiktok.com/@username/live formasında LIVE linki yapışdırmaq olar.
- Səhifə linkdən @username hissəsini çıxarıb 5 hesablıq izləmə siyahısına əlavə edir.
- Qısa paylaşım linkləri (vm.tiktok.com və vt.tiktok.com) bu ilkin versiyada avtomatik açıla bilməz; birbaşa @username/live linkindən istifadə et.
- Linkdən istifadəçi adının çıxarılması LIVE-a qoşulma və sandıq vaxtının mütləq tapılması demək deyil. Server yalnız TikTokLive-dan həqiqi hadisə alarsa məlumat göstərəcək.
