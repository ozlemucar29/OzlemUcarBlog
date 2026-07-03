# Özlem Uçar - Django Blog Projesi

Bu proje, Django kullanılarak geliştirilmiş, modern tasarıma sahip kişisel bir blog web uygulamasıdır. Proje hem yerel bilgisayarınızda çalıştırılabilir hem de PythonAnywhere üzerinde yayına alınabilir durumda yapılandırılmıştır.

---

## 🔑 Yönetici Giriş Bilgileri (Admin Login)

Sitenin yönetim paneline veya yazı ekleme/düzenleme sayfalarına erişmek için kullanabileceğiniz hazır yönetici hesabı bilgileri aşağıdadır:

| Ortam | Giriş Adresi (URL) | Kullanıcı Adı | Şifre |
| :--- | :--- | :--- | :--- |
| **Yerel (Lokal)** | [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) | `admin` | `admin123` |
| **Canlı (Sunucu)** | [https://renn000.pythonanywhere.com/login/](https://renn000.pythonanywhere.com/login/) | `admin` | `admin123` |

> ℹ️ **Not:** Canlı sitede bu bilgilerin aktif olması için sunucu konsolunda `python populate_db.py` komutunun çalıştırılmış olması gerekmektedir.

---

## 🛠️ Yerelde Çalıştırma

Projenizi kendi bilgisayarınızda test etmek veya geliştirmek için şu adımları izleyin:

1. **Sanal Ortamı Aktif Edin:**
   - PowerShell: `.\venv\Scripts\Activate.ps1`
   - CMD (Komut İstemi): `.\venv\Scripts\activate.bat`

2. **Geliştirme Sunucusunu Başlatın:**
   ```bash
   python manage.py runserver
   ```
3. **Tarayıcıda Açın:** Tarayıcınızdan [http://127.0.0.1:8000/](http://127.0.0.1:8000/) adresine gidin.

---

## 🚀 Sunucuda Yayınlama ve Güncelleme

Projenin PythonAnywhere sunucusuna nasıl kurulacağı, güncelleneceği ve yönetileceği ile ilgili detaylı rehbere [YAYINLAMA_KILAVUZU.md](YAYINLAMA_KILAVUZU.md) dosyasından ulaşabilirsiniz.
