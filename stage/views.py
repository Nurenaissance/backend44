from django.shortcuts import render

# Create your views here.

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import Stage
from tenant.models import Tenant
from .defaults import get_or_create_default_stages
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import json


def get_tenant_from_headers(request):
    tenant_id = request.headers.get('X-Tenant-Id')
    if not tenant_id:
        return None
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        return tenant
    except Tenant.DoesNotExist:
        return None
    
@permission_classes([AllowAny])
@require_http_methods(["GET"])
def stage_list(request, model_name):
    tenant = get_tenant_from_headers(request)

    if tenant is None:
        return JsonResponse({'error': 'Tenant not found'}, status=400)

    # Retrieve or create default stages if they don't exist
    get_or_create_default_stages(tenant, model_name)

    # Get all stages for the given model_name and tenant
    all_stages = Stage.objects.filter(tenant=tenant, model_name=model_name).order_by('id')

    stages_data = [{'id': stage.id, 'status': stage.status} for stage in all_stages]
    return JsonResponse(stages_data, safe=False, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def stage_create(request):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        model_name = data.get('model_name')

        tenant = get_tenant_from_headers(request)

        if not status:
            return JsonResponse({'error': 'Missing status'}, status=400)
        if not model_name:
            return JsonResponse({'error': 'Missing model_name'}, status=400)
        if not tenant:
            return JsonResponse({'error': 'Tenant not found'}, status=400)

        # Check if the model_name is valid (you might want to validate against allowed values)
        if model_name not in ['lead', 'opportunity']:
            return JsonResponse({'error': 'Invalid model_name'}, status=400)

        # Create the stage object
        stage_obj = Stage.objects.create(status=status, model_name=model_name, tenant=tenant)

        # Return success response
        return JsonResponse({'id': stage_obj.id, 'status': stage_obj.status, 'model_name': stage_obj.model_name}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def stage_update(request, stage_id):
    try:
        stage_obj = get_object_or_404(Stage, id=stage_id)
        data = json.loads(request.body)
        status = data.get('status')

        if not status:
            return JsonResponse({'error': 'Missing status'}, status=400)

        stage_obj.status = status
        stage_obj.save()
        return JsonResponse({'id': stage_obj.id, 'status': stage_obj.status, 'model_name': stage_obj.model_name}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def stage_delete(request, stage_id):
    try:
        stage_obj = get_object_or_404(Stage, id=stage_id)
        stage_obj.delete()
        return JsonResponse({'message': 'Stage deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
