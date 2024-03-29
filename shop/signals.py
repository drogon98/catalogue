from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProductImage,Product,Review

@receiver(post_save,sender=ProductImage)
def save_img_url(sender,instance,created=False,**kwargs):
    if created:
        img_url = instance.image.url
        product = Product.objects.filter(id=instance.product.id)
        c = product[0].img_urls
        if c:
            s = c+","+img_url
        else:
            s = img_url
        product.update(img_urls = s)


@receiver(post_save,sender=Review)
def update_product_reviews(sender,instance,created=False,**kwargs):
    if created:
        product = Product.objects.filter(id=instance.product.id)
        count_ = product[0].reviews+1
        product.update(reviews=count_)