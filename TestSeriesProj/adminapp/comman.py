from adminapp.models import Category, SubCategory


def get_categories():
    try:
        categoris = []
        for category in Category.objects.filter(record_status='ACTIVE'):
            categoris.append({'id': category.id, 'category': category.category})
    except Exception, ex:
        print 'Exception|comman|get_categories|', ex
    return categoris
