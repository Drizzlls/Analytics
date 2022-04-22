from django.shortcuts import render
from tapi_yandex_direct import YandexDirect
from fast_bitrix24 import Bitrix
from bitrix24 import *
import datetime
import time
import pprint
from .models import YandexData
from .forms import DateForm
import re

# Create your views here.

class Analytics_yandex:
    def __init__(self,settings):
        self.settings = settings

    def yandex_analytics(self):
        client = YandexDirect(
            access_token = self.settings["ApiKey"],
            login = self.settings["Login"],
            is_sandbox=False,
            retry_if_not_enough_units=False,
            language="ru",
            retry_if_exceeded_limit=True,
            retries_if_server_error=5,
            processing_mode="offline",
            wait_report=True,
            return_money_in_micros=False,
            skip_report_header=True,
            skip_column_header=False,
            skip_report_summary=True,
        )

        body = {
            "params": {
                "SelectionCriteria": {
                    "DateFrom": self.settings['DateFrom'],
                    "DateTo": self.settings['DateTo'],
                    # "Filter": [{
                    #     "Field": "Impressions",
                    #     "Operator": "GREATER_THAN",
                    #     "Values": ["0"]
                    # }],
                    "Filter": [{
                        "Field": self.settings['Field'] ,
                        "Operator": self.settings['Operator'],
                        "Values": self.settings['Values']
                    },

                    ],

                },
                "ReportType": self.settings["ReportType"],
                "OrderBy": [{
                    "Field": "Year"
                }],

                "FieldNames": self.settings['FieldNames'],
                "ReportName": "Actual "
                              f"{datetime.datetime.now()}",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "YES",
                "IncludeDiscount": "YES"
            }
        }
        report = client.reports().post(data=body)
        yandex_dict = report().to_dict()
        return yandex_dict

class Analytics_bitrix24:
    def __init__(self,data,date_from,date_to,utm):
        self.data = data
        self.date_from = date_from
        self.date_to = date_to
        self.utm = utm

    def bitrix24_analytics(self):
        bitrix_dict = self.data
        webhook = "https://novoedelo.bitrix24.ru/rest/16/6635dozezxf564a7/"
        b = Bitrix24(webhook)
        '''
        1) Не обработан — NEW
        2) НЕДОЗВОН — 22
        3) Долгосрочные/Залог — 65 (V)
        4) Разбор — 69 v
        5) Встреча/Консультация — 71 (V)
        6) Решение — 75 (V)
        7) Договор/Оплата — 72 (V)
        8) Дозагрузка документов — 78 (V)
        9) Возвращен на доработку — 77 (V)
        10) Проверка — 76 (V)
        11) Документы — 70 (V)
        12) Качественный — CONVERTED (V)
        '''

        сoncludedAgreements = ["78","77","76","CONVERTED"]
        qualitativeLeads = ["65", "69", "71", "75", "72", "78", "77", "76", "70", "CONVERTED"]
        for r in bitrix_dict:
            deals = b.callMethod(
                'crm.lead.list',
                filter={
                    f'{self.utm}.': r['CampaignId'],
                    '>DATE_CREATE': self.date_from,
                    '<DATE_CREATE': self.date_to,
                })

            filterForDataBitrix = {
                "Deal": len([item for item in deals if item['STATUS_ID'] in сoncludedAgreements]),
                "Leads": len([item for item in deals]),
                "Qualitative": len([item for item in deals if item["STATUS_ID"] in qualitativeLeads]),
            }

            filterForDataYandex = {
                "CostPerConversion": float(r['Cost']) / float(r['Conversions']) if r['Conversions'] != '--' else 0,
                "CostOfQualityLead": float(r['Cost']) / filterForDataBitrix['Qualitative'] if filterForDataBitrix['Qualitative'] != 0 else 0,
                "ContractPrice": float(r['Cost']) / filterForDataBitrix['Deal'] if filterForDataBitrix['Deal'] != 0 else 0,
                "Profit": filterForDataBitrix['Deal'] * 100000 - float(r['Cost'])
            }

            r.update(filterForDataBitrix)
            r.update(filterForDataYandex)
            time.sleep(1)
        return bitrix_dict



def index(request):
    accounts = YandexData.objects.all()

    if request.POST:
        form = DateForm(request.POST)
        if form.is_valid():
            a = str(form.cleaned_data["dateFrom"])[:-15]
            print(a)

    else:
        form = DateForm
    return render(request,"yandex_analytics/index.html",{"accounts":accounts,'form' : form})

def index_company(request,company_id):
    UrlStr = request.path
    new_url = UrlStr.split('/')
    settings = {
        "FieldNames": ["CampaignId", "Clicks", "Cost", "Conversions", "AvgCpc", "BounceRate", "Year"],
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "Field": "CampaignId",
        "Operator" : "EQUALS",
        "Values": ["59472447"],
        "ApiKey" : YandexData.objects.get(login = company_id).apiKey,
        "Login": YandexData.objects.get(login=company_id).login,
        "UTM": "UTM_CAMPAIGN",

    }
    if request.POST:
        settings['DateFrom'] = request.POST["date_from"]
        settings['DateTo'] = request.POST["date_to"]
    else:
        settings['DateFrom'] = datetime.date.today()
        settings['DateTo'] = datetime.date.today()

    company_yandex = Analytics_yandex(settings=settings)
    get_company = company_yandex.yandex_analytics()

    company_bitrix24 = Analytics_bitrix24(data = get_company,date_to = settings['DateTo'],date_from = settings['DateFrom'],utm=settings['UTM'])
    full_data = company_bitrix24.bitrix24_analytics()
    return render(request, 'yandex_analytics/indexCompany.html',{'req':full_data,'url_comp':new_url[2]})

def index_group(request,company_id,group_id):
    UrlStr = request.path
    new_url = UrlStr.split('/')
    settings = {
        "FieldNames": ["CampaignId", "Clicks", "Cost", "Conversions", "AvgCpc", "BounceRate", "Year","AdGroupName","AdGroupId"],
        "ReportType": "ADGROUP_PERFORMANCE_REPORT",
        "Field": "CampaignId",
        "Operator" : "EQUALS",
        "Values": [f"{group_id}"],
        "ApiKey": YandexData.objects.get(login=company_id).apiKey,
        "Login": YandexData.objects.get(login=company_id).login,
        "UTM": "UTM_CAMPAIGN"

    }
    if request.POST:
        settings['DateFrom'] = request.POST["date_from"]
        settings['DateTo'] = request.POST["date_to"]
    else:
        settings['DateFrom'] = datetime.date.today()
        settings['DateTo'] = datetime.date.today()

    group_yandex = Analytics_yandex(settings=settings)
    get_group = group_yandex.yandex_analytics()

    group_bitrix24 = Analytics_bitrix24(data = get_group,date_to = settings['DateTo'],date_from = settings['DateFrom'],utm=settings['UTM'])
    full_data_group = group_bitrix24.bitrix24_analytics()
    return render(request, 'yandex_analytics/campn.html',{'req':full_data_group,"group":group_id,'url_comp':new_url[2],"url_group":new_url[3]})

def index_ad(request,company_id,group_id,ad_id):
    settings = {
        "FieldNames": ["CampaignId", "Clicks", "Cost", "Conversions", "AvgCpc", "BounceRate", "Year", "AdId"],
        "ReportType": "AD_PERFORMANCE_REPORT",
        "Field": "AdGroupId",
        "Operator": "EQUALS",
        "Values": [f"{ad_id}"],
        "ApiKey": YandexData.objects.get(login=company_id).apiKey,
        "Login": YandexData.objects.get(login=company_id).login,
        "UTM": "UTM_CONTENT",
        'Search': 'AdId'
    }
    if request.POST:
        settings['DateFrom'] = request.POST["date_from"]
        settings['DateTo'] = request.POST["date_to"]
    else:
        settings['DateFrom'] = datetime.date.today()
        settings['DateTo'] = datetime.date.today()
    group_yandex = Analytics_yandex(settings=settings)
    get_group = group_yandex.yandex_analytics()
    group_bitrix24 = Analytics_bitrix24(data=get_group, date_to=settings['DateTo'], date_from=settings['DateFrom'],utm=settings['UTM'])
    full_data_ad = group_bitrix24.bitrix24_analytics()
    return render(request, 'yandex_analytics/ad.html', {'req': full_data_ad})


