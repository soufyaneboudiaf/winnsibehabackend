from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import user , review , picture , product , reservation
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail



@api_view(['POST'])
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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
    

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

    



@api_view(['POST'])
@csrf_exempt
def login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]
        password = data["password"]
        
        if email == "" or password == "":
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data= {
                "message": "fields are required."
            })
        
        user = authenticate(email=email , password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response(status=status.HTTP_200_OK, data= {
                "message": "User logged in successfully.",
                "access_token": access_token,
                "refresh_token": refresh_token
            })
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Invalid credentials."
            })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })


@api_view(['POST'])
@csrf_exempt
def logout(request):
    if request.method == "POST":
        data = json.loads(request.body)
        refresh_token = data["refresh_token"]
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Invalid token."
            })
        
        return Response(status=status.HTTP_200_OK, data= {
            "message": "User logged out successfully."
        })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
    


@api_view(['POST'])
@csrf_exempt
def favoris(request):
    if request.method == "POST" and request.user.category == "user":
        data = json.loads(request.body)
        product_id = data["product_id"]
        
        try:
            product = product.objects.get(id=product_id)
        except product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "Product not found."
            })
        
        request.user.favoris.add(product)
        
        return Response(status=status.HTTP_200_OK, data= {
            "message": "Product added to favoris."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
    

@api_view(['Post'])
@csrf_exempt
def forgetpasssword(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]    
        
        try:
            user = user.objects.get(email=email)
        except user.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "User not found."
            })
        
        return Response(status=status.HTTP_200_OK, data= {
        "message": "Password sent to email."
        })
    
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })
    
@api_view(['POST'])
@csrf_exempt
def sign_in(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]
        password = data["password"]
        if email == "" or password == "":
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data= {
                "message": "fields are required."
            })
        
        user = authenticate(email=email , password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response(status=status.HTTP_200_OK, data= {
                "message": "User logged in successfully.",
                "access_token": access_token,
                "refresh_token": refresh_token
            })
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Invalid credentials."
            })
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST , data= {
            "message": "POST request required."
        })




# @api_view(['POST'])
# @csrf_exempt
# def sign_in_with_google(reqeuest):
#     if reqeuest.method == "POST":
#     
#
#
#
#
#
#
#
#
#
#
#
#
#

    

@api_view(['POST' , 'GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def reserveProduct(request , requestId):
    if request.method == "POST":
        
        data = json.loads(request.body)
        firstName = data["firstName"]
        lastName = data["lastName"]       
        wilaya = data["wilaya"]
        commune = data["commune"]
        phone_number = data["phone_number"]

        try:
            product = product.objects.get(id=requestId)
        except product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data= {
                "message": "Product not found."
            })
        try :
            
            reservation = reservation.objects.create(product=product , seller=product.seller , firstName=firstName , lastName=lastName , phone_number=phone_number , wilaya=wilaya , commune=commune)
            reservation.save()
        except IntegrityError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data= {
                "message": "Reservation already exists."
            })
        message = "New reservation from " + firstName + " " + lastName + " for " + product.name + " by " + request.user.email + 'wilaya : ' + wilaya + 'commune : ' + commune + 'phone number : ' + phone_number
        send_mail(
            'New reservation',  # subject
            message,  # message
            "winsibeha@gmail.com",  # from email
            [product.seller.email],  # to email
            fail_silently=False,
        )

        
            