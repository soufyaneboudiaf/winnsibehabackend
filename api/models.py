from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class user(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    category = models.CharField(max_length=20 , default="user")# user | seller
    location = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20 , null=True)
    is_staff = models.BooleanField(default=True)  # Add this line
    is_superuser = models.BooleanField(default=True)  # Add this line
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email


class review(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    product = models.ForeignKey('product', on_delete=models.CASCADE)
    rating = models.FloatField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class picture(models.Model):
    image = models.CharField(max_length=100)
    product = models.ForeignKey('product' , on_delete=models.CASCADE)

    def __str__(self):
        return self.image.url



class product(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField()
    description = models.TextField()
    price = models.FloatField()
    seller = models.ForeignKey(user, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0)
    product_type = models.CharField(max_length=20 , default="product")# product | service

    

    def __str__(self):
        return self.name





class reservation(models.Model):
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    seller = models.ForeignKey(user, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    wilaya = models.CharField(max_length=20)
    commune = models.CharField(max_length=20)




