from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import user , review , picture , product , reservation




@api_view(('POST'))
@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data["username"]
        email = data["email"]
        password = data["password"]
        number = data["number"]
        category = data["category"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        if password == "" or email == "" or username == "" or number == "" or category == "":
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data= {
                "message": "fields are required."
            })
        
        
        try:
            newuser = user.objects.create_user(email=email , password=password , category=category , username=username , number=number , first_name=first_name , last_name=last_name)
            newuser.save()
        except IntegrityError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Email address already taken."
            })
        
        
        refresh = RefreshToken.for_user(newuser)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "User created successfully.",
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
    
@api_view(('GET'))
@csrf_exempt
def search(request):
    if request.method == "GET":
        data = json.loads(request.body)
        query = data["search"]
        products = product.objects.filter(name__icontains=query)
        response = []
        for product in products:
            response.append({
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "seller": product.seller.email,
                "category": product.category
            })
        return Response(status=status.HTTP_200_OK, data= {
            "products": response
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "GET request required."
        })
    

    
@api_view(('POST'))
@csrf_exempt
def addProduct(request):
    if request.method == "POST" and request.user.category == "seller":
        data = json.loads(request.body)
        name = data["name"]
        description = data["description"]
        price = data["price"]
        category = data["category"]
        seller = data["seller"]
        quantity = data["quantity"]
        if name == "" or description == "" or price == "" or category == "" or seller == "":
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data= {
                "message": "All fields are required."
            })
        
        try:
            newproduct = product.objects.create(name=name , description=description , price=price , category=category , seller=seller , quantity=quantity)
            if "product_type" in data:
                newproduct.product_type = data["product_type"]
            newproduct.save()
        except IntegrityError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Product already exists."
            })
        
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "Product added successfully."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })


def addReview(request):
    if request.method == "POST" and request.user.category == "user":
        data = json.loads(request.body)
        product_id = data["product_id"]
        rating = data["rating"]
        review = data["review"]
        
        try:
            product = product.objects.get(id=product_id)
        except product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "Product not found."
            })
        
        newreview = review.objects.create(user=request.user , product=product , rating=rating , review=review)
        newreview.save()
        
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "Review added successfully."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
@api_view(('POST'))
@csrf_exempt
def addPicture(request):
    if request.method == "POST" and request.user.category == "seller":
        data = json.loads(request.body)
        image = data["image"]
        product_id = data["product_id"]
        
        try:
            product = product.objects.get(id=product_id)
        except product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "Product not found."
            })
        
        newpicture = picture.objects.create(image=image , product=product)
        newpicture.save()
        
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "Picture added successfully."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
    
@api_view(('POST'))
@csrf_exempt
def reserveProduct(request):
    if request.method == "POST" and request.user.category == "user":
        data = json.loads(request.body)
        product_id = data["product_id"]
        quantity = data["quantity"]
        
        try:
            product = product.objects.get(id=product_id)
        except product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "Product not found."
            })
        
        if product.quantity < quantity:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Not enough quantity."
            })
        
        newreservation = reservation.objects.create(user=request.user , product=product , quantity=quantity)
        newreservation.save()

        product.quantity -= quantity
        product.save()
        
        return Response(status=status.HTTP_201_CREATED, data= {
            "message": "Product reserved successfully."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })


