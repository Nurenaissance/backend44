"""simplecrm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from accounts import views as aviews 
from leads import views as lviews
from opportunities import views as oviews
from contacts import views as cviews
from interaction import views as inviews
from tasks import views as tviews
from reminder import views as rviews
from simplecrm import Register_login as Reg
from simplecrm import ingestexcel as ingex
from simplecrm import get_column_name as getxcol
from simplecrm import get_user as getuser
from tenant import views as tenview
from campaign import views as campview
from interaction.active_account import get_most_active_accounts
from node_temps import views as nviews
from interaction.views import extract_cltv
from simplecrm import recent_request as rr
from interaction.active_account import get_most_active_accounts
from interaction.active_account import get_most_active_contacts
from interaction.active_account import get_lead_summation
from vendors import views as vendview
from product import views as prodview
from documents import views as docview
from dynamic_entities import views as dyv
# from loyalty import views as lv
from simplecrm import views as simviews
from simplecrm import tracking as track
from custom_fields import views as cfviews
from simplecrm import tractcount as trac
from tickets import views as tickview
from analytics import views as analyticsviews
from drafts import views as draftview
from wallet import views as wallview
from stage import views as stageview
from helpers import upload_dispatch as u_dispatch, query_dispatch as q_dispatch
from .etl2  import add_nodes
from .new_database import process_nodes
from custom_fields.views import export_data_for_custom_field as edfc
from topicmodelling import views as topicviews
from whatsapp_chat import views as wa_chat_views
from rest_framework.routers import DefaultRouter
from communication import insta_msg as imsg 
from communication import views as commviews
from communication import prompting as commprom

router = DefaultRouter()
router.register(r'groups', inviews.GroupViewSet, basename='group')

urlpatterns = router.urls


urlpatterns = [
    #path('admin/', admin.site.urls),
    path('register/', Reg.register, name='register'),  # Endpoint for user registration
    path('login/', Reg.LoginView.as_view(), name='login'), 
    path(r'accounts/', aviews.AccountListCreateAPIView.as_view(), name='account-list'),
    path('accounts/<int:pk>/', aviews.AccountDetailAPIView.as_view(), name='account-detail'),
    path("active_accounts/",get_most_active_accounts, name="most-active-entites"),
    path(r'leads/', lviews.LeadListCreateAPIView.as_view(), name='lead-list'),
    path('leads/<int:pk>/',lviews.LeadDetailAPIView.as_view(), name='lead-detail'),
    path(r'opportunities/', oviews.OpportunityListAPIView.as_view(), name='opportunity-list'),
    path('opportunities/<int:pk>/', oviews.OpportunityDetailAPIView.as_view(), name='opportunity-detail'),
    path('contacts/', cviews.ContactListCreateAPIView.as_view(), name='contact-list-create'),
    path('contacts/<int:pk>/', cviews.ContactDetailAPIView.as_view(), name='contact-detail'),

    path('meetings/', inviews.MeetingListCreateAPIView.as_view(), name='meeting-list-create'),
    path('meetings/<int:pk>/', inviews.MeetingDetailAPIView.as_view(), name='meeting-detail'),
    path('calls/', inviews.callsListAPIView.as_view(), name='calls'), 
    path('calls/<int:pk>/', inviews.callsDetailAPIView.as_view(), name='calls-detail'),
    path('interaction/', inviews.InteractionListAPIView.as_view(), name='interaction'),  
    path('interaction/<int:pk>/',inviews.InteractionDetailAPIView.as_view(), name='interaction-detail'),
    path('tasks/', tviews.TaskListCreateAPIView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', tviews.TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-detail'), 
    path('reminders/', rviews.ReminderListAPIView.as_view(), name='reminder-list'),
    path('reminder/<int:pk>/', rviews.ReminderDetailAPIView.as_view(), name='reminder-detail'), 
    path('uploadexcel/', ingex.ImportLeadData, name='excel'),
    path('excel-column/', getxcol.get_excel_columns, name='column_excel'),
    path('get-user/<str:username>/', getuser.get_user_by_username, name='get_user'),
    path('get-all-user/', getuser.get_all_users, name='get_all_user'),
    path('createTenant/', tenview.tenant_list, name='tenant'),
    path('logout/', Reg.LogoutView.as_view(), name='logout'),
    path('campaign/', campview.CampaignViewSet.as_view(), name='campaigns'),
    path('campaign/<int:pk>/', campview.CampaignDetailAPIView.as_view(), name='campaigns'),
    path('campaign/stats/', campview.CampaignStatsAPIView.as_view(), name='campaign-stats'),  # Add this line
    path(r'node-templates/', nviews.NodeTemplateListCreateAPIView.as_view(), name='node-template-list-create'),
    path('node-templates/<int:pk>/', nviews.NodeTemplateDetailAPIView.as_view(), name='node-template-detail'),
    path('extract_cltv/<int:entity_type_id>/', extract_cltv, name='extract_cltv'),
    path ('report/<str:report_id>/', oviews.get_report_by_id, name='get_report_by_id'),
    path('recent_request/<str:model_name>/',rr.recent_request, name='recent_request'),
    path("active_accounts/",get_most_active_accounts, name="most-active-entites"),
    path("active_contacts/",get_most_active_contacts, name="most-active-entites"),
    path("leads_sum/",get_lead_summation, name="most-active-entites"),
    path('products/', prodview.get_products, name='products-list'),
    path('product/<int:pk>/', prodview.ProductDetailAPIView.as_view(), name='product-detail'),
    path('experience/',prodview.ExperienceListAPIView.as_view() , name='experience-list'),
    path('experience/<int:pk>/', prodview.ExperienceDetailAPIView.as_view(), name='experience-detail'),
    path('vendors', vendview.VendorsListAPIView.as_view(), name='vendors-list'),
    path('vendor/<int:pk>', vendview.VendorDetailAPIView.as_view(), name='vendor-detail'),
    path('documents/', docview.DocumentListAPIView.as_view(), name='vendors-list'),
    path('documents/<int:pk>/', docview.DocumentDetailAPIView.as_view(), name='vendor-detail'),
    path('return-documents/<int:entity_type>/<int:entity_id>/', docview.RetrieveDocumentsView.as_view(), name='retrieve-documents'),
    path('return-documents/<int:entity_type>/', docview.RetrieveDocumentsView.as_view(), name='retrieve-documents'),    
    path('create-dynamic-model/', dyv.CreateDynamicModelView.as_view(), name='create_dynamic_model'),
    path('dynamic-models/', dyv.DynamicModelListView.as_view(), name='dynamic_model_list'),
    path('dynamic-model-data/<str:model_name>/', dyv.DynamicModelDataView.as_view(), name='dynamic_model_data'),
    path('delete-dynamic-model/<str:model_name>/', dyv.DeleteDynamicModelView.as_view(), name='delete_dynamic_model'),
    path('return-interaction/<int:entity_type>/<int:entity_id>/', inviews.RetrieveInteractionsView.as_view(), name='retrieve-interaction'),
    path('return-interaction/<int:entity_type>/', inviews.RetrieveInteractionsView.as_view(), name='retrieve-interaction'),    
    path('deduplicate/', simviews.deduplicate_view, name='deduplicate'),
    path('create-custom-field/', cfviews.create_custom_field, name='create_custom_field'),
    path('user/<int:user_id>/tasks/', tviews.UserTasksListAPIView.as_view(), name='user-tasks-list'),
    path('track_open/<str:tracking_id>/', track.TrackOpenView.as_view(), name='track_open'),
    path('track_click/<str:trackingId>/<str:linktrackingId>/', track.TrackLinkView.as_view(), name='track_click'),
    path('track_open_count/', trac.TrackOpenCountView.as_view(), name='track_open_count'),
    path('tickets/', tickview.TicketListAPIView.as_view(), name='ticket-list'),
    path('tickets/<int:pk>/', tickview.TicketDetailAPIView.as_view(), name='ticket-detail'),
    path('stage/list/<str:model_name>/', stageview.stage_list, name='stage-list'),#stage
    path('stage/create/', stageview.stage_create, name='stage-create'),
    path('stage/update/<int:stage_id>/', stageview.stage_update, name='stage-update'),
    path('stage/delete/<int:stage_id>/', stageview.stage_delete, name='stage-delete'),
    path('opportunity/<int:opportunity_id>/stage/', oviews.opportunity_stage, name='opportunity_stage'),
    path('lead/<int:lead_id>/stage/', lviews.lead_stage, name='lead_stage'), 
    path('lead/stage/', lviews.all_stages, name='all_lead_stage'), 
    path('opportunity/stage/', oviews.all_stages, name='all_opportunity_stage'), 
    path('generate-report/', lviews.generate_and_get_report_view, name='generate_report'),#report
    path('retrieve-reports/', lviews.retrieve_all_reports_view, name='retrieve_reports'),
    path('today/', lviews.retrieve_today_report_view, name='retrieve_today_report'),
    path('yesterday/', lviews.retrieve_yesterday_report_view, name='retrieve_yesterday_report'),
    path('execute-query/', analyticsviews.ExecuteQueryView.as_view(), name='execute_query'),
    path('whatsapp_convo_post/<str:contact_id>/', inviews.save_conversations, name='save_whatsapp_convo'),
    path('whatsapp_convo_get/<str:contact_id>/',inviews.view_conversation, name='get_whatsapp_convo'),
    path('unique_insta_profiles/',inviews.get_unique_instagram_contact_ids, name='get_all_insta'),
    path('drafts/', draftview.DraftListCreateAPIView.as_view()),           # List and create drafts
    path('drafts/<int:id>/', draftview.DraftDetailAPIView.as_view()),
    path('contacts_of_account/<int:account_id>/',cviews.ContactByAccountAPIView.as_view(), name='contacts-by-account'),
    path('contacts-by-phone/<int:phone>/', cviews.ContactByPhoneAPIView.as_view(), name='contacts-by-phone'),
    path('wallet/recharge/',wallview.recharge_wallet, name='recharge_wallet'),
    path('wallet/deduct/',wallview.deduct_from_wallet, name='deduct_from_wallet'),
    path('wallet/balance/',wallview.get_wallet_balance, name='get_wallet_balance'),
    path('wallet/transactions/',wallview.get_last_n_transactions, name='get_wallet_balance'),
    path('query/', q_dispatch.dispatch, name='query'),
    path('upload/', u_dispatch.dispatcher, name='upload_dispatch'),
    path('addrows/' , add_nodes, name="add nodes"),
    path('processrows/' ,process_nodes, name="process nodes"),
    path('test/', edfc, name="export_custom_field"),
    path('perform-topic-modelling/', topicviews.perform_topic_modelling, name='perform_topic_modeling'),
    path('email-campaigns/', campview.EmailCampaignViewSet.as_view({'get': 'list', 'post': 'create'}), name='email-campaign-list'),
    path('email-campaigns/<int:pk>/', campview.EmailCampaignViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='email-campaign-detail'),
    path('instagram-campaigns/', campview.InstagramCampaignViewSet.as_view({'get': 'list', 'post': 'create'}), name='instagram-campaign-list'),
    path('instagram-campaigns/<int:pk>/', campview.InstagramCampaignViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='instagram-campaign-detail'),
    path('whatsapp-campaigns/', campview.WhatsAppCampaignViewSet.as_view({'get': 'list', 'post': 'create'}), name='whatsapp-campaign-list'),
    path('whatsapp-campaigns/<int:pk>/', campview.WhatsAppCampaignViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='whatsapp-campaign-detail'),
    path('save-flow/', wa_chat_views.saveFlow, name = "set whatsapp flow"),
    path('call-campaigns/', campview.CallCampaignViewSet.as_view({'get': 'list', 'post': 'create'}), name='call-campaign-list'),
    path('call-campaigns/<int:pk>/', campview.CallCampaignViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='call-campaign-detail'),
    path('emails/', inviews.EmailListAPIView.as_view(), name='email-list'),
    path('emails/<int:pk>/', inviews.EmailDetailAPIView.as_view(), name='email-detail'),
    path('sev/', prodview.simple_experience_view),
    path('get-flow/', wa_chat_views.get_flow),
    path('set-flow/', wa_chat_views.set_flow),
    path('insert-data/', wa_chat_views.insert_whatsapp_tenant_data),
    path('whatsapp_tenant/', wa_chat_views.get_whatsapp_tenant_data),
    path('save-messages/', imsg.save_messages, name='save-messages'),  # Save messages
    path('save-email-messages/', imsg.save_email_messages, name='save-email-messages'),  # Save email messages
    path('store-selected-emails/', simviews.store_selected_emails, name='store_selected_emails'),  # Store selected emails
    path('fetch-all-emails/', simviews.fetch_all_emails, name='fetch_all_emails'),  # Fetch all emails
    path('set-status/', wa_chat_views.update_message_status),

    path('conversations/', commviews.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', commviews.ConversationDetailView.as_view(), name='conversation-detail'),

    path('messages/', commviews.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', commviews.MessageDetailView.as_view(), name='message-detail'),

    # whatsapp interaction to message
    path('save_whatsapp_conversations/', inviews.save_whatsapp_conversations_to_messages, name='save_interaction_conversations'),

    # all message to conversations
    path('group-messages/', commviews.GroupMessagesView.as_view(), name='group_messages'),

     # Sentiment Analysis URLs
    path('sentiment-analyses/', commviews.SentimentAnalysisListCreateView.as_view(), name='sentiment-analysis-list-create'),
    path('sentiment-analyses/<int:pk>/', commviews.SentimentAnalysisDetailView.as_view(), name='sentiment-analysis-detail'),

    # Behavioral Metrics URLs
    path('behavioral-metrics/', commviews.BehavioralMetricsListCreateView.as_view(), name='behavioral-metrics-list-create'),
    path('behavioral-metrics/<int:pk>/', commviews.BehavioralMetricsDetailView.as_view(), name='behavioral-metrics-detail'),

    # sentiment-analysis on messages
    #path('analyze-sentiment/', commviews.SentimentAnalysisView.as_view(), name='iment'),

    path('generate-prompt/', commprom.GeneratePromptView.as_view(), name='generate_prompt'),

    path('generate-reply/<str:conversation_id>/', commviews.GenerateReplyView.as_view(), name='generate_reply'),


]
urlpatterns += router.urls