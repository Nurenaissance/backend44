from django.shortcuts import render
from rest_framework import generics
from .models import Opportunity
from .serializers import OpportunitySerializer
from rest_framework.permissions import IsAdminUser
from django.http import JsonResponse
from .utils import calculate_rfm_metrics


from datetime import datetime, timedelta,date
from django.db.models import Count,Sum
from .models import Contact , Account
from leads.models import Lead
from interaction.models import Interaction, Calls, Meetings
from campaign.models import Campaign
from django.contrib.auth import get_user_model
from vendors.models import Vendors
from django.views.decorators.http import require_http_methods
from leads.models import Stage  # Import your Stage model here
import json
from django.utils import timezone

# Create your views here.

class OpportunityListAPIView(generics.ListCreateAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    #permission_classes = (IsAdminUser,)

# views.py
class OpportunityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    # Uncomment the line below to restrict access to admin users only
    # permission_classes = (IsAdminUser,)


def rfm_analysis(request):
    customers = Opportunity.objects.all().values_list('account', flat=True).distinct()
    rfm_data = []
    for customer_id in customers:
        customer_opportunities = Opportunity.objects.filter(account_id=customer_id)
        recency, frequency, monetary = calculate_rfm_metrics(customer_opportunities)
        rfm_data.append({'customer_id': customer_id, 'recency': recency, 'frequency': frequency, 'monetary': monetary})
    return JsonResponse(rfm_data, safe=False)

#stage for opportunity

@require_http_methods(["GET"])
def opportunity_stage(request, opportunity_id):
    try:
        opportunity = Opportunity.objects.get(id=opportunity_id)
        if opportunity.stage_id:
            stage = Stage.objects.get(id=opportunity.stage_id, model_name='opportunity')  # Assuming model_name field exists in Stage
            stage_data = {
                'id': stage.id,
                'status': stage.status,
                'model_name': stage.model_name,
            }
            return JsonResponse(stage_data, status=200)
        else:
            return JsonResponse({'error': 'Opportunity stage not found'}, status=404)
    except Opportunity.DoesNotExist:
        return JsonResponse({'error': 'Opportunity not found'}, status=404)
    except Stage.DoesNotExist:
        return JsonResponse({'error': 'Stage not found for this opportunity'}, status=404)
    
@require_http_methods(["GET"])
def all_stages(request):
    tenant_id = request.headers.get('X-Tenant-Id')
    if not tenant_id:
        return JsonResponse({'error': 'Tenant ID is required in headers'}, status=400)

    try:
        stages = Stage.objects.filter(model_name='opportunity', tenant_id=tenant_id)  # Adjust the filter as per your model

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



CustomUser = get_user_model()

def get_report_by_id(request, report_id):

    report_id_to_function = {
        'total_leads': get_total_leads,
        'this_month_leads': get_new_leads_this_month,
        'today_lead':get_leads_by_today,
        'converted_leads':get_converted_leads,
        'lead_source':get_leads_by_source,
        'total_calls': get_calls_report_data,
        'total_opportunities': get_opportunity_report_data,
        'total_meetings': get_meetings_report_data,
        'top_users': get_top_users, 
        'Contact_mailing_list':get_contact_address,
        'total_calls_emails':get_calls_emails,
        'total_campaign':get_total_campaign,
        'total_interaction':get_interaction_total,
        'leads_account_name':get_leads_by_account_name,
        'campaign_status':get_campaign_status,
        'today_sales':get_todays_sales,
        'sales_by_lead_source':get_sales_by_lead_source,
        'sales_this_month':get_sales_this_month,
        'deal_lost':deal_lost,
        'vendor_owner':get_vendors_owner,
        'lead_stages':get_lead_status_counts,
        'opportunity_stages':get_opportunity_status_counts,
  

    }
    report_function = report_id_to_function.get(report_id)

    if not report_function:
        return JsonResponse({'error': 'Invalid report type'}, status=400)

    try:
        report_data = report_function()
        return JsonResponse(report_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#--------leads-----

def get_total_leads():
        leads = Lead.objects.all()
        return{'total_leads': leads.count(), 'leads': list(leads.values(
        'id',
        'title',
        'first_name',
        'last_name',
        'email',
        'phone',
        'stage__status', 
        'source',
        'address',
        'website',
        'description',
        'assigned_to',
        'account__Name',  
        'opportunity_amount',
        'createdBy', 
        'createdOn',
        'isActive',
        'enquery_type',
        'money',
        'tenant',  
        'priority'))}

def get_new_leads_this_month():
     # Get the current date and time with timezone information
    today = timezone.now()

    # Replace to get the start of the month, ensuring it's timezone-aware
    start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculate the start of the next month and ensure it's timezone-aware
    next_month = start_date + timedelta(days=32)
    end_date = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Filter leads created within this month
    new_leads_count = Lead.objects.filter(createdOn__gte=start_date, createdOn__lt=end_date).count()

    return {'new_leads_count': new_leads_count}

def get_converted_leads():
    converted_leads = Lead.objects.filter(stage__status='converted')
    return{'total_converted leads':converted_leads.count(),'converted_leads':list(converted_leads.values('id', 'first_name', 'last_name','phone','stage__status','account'))}


def get_leads_by_source():
    lead_source = Lead.objects.filter(source__isnull=False)
    return{'total lead':lead_source.count(), 'source':list(lead_source.values('id', 'source','email','createdOn','createdBy','account_name','first_name','last_name'))}
    

def get_leads_by_today():
    today_date = date.today()
    leads_today = Lead.objects.filter(createdOn__date=today_date)
    return {'total_today_leads':leads_today.count(), 'today_leads':list(leads_today.values('email','phone','source','stage__status')) }
  
def get_leads_by_account_name():
    Account_name = Lead.objects.filter()
    return {'total_leads_account_name':Account_name.count(),'leads_account_name':list(Account_name.values('id','account_name'))}
  
def get_sales_by_lead_source():
    opportunities = Opportunity.objects.filter(stage__status='CLOSED WON')
    sales_by_source = opportunities.values('lead_source').annotate(total_sales=Sum('amount'))
    sales_data = list(sales_by_source)
    return {'total_sales_by_lead_source': sales_data}

#-----end leads------

def get_calls_report_data():
    call = Calls.objects.all()
    return {'total_calls': call.count(), 'calls': list(call.values())}


def get_opportunity_report_data():
    Opportunities = Opportunity.objects.all()
    return {'total_opportunity': Opportunities.count(), 'opportunity':list(Opportunities.values())}


def get_meetings_report_data():
    Meeting  = Meetings.objects.all()
    return {'total_meeting': Meeting.count(),'meetings':list(Meeting.values())}
 
def get_top_users():
    top_users = CustomUser.objects.order_by('-date_joined')[:10]
    return {'top_users': list(top_users.values('id', 'username', 'date_joined'))}


def get_contact_address():
    contacts = Contact.objects.all()
    return {'total contacts': contacts.count(), 'Contacts': list(contacts.values('id','name', 'address'))}


def get_calls_emails():
    call = Calls.objects.all()
    email = Contact.objects.all()
    call_data = list(call.values())
    email_data = list(email.values())
    return {'total calls':call.count(),'calls':call_data,'total emails': email.count(), 'eamils':email_data}
 

def get_total_campaign():
    total_campaign = Campaign.objects.all()
    return {'total campaign':total_campaign.count(), 'campaign':list(total_campaign.values('campaign_owner','campaign_name'))}
 

def get_campaign_status():
    status = Campaign.objects.all()
    return {'total_status':status.count(), 'status':list(status.values('id','status','campaign_owner','campaign_name','start_date','end_date'))}


def get_interaction_total():
    total_interaction = Interaction.objects.all()
    return {'total_interaction':total_interaction.count(), 'interaction': list(total_interaction.values('id','notes','entity_type'))}
 

def get_todays_sales():
    today = date.today()
    opportunities = Opportunity.objects.filter(stage__status='CLOSED WON', closedOn=today)
    total_sales = sum(opportunity.amount for opportunity in opportunities)
    return {'total_sales': total_sales, 'opportunities': list(opportunities.values())}




def get_sales_this_month():
    today = date.today()
    start_of_month = today.replace(day=1)    
    opportunities = Opportunity.objects.filter(
        stage__status='CLOSED WON',
        closedOn__gte=start_of_month,
        closedOn__lte=today
    ) 
    total_sales = opportunities.aggregate(total_sales=Sum('amount'))['total_sales'] or 0
    return {'total_sales_this_month': total_sales}
  

def deal_lost():
    Opportunities = Opportunity.objects.filter(stage__status='CLOSED LOST')
    deal_lost= {'total_lost_deal':Opportunities.count(),'deal_lost':list(Opportunities.values())}
    return deal_lost


def get_vendors_owner():
    vender = Vendors.objects.all()
    owner_data = {'total_owner':vender.count(),'vendor_owner':list(vender.values('vendor_owner'))}
    return owner_data

def get_lead_status_counts():
    # Query to count leads grouped by stage__status
    status_counts = Lead.objects.values('stage__status').annotate(count=Count('id'))
    
    # Prepare data in the desired format
    data = [['Stage', 'Count']]  # Initial header row
    
    for item in status_counts:
        data.append([item['stage__status'], item['count']])
    
    # Return data as JSON response
    return data

def get_opportunity_status_counts():
    # Query to count opportunities grouped by stage__status
    status_counts = Opportunity.objects.values('stage__status').annotate(count=Count('id'))
    
    # Prepare data in the desired format
    data = [['Stage', 'Count']]  # Initial header row
    
    for item in status_counts:
        data.append([item['stage__status'], item['count']])
    
    return data
