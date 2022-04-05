from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Category Title")
    url_slug = models.SlugField(max_length=55, verbose_name="Category URL Slug")
    category_image = models.ImageField(upload_to='category', blank=True, null=True, verbose_name="Category Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Product Title")
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Product Image")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, verbose_name="Product Categoy", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title


class Cart(models.Model):
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    def __str__(self):
        return str(self.product)
    
    @property
    def total_price(self):
        return self.quantity * self.product.price     