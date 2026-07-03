import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_project.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, Post, Comment

def populate():
    print("Database seeding started...")
    
    # 1. Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("- Created superuser (username: admin, password: admin123)")
    else:
        print("- Superuser admin already exists.")

    # 2. Create Categories
    cat_yazilim, _ = Category.objects.get_or_create(name='Yazılım')
    cat_tasarim, _ = Category.objects.get_or_create(name='Tasarım')
    cat_pazarlama, _ = Category.objects.get_or_create(name='Dijital Pazarlama')
    print("- Created categories ('Yazılım', 'Tasarım', 'Dijital Pazarlama')")

    # 3. Create Posts
    user = User.objects.get(username='admin')

    post1_content = """Django ile web uygulaması geliştirmek günümüzde oldukça popüler. Django, 'hızlı geliştirme' (fast development) ve 'temiz, pragmatik tasarım' ilkeleriyle inşa edilmiş yüksek seviyeli bir Python web çatısıdır.

Neden Django Kullanmalısınız?
1. Güvenlik: Django, SQL enjeksiyonu, siteler arası betik çalıştırma (XSS), siteler arası istek sahteciliği (CSRF) gibi güvenlik açıklarından uygulamanızı otomatik olarak korur.
2. Ölçeklenebilirlik: En yoğun trafik alan siteler bile Django'nun esnek yapısı sayesinde kolayca ölçeklenebilir.
3. Kapsamlılık (Batteries Included): Veritabanı yönetim aracı (Admin panel), kimlik doğrulama sistemi, oturum yönetimi gibi ihtiyaç duyabileceğiniz birçok araç paketle birlikte gelir.

Bu yazıda Django ile yeni bir projeye nasıl başlanacağını ve temel dosya yapısını inceledik. Bir sonraki yazımızda veritabanı ilişkileri ve modeller üzerinde duracağız."""

    post1, created1 = Post.objects.get_or_create(
        title='Django ile Web Geliştirmeye Giriş',
        defaults={
            'author': user,
            'category': cat_yazilim,
            'summary': 'Django web çatısı ile sıfırdan modern web projeleri geliştirmek için bilmeniz gereken temel adımlar ve Django\'nun sunduğu benzersiz avantajlar.',
            'content': post1_content,
            'status': 'published',
        }
    )

    post2_content = """Kullanıcı deneyimi (UX) ve kullanıcı arayüzü (UI) tasarımı, bir web sitesinin başarısında en önemli rollerden birini üstlenir. Harika kodlanmış bir site bile, kullanıcı dostu olmayan bir tasarım nedeniyle ziyaretçi kaybedebilir.

2026 Tasarım Trendleri:
- Cam Morfizasyonu (Glassmorphism): Buzlu cam görünümü veren yarı şeffaf katmanlar ve neon renkli arka plan ışıkları.
- Karanlık Mod Önceliği: Göz yorgunluğunu azaltan ve pil tasarrufu sağlayan şık, koyu temalar.
- Mikro Etkileşimler: Kullanıcının butonlara tıklaması veya hover yapması durumunda devreye giren küçük, akıcı animasyonlar.

İyi bir tasarım, kullanıcının sitede daha fazla kalmasını ve sunulan içeriğe daha rahat odaklanmasını sağlar. Bu yazımızda, modern tasarım prensiplerini ve blog sitemizde uyguladığımız teknikleri ele alacağız."""

    post2, created2 = Post.objects.get_or_create(
        title='Kullanıcı Deneyimi ve Modern Arayüz Tasarımı',
        defaults={
            'author': user,
            'category': cat_tasarim,
            'summary': 'Web sitelerinde kullanıcı deneyimini (UX) artıracak modern tasarım teknikleri, cam morfizasyonu ve etkileşimli öğelerin önemi.',
            'content': post2_content,
            'status': 'published',
        }
    )

    post3_content = """CSS (Cascading Style Sheets), web geliştirmenin en temel taşlarından biridir. CSS Grid ve Flexbox gibi modern araçlar sayesinde artık çok karmaşık düzenleri bile birkaç satır kodla oluşturmak mümkün.

Bu yazımızda, blog sitemiz için geliştirdiğimiz Vanilla CSS yapısını ve responsive ızgara (grid) sistemlerini yakından inceliyoruz. Sadece CSS kullanarak nasıl harika temalar ve responsive menüler oluşturabileceğinizi kod örnekleriyle göreceğiz."""

    post3, created3 = Post.objects.get_or_create(
        title='Vanilla CSS ile Responsive Tasarımın Gücü',
        defaults={
            'author': user,
            'category': cat_tasarim,
            'summary': 'Framework kullanmadan, saf CSS (Vanilla CSS) ile modern, responsive ve performansı yüksek web düzenleri kurma teknikleri.',
            'content': post3_content,
            'status': 'published',
        }
    )
    post4_content = """Başarılı bir blog yazarı olmak sadece yazı yazmaktan ibaret değildir. İçeriğinizi doğru kitleye ulaştırmak, okuyucularınızla etkileşim kurmak ve düzenli bir yayın takvimi takip etmek başarının anahtarıdır.

Kitlenizi Büyütmenin Yolları:
1. Düzenli İçerik Üretimi: Okuyucularınızın sitenizi ne zaman ziyaret edeceklerini bilmeleri önemlidir. Haftada en az bir veya iki kaliteli yazı yayınlayın.
2. Sosyal Medya Kullanımı: Yazılarınızı Twitter, LinkedIn ve Instagram gibi platformlarda paylaşarak görünürlüğünüzü artırın.
3. Yorumlara Yanıt Verin: Okuyucularınızın yorumlarına samimi ve bilgilendirici yanıtlar vererek topluluk bilinci oluşturun.

Kişisel blogunuzda kendi sesinizi bulmak zaman alacaktır, ancak samimi ve özgün içerikler her zaman doğru okuyucuları çekecektir."""

    post4, created4 = Post.objects.get_or_create(
        title='Blog Yazarak Kendi Kitlenizi Nasıl Oluşturursunuz?',
        defaults={
            'author': user,
            'category': cat_pazarlama,
            'summary': 'Kişisel bir blog kurduktan sonra düzenli içerik üretimi ve doğru stratejilerle sadık bir okuyucu kitlesi oluşturmanın pratik yolları.',
            'content': post4_content,
            'status': 'published',
        }
    )

    post5_content = """Arama Motoru Optimizasyonu (SEO), blogunuzun Google gibi arama motorlarında organik olarak üst sıralarda yer almasını sağlayan tekniklerin bütünüdür. Harika içerikler yazsanız bile, eğer arama motorları sitenizi doğru tarayamazsa hak ettiğiniz trafiği alamazsınız.

Temel SEO Adımları:
1. Anahtar Kelime Araştırması: Okuyucuların hangi terimleri arattığını öğrenin ve yazı başlıklarınızı buna göre seçin.
2. Temiz Kod Yapısı ve Hız: Django gibi hızlı web çatısı kullanmak ve resimleri optimize etmek site hızını artırarak SEO puanınızı iyileştirir.
3. Mobil Uyum (Responsive): Ziyaretçilerin büyük çoğunluğu mobil cihazlardan geldiği için sitenizin tüm ekranlarda kusursuz görünmesi şarttır.

SEO uzun vadeli bir süreçtir, sabırlı ve düzenli çalışmalarla meyvesini mutlaka verecektir."""

    post5, created5 = Post.objects.get_or_create(
        title='Blog Siteleri İçin Temel SEO Rehberi',
        defaults={
            'author': user,
            'category': cat_pazarlama,
            'summary': 'Blog yazılarınızın arama motorlarında daha üst sıralarda yer alması için uygulayabileceğiniz temel SEO teknikleri ve ipuçları.',
            'content': post5_content,
            'status': 'published',
        }
    )

    post6_content = """Django REST Framework (DRF), Django kullanarak hızlı ve güvenli API\'ler (Uygulama Programlama Arayüzleri) geliştirmek için en popüler araçtır. Günümüzde modern web uygulamalarında backend ile frontend (React, Vue, mobil uygulamalar vb.) arasındaki iletişim API\'ler üzerinden sağlanır.

Neden Django REST Framework?
- Güçlü Serializer yapısı sayesinde veritabanı modellerini kolayca JSON formatına dönüştürür.
- Hazır yetkilendirme (Authentication) ve izin (Permissions) mekanizmaları sunar.
- API belgelerini (Browsable API) otomatik olarak tarayıcıda görselleştirebilirsiniz.

Bu yazıda DRF kurulumunu yapıp ilk basit API endpoint\'imizi (yazı listeleme API\'si) nasıl oluşturacağımızı adım adım inceleyeceğiz."""

    post6, created6 = Post.objects.get_or_create(
        title='Django REST Framework ile API Geliştirmeye Giriş',
        defaults={
            'author': user,
            'category': cat_yazilim,
            'summary': 'Django projelerinizi dış dünyaya açmak veya modern ön yüz framework\'leri ile bağlamak için Django REST Framework kullanarak ilk API endpoint\'inizi yazın.',
            'content': post6_content,
            'status': 'published',
        }
    )

    print("- Seeded 6 blog posts")

    # 4. Create Comment if post created
    Comment.objects.get_or_create(
        post=post1,
        name='Ahmet Yılmaz',
        email='ahmet@ornek.com',
        defaults={
            'content': 'Harika bir başlangıç rehberi olmuş Özlem Hanım. Django ile ilgili sonraki yazıları sabırsızlıkla bekliyorum!',
            'is_approved': True
        }
    )
    print("- Seeded sample comments")
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    populate()
