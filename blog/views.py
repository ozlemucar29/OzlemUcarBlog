from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Category, Post, Comment, ContactMessage, Profile
from .forms import PostForm, UserRegisterForm, UserProfileForm, ProfileForm

def post_list(request):
    category_slug = request.GET.get('category', '')
    active_category = None
    
    if category_slug == 'onay':
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            posts = Post.objects.filter(status='draft')
            class DummyCategory:
                name = "Onay Bekleyenler"
                slug = "onay"
            active_category = DummyCategory()
        else:
            from django.http import Http404
            raise Http404("Bu sayfaya erişim yetkiniz yok.")
    else:
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                posts = Post.objects.filter(status='published')
            else:
                posts = Post.objects.filter(Q(status='published') | Q(author=request.user))
        else:
            posts = Post.objects.filter(status='published')
            
        if category_slug:
            active_category = get_object_or_404(Category, slug=category_slug)
            posts = posts.filter(category=active_category)
            
    categories = Category.objects.all()

    # 1. Search Query Filter
    query = request.GET.get('search', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )

    # 3. Pagination (6 posts per page)
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    try:
        page_posts = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_posts = paginator.get_page(1)

    context = {
        'posts': page_posts,
        'categories': categories,
        'active_category': active_category,
        'search_query': query,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Yazı taslak ise sadece yazarı veya yöneticiler (staff/superuser) görebilir
    can_view = post.status == 'published' or (
        request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_staff or post.author == request.user
        )
    )
    if not can_view:
        from django.http import Http404
        raise Http404("Bu yazı henüz yayınlanmamış veya görüntüleme yetkiniz yok.")
    
    # Increment views
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Comments: Yazar veya yöneticiler (staff/superuser) onay bekleyen yorumları da görebilir.
    is_manager = request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff or post.author == request.user)
    if is_manager:
        comments = post.comments.all()
    else:
        comments = post.comments.filter(is_approved=True)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.user.get_full_name() or request.user.username
            email = request.user.email or f"{request.user.username}@example.com"
            content = request.POST.get('content', '').strip()
        else:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            content = request.POST.get('content', '').strip()
        
        if name and email and content:
            # Yazar veya yönetici yorum yaptıysa doğrudan onaylı olarak kaydet
            is_approved = False
            if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff or post.author == request.user):
                is_approved = True
                
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content,
                is_approved=is_approved
            )
            if is_approved:
                messages.success(request, "Yorumunuz başarıyla yayınlandı!")
            else:
                messages.success(request, "Yorumunuz alındı! Yönetici onayından sonra yayınlanacaktır.")
            return redirect('post_detail', slug=post.slug)
        else:
            messages.error(request, "Lütfen yorum formundaki tüm alanları doldurun.")

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)


def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Mesajınız başarıyla gönderildi! Teşekkürler.")
            return redirect('contact')
        else:
            messages.error(request, "Lütfen tüm alanları doldurun.")
            
    return render(request, 'blog/contact.html')


# --- AUTHENTICATION VIEWS ---

def login_user(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Tekrar hoş geldiniz, {user.username}!")
            # Redirect to next parameter or home
            next_url = request.GET.get('next', 'post_list')
            return redirect(next_url)
        else:
            messages.error(request, "Hatalı kullanıcı adı veya şifre.")
            
    return render(request, 'blog/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('post_list')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.")
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request, 'blog/register.html', {'form': form})


# --- POST MANAGEMENT (CRUD) VIEWS ---

@login_required(login_url='login')
def post_create(request):
    is_staff = request.user.is_staff or request.user.is_superuser
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if not is_staff:
            form.fields.pop('status', None)
            
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if not is_staff:
                post.status = 'draft'
                post.save()
                messages.success(request, "Blog yazınız başarıyla oluşturuldu ve yönetici onayına gönderildi!")
                return redirect('post_list')
            else:
                post.save()
                messages.success(request, "Blog yazınız başarıyla oluşturuldu!")
                if post.status == 'published':
                    return redirect('post_detail', slug=post.slug)
                else:
                    return redirect('post_list')
    else:
        form = PostForm()
        if not is_staff:
            form.fields.pop('status', None)
        
    context = {
        'form': form,
        'title': 'Yeni Yazı Oluştur',
    }
    return render(request, 'blog/post_form.html', context)


@login_required(login_url='login')
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Security check: Ensure current logged user is author
    if post.author != request.user:
        messages.error(request, "Bu yazıyı düzenleme yetkiniz bulunmamaktadır.")
        return redirect('post_list')
        
    is_staff = request.user.is_staff or request.user.is_superuser
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if not is_staff:
            form.fields.pop('status', None)
            
        if form.is_valid():
            post = form.save(commit=False)
            if not is_staff:
                post.status = 'draft'
                post.save()
                messages.success(request, "Blog yazınız güncellendi ve yönetici onayına gönderildi!")
                return redirect('post_list')
            else:
                post.save()
                messages.success(request, "Blog yazınız başarıyla güncellendi!")
                if post.status == 'published':
                    return redirect('post_detail', slug=post.slug)
                else:
                    return redirect('post_list')
    else:
        form = PostForm(instance=post)
        if not is_staff:
            form.fields.pop('status', None)
        
    context = {
        'form': form,
        'title': 'Yazıyı Düzenle',
        'post': post,
    }
    return render(request, 'blog/post_form.html', context)


@login_required(login_url='login')
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Security check: Ensure current logged user is author
    if post.author != request.user:
        messages.error(request, "Bu yazıyı silme yetkiniz bulunmamaktadır.")
        return redirect('post_list')
        
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Blog yazısı başarıyla silindi.")
        return redirect('post_list')
        
    context = {
        'post': post
    }
    return render(request, 'blog/post_confirm_delete.html', context)


# --- COMMENT MANAGEMENT VIEWS ---

@login_required(login_url='login')
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Yetki kontrolü: süper kullanıcı, staff veya yazının yazarı
    if request.user.is_superuser or request.user.is_staff or comment.post.author == request.user:
        comment.is_approved = True
        comment.save()
        messages.success(request, "Yorum başarıyla onaylandı.")
    else:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
    return redirect('post_detail', slug=comment.post.slug)


@login_required(login_url='login')
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Yetki kontrolü: süper kullanıcı, staff veya yazının yazarı
    if request.user.is_superuser or request.user.is_staff or comment.post.author == request.user:
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, "Yorum başarıyla silindi.")
        return redirect('post_detail', slug=post_slug)
    else:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('post_detail', slug=comment.post.slug)


@login_required(login_url='login')
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profil bilgileriniz başarıyla güncellendi!")
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'blog/profile.html', context)


@login_required(login_url='login')
def post_approve(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Yetki kontrolü: Yalnızca yöneticiler (staff/superuser) onaylayabilir
    if request.user.is_superuser or request.user.is_staff:
        post.status = 'published'
        post.save()
        messages.success(request, f"'{post.title}' yazısı başarıyla onaylandı ve yayınlandı!")
        return redirect('post_detail', slug=post.slug)
    else:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('post_list')


@login_required(login_url='login')
def post_reject(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Yetki kontrolü: Yalnızca yöneticiler (staff/superuser) reddedebilir
    if request.user.is_superuser or request.user.is_staff:
        post.status = 'rejected'
        post.save()
        messages.success(request, f"'{post.title}' yazısı reddedildi.")
        return redirect('post_list')
    else:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('post_list')


@login_required(login_url='login')
def contact_messages(request):
    # Yetki kontrolü: Yalnızca yöneticiler (staff/superuser) görebilir
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Bu sayfaya erişim yetkiniz bulunmamaktadır.")
        return redirect('post_list')
        
    messages_list = ContactMessage.objects.all()
    context = {
        'contact_messages': messages_list
    }
    return render(request, 'blog/contact_messages.html', context)


@login_required(login_url='login')
def contact_message_read(request, pk):
    # Yetki kontrolü: Yalnızca yöneticiler (staff/superuser) okundu yapabilir
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('post_list')
        
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = True
    message.save()
    messages.success(request, "Mesaj okundu olarak işaretlendi.")
    return redirect('contact_messages')


@login_required(login_url='login')
def contact_message_delete(request, pk):
    # Yetki kontrolü: Yalnızca yöneticiler (staff/superuser) silebilir
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('post_list')
        
    message = get_object_or_404(ContactMessage, pk=pk)
    message.delete()
    messages.success(request, "Mesaj başarıyla silindi.")
    return redirect('contact_messages')

