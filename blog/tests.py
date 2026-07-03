from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Post, Comment, ContactMessage

class BlogViewsTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        # Create second user for authorization tests
        self.other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='password123')
        
        # Create category
        self.category = Category.objects.create(name='Test Kategori')
        
        # Create post
        self.post = Post.objects.create(
            title='Test Basligi',
            author=self.user,
            category=self.category,
            summary='Test ozetidir.',
            content='Test icerigidir.',
            status='published'
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Basligi')
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_detail_view(self):
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test icerigidir.')
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_about_view(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/about.html')

    def test_contact_view_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/contact.html')

    def test_contact_view_post(self):
        data = {
            'name': 'Kemal Yilmaz',
            'email': 'kemal@test.com',
            'subject': 'Test Konusu',
            'message': 'Test mesaji icerigi.'
        }
        response = self.client.post(reverse('contact'), data)
        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Kemal Yilmaz')
        self.assertEqual(msg.subject, 'Test Konusu')

    # --- PHASE 2 TESTS ---

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/login.html')

    def test_login_view_post_success(self):
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, reverse('post_list'))
        # Check if session is logged in
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_view_post_fail(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/login.html')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('post_list'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_post_create_view_anonymous_redirect(self):
        response = self.client.get(reverse('post_create'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post_create')}")

    def test_post_create_view_regular_user_draft_success(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'title': 'Yeni Olusturulan Yazi',
            'category': self.category.id,
            'summary': 'Yeni yazi ozeti.',
            'content': 'Yeni yazi icerigi buradadir.',
            'status': 'published'  # even if 'published' is passed, it should be forced to draft
        }
        response = self.client.post(reverse('post_create'), data)
        self.assertEqual(Post.objects.filter(title='Yeni Olusturulan Yazi').count(), 1)
        new_post = Post.objects.get(title='Yeni Olusturulan Yazi')
        self.assertEqual(new_post.status, 'draft')  # should be draft
        self.assertRedirects(response, reverse('post_list'))  # should redirect to post_list
        self.assertEqual(new_post.author, self.user)

    def test_post_create_view_staff_published_success(self):
        # Make user staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        data = {
            'title': 'Staff Yazisi',
            'category': self.category.id,
            'summary': 'Staff yazi ozeti.',
            'content': 'Staff yazi icerigi.',
            'status': 'published'
        }
        response = self.client.post(reverse('post_create'), data)
        self.assertEqual(Post.objects.filter(title='Staff Yazisi').count(), 1)
        new_post = Post.objects.get(title='Staff Yazisi')
        self.assertEqual(new_post.status, 'published')  # should be published
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': new_post.slug}))
        self.assertEqual(new_post.author, self.user)

    def test_post_update_view_anonymous_redirect(self):
        response = self.client.get(reverse('post_edit', kwargs={'slug': self.post.slug}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post_edit', kwargs={'slug': self.post.slug})}")

    def test_post_update_view_non_author_redirect(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('post_edit', kwargs={'slug': self.post.slug}))
        self.assertRedirects(response, reverse('post_list'))

    def test_post_update_view_author_success(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'title': 'Guncellenmis Baslik',
            'category': self.category.id,
            'summary': 'Guncellenmis ozet.',
            'content': 'Guncellenmis icerik.',
            'status': 'published'  # gets forced to draft
        }
        response = self.client.post(reverse('post_edit', kwargs={'slug': self.post.slug}), data)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Guncellenmis Baslik')
        self.assertEqual(self.post.status, 'draft')  # becomes draft
        self.assertRedirects(response, reverse('post_list'))  # redirects to post_list

    def test_post_update_view_staff_success(self):
        # Make user staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        data = {
            'title': 'Staff Guncellenmis Baslik',
            'category': self.category.id,
            'summary': 'Guncellenmis ozet.',
            'content': 'Guncellenmis icerik.',
            'status': 'published'
        }
        response = self.client.post(reverse('post_edit', kwargs={'slug': self.post.slug}), data)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Staff Guncellenmis Baslik')
        self.assertEqual(self.post.status, 'published')  # stays published
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))

    def test_post_delete_view_anonymous_redirect(self):
        response = self.client.post(reverse('post_delete', kwargs={'slug': self.post.slug}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post_delete', kwargs={'slug': self.post.slug})}")

    def test_post_delete_view_non_author_redirect(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(reverse('post_delete', kwargs={'slug': self.post.slug}))
        self.assertRedirects(response, reverse('post_list'))

    def test_post_delete_view_author_success(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('post_delete', kwargs={'slug': self.post.slug}))
        self.assertRedirects(response, reverse('post_list'))
        self.assertEqual(Post.objects.filter(slug=self.post.slug).count(), 0)

    # --- PHASE 3 TESTS (REGISTRATION & COMMENT MANAGEMENT) ---

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html')

    def test_register_view_post_success(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'Yeni',
            'last_name': 'Kullanici',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_password_mismatch(self):
        data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'first_name': 'Yeni',
            'last_name': 'Kullanici',
            'password': 'newpassword123',
            'password_confirm': 'mismatch'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html')
        self.assertFalse(User.objects.filter(username='newuser2').exists())

    def test_guest_comment_requires_approval(self):
        # Visitor comments
        data = {
            'name': 'Ziyaretci',
            'email': 'ziyaretci@example.com',
            'content': 'Ziyaretci yorumu.'
        }
        response = self.client.post(reverse('post_detail', kwargs={'slug': self.post.slug}), data, HTTP_HOST='localhost')
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        
        # Verify comment is created but not approved
        self.assertEqual(Comment.objects.filter(name='Ziyaretci').count(), 1)
        comment = Comment.objects.get(name='Ziyaretci')
        self.assertFalse(comment.is_approved)
        
        # Verify it doesn't show up for other guests
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.post.slug}), HTTP_HOST='localhost')
        self.assertNotContains(response, 'Ziyaretci yorumu.')

    def test_admin_comment_auto_approved(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'content': 'Yazar/Admin yorumu.'
        }
        response = self.client.post(reverse('post_detail', kwargs={'slug': self.post.slug}), data, HTTP_HOST='localhost')
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        
        # Verify comment is created and auto-approved
        comment = Comment.objects.get(content='Yazar/Admin yorumu.')
        self.assertTrue(comment.is_approved)

    def test_comment_approve_by_admin(self):
        # Create unapproved comment
        comment = Comment.objects.create(
            post=self.post,
            name='Misafir',
            email='misafir@example.com',
            content='Bekleyen yorum.',
            is_approved=False
        )
        
        # Try to approve without login
        response = self.client.get(reverse('comment_approve', kwargs={'pk': comment.pk}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('comment_approve', kwargs={'pk': comment.pk})}")
        
        # Login and approve
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('comment_approve', kwargs={'pk': comment.pk}))
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        
        comment.refresh_from_db()
        self.assertTrue(comment.is_approved)

    def test_comment_delete_by_admin(self):
        # Create comment
        comment = Comment.objects.create(
            post=self.post,
            name='Misafir',
            email='misafir@example.com',
            content='Silinecek yorum.',
            is_approved=True
        )
        
        # Login and delete
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('comment_delete', kwargs={'pk': comment.pk}))
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(Comment.objects.filter(pk=comment.pk).count(), 0)

    # --- NEW PROFILE & POST APPROVAL TESTS ---

    def test_profile_edit_view_anonymous_redirect(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_edit_view_get(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/profile.html')
        self.assertContains(response, 'testuser@example.com')

    def test_profile_edit_view_post_success(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'first_name': 'Ahmet',
            'last_name': 'Yurt',
            'email': 'ahmet@example.com',
            'title': 'Yazilimci',
            'bio': 'Test biyografisi.'
        }
        response = self.client.post(reverse('profile'), data)
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Ahmet')
        self.assertEqual(self.user.email, 'ahmet@example.com')
        self.assertEqual(self.user.profile.title, 'Yazilimci')

    def test_profile_edit_view_post_email_taken(self):
        # other_user has email otheruser@example.com
        self.client.login(username='testuser', password='password123')
        data = {
            'first_name': 'Ahmet',
            'last_name': 'Yurt',
            'email': 'otheruser@example.com',
            'title': '',
            'bio': ''
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/profile.html')
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, 'otheruser@example.com')

    def test_post_approve_view(self):
        # Create a draft post
        draft_post = Post.objects.create(
            title='Taslak Yazi',
            author=self.user,
            category=self.category,
            summary='Taslak ozeti.',
            content='Taslak icerigi.',
            status='draft'
        )
        
        # Try to approve without login
        response = self.client.get(reverse('post_approve', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post_approve', kwargs={'slug': draft_post.slug})}")
        
        # Try to approve as regular user
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('post_approve', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, reverse('post_list'))
        draft_post.refresh_from_db()
        self.assertEqual(draft_post.status, 'draft')
        
        # Approve as staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('post_approve', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': draft_post.slug}))
        draft_post.refresh_from_db()
        self.assertEqual(draft_post.status, 'published')

    def test_post_reject_view(self):
        # Create a draft post
        draft_post = Post.objects.create(
            title='Reddedilecek Yazi',
            author=self.user,
            category=self.category,
            summary='Ozeti.',
            content='Icerigi.',
            status='draft'
        )
        
        # Try to reject without login
        response = self.client.get(reverse('post_reject', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('post_reject', kwargs={'slug': draft_post.slug})}")
        
        # Try to reject as regular user
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('post_reject', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, reverse('post_list'))
        draft_post.refresh_from_db()
        self.assertEqual(draft_post.status, 'draft')
        
        # Reject as staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('post_reject', kwargs={'slug': draft_post.slug}))
        self.assertRedirects(response, reverse('post_list'))
        draft_post.refresh_from_db()
        self.assertEqual(draft_post.status, 'rejected')

    def test_post_list_visibility_for_drafts(self):
        # Create a draft post by otheruser
        draft_post = Post.objects.create(
            title='Other User Taslak',
            author=self.other_user,
            category=self.category,
            summary='Ozeti.',
            content='Icerigi.',
            status='draft'
        )
        
        # Guest sees only published (1 post from setUp)
        response = self.client.get(reverse('post_list'))
        self.assertNotContains(response, 'Other User Taslak')
        
        # otheruser sees their own draft
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('post_list'))
        self.assertContains(response, 'Other User Taslak')
        
        # testuser (not author, not staff) does not see otheruser's draft
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('post_list'))
        self.assertNotContains(response, 'Other User Taslak')
        
        # staff user does not see draft on default page
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('post_list'))
        self.assertNotContains(response, 'Other User Taslak')

        # staff user sees draft on category=onay page
        response = self.client.get(reverse('post_list') + '?category=onay')
        self.assertContains(response, 'Other User Taslak')

    def test_post_detail_draft_access_control(self):
        draft_post = Post.objects.create(
            title='Gizli Taslak',
            author=self.user,
            category=self.category,
            summary='Ozeti.',
            content='Icerigi.',
            status='draft'
        )
        
        # Guest gets 404
        response = self.client.get(reverse('post_detail', kwargs={'slug': draft_post.slug}))
        self.assertEqual(response.status_code, 404)
        
        # otheruser (non-author, non-staff) gets 404
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('post_detail', kwargs={'slug': draft_post.slug}))
        self.assertEqual(response.status_code, 404)
        
        # testuser (author) gets 200
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('post_detail', kwargs={'slug': draft_post.slug}))
        self.assertEqual(response.status_code, 200)

    # --- CONTACT MESSAGES DASHBOARD TESTS ---

    def test_contact_messages_list_view_anonymous_redirect(self):
        response = self.client.get(reverse('contact_messages'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('contact_messages')}")

    def test_contact_messages_list_view_regular_user_redirect(self):
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(reverse('contact_messages'))
        self.assertRedirects(response, reverse('post_list'))

    def test_contact_messages_list_view_staff_success(self):
        # Create a contact message
        msg = ContactMessage.objects.create(
            name='Gonderen Kisi',
            email='gonderen@test.com',
            subject='Baslik',
            message='Icerik'
        )
        # Make user staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('contact_messages'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/contact_messages.html')
        self.assertContains(response, 'Gonderen Kisi')
        self.assertContains(response, 'Baslik')

    def test_contact_message_read_view(self):
        msg = ContactMessage.objects.create(
            name='Gonderen Kisi',
            email='gonderen@test.com',
            subject='Baslik',
            message='Icerik',
            is_read=False
        )
        # Make user staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('contact_message_read', kwargs={'pk': msg.pk}))
        self.assertRedirects(response, reverse('contact_messages'))
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_contact_message_delete_view(self):
        msg = ContactMessage.objects.create(
            name='Gonderen Kisi',
            email='gonderen@test.com',
            subject='Baslik',
            message='Icerik'
        )
        # Make user staff
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('contact_message_delete', kwargs={'pk': msg.pk}))
        self.assertRedirects(response, reverse('contact_messages'))
        self.assertEqual(ContactMessage.objects.filter(pk=msg.pk).count(), 0)
