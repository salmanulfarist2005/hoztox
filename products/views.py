from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger(__name__) 
from datetime import datetime 
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny   
from django.contrib.auth import get_user_model
from urllib.parse import unquote
user_model = get_user_model()
import csv
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile   
logger.setLevel(logging.DEBUG)  
handler = logging.StreamHandler() 
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
from rest_framework import generics, permissions, status
from django.core.mail import send_mail
from django.conf import settings 
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum   
from django.utils.timezone import localtime
from django.db.models.functions import Replace, Lower
from django.db.models import Value
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import csv
import os
from .models import Product, Category, UserType, Media
from .serializers import MediaSerializer
import django.db.models as models
 


class UserTypeListCreateView(generics.ListCreateAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer



class UserTypeListView(generics.ListAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

    def list(self, request, *args, **kwargs):
     
        response = super().list(request, *args, **kwargs)
        
 
        print("Response Data:", response.data)   
        
   
        return response
 
class UserTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer
    
class CategoryCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve categories and order by ID
        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None

    def get(self, request, id, *args, **kwargs):
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id, *args, **kwargs):
        print("request.data", request.data)
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwargs):
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    
    
    
 



class ProductListCreateView(APIView):
    def post(self, request):
        print("Request Data:", request.data)

       
        if Product.objects.filter(SKU=request.data.get('SKU').strip()).exists():
            return Response({"error": "Product with this SKU already exists."}, status=status.HTTP_400_BAD_REQUEST)

        usertypes = request.data.getlist('usertypes')
        cleaned_usertypes = [int(u) for u in usertypes if u.isdigit()]

        usertype_instances = UserType.objects.filter(id__in=cleaned_usertypes)
        if len(usertype_instances) != len(cleaned_usertypes):
            raise ValidationError("One or more user types do not exist.")

        cleaned_data = {
            'SKU': request.data.get('SKU').strip(),  
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
            'color': request.data.get('color'),
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),           
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
            'product_image': request.FILES.get('product_image'),
        }

        serializer = ProductSerializer(data=cleaned_data)

        if serializer.is_valid():
            product = serializer.save()

        
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                ProductMultipleImages.objects.create(product=product, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
 
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
      
        return Response(serializer.data, status=status.HTTP_200_OK)
 


class ProductuserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):      
        current_user_usertype = request.user.usertypes  
        products = Product.objects.filter(usertypes=current_user_usertype)      
        serializer = ProductListSerializer(products, many=True)    
        return Response(serializer.data)

 
class ProductUpdateView(APIView):
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

  
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)

 
        usertypes = request.data.get('usertypes', '').split(',')
        cleaned_usertypes = [int(u.strip()) for u in usertypes if u.strip().isdigit()]

     
        cleaned_data = {
            'SKU': request.data.get('SKU'),
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
            'color': request.data.get('color'),
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
          
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
        }

       
        product_image = request.FILES.get('product_image')
        if product_image:
            cleaned_data['product_image'] = product_image

        
        additional_images = request.FILES.getlist('additional_images')
        print("Additional Images Received:", additional_images)

     
        images_to_remove = request.data.getlist('images_to_remove[]')
        print("Images to Remove:", images_to_remove)

        
        serializer = ProductSerializer(product, data=cleaned_data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

   
            if images_to_remove:
                ProductMultipleImages.objects.filter(id__in=images_to_remove, product=product).delete()
        
            for image in additional_images:
                ProductMultipleImages.objects.create(product=product, image=image)  
                        
            updated_product = Product.objects.prefetch_related('additional_images').get(pk=product.pk)
            updated_serializer = ProductSerializer(updated_product)
            print("Product updated successfully:", updated_serializer.data)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductDeleteView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    def delete(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get image path of the product
        image_field = product.product_image
        image_name = image_field.name if image_field else None

        # Check if the image exists in Media model
        if image_name:
            image_in_media = Media.objects.filter(image=image_name).exists()

            # If the image is not managed by Media, delete it
            if not image_in_media and default_storage.exists(image_name):
                image_field.delete(save=False)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
    #***************************************************************************************************************************************
    
    
    
class CustomizedProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomizedProduct.objects.all()
    serializer_class = CustomizedProductListSerializer
    
    
    


class CustomizedProductListCreateView(APIView):
    def post(self, request):
        print("Request Data:", request.data)

       
        if CustomizedProduct.objects.filter(SKU=request.data.get('SKU').strip()).exists():
            return Response({"error": "Product with this SKU already exists."}, status=status.HTTP_400_BAD_REQUEST)

        usertypes = request.data.getlist('usertypes')
        cleaned_usertypes = [int(u) for u in usertypes if u.isdigit()]

        usertype_instances = UserType.objects.filter(id__in=cleaned_usertypes)
        if len(usertype_instances) != len(cleaned_usertypes):
            raise ValidationError("One or more user types do not exist.")

        cleaned_data = {
            'SKU': request.data.get('SKU').strip(),  
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
           
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
       
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
            'product_image': request.FILES.get('product_image'),
        }

        serializer = CustomizedProductSerializer(data=cleaned_data)

        if serializer.is_valid():
            product = serializer.save()

        
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                CustomizedProductMultipleImages.objects.create(product=product, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
 
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomizedProductListView(APIView):
    def get(self, request):
        products = CustomizedProduct.objects.all()
        serializer = CustomizedProductListSerializer(products, many=True)
        print("serializer.data",serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
 

class CustomProductuserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
  
        current_user_usertype = request.user.usertypes
  
        products = CustomizedProduct.objects.filter(usertypes=current_user_usertype)  
        print("Fetched Products:", products)     
        serializer = CustomizedProductListSerializer(products, many=True) 
        print("Serialized Product Data:", serializer.data)   
        return Response(serializer.data)

 
class CustomizedProductUpdateView(APIView):
    def put(self, request, pk):
        try:
            product = CustomizedProduct.objects.get(pk=pk)
        except CustomizedProduct.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)         
        usertypes = request.data.get('usertypes', '').split(',')
        cleaned_usertypes = [int(u.strip()) for u in usertypes if u.strip().isdigit()]

        cleaned_data = {
            'SKU': request.data.get('SKU'),
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
           
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
        
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
        }

        product_image = request.FILES.get('product_image')
        if product_image:
            cleaned_data['product_image'] = product_image

        additional_images = request.FILES.getlist('additional_images')
        print("Additional Images Received:", additional_images)

        images_to_remove = request.data.getlist('images_to_remove[]')
        print("Images to Remove:", images_to_remove)

        serializer = CustomizedProductSerializer(product, data=cleaned_data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            if images_to_remove:
                CustomizedProductMultipleImages.objects.filter(id__in=images_to_remove, product=product).delete()

            for image in additional_images:
                CustomizedProductMultipleImages.objects.create(product=product, image=image)

            updated_product = CustomizedProduct.objects.prefetch_related('additional_images').get(pk=product.pk)
            updated_serializer = CustomizedProductSerializer(updated_product)

            print("Product updated successfully:", updated_serializer.data)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomizedProductDeleteView(APIView):

    def get_object(self, id):
        try:
            return CustomizedProduct.objects.get(id=id)
        except CustomizedProduct.DoesNotExist:
            return None

    def delete(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
 
        if product.product_image:
            product.product_image.delete(save=False)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



 

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        print("Incoming Data:", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # This ensures even if the frontend sends false, we ignore it
        serializer.validated_data['is_active'] = True  

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()   
        print("Queryset:", users)   
        
        serializer = self.get_serializer(users, many=True)
        print("serializer.data",serializer.data)
        return Response(serializer.data)  
    

   
 

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'id'

    def get_object(self):

        return super().get_object()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

    
        print("Incoming Request Data:", request.data)

     
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

     
        if serializer.is_valid():
            self.perform_update(serializer)
            print("Updated User Data:", serializer.data)
            return Response(serializer.data)

       
        print("Update Errors:", serializer.errors)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer  

    def delete(self, request, *args, **kwargs):
        user = self.get_object()  
        user.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
    

 



class AdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        logger.info(f"Attempting to login user with email: {email}")

        if email is None or password is None:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        logger.warning(f"Failed login attempt for user: {email}")
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


 
 

class ChangePasswordView(APIView):
    def put(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Both new password and confirm password must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'},
                            status=status.HTTP_400_BAD_REQUEST)

      
        admin_users = User.objects.filter(is_staff=True, is_superuser=True)

        if not admin_users.exists():
            return Response({'error': 'No admin users found.'},
                            status=status.HTTP_404_NOT_FOUND)

       
        for admin_user in admin_users:
        
            print(f"Admin User Data:")
            print(f"Email: {admin_user.email}")
            print(f"Full Name: {admin_user.full_name}")
            print(f"Mobile Number: {admin_user.mobile_number}")
            print(f"Is Staff: {admin_user.is_staff}")
            print(f"Is Superuser: {admin_user.is_superuser}")
            print(f"User ID: {admin_user.id}")

         
            admin_user.set_password(new_password)
            admin_user.save()

        return Response({'message': 'Password changed successfully for all admin users.'},
                        status=status.HTTP_200_OK)





from django.db.models.functions import Replace, Lower
from django.db.models import Value

class MediaUploadView(APIView):
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        
        if not images:
            return Response({"error": "No images uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        media_objects = []
        
        for image in images:
            file_path = image.name
            
            # Check for products already using this image path
            products_with_this_image = Product.objects.filter(
                models.Q(product_image=file_path) | 
                models.Q(product_image=f'media/{file_path}')
            )
            
            # Delete existing file and media records if they exist
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                Media.objects.filter(
                    models.Q(image=file_path) | 
                    models.Q(image=f'media/{file_path}')
                ).delete()
            
            # Save the new image
            saved_path = default_storage.save(file_path, ContentFile(image.read()))
            
            print(f"Original filename: {image.name}")
            print(f"File path used: {file_path}")
            print(f"Saved path returned: {saved_path}")
            print(f"Storage location: {default_storage.path(saved_path)}")
            
            # Create media instance
            media_instance = Media()
            media_instance.image.name = saved_path
            media_instance.save()
            
            media_objects.append(media_instance)
            
            # Update products that were using this image path
            for product in products_with_this_image:
                product.product_image = saved_path
                product.save()
                print(f"Updated existing product {product.SKU} with image: {saved_path}")
            
            # Match products by normalized SKU
            filename_without_ext = os.path.splitext(image.name)[0]
            normalized_filename = filename_without_ext.replace(" ", "").replace("_", "").replace("-", "").lower()
            
            print(f"Looking for products with SKU matching (normalized): {normalized_filename}")
            
            matching_products = Product.objects.annotate(
                sku_normalized=Lower(
                    Replace(
                        Replace(
                            Replace('SKU', Value(' '), Value('')),
                            Value('_'), Value('')
                        ),
                        Value('-'), Value('')
                    )
                )
            ).filter(sku_normalized=normalized_filename)
            
            for product in matching_products:
                product.product_image = saved_path
                product.save()
                print(f"Updated product SKU: {product.SKU} with image: {saved_path}")
            
            print(f"Total products updated for {image.name}: {matching_products.count()}")
            print("="*50)
        
        serializer = MediaSerializer(media_objects, many=True)
        return Response({
            "message": f"Successfully uploaded {len(media_objects)} images.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class ProductCSVUploadView(APIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        
        if not csv_file:
            return Response({"error": "No file uploaded. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log media records before processing
        media_count_before = Media.objects.count()
        print(f"[ProductCSVUploadView] Media records before processing: {media_count_before}")
        
        file_path = default_storage.save(f'tmp/{csv_file.name}', ContentFile(csv_file.read()))
        
        try:
            with default_storage.open(file_path) as file:
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                expected_headers = {
                    'SKU', 'product_name', 'category',
                    'gross_weight', 'diamond_weight', 'colour_stones',
                    'net_weight', 'product_image', 'usertypes'
                }
                
                if not expected_headers.issubset(set(reader.fieldnames or [])):
                    missing_headers = expected_headers - set(reader.fieldnames or [])
                    return Response({"error": f"CSV file is missing required headers: {missing_headers}"}, status=status.HTTP_400_BAD_REQUEST)
                
                products_created = 0
                products_updated = 0
                errors = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate required fields
                        required_fields = ['SKU', 'product_name', 'category', 'gross_weight', 'net_weight']
                        for field in required_fields:
                            if not row.get(field):
                                raise ValueError(f"Field '{field}' is required but missing or empty in row {row_num}.")
                        
                        # Get or create category
                        category_name = row['category']
                        category, _ = Category.objects.get_or_create(category_name=category_name)
                        
                        # Check if product exists (case insensitive)
                        sku = row['SKU'].strip()
                        existing_product = Product.objects.filter(SKU__iexact=sku).first()
                        
                        # Find matching image
                        image_path = self.find_product_image(sku)
                        print(f"[ProductCSVUploadView] Image path for SKU {sku}: {image_path}")
                        
                        if existing_product:
                            # Update existing product
                            existing_product.SKU = sku
                            existing_product.product_name = row['product_name']
                            existing_product.category = category
                            existing_product.gross_weight = float(row['gross_weight']) if row['gross_weight'] else None
                            existing_product.diamond_weight = float(row.get('diamond_weight', 0)) if row.get('diamond_weight') else None
                            existing_product.colour_stones = float(row.get('colour_stones', 0)) if row.get('colour_stones') else None
                            existing_product.net_weight = float(row['net_weight']) if row['net_weight'] else None
                            existing_product.product_image = image_path
                            
                            existing_product.usertypes.clear()
                            if row.get('usertypes'):
                                usertypes_list = [ut.strip() for ut in row['usertypes'].split(',') if ut.strip()]
                                for usertype_name in usertypes_list:
                                    usertype, _ = UserType.objects.get_or_create(usertype=usertype_name)
                                    existing_product.usertypes.add(usertype)
                            
                            existing_product.save()
                            products_updated += 1
                            print(f"[ProductCSVUploadView] Updated product SKU: {sku} with image: {image_path}")
                        else:
                            # Create new product
                            product = Product.objects.create(
                                SKU=sku,
                                product_name=row['product_name'],
                                category=category,
                                gross_weight=float(row['gross_weight']) if row['gross_weight'] else None,
                                diamond_weight=float(row.get('diamond_weight', 0)) if row.get('diamond_weight') else None,
                                colour_stones=float(row.get('colour_stones', 0)) if row.get('colour_stones') else None,
                                net_weight=float(row['net_weight']) if row['net_weight'] else None,
                                product_image=image_path
                            )
                            
                            if row.get('usertypes'):
                                usertypes_list = [ut.strip() for ut in row['usertypes'].split(',') if ut.strip()]
                                for usertype_name in usertypes_list:
                                    usertype, _ = UserType.objects.get_or_create(usertype=usertype_name)
                                    product.usertypes.add(usertype)
                            
                            products_created += 1
                            print(f"[ProductCSVUploadView] Created product SKU: {sku} with image: {image_path}")
                    
                    except ValueError as ve:
                        errors.append(f"Row {row_num}: {str(ve)}")
                        continue
                    except Exception as e:
                        errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
                        continue
            
            # Log media records after processing
            media_count_after = Media.objects.count()
            print(f"[ProductCSVUploadView] Media records after processing: {media_count_after}")
            if media_count_before != media_count_after:
                print(f"[ProductCSVUploadView] WARNING: Media record count changed! Before: {media_count_before}, After: {media_count_after}")
            
            # Clean up temporary file
            default_storage.delete(file_path)
            
            response_data = {
                "message": f"CSV processed successfully. Created: {products_created} products, Updated: {products_updated} products.",
                "created": products_created,
                "updated": products_updated
            }
            
            if errors:
                response_data["errors"] = errors[:10]
                response_data["total_errors"] = len(errors)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            return Response({"error": f"Failed to process the uploaded file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def find_product_image(self, sku):
        """
        Find the best matching image for a given SKU.
        Returns the image path if found, None otherwise.
        """
        print(f"[find_product_image] Finding image for SKU: {sku}")
        
        # Check Media model first
        media_image = self.find_image_in_media_model(sku)
        if media_image:
            print(f"[find_product_image] Returning media image: {media_image}")
            return media_image
        
        # Fallback to filesystem (optional, can be removed if not needed)
        print("[find_product_image] No image found in Media model, checking filesystem")
        normalized_sku = sku.lower().replace(" ", "").replace("_", "").replace("-", "")
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        base_paths = ['media/', 'media/media/', 'products/', '']
        
        for base_path in base_paths:
            for ext in extensions:
                image_filename = f"{normalized_sku}{ext}"
                full_path = f"{base_path}{image_filename}"
                if default_storage.exists(full_path):
                    print(f"[find_product_image] Found image in filesystem: {full_path}")
                    return os.path.basename(full_path)
                
                image_filename = f"{sku}{ext}"
                full_path = f"{base_path}{image_filename}"
                if default_storage.exists(full_path):
                    print(f"[find_product_image] Found image in filesystem: {full_path}")
                    return os.path.basename(full_path)
        
        print(f"[find_product_image] No image found for SKU: {sku}")
        return None
    
    def find_image_in_media_model(self, sku):
        """
        Find matching image in Media model based on SKU patterns.
        Returns the image path if found, None otherwise.
        """
        normalized_sku = sku.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
        print(f"[find_image_in_media_model] Searching for media image with normalized SKU: {normalized_sku}")
        
        media_objects = Media.objects.all()
        for media in media_objects:
            if media.image and media.image.name:
                image_filename = os.path.basename(media.image.name)
                filename_without_ext = os.path.splitext(image_filename)[0]
                normalized_filename = filename_without_ext.lower().replace(" ", "").replace("_", "").replace("-", "")
                
                print(f"[find_image_in_media_model] Checking media image: {media.image.name} (normalized: {normalized_filename})")
                
                if normalized_sku == normalized_filename:
                    if default_storage.exists(media.image.name):
                        print(f"[find_image_in_media_model] Found matching image: {media.image.name}")
                        return os.path.basename(media.image.name)
                    else:
                        print(f"[find_image_in_media_model] Image {media.image.name} does not exist in storage")
        
        print(f"[find_image_in_media_model] No matching image found for SKU: {sku}")
        return None
class MediaDeleteView(APIView):
    def delete(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)
            
        
            image_path = media.image.name if media.image else None
            image_name = None
            
            if image_path:
                # Extract filename from path
                image_name = os.path.basename(image_path)
                
                # Find and clear product_image field for products that reference this image
                products_with_this_image = Product.objects.filter(product_image=image_path)
                products_updated_by_reference = products_with_this_image.count()
                products_with_this_image.update(product_image=None)
                
                # Extract SKU from filename (remove extension)
                filename_without_ext = os.path.splitext(image_name)[0]
                
                # Try different SKU matching patterns to find and clear image field for matching products
                sku_patterns = [
                    filename_without_ext,  # Exact match
                    filename_without_ext.replace("_", " "),  # Replace underscores with spaces
                    filename_without_ext.replace("-", " "),  # Replace hyphens with spaces
                    filename_without_ext.replace("_", ""),   # Remove underscores
                    filename_without_ext.replace("-", ""),   # Remove hyphens
                    filename_without_ext.replace(" ", ""),   # Remove spaces
                ]
                
                products_updated_by_sku = 0
                for sku_pattern in sku_patterns:
                    # Only update products that haven't already been updated by reference
                    matching_products = Product.objects.filter(
                        SKU__iexact=sku_pattern
                    ).exclude(
                        product_image=None  # Avoid updating products already cleared by reference
                    )
                    count = matching_products.count()
                    matching_products.update(product_image=None)
                    products_updated_by_sku += count
                
                # Delete the media file from storage
                if media.image and default_storage.exists(media.image.name):
                    default_storage.delete(media.image.name)
            
            # Delete the media record
            media.delete()
            
            response_data = {
                'message': 'Media deleted successfully',
                'deleted_media': 1,
                'products_image_cleared_by_reference': products_updated_by_reference if image_path else 0,
                'products_image_cleared_by_sku': products_updated_by_sku if image_path else 0,
                'total_products_updated': (products_updated_by_reference + products_updated_by_sku) if image_path else 0
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Media.DoesNotExist:
            return Response({'error': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Failed to delete media: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# class ProductCSVUploadView(APIView):
#     def post(self, request, *args, **kwargs):
#         csv_file = request.FILES.get('file')
        
#         if not csv_file:
#             return Response({"error": "No file uploaded. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)
            
#         file_path = default_storage.save(f'tmp/{csv_file.name}', ContentFile(csv_file.read()))
        
#         try:
#             with default_storage.open(file_path) as file:
#                 decoded_file = file.read().decode('utf-8').splitlines()
#                 reader = csv.DictReader(decoded_file)
                
#                 expected_headers = {
#                     'SKU', 'product_name', 'category',
#                     'gross_weight', 'diamond_weight', 'colour_stones',
#                     'net_weight', 'product_image', 'usertypes'
#                 }
                
#                 if not expected_headers.issubset(set(reader.fieldnames or [])):
#                     missing_headers = expected_headers - set(reader.fieldnames or [])
#                     return Response({"error": f"CSV file is missing required headers: {missing_headers}"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 products_created = 0
#                 products_updated = 0
#                 errors = []
                
#                 for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header row
#                     try:
#                         # Validate required fields
#                         required_fields = ['SKU', 'product_name', 'category', 'gross_weight', 'net_weight']
#                         for field in required_fields:
#                             if not row.get(field):
#                                 raise ValueError(f"Field '{field}' is required but missing or empty in row {row_num}.")
                        
#                         # Get or create category
#                         category_name = row['category']
#                         category, _ = Category.objects.get_or_create(category_name=category_name)
                        
#                         # Check if product exists (case insensitive)
#                         sku = row['SKU'].strip()
#                         existing_product = Product.objects.filter(SKU__iexact=sku).first()
                        
#                         # Find the best matching image
#                         image_path = self.find_product_image(sku)
                        
#                         if existing_product:
#                             # Update existing product - OVERRIDE all fields
#                             existing_product.SKU = sku  # Ensure consistent case
#                             existing_product.product_name = row['product_name']
#                             existing_product.category = category
#                             existing_product.gross_weight = float(row['gross_weight']) if row['gross_weight'] else None
#                             existing_product.diamond_weight = float(row.get('diamond_weight', 0)) if row.get('diamond_weight') else None
#                             existing_product.colour_stones = float(row.get('colour_stones', 0)) if row.get('colour_stones') else None
#                             existing_product.net_weight = float(row['net_weight']) if row['net_weight'] else None
                            
#                             # OVERRIDE image - set to found image or None
#                             existing_product.product_image = image_path
                            
#                             # OVERRIDE usertypes - clear all and add new ones
#                             existing_product.usertypes.clear()
#                             if row.get('usertypes'):
#                                 usertypes_list = [ut.strip() for ut in row['usertypes'].split(',') if ut.strip()]
#                                 for usertype_name in usertypes_list:
#                                     usertype, _ = UserType.objects.get_or_create(usertype=usertype_name)
#                                     existing_product.usertypes.add(usertype)
                            
#                             existing_product.save()
#                             products_updated += 1
#                         else:
#                             # Create new product
#                             product = Product.objects.create(
#                                 SKU=sku,
#                                 product_name=row['product_name'],
#                                 category=category,
#                                 gross_weight=float(row['gross_weight']) if row['gross_weight'] else None,
#                                 diamond_weight=float(row.get('diamond_weight', 0)) if row.get('diamond_weight') else None,
#                                 colour_stones=float(row.get('colour_stones', 0)) if row.get('colour_stones') else None,
#                                 net_weight=float(row['net_weight']) if row['net_weight'] else None,
#                                 product_image=image_path
#                             )
                            
#                             # Add usertypes
#                             if row.get('usertypes'):
#                                 usertypes_list = [ut.strip() for ut in row['usertypes'].split(',') if ut.strip()]
#                                 for usertype_name in usertypes_list:
#                                     usertype, _ = UserType.objects.get_or_create(usertype=usertype_name)
#                                     product.usertypes.add(usertype)
                            
#                             products_created += 1
                    
#                     except ValueError as ve:
#                         errors.append(f"Row {row_num}: {str(ve)}")
#                         continue
#                     except Exception as e:
#                         errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
#                         continue
            
#             # Clean up temporary file
#             default_storage.delete(file_path)
            
#             response_data = {
#                 "message": f"CSV processed successfully. Created: {products_created} products, Updated: {products_updated} products.",
#                 "created": products_created,
#                 "updated": products_updated
#             }
            
#             if errors:
#                 response_data["errors"] = errors[:10]  # Limit to first 10 errors
#                 response_data["total_errors"] = len(errors)
            
#             return Response(response_data, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             # Clean up temporary file on error
#             if default_storage.exists(file_path):
#                 default_storage.delete(file_path)
#             return Response({"error": f"Failed to process the uploaded file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     def find_product_image(self, sku):
#         """
#         Find the best matching image for a given SKU.
#         Returns the image path if found, None otherwise.
#         """
#         # Clean SKU for filename matching
#         clean_sku = sku.replace(" ", "").replace("_", "")
        
#         # Possible image extensions
#         extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
#         # Possible paths to check (in order of preference)
#         base_paths = [
#             'media/',
#             'media/media/',
#             'products/',
#             ''
#         ]
        
#         for base_path in base_paths:
#             for ext in extensions:
#                 # Try exact match
#                 image_filename = f"{clean_sku}{ext}"
#                 full_path = f"{base_path}{image_filename}"
                
#                 if default_storage.exists(full_path):
#                     return full_path
                
#                 # Try with original SKU (with spaces/underscores)
#                 image_filename = f"{sku}{ext}"
#                 full_path = f"{base_path}{image_filename}"
                
#                 if default_storage.exists(full_path):
#                     return full_path
        
#         return None






class MediaListView(APIView):
    def get(self, request, *args, **kwargs):
        media_images = Media.objects.all()
        serializer = MediaSerializer(media_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
 
        
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

user_model = get_user_model()

class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = user_model.objects.get(email=email)

            if user.is_staff or user.is_superuser:
                return Response({'error': 'Admins cannot log in through this endpoint'}, status=status.HTTP_403_FORBIDDEN)

            if not user.check_password(password):
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

       
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

           
            print("Access Token:", access_token)
            print("Refresh Token:", refresh_token)

            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "usertype": getattr(user, "usertypes_id", None),
            }

            print("Authenticated User Data:", user_data)

            return Response({
                'access': access_token,
                'refresh': refresh_token,
                'user': user_data,
            }, status=status.HTTP_200_OK)

        except user_model.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)



class ProductDetailView(APIView):
    def get(self, request, pk):  
        try:
            product = Product.objects.get(id=pk)   
            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
 


 

class ProductSKUDetailView(APIView):
    def get(self, request, SKU): 
        try:
            product = Product.objects.get(SKU=SKU)   
            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

 
 

 
class AddToCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        color = request.data.get('color', '') 

        try:
            existing_item = self.queryset.get(product_id=product_id, user=request.user)

        
            existing_item.quantity += quantity

            product = Product.objects.get(id=product_id)

            existing_item.gross_weight = product.gross_weight * existing_item.quantity
            existing_item.diamond_weight = (product.diamond_weight or 0) * existing_item.quantity
            existing_item.colour_stones = product.colour_stones * existing_item.quantity
            existing_item.net_weight = product.net_weight * existing_item.quantity
            existing_item.color = color  

            existing_item.save()

            serializer = self.get_serializer(existing_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
          
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, color=color) 
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print("serializer.errors",serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
    
class CartItemsView(generics.ListAPIView):
    serializer_class = CartGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # print("serializer.datassssssssssssssssss:", serializer.data)   
        return Response(serializer.data)

    

    
class CartItemDeleteAPIView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
       
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        sku = self.kwargs.get("sku")
  
        cart_items = self.get_queryset().filter(product__SKU=sku)

        if not cart_items.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)  # 
        
      
        deleted_count, _ = cart_items.delete()
        
        if deleted_count == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)  

        return Response(status=status.HTTP_204_NO_CONTENT)


 
 
 



class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
     
        order = serializer.save(user=self.request.user)       
        Cart.objects.filter(user=self.request.user).delete()         
        self.send_order_confirmation_email(order)

        return order 

    def send_order_confirmation_email(self, order):
        subject = f"New Order Created: {order.id}"
        message = f"Order ID: {order.id}\n" \
                  f"User: {order.user.username}\n" \
                  f"Total Gross Weight: {order.total_gross_weight}\n" \
                  f"Total Diamond Weight: {order.total_diamond_weight}\n" \
                  f"Total Colour Stones: {order.total_colour_stones}\n" \
                  f"Total Net Weight: {order.total_net_weight}\n" \
                  f"Created At: {order.created_at}\n" \
                  f"Order Items: \n"
        
        for item in order.order_items.all():
            message += f"- {item.product.product_name} (Quantity: {item.quantity})\n"

        admin_email = "admin@example.com"
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, 
            [admin_email],  
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = self.perform_create(serializer)
        order_data = {
            "id": order.id,
            "user": order.user.username,
            "total_gross_weight": str(order.total_gross_weight),
            "total_diamond_weight": str(order.total_diamond_weight),
            "total_colour_stones": str(order.total_colour_stones),
            "total_net_weight": str(order.total_net_weight),
            "created_at": order.created_at.isoformat(),
            "order_items": [
                {
                    "product": item.product.product_name,
                    "quantity": item.quantity,
                    "color":item.color,
                    "additional_notes": item.additional_notes,
                } for item in order.order_items.all()
            ]
        }
        
        print("Created order data:", order_data)
        return Response(order_data, status=status.HTTP_201_CREATED)






class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("Authorization header:", request.headers.get('Authorization'))
        print("User object:", request.user)
        print("Is authenticated:", request.user.is_authenticated)

        serializer = UserGetSerializer(request.user)
        return Response(serializer.data)

    
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer 
    update_serializer_class = UserGetSerializer   
    permission_classes = [IsAuthenticated]  

    def get_object(self):
   
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.update_serializer_class(self.object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

 



class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, sku):
        sku = unquote(sku) 
        user = request.user
        quantity = request.data.get('quantity')
        color = request.data.get('color')

        print("Decoded SKU:", sku)
        print("Quantity:", quantity)
        print("Color:", color)

        if quantity is None or quantity < 1:
            print("Invalid quantity or missing quantity")
            return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = Cart.objects.get(user=user, product__SKU=sku)
            print("Found cart item:", cart_item)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.quantity = quantity
        cart_item.color = color
        cart_item.gross_weight = cart_item.product.gross_weight * quantity
        cart_item.diamond_weight = (cart_item.product.diamond_weight or 0) * quantity
        cart_item.colour_stones = cart_item.product.colour_stones * quantity
        cart_item.net_weight = cart_item.product.net_weight * quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)





class CartItemListView(generics.ListAPIView):
    serializer_class = CartGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_carts = Cart.objects.filter(user=self.request.user)

      
        total_weights = user_carts.aggregate(
            total_gross_weight=Sum('gross_weight'),
            total_diamond_weight=Sum('diamond_weight'),
            total_colour_stones=Sum('colour_stones'),
            total_net_weight=Sum('net_weight')
        )

        return {
            'cart_items': user_carts,
            'totals': total_weights
        }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        cart_items = queryset['cart_items']
        totals = queryset['totals']
        
        
        serializer = self.get_serializer(cart_items, many=True)

        return Response({
            'cart_items': serializer.data,
            'totals': totals
        })
        
class UserOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializerss

    def get_queryset(self):
        user = self.request.user
        print(f"Authenticated user: {user.username}")  

        user_orders = Order.objects.filter(user=user, status='pending')

        print(f"User Orders: {user_orders}")  

      
        for order in user_orders:
            print(f"Order ID: {order.id}, Total Gross Weight: {order.total_gross_weight}, "
                  f"Total Diamond Weight: {order.total_diamond_weight}, "
                  f"Total Color Stones: {order.total_colour_stones}, "
                  f"Total Net Weight: {order.total_net_weight}, Status: {order.status}")
        
        return user_orders


class UserApprovedOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
     
        user = request.user
        
      
        pending_orders = CustomizedOrder.objects.filter(
            user=user, 
         
        ).exclude(new_status='delivered')
        
      
        serializer = CustomizedOrderSerializer(pending_orders, many=True)
        
        return Response(serializer.data)
class  UserApprovedFullOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
   
        user = request.user
        
      
        pending_orders = FullCustomizedOrder.objects.filter(
            user=user, 
         
        ).exclude(new_status='delivered')
        
   
        serializer = FullCustomizedGetSerializer(pending_orders, many=True)
        
        return Response(serializer.data)
    
    
class CustomizedProductDetail(generics.RetrieveAPIView):
    queryset = CustomizedProduct.objects.all()
    serializer_class = CustomizedProductListSerializer

class CustomizedProductSKUDetailView(APIView):
    def get(self, request, SKU): 
        try:
            product = CustomizedProduct.objects.get(SKU=SKU)   
            serializer =CustomizedProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


 
 

class CustomizedOrderCreateView(generics.CreateAPIView):
    queryset = CustomizedOrder.objects.all()
    serializer_class = CustomizedOrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
   
        order = serializer.save(user=self.request.user)

       
        self.send_order_confirmation_email(order)

        return order

    def send_order_confirmation_email(self, order):
 
        subject = f"New Customized Order Created: {order.id}"
        message = (
            f"Order ID: {order.id}\n"
            f"User: {order.user.username}\n"
            f"Product: {order.product.product_name}\n"
            f"Size: {order.size}\n"
            f"Gram: {order.gram}\n"
            f"Cent: {order.cent}\n"
            f"Color: {order.color.color}\n"
            f"Description: {order.description}\n"
            f"Quantity: {order.quantity}\n"
            f"Status: {order.status}\n"
            f"New Status: {order.new_status}\n"
            f"Due Date: {localtime(order.due_date).strftime('%Y-%m-%d %H:%M:%S') if order.due_date else 'N/A'}\n"
            f"Created At: {localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    
        admin_email = "admin@example.com"   
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  
            [admin_email],  
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Received data:", request.data)
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            order = self.perform_create(serializer) 
            headers = self.get_success_headers(serializer.data)
            print("serializer.data", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print("Validation Error:", e)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ColorListCreate(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class ColorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorupdateSerializer
    
class ColorListView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    
    
 

class FullCustomizedOrderCreateView(generics.CreateAPIView):
    queryset = FullCustomizedOrder.objects.all()
    serializer_class = FullCustomizedOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):

        order = serializer.save(user=self.request.user)

   
        files = self.request.FILES.getlist('product_images')
        for file in files:
            FullCustomizedMultipleImages.objects.create(product_images=order, image=file)


        self.send_order_confirmation_email(order)

        return order

    def send_order_confirmation_email(self, order):
    
        subject = f"New Full Customized Order Created: {order.id}"
        message = (
            f"Order ID: {order.id}\n"
            f"User: {order.user.username}\n"
            f"Category: {order.category.category_name}\n"
            f"Design Number: {order.design_number}\n"
            f"Size: {order.size}\n"
            f"Gram: {order.gram}\n"
            f"Cent: {order.cent}\n"
            f"Color: {order.color.color}\n"
            f"Description: {order.description}\n"
            f"Quantity: {order.quantity}\n"
            f"Status: {order.status}\n"
            f"New Status: {order.new_status}\n"
            f"Due Date: {localtime(order.due_date).strftime('%Y-%m-%d %H:%M:%S') if order.due_date else 'N/A'}\n"
            f"Created At: {localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Order Images: \n"
        )

   
        for image in FullCustomizedMultipleImages.objects.filter(product_images=order):
            message += f"- {image.image.url}\n" 

    
        admin_email = "admin@example.com"
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, 
            [admin_email], 
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = self.perform_create(serializer)
        order_data = {
            "id": order.id,
            "user": order.user.username,
            "design_number": order.design_number,
            "size": order.size,
            "gram": str(order.gram),
            "cent": str(order.cent),
            "color": order.color.color,
            "description": order.description,
            "quantity": order.quantity,
            "status": order.status,
            "new_status": order.new_status,
            "due_date": order.due_date.isoformat() if order.due_date else None,
            "created_at": order.created_at.isoformat(),
            "order_images": [image.image.url for image in FullCustomizedMultipleImages.objects.filter(product_images=order)]
        }

        print("Created order data:", order_data)
        return Response(order_data, status=status.HTTP_201_CREATED)



    
class UserCartItemCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
 
        cart_item_count = Cart.objects.filter(user=request.user).count()
        return Response({'cart_item_count': cart_item_count})
    
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializerss


class OrderPendingListView(generics.ListAPIView):
    serializer_class = OrderSerializerss

    def get_queryset(self):
        return Order.objects.filter(status='pending')
    

class OrderItemsByOrderIdView(generics.ListAPIView):
    serializer_class = OrderSerializerss

    def get_queryset(self):
 
        order_id = self.kwargs.get('order_id') 

        if order_id:

            return Order.objects.filter(id=order_id, status='pending')
        else:

            return Order.objects.filter(status='pending')


class OrderAcceptOrderIdView(generics.ListAPIView):
    serializer_class = OrderSerializerss

    def get_queryset(self):
 
        order_id = self.kwargs.get('order_id') 

        if order_id:

            return Order.objects.filter(id=order_id, status='accepted')
        else:

            return Order.objects.filter(status='accepted')


class OrderCompleteListView(generics.ListAPIView):
    serializer_class = OrderSerializerss

    def get_queryset(self):
        return Order.objects.filter(status='delivered')
    
class OrderAcceptedView(generics.ListAPIView):
    serializer_class = OrderSerializerss

    def get_queryset(self):
        return Order.objects.filter(status='accepted')
    
class OrderUpdateAPIView(APIView):
    def patch(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderIdSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderUpdateAPIView(APIView):
    def patch(self, request, pk):
  
        order = Order.objects.filter(pk=pk).first()
        
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        print("Received data:", request.data)   
        
   
        ordercode = request.data.get('ordercode', order.ordercode)
        order.ordercode = ordercode
        order.save()   

    
        order_items_data = request.data.get('order_items', [])
        for item_data in order_items_data:
            print("Processing item data:", item_data)

            item_id = item_data.get('id') 
            if item_id is not None:   
       
                item = OrderItem.objects.filter(pk=item_id).first()
                
                if item:
                
                    quantity = int(item_data.get('quantity', item.quantity))
                    item.quantity = quantity
                    item.save()   
                else:
                    print("No ID found in item data:", item_data)
                    return Response({"detail": f"OrderItem with id {item_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({'ordercode': order.ordercode, 'order_items': order_items_data}, status=status.HTTP_200_OK)


class DeleteOrderView(APIView):
    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
 


class PendingOrdersView(APIView):
    def get(self, request):
        pending_orders = CustomizedOrder.objects.filter(status='pending')
        serializer = CustomizedOrderSerializer(pending_orders, many=True)
        return Response(serializer.data)



class OrderApprovalView(APIView):
    def patch(self, request, pk):
        try:
            order = CustomizedOrder.objects.get(pk=pk)
        except CustomizedOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = request.data.get("approved")
        
        if approved is not None:
    
            order.status = 'approved' if approved else 'rejected'
            order.save()
            return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)
class RejectOrderAPIView(APIView):
    def patch(self, request, pk):
        try:
            order = CustomizedOrder.objects.get(pk=pk)
        except CustomizedOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    
        order.status = 'rejected'
        order.save()

        serializer = CustomizedOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class  ApprovedOrdersView(APIView):
    def get(self, request):
        pending_orders = CustomizedOrder.objects.filter(status='approved').exclude(new_status='delivered')
        serializer = CustomizedOrderSerializer(pending_orders, many=True)
        return Response(serializer.data)
    



 
class GenerateOrderIDView(APIView):
    def patch(self, request, pk=None):
        order = get_object_or_404(CustomizedOrder, pk=pk)
        ordercode = request.data.get('ordercode')
        due_date = request.data.get('due_date')

        if ordercode:
            order.ordercode = ordercode

            if due_date is not None:
                order.due_date = due_date

            order.save()

            return Response({
                'status': 'Order ID generated',
                'ordercode': order.ordercode,
                'due_date': order.due_date
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Order code not provided'}, status=status.HTTP_400_BAD_REQUEST)



    
class UpdateCustomizedOrderView(APIView):
    def patch(self, request, order_id):
        try:
      
            order = CustomizedOrder.objects.get(id=order_id)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

 
        serializer = CustomizedOrderSerializer(order, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteCustomizedOrderView(APIView):
    def delete(self, request, order_id):
        try:
        
            order = CustomizedOrder.objects.get(id=order_id)
            order.delete()  
            return Response({'message': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class FullCustomizedOrderListAPIView(APIView):
    def get(self, request):
     
        pending_orders = FullCustomizedOrder.objects.filter(status='pending')
        serializer = FullCustomizedOrderListSerializer(pending_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderFullApprovalView(APIView):
    def patch(self, request, pk):
        try:
            order = FullCustomizedOrder.objects.get(pk=pk)
        except FullCustomizedOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = request.data.get("approved")
        
        if approved is not None:
          
            order.status = 'approved' if approved else 'rejected'
            order.save()
            return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)
        
class RejectFullOrderAPIView(APIView):
    def patch(self, request, pk):
        try:
            order = FullCustomizedOrder.objects.get(pk=pk)
        except FullCustomizedOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
 
        order.status = 'rejected'
        order.save()

        serializer = FullCustomizedOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class  ApprovedFullOrdersView(APIView):
    def get(self, request):
        pending_orders = FullCustomizedOrder.objects.filter(status='approved').exclude(new_status='delivered')
        serializer = FullCustomizedOrderListSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
 
    
class GenerateFullOrderIDView(APIView):
    def patch(self, request, pk=None):
        order = get_object_or_404(FullCustomizedOrder, pk=pk)
        ordercode = request.data.get('ordercode')
        due_date = request.data.get('due_date')  

        if ordercode:
            order.ordercode = ordercode

        
            if due_date:
                try:
                    order.due_date = datetime.fromisoformat(due_date)   
                except ValueError:
                    return Response({'error': 'Invalid due_date format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                order.due_date = None  

            order.save()
            return Response({
                'status': 'Order ID generated',
                'ordercode': order.ordercode,
                'due_date': order.due_date
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Order code not provided'}, status=status.HTTP_400_BAD_REQUEST)




class UpdateFullCustomizedOrderView(APIView):
    def patch(self, request, order_id):
        try:
      
            order = FullCustomizedOrder.objects.get(id=order_id)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

 
        serializer = FullCustomizedOrderSerializer(order, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteFullCustomizedOrderView(APIView):
    def delete(self, request, order_id):
        try:
        
            order = FullCustomizedOrder.objects.get(id=order_id)
            order.delete()  
            return Response({'message': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class UpdateOrderStatusView(APIView):
    def patch(self, request, order_id):
        print("request",request.data)
        try:
            order = CustomizedOrder.objects.get(id=order_id)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomizedOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("serializer.data",serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("serializer.data",serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateFullOrderStatusView(APIView):
    def patch(self, request, order_id):
        print("request",request.data)
        try:
            order = FullCustomizedOrder.objects.get(id=order_id)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FullCustomizedOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("serializer.data",serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("serializer.data",serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 


class StatusCSVUploadView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if not file.name.endswith('.csv'):
            return Response({'error': 'File type not supported. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        reader = csv.DictReader(decoded_file.splitlines())

        updated_orders = []
        not_found_orders = []  

        for row in reader:
            print(f"Row data: {row}") 

            order_id = row.get('Order Id')
            order_status = row.get('New Status', '').strip()  

            if not order_id:
                print(f"Order Id is missing in this row. Skipping.")
                continue  

            order = None
            if CustomizedOrder.objects.filter(ordercode=order_id).exists():
                order = CustomizedOrder.objects.get(ordercode=order_id)
            elif FullCustomizedOrder.objects.filter(ordercode=order_id).exists():
                order = FullCustomizedOrder.objects.get(ordercode=order_id)

            if not order:
                print(f"Order with ordercode {order_id} does not exist.")
                not_found_orders.append(order_id)  
                continue   

            if order_status:

                if isinstance(order, CustomizedOrder):
                    valid_statuses = dict(CustomizedOrder.NEW_STATUS_CHOICES)
                else:
                    valid_statuses = dict(FullCustomizedOrder.NEW_STATUS_CHOICES)

                if order_status.lower() not in valid_statuses:
                    print(f"Invalid status '{order_status}' for order {order_id}. Skipping.")
                    continue  

                try:

                    order.new_status = order_status.lower()   
                    order.save()
                    print(f"Order {order_id} status updated to {order_status}.")
                    updated_orders.append(order_id)
                except Exception as e:
                    print(f"Failed to update order {order_id}: {str(e)}")
                    return Response({'error': f'Failed to update order {order_id}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print(f"No status provided for order {order_id}, skipping status update.")

        response_data = {}
        if updated_orders:
            response_data['success'] = f'Updated statuses for orders: {updated_orders}'
        if not_found_orders:
            response_data['not_found'] = f'Orders not found: {not_found_orders}'

        return Response(response_data, status=status.HTTP_200_OK)



class StatusFullCSVUploadView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if not file.name.endswith('.csv'):
            return Response({'error': 'File type not supported. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        reader = csv.DictReader(decoded_file.splitlines())

        updated_orders = []
        not_found_orders = []  

        for row in reader:
            print(f"Row data: {row}") 

            order_id = row.get('Order Id')
            order_status = row.get('New Status').strip()  

            
            if not FullCustomizedOrder.objects.filter(ordercode=order_id).exists():
                print(f"Order with ordercode {order_id} does not exist.")
                not_found_orders.append(order_id)  
                continue   
            
   
            if order_status.lower() not in dict(FullCustomizedOrder.NEW_STATUS_CHOICES):
                print(f"Invalid status '{order_status}' for order {order_id}.")
                continue  
            try:
                order = FullCustomizedOrder.objects.get(ordercode=order_id)
                order.new_status = order_status.lower()   
                order.save()
                print(f"Order {order_id} status updated to {order_status}.")
                updated_orders.append(order_id)
            except Exception as e:
                print(f"Failed to update order {order_id}: {str(e)}")
                return Response({'error': f'Failed to update order {order_id}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
        response_data = {}
        if updated_orders:
            response_data['success'] = f'Updated statuses for orders: {updated_orders}'
        if not_found_orders:
            response_data['not_found'] = f'Orders not found: {not_found_orders}'

        return Response(response_data, status=status.HTTP_200_OK)
    

class ContactMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = self.request.user
            try:    
                message = serializer.save()
                subject = f"New Contact Message from {message.full_name}"
                message_body = f"Name: {message.full_name}\nEmail: {message.email}\nPhone: {message.phone}\nMessage:\n{message.message}"
                recipient_email = settings.EMAIL_HOST_USER

                try:
                    send_mail(subject, message_body, settings.EMAIL_HOST_USER, [recipient_email])
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    return Response({'status': 500, 'error': 'Failed to send email notification. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                print(f"Error saving contact message: {e}")
                return Response({'status': 500, 'error': 'Failed to save contact message. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
class DeliveredOrdersView(APIView):
    def get(self, request, format=None): 
        delivered_orders = CustomizedOrder.objects.filter(new_status='delivered')   
        serializer = CustomizedOrderSerializer(delivered_orders, many=True)    
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeliveredFullOrdersView(APIView):
    def get(self, request, format=None):
        delivered_orders = FullCustomizedOrder.objects.filter(new_status='delivered')   
        serializer = FullCustomizedOrderListSerializer(delivered_orders, many=True)     
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderStatusUpdateAPIView(APIView):
    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompleteOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializerss

    def get_queryset(self):
        user = self.request.user
        print(f"Authenticated user: {user.username}")  

        user_orders = Order.objects.filter(user=user, status='delivered')

        print(f"User Orders: {user_orders}")  

      
        for order in user_orders:
            print(f"Order ID: {order.id}, Total Gross Weight: {order.total_gross_weight}, "
                  f"Total Diamond Weight: {order.total_diamond_weight}, "
                  f"Total Color Stones: {order.total_colour_stones}, "
                  f"Total Net Weight: {order.total_net_weight}, Status: {order.status}")
        
        return user_orders



class UserCompleteApprovedOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
     
        user = request.user      
        pending_orders = CustomizedOrder.objects.filter(
            user=user, new_status='delivered'        
        )       
        serializer = CustomizedOrderSerializer(pending_orders, many=True)      
        return Response(serializer.data)
    
    
class  UserCompleteApprovedFullOrdersView(APIView):   
    permission_classes = [IsAuthenticated]
    def get(self, request):   
        user = request.user     
        pending_orders = FullCustomizedOrder.objects.filter(
            user=user, new_status='delivered'        
        ) 
        serializer = FullCustomizedOrderSerializer(pending_orders, many=True)
        
        return Response(serializer.data)
    
    
