import json
import yaml
from yaml.loader import SafeLoader
from django.http import HttpResponse


class UpdateData(models.Model):

    def upload_file(request):
        if request.method == 'POST':
            form = ModelFormWithFileField(request.POST, request.FILES)
            if form.is_valid():
                filetype = request.FILES['product_data'].content_type
                if filetype == 'application/yaml':
                    # file is saved
                    form.save()
                    return HttpResponseRedirect('index')
                else:
                    return JsonResponse({'Status': False, 'Error': 'Допускаются только файлы формата yaml.'},
                                        status=403)
            else:
                return JsonResponse({'Status': False, 'Error': 'Файл не прошел проверку.'}, status=403)

        data = yaml.load(product_data, Loader=SafeLoader)

        shop = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
        for category in data['categories']:
            category_object = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)

        return JsonResponse({'Status': True})

        else:
        form = ModelFormWithFileField()

    return render(request, 'upload.yaml', {'form': form})
