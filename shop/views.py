import json
from django.db.models import F
from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.generics import *
from rest_framework.parsers import FileUploadParser
from django_filters import rest_framework as filters
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db.models import Q

from .serializers import *
from .models import *
from .pagination_mixin import PaginationMixin
from .filters import ProductFilter,CartFilter,OrderFilter
from account.serializers import UserSerializer
from account.browsable_mixin import AdminBrowsableMixin
from account.currency import currencies as c


User = get_user_model()


def is_admin(email):
    try:
        user = User.objects.get(email = email)
        return user.is_admin
    except User.DoesNotExist:
        return False


class ProductListCreateView(AdminBrowsableMixin,APIView,PaginationMixin):

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    permission_classes = []

    authentication_classes = []

    def post(self,request,format=None):
        payload = request.data
        serialized_data = ProductSerializer(data=payload)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        return Response(serialized_data.data,status=status.HTTP_201_CREATED)


    def get(self,request,format=None):
        queryset = Product.objects.filter(published=True)
        page = self.paginate_queryset(queryset)
        serialized_products = SimpleProductSerializer(page,many=True)
        if page is not None:
            serialized_products = SimpleProductSerializer(page,many=True)
            return self.get_paginated_response(serialized_products.data)
        return Response(serialized_products.data,status=status.HTTP_200_OK)


class ProductSearchView(AdminBrowsableMixin,APIView,PaginationMixin):
    permission_classes = []

    authentication_classes = []

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self,request,format=None):
        query = None
        category = None
        sub_category = None
        categories = ["laptop","laptops","phone","phones","smartphone","smartphones","accessory","accessories"]
        sub_categories = SubCategory.objects.all().values_list("name")
        s = []
        for i in list(sub_categories):
            s.append(i[0])
        sub_categories = s
        search_string = request.GET.get("search").lower()  
        search_str_sections = search_string.split(" ")

        for section in search_str_sections:
            if section in categories:
                if not section.endswith("s"):
                    section+"s"
                if section == "phone" or section == "phones":
                    category = "smartphones"
                if section == "accessory":
                    category = "accessories"
                else:
                    category = section
                search_str_sections.remove(section)        

        if len(search_str_sections) >= 1:
            for section in search_str_sections:
                if section in sub_categories:
                    sub_category = section
                    search_str_sections.remove(section)


        main_query = None
        if len(search_str_sections)==0:
            if category and sub_category:
                main_query = Product.objects.filter(sub_category__name__icontains=sub_category)
            else:
                if category: 
                    main_query = Product.objects.filter(Q(category__name__icontains=category))
                elif sub_category:
                    main_query = Product.objects.filter(Q(sub_category__name__icontains=sub_category))
        else:

            if category and sub_category:
                main_query = Product.objects.filter(sub_category__name__icontains=sub_category)
            else:
                if category: 
                    main_query = Product.objects.filter(Q(category__name__icontains=category))
                elif sub_category:
                    main_query = Product.objects.filter(Q(sub_category__name__icontains=sub_category))

            q = Q()

            if len(search_str_sections) >=1:
                for section in search_str_sections:
                    q |= Q(name__icontains = section)

                secondary_query = Product.objects.filter(q)

                if main_query:
                    main_query = main_query & secondary_query
                else:
                    main_query = secondary_query

        serialized_products = SimpleProductSerializer(main_query,many=True)

        if main_query is not None:
            if len(main_query) == 0:
                return Response({},status=status.HTTP_200_OK)
            page = self.paginate_queryset(main_query)
            if page:
                serialized_products = SimpleProductSerializer(page,many=True)
                return self.get_paginated_response(serialized_products.data)
            return Response(serialized_products.data,status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_400_BAD_REQUEST)




class ProductCategoryListView(AdminBrowsableMixin,APIView,PaginationMixin):

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    permission_classes = []

    authentication_classes = []

    def get(self,request,category,format=None):
        category = Category.objects.get(name=category)
        queryset = Product.objects.filter(category=category)
        page = self.paginate_queryset(queryset)
        serialized_products = SimpleProductSerializer(page,many=True)
        if page is not None:
            return self.get_paginated_response(serialized_products.data)
        return Response(serialized_products.data,status=status.HTTP_200_OK)


class ProductFetchRelated(AdminBrowsableMixin,APIView):

    permission_classes = []

    authentication_classes = []

    def get(self,request,slug,format=None):
        category = Product.objects.get(slug=slug).category
        related_products = Product.objects.filter(category=category).exclude(slug=slug)
        serialized_products = SimpleProductSerializer(related_products,many=True)
        return Response(serialized_products.data,status=status.HTTP_200_OK)
        



class ProductRetrieveView(AdminBrowsableMixin,APIView):

    permission_classes = []

    authentication_classes = []

    def get_product(self,slug):
        try:
            product = Product.objects.get(slug=slug)
            return product
        except:
            return None #give a 404

    def get(self,request,slug,format=None):
        product = self.get_product(slug)
        if product:
            serialized_product = ProductSerializer(product)
            return Response(serialized_product.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    


class ProductUpdateDestroyView(AdminBrowsableMixin,APIView):

    def put(self,request,id,format=None):
        if is_admin(request.user):
            product = Product.objects.get(id=id)
            if request.data.get("type") == "deal":
                data = request.data
                data["hot_deal"] = True
                serialized_product = ProductSerializer(instance=product,data=data,partial=True)
            else: 
                serialized_product = ProductSerializer(instance=product,data=request.data,partial=True)
            serialized_product.is_valid(raise_exception=True)
            serialized_product.save()
            return Response(serialized_product.data,status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_403_FORBIDDEN)


class DeleteProductImage(AdminBrowsableMixin,APIView):

    def put(self,request,id,format=None):
        raw_saved_image = "/".join(request.data["url"].split("/")[-3:])
        saved_image = f"/{raw_saved_image}"
        product = Product.objects.get(id=id)
        img_urls = product.img_urls.split(",")
        try:
            img_urls.remove(saved_image)
            product.img_urls = ",".join(img_urls)
            product.save()
        except Exception as e:
            product.save()
        return Response({},status=status.HTTP_200_OK)




class CartListCreateView(AdminBrowsableMixin,APIView,PaginationMixin):

    permission_classes = (permissions.IsAuthenticated,)

    def process_cart_product_duplicates_same_buyer(self,obj,payload,qty):
        buyer = User.objects.get(id=payload["buyer"]["id"])
        product = Product.objects.get(id=payload["product"]["id"])
        cart = Cart.objects.filter(buyer=buyer,product=product).exclude(ordered=True)
        if cart.exists():
            cart = Cart.objects.get(buyer=buyer,product=product).exclude(ordered=True)
            cart.quantity = int(cart.quantity)+int(qty)
            cart.save()
        else:
            obj.is_valid(raise_exception=True)
            obj.save()




    def post(self,request,format=None):
        user = User.objects.get(email=request.user)
        if type(request.data) == dict:
            payload = request.data
            qty=payload["quantity"]
            payload["buyer"]={"id":user.id,"password":user.password}
            serialized_cart = CartSerializer(data=payload)
            self.process_cart_product_duplicates_same_buyer(serialized_cart,payload,qty)
            return Response({"count":qty},status=status.HTTP_201_CREATED)
        elif type(request.data) == list:
            # if request.data == []:
            #     return Response(status=status.HTTP_200_OK)
            for item in request.data:
                qty=item["quantity"]
                item["buyer"]={"id":user.id,"password":user.password}
                serialized_cart = CartSerializer(data=item)
                self.process_cart_product_duplicates_same_buyer(serialized_cart,item,qty)

            return Response(status=status.HTTP_201_CREATED)

    def get(self,request,format=None):
        user = User.objects.get(email=request.user)
        cart_items = Cart.objects.filter(buyer=user).exclude(ordered=True)
        serialized_items = CartSerializer(cart_items,many=True)
        return Response(serialized_items.data,status=status.HTTP_200_OK)


    def put(self,request,format=None):
        """
        The only thing to update in cart is quantity which in turn updates total price
        """
        op_type = request.data["op_type"]
        cart = Cart.objects.get(id=request.data["id"])
        if op_type == "INC":
            cart.quantity+=1
        elif op_type == "DEC" and cart.quantity > 1:
            cart.quantity-=1
        cart.save()
        serialized_cart = CartSerializer(cart)
        return Response(serialized_cart.data,status=status.HTTP_200_OK)

    def delete(self,request,id,format=None):
        """
        Delete a cart record
        """
        cart = Cart.objects.get(id=id)
        quantity = cart.quantity
        cart.delete()
        return Response({"id":id,"qty":quantity},status=status.HTTP_200_OK)



class WishListCreateListView(AdminBrowsableMixin,APIView):


    def process_wishlist_product_duplicates_same_buyer(self,obj,payload):
        saver = User.objects.get(id=payload["saver"]["id"])
        product = Product.objects.get(name=payload["product"]["name"])
        wishlist = WishList.objects.filter(saver=saver,product=product)
        if wishlist.exists():
            wishlist = WishList.objects.get(saver=saver,product=product)
            # wishlist.quantity = int(wishlist.quantity)+int(qty)
            wishlist.save()
        else:
            obj.is_valid(raise_exception=True)
            obj.save()

    def get(self,request,format=None):
        wishlist_items = WishList.objects.filter(saver=User.objects.get(email=request.user))
        serialized_wishlist = WishListSerializer(wishlist_items,many=True)
        return Response(serialized_wishlist.data,status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if type(request.data) == dict:
            payload=request.data
            product=Product.objects.get(id=request.data["id"])
            payload["product"] = {"name":product.name}
            user = User.objects.get(email=request.user)
            payload["saver"] = {"id":user.id,"password":user.password}
            payload.pop("id")
            serialized_wishlist = WishListSerializer(data=payload)
            self.process_wishlist_product_duplicates_same_buyer(serialized_wishlist,payload)
            wishlist_items = WishList.objects.filter(saver=user)
            return Response({"count":len(wishlist_items)},status=status.HTTP_201_CREATED)
        elif type(request.data) == list:
            for item in request.data:
                product=Product.objects.get(id=item["id"])
                item["product"] = {"name":product.name}
                user = User.objects.get(email=request.user)
                item["saver"] = {"id":user.id,"password":user.password}
                item.pop("id")
                serialized_wishlist = WishListSerializer(data=item)
                self.process_wishlist_product_duplicates_same_buyer(serialized_wishlist,item)

            wishlist_items = WishList.objects.filter(saver=user)
            return Response({"count":len(wishlist_items)},status=status.HTTP_201_CREATED)

    def delete(self,request,id,format=None):
        to_delete = WishList.objects.get(id=id)
        to_delete.delete()
        return Response({"id":id},status=status.HTTP_200_OK)





class GetCartCount(AdminBrowsableMixin,APIView):

    def get(self,request,format=None):
        qty=0
        user = User.objects.get(email=request.user)
        cart_items = Cart.objects.filter(buyer=user).exclude(ordered=True)
        for item in cart_items:
            qty+=item.quantity
        return Response({"count":qty},status=status.HTTP_200_OK)



class WishListCount(AdminBrowsableMixin,APIView):

    def get(self,request,format=None):
        qty=0
        user = User.objects.get(email=request.user)
        wishlist_items = WishList.objects.filter(saver=user)
        return Response({"count":len(wishlist_items)},status=status.HTTP_200_OK)




class OrderListCreateView(AdminBrowsableMixin,APIView,PaginationMixin):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request,format=None):
        q = Order.objects.filter(owner=request.user)
        serialized_q = SimpleOrderSerializer(q,many=True)
        return Response(serialized_q.data,status=status.HTTP_200_OK)


    def post(self,request,format=None):
        payment_method = request.data.get("method")
        currency = request.data.get("currency")
        if not payment_method:            
            return Response({},status=status.HTTP_400_BAD_REQUEST)
        owner = request.user
        products = self.stringify_cart(owner,c()[currency])
        amount = self.get_total_amount(products)
        currency_value = c()[currency] # base KSH
        order = Order.objects.create(owner=owner,currency=currency,currency_value=currency_value,products=products,payment_method=payment_method,amount=amount)
        return Response({"id":order.id},status=status.HTTP_201_CREATED)

    
    def process_product_price(self,cart_item,currency_value):
        if cart_item.product.hot_deal:
            return round(cart_item.product.deal_price*currency_value)
        return round(cart_item.product.price*currency_value)


    def stringify_cart(self,user,currency_value):
        cart_items = Cart.objects.filter(buyer=user).exclude(ordered=True)
        output = []
        for cart in list(cart_items):
            raw_item = {}
            raw_item["product_id"] = cart.product.id
            raw_item["product_name"] = cart.product.name
            raw_item["product_price"] = self.process_product_price(cart,currency_value)
            raw_item["product_image_url"] = cart.product_image_url
            raw_item["quantity"] = cart.quantity
            raw_item["total_price"] = self.process_product_price(cart,currency_value)*cart.quantity
            raw_item["cart_id"] = cart.id
            output.append(raw_item)

        for cart in cart_items:
            cart.ordered = True

        Cart.objects.bulk_update(cart_items,["ordered"])

        return json.dumps(output)


    def get_total_amount(self,products):
        products = json.loads(products)
        total=0
        for product in products:
            total+=product.get("total_price")
        return total


class OrderDetailsView(AdminBrowsableMixin,APIView):

    def get(self,request,id,format=None):
        order = Order.objects.get(id=id)
        if not order:
            return Response({},status=status.HTTP_404_NOT_FOUND)
        serialized_order = OrderSerializer(order)
        raw_order = dict(serialized_order.data)
        products = raw_order.pop("products")
        raw_order["products"] = json.loads(products)
        return Response(raw_order,status=status.HTTP_200_OK)






class AllOrdersListView(AdminBrowsableMixin,ListAPIView):  #for admin
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()



class UploadProductImageView(AdminBrowsableMixin,APIView):

    parser_class = (FileUploadParser,)

    def post(self,request,format=None):
        serialized_product_image = ProductImageSerializer(data=request.data)
        serialized_product_image.is_valid(raise_exception=True)
        serialized_product_image.save()
        return Response(serialized_product_image.data,status=status.HTTP_201_CREATED)



class CategoriesView(AdminBrowsableMixin,ListAPIView):

    permission_classes = []

    authentication_classes = []

    def get(self,request,format=None):
        sub_categories = SubCategory.objects.all()
        serialized_categories = SubCategorySerializer(sub_categories,many=True)
        return Response(serialized_categories.data,status=status.HTTP_200_OK)



class DealsView(AdminBrowsableMixin,APIView):

    permission_classes = []

    authentication_classes = []

    def get(self,request,format=None):
        deal_products = Product.objects.filter(hot_deal = True)
        serialized_products = ProductSerializer(deal_products,many=True)
        return Response(serialized_products.data,status=status.HTTP_200_OK)



class ContactView(AdminBrowsableMixin,APIView):

    permission_classes = []

    authentication_classes = []

    def post(self,request,format=None):
        contact_payload = request.data
        serialized_contact = ContactSerializer(data=contact_payload)
        serialized_contact.is_valid(raise_exception=True)
        serialized_contact.save()
        return Response({},status=status.HTTP_200_OK)



class ReviewCreateView(AdminBrowsableMixin,APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,format=None):
        review_payload = request.data
        review_payload["reviewer"] = {"password":request.user.password}
        product = Product.objects.get(id=review_payload.get("product"))
        review_payload["product"] = dict(SimpleProductSerializer(product).data)
        serialized_review = ReviewSerializer(data=review_payload)       
        serialized_review.is_valid(raise_exception=True)
        serialized_review.save()
        return Response({},status=status.HTTP_201_CREATED)



class ListReviewsView(AdminBrowsableMixin,APIView):

    permission_classes = []

    authentication_classes = []

    def get(self,request,format=None):
        product_id = int(dict(request.GET).get("id")[0])
        reviews = Review.objects.filter(product=Product.objects.get(id=product_id))
        if reviews is not None:
            serialized_reviews = ReviewSerializer(reviews,many=True)
            return Response(serialized_reviews.data,status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_400_BAD_REQUEST)






