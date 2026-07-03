# Django Blog Projesi - Çalıştırma ve Yayınlama Kılavuzu

Bu kılavuz, projenizi yerelde nasıl çalıştıracağınızı, **PythonAnywhere** üzerinde ücretsiz olarak nasıl yayına alacağınızı ve yeni geliştirmeleri sunucuya nasıl yansıtacağınızı adım adım açıklamaktadır.

---

## 1. Yerelde Çalıştırma Adımları

Projeniz halihazırda örnek verilerle doldurulmuş durumdadır. Yerelde çalıştırmak için:

1. **Sanal Ortamı Aktif Edin:**
   - PowerShell: `.\venv\Scripts\Activate.ps1`
   - CMD (Komut İstemi): `.\venv\Scripts\activate.bat`

2. **Geliştirme Sunucusunu Başlatın:**
   ```bash
   python manage.py runserver
   ```
3. **Sitenize Giriş Yapın:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) adresine gidin.
4. **Yönetici Giriş Bilgileri:**
   - **Giriş Adresi:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
   - **Kullanıcı Adı:** `admin`
   - **Şifre:** `admin123`

---

## 2. PythonAnywhere Güncelleme Adımları (Yeni Özellikleri Yükleme)

Sitede yapılan yeni geliştirmeleri (Giriş Yapma, Yazı Ekleme, Düzenleme ve Silme) PythonAnywhere sunucunuza aktarmak için aşağıdaki adımları sırasıyla gerçekleştirin:

### Adım 1: Kodları GitHub'a Gönderin
Kendi bilgisayarınızdaki proje klasöründe terminal (PowerShell veya CMD) açıp şu komutları sırasıyla yazarak güncel kodları GitHub'a gönderin:
```bash
git add .
git commit -m "feat: giris yapma ve yazi ekleme-duzenleme ozellikleri"
git push
```

### Adım 2: Sunucuda Kodları Çekin ve Statik Dosyaları Derleyin
1. PythonAnywhere panelinizde **Consoles** sekmesinden **Bash** konsolunuzu açın.
2. Aşağıdaki komutları çalıştırarak güncel kodları çekin ve statik dosyaları güncelleyin:
   ```bash
   cd ~/OzlemUcarBlog
   git pull
   source venv/bin/activate
   python manage.py collectstatic --noinput
   ```

### Adım 3: Sitenizi Yeniden Başlatın
1. PythonAnywhere panelinizdeki **Web** sekmesine gidin.
2. Sayfanın en üstündeki yeşil **"Reload Renn000.pythonanywhere.com"** butonuna tıklayın.
3. Siteniz güncellenmiş haliyle yayında!

---

## 3. İlk Kurulum Adımları (Sıfırdan Kurulum Gerekirse)

Eğer projeyi sıfırdan başka bir PythonAnywhere hesabına kurmak isterseniz:

### Adım 1: PythonAnywhere Bash Konsolunda Klonlama ve venv
```bash
git clone https://github.com/ozlemucar29/OzlemUcarBlog.git
cd OzlemUcarBlog
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Adım 2: Veritabanı ve Statik Dosya Hazırlığı
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### Adım 3: PythonAnywhere Web Arayüzü Yapılandırması
1. **Web** sekmesinden **"Add a new web app"** deyin, **"Manual Configuration"** seçin ve **Python 3.12** seçin.
2. Dosya yollarını ayarlayın:
   - **Source code:** `/home/renn000/OzlemUcarBlog`
   - **Working directory:** `/home/renn000/OzlemUcarBlog`
   - **Virtualenv:** `/home/renn000/OzlemUcarBlog/venv`
3. **WSGI configuration file** linkine tıklayıp içindekileri şununla değiştirin (kodların başında hiç boşluk/girinti olmadığından emin olun):

```python
import os
import sys

path = '/home/renn000/OzlemUcarBlog'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'blog_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
4. **Static files** tablosuna iki satır ekleyin:
   - **URL:** `/static/`  |  **Directory:** `/home/renn000/OzlemUcarBlog/staticfiles`
   - **URL:** `/media/`  |  **Directory:** `/home/renn000/OzlemUcarBlog/media`
5. En üstteki yeşil **"Reload"** butonuna basın.
