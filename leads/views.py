from django.shortcuts import render
from rest_framework import generics
from .models import Lead
from django.http import HttpResponse
from .serializers import LeadSerializer
from rest_framework.permissions import AllowAny  # Import AllowAny
from django.http import JsonResponse
# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.views.decorators.http import require_http_methods
from .models import Stage  # Import your Stage model here
from .tasks import generate_or_get_report, get_today_report, get_yesterday_report,get_today,get_yesterday

class LeadListCreateAPIView(ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = (AllowAny,)  # Use AllowAny permission

class LeadDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = (AllowAny,)  # Use AllowAny permission


#stage for lead

@require_http_methods(["GET"])
def lead_stage(request, lead_id):
    try:
        lead = Lead.objects.get(id=lead_id)
        if lead.stage_id:
            stage = Stage.objects.get(id=lead.stage_id, model_name='lead')  # Assuming model_name field exists in Stage
            stage_data = {
                'id': stage.id,
                'status': stage.status,
                'model_name': stage.model_name,
            }
            return JsonResponse(stage_data, status=200)
        else:
            return JsonResponse({'error': 'Lead stage not found'}, status=404)
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)
    except Stage.DoesNotExist:
        return JsonResponse({'error': 'Stage not found for this lead'}, status=404)



@require_http_methods(["GET"])
def all_stages(request):
    tenant_id = request.headers.get('X-Tenant-Id')
    if not tenant_id:
        return JsonResponse({'error': 'Tenant ID is required in headers'}, status=400)

    try:
        stages = Stage.objects.filter(model_name='lead', tenant_id=tenant_id)  # Adjust the filter as per your model

        if stages.exists():
            stages_data = [{
                'id': stage.id,
                'status': stage.status,
            } for stage in stages]
            return JsonResponse({'stages': stages_data}, status=200)
        else:
            return JsonResponse({'error': 'No stages found for the given tenant'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.db.models import Sum
from opportunities.models import Opportunity
from .models import Report
from datetime import date, timedelta


# Function to get today's date
def get_today():
    return date.today()

# Function to get yesterday's date
def get_yesterday():
    return date.today() - timedelta(days=1)

def get_yesterday_report():
    yesterday = get_yesterday()
    report_yesterday = Report.objects.filter(
        created_at__date=yesterday
    ).first()
    return report_yesterday

def generate_or_get_report():
        today = get_today()
        yesterday = get_yesterday()
        
    
        report_today = Report.objects.filter(created_at__date=today).first()
        
        if report_today:
            return report_today
        
    
        #report_yesterday = Report.objects.filter(created_at__date=yesterday).first()
        
 
        # Generate a new report for today
        closed_won_revenue = Opportunity.objects.filter(stage__status='CLOSED WON').aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0
        other_lead_amount = Lead.objects.exclude(stage__status='closed won').aggregate(total_amount=Sum('opportunity_amount'))['total_amount'] or 0
        total_leads = Lead.objects.count()

        new_report = Report(
            leads_amount=other_lead_amount,
            revenue=closed_won_revenue,
            total_leads=total_leads,
            created_at=today  # Set the created_at field to today's date
        )
        new_report.save()
        
        return new_report
    

# View function to generate or retrieve the latest report
def generate_and_get_report_view(request):
    report = generate_or_get_report()

    if report:
        # Prepare the data for the latest report
        data = {
            'created_at': report.created_at,
            'leads_amount': report.leads_amount,
            'revenue': report.revenue,
            'total_leads': report.total_leads,
        }
    else:
        # Handle the case where report could not be generated (e.g., no report for yesterday)
        data = {
            'error': 'Could not generate report for today. Ensure there is a report for yesterday.'
        }

    return JsonResponse(data)

# View function to retrieve all reports
def retrieve_all_reports_view(request):
    reports = Report.objects.all()

    # Prepare the data for all reports
    all_reports_data = []
    for report in reports:
        report_data = {
            'created_at': report.created_at,
            'leads_amount': report.leads_amount,
            'revenue': report.revenue,
            'total_leads': report.total_leads,
        }
        all_reports_data.append(report_data)

    return JsonResponse(all_reports_data, safe=False)

def get_today_report():
    today = get_today()
    report_today = Report.objects.filter(created_at__date=today).first()
    return report_today

# View function to retrieve today's report
def retrieve_today_report_view(request):
    report_today = get_today_report()

    if report_today:
        data = {
            'created_at': report_today.created_at,
            'leads_amount': report_today.leads_amount,
            'revenue': report_today.revenue,
            'total_leads': report_today.total_leads,
        }
    else:
        data = {
            'error': 'No report found for today.'
        }

    return JsonResponse(data)

# View function to retrieve yesterday's report
def retrieve_yesterday_report_view(request):
    report_yesterday = get_yesterday_report()

    if report_yesterday:
        data = {
            'created_at': report_yesterday.created_at,
            'leads_amount': report_yesterday.leads_amount,
            'revenue': report_yesterday.revenue,
            'total_leads': report_yesterday.total_leads,
        }
    else:
        data = {
            'error': 'No report found for yesterday.'
        }

    return JsonResponse(data)

