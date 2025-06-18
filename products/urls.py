from django.urls import path
 
from .views import *

urlpatterns = [
   
   # usertype
   path('usertypes/', UserTypeListCreateView.as_view(), name='usertype-list-create'),
   path('usertypes/<int:pk>/', UserTypeDetailView.as_view(), name='usertype-detail'),
   path('usertypes_list/', UserTypeListView.as_view(), name='user-type-list'),
   
   # category
   path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
   path('categories/', CategoryListAPIView.as_view(), name='category-list'),
   path('categories/<int:id>/', CategoryDetailAPIView.as_view(), name='category-detail'),
   
   # products
   path('products/', ProductListCreateView.as_view(), name='product-list-create'),
   path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
   path('products_list/', ProductListView.as_view(), name='product-list'),
   path('products_user_list/', ProductuserListView.as_view(), name='product-list'),
   path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
   path('product/<int:id>/delete/', ProductDeleteView.as_view(), name='product-delete'),
   path('upload-csv/', ProductCSVUploadView.as_view(), name = 'csv-upload'),
   path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
   path('products/<str:SKU>/', ProductSKUDetailView.as_view(), name='product-detail-by-sku'),
   
   # customized products
   path('customized_products/', CustomizedProductListCreateView.as_view(), name='product-list-create'),
   path('customized_products/<int:pk>/', CustomizedProductDetailView.as_view(), name='product-detail'),
   path('customized_products_list/', CustomizedProductListView.as_view(), name='product-list'),
   path('custom_products_user_list/', CustomProductuserListView.as_view(), name='product-list'),
   path('customized_products/<int:pk>/update/', CustomizedProductUpdateView.as_view(), name='product-update'),
   path('customized_product/<int:id>/delete/', CustomizedProductDeleteView.as_view(), name='product-delete'),
   path('customized-products/<int:pk>/', CustomizedProductDetail.as_view(), name='customized-product-detail'),
   path('customized-products/<str:SKU>/', CustomizedProductSKUDetailView.as_view(), name='customized-product-detail'),
   
   # user    
   path('users/create/', UserCreateView.as_view(), name='user-create'),
   path('users/', UserListAPIView.as_view(), name='user-list'),   
   path('users/<int:id>/', UserUpdateAPIView.as_view(), name='user-update'),
   path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
   path('change-password/', ChangePasswordView.as_view(), name='admin_change_password'),
   path('current-user/', CurrentUserView.as_view(), name='current-user'),
   path('update-profile/', UserProfileView.as_view(), name='current-user'),
   path('user/login/', UserLoginView.as_view(), name='user-login'),
   
   
   # admin login
   path('login/', AdminLoginView.as_view(), name='admin-login'),

  
   # media
   path('upload-media/', MediaUploadView.as_view(), name='upload-media'),  
   path('media/images/', MediaListView.as_view(), name='media-images-list'),
   path('media/images/<int:pk>/', MediaDeleteView.as_view(), name='media-delete'),

   # cart
   path('cart/add/', AddToCartView.as_view(), name='add-to-cart'), 
   path('cart/items/', CartItemListView.as_view(), name='cart-items'),   
   path('cart/<str:sku>/', CartItemDeleteAPIView.as_view(), name='cart-item-delete'),  
   path('cart/update/<str:sku>/', UpdateCartQuantityView.as_view(), name='update-cart-quantity'), 
   path('cart-items/', CartItemsView.as_view(), name='cart-items-list'),
   path('cart/item-count/', UserCartItemCountView.as_view(), name='user-cart-item-count'),
  
  #  contact
   path('contact/', ContactMessageAPIView.as_view(), name='contact-form'),

 
   # colours
   path('colors/', ColorListCreate.as_view(), name='color-list-create'),
   path('colors/<int:pk>/', ColorRetrieveUpdateDestroy.as_view(), name='color-detail'),
   path('colors_list/', ColorListView.as_view(), name='color-list'),
   
    
   # orders
   path('orders/', OrderCreateView.as_view(), name='order-create'),  
   path('my-orders/', UserOrderListView.as_view(), name='user-order-list'),
   path('user-cus-orders/', UserApprovedOrdersView.as_view(), name='user-order-list'),
   path('user-fullcus-orders/', UserApprovedFullOrdersView.as_view(), name='user-order-list'),
   path('customized-orders/', CustomizedOrderCreateView.as_view(), name='customized-order-create'),
   path('full-cutome-order/', FullCustomizedOrderCreateView.as_view(), name='full_customized_order_with_images_create'), 
   path('admin-orders/', OrderListView.as_view(), name='order-list'),
   path('ordersid/<int:pk>/', OrderUpdateAPIView.as_view(), name='order-update'),
   path('orders/<int:pk>/update/', OrderUpdateAPIView.as_view(), name='admin-order-update'),
   path('orders/<int:order_id>/delete/', DeleteOrderView.as_view(), name='api_delete_order'),
   path('customized-pending/', PendingOrdersView.as_view(), name='customized_order_list'),
   path('orders/<int:pk>/approve/', OrderApprovalView.as_view(), name='approve_order'),
   path('orders/<int:pk>/reject/', RejectOrderAPIView.as_view(), name='approve_order'),
   path('customized-approved/', ApprovedOrdersView.as_view(), name='customized_order_list'),
   path('custom-orders/<int:pk>/generate-order-id/', GenerateOrderIDView.as_view(), name='generate-order-id'),
   path('custom-orders/<int:order_id>/', UpdateCustomizedOrderView.as_view(), name='update_custom_order'),
   path('custom-orders/<int:order_id>/delete/', DeleteCustomizedOrderView.as_view(), name='delete_custom_order'),
   path('full-cusom-pending/', FullCustomizedOrderListAPIView.as_view(), name='full-customized-order-list'),
   path('full-orders/<int:pk>/approve/', OrderFullApprovalView.as_view(), name='approve_order'),
   path('full-orders/<int:pk>/reject/', RejectFullOrderAPIView.as_view(), name='approve_order'),
   path('full-customized-approved/', ApprovedFullOrdersView.as_view(), name='customized_order_list'),
   path('custom-full-orders/<int:pk>/generate-order-id/', GenerateFullOrderIDView.as_view(), name='generate-order-id'),
   path('custom-full-orders/<int:order_id>/', UpdateFullCustomizedOrderView.as_view(), name='update_custom_order'),
   path('custom-full-orders/<int:order_id>/delete/', DeleteFullCustomizedOrderView.as_view(), name='delete_custom_order'),
   path('orders/<int:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
   path('full-orders/<int:order_id>/update-status/', UpdateFullOrderStatusView.as_view(), name='update-order-status'),
   path('status/upload-csv/', StatusCSVUploadView.as_view(), name='upload_csv'),
   path('full-status/upload-csv/', StatusFullCSVUploadView.as_view(), name='upload_csv'),   
   path('delivered-orders/', DeliveredOrdersView.as_view(), name='delivered_orders_api'),
   path('full-delivered-orders/', DeliveredFullOrdersView.as_view(), name='delivered_orders_api'),
   path('order/<int:order_id>/update-status/', OrderStatusUpdateAPIView.as_view(), name='order_status_update'),
   path('orders/pending/', OrderPendingListView.as_view(), name='pending_orders'),
   path('orders/<int:order_id>/', OrderItemsByOrderIdView.as_view(), name='order-items-by-id'),
   path('accept-orders/<int:order_id>/', OrderAcceptOrderIdView.as_view(), name='order-items-by-id'),
   
   path('orders/delivered/', OrderCompleteListView.as_view(), name='pending_orders'),
   path('orders/accepted/', OrderAcceptedView.as_view(), name='pending_orders'),
   path('my-complete-orders/', UserCompleteOrderListView.as_view(), name='user-order-list'),
   path('user-complete-cus-orders/', UserCompleteApprovedOrdersView.as_view(), name='user-order-list'),
   path('user-complete-fullcus-orders/', UserCompleteApprovedFullOrdersView.as_view(), name='user-order-list'),
      
]
 