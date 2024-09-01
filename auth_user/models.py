from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, Group, Permission



class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError('Email Address is Required')
            
        if not password:
            raise ValueError('Password is Required')

   
        try:
            user = self.model(
                email = self.normalize_email(email),
                
                *args,
                **kwargs
            )
        
            user.set_password(password)
            user.save()
            
            return user
        except:
               raise ValueError('An Error Occured Please Try Again')         
        

    def create_superuser(self, email, first_name, password=None, *args, **kwargs):
        try:
            user = self.create_user(
                    email,
                    first_name = first_name,
                    password=password,
                    is_admin=True,
                    is_superuser=True,
                    is_staff=True,
                    *args,
                    **kwargs
            )
            
            return user
        except:
               raise ValueError('An Error Occured Please Try Again')  


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username =None
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
   
    def __str__(self):
        return self.first_name




class BlacklistedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    class Meta:
        db_table = 'blacklisted_tokens'
 


