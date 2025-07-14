from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manufacturer
from .serializers import ManufacturerSerializer
from rest_framework.parsers import JSONParser

#dodawać manufacturera może tylko administrator, wypisywać mogą wszyscy
@api_view(['GET','POST'])
def manufacturer_list(request):
    if request.method == 'GET':
        manufacturers=Manufacturer.objects.all()
        serializer=ManufacturerSerializer(manufacturers,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data=JSONParser().parse(request)
        serializer=ManufacturerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
    else:
        return Response({'Allowed methods':'GET, POST'},status=405)
