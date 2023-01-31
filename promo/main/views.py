from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from main.models import Profile,ProfileCompany, Company, House, Apartment
from main.models import REACTION
from .forms import CompanyForm, companyDetailsForm, houseDetailsForm
from django.db import connection
from django.db import reset_queries

from datetime import datetime
from django.utils import timezone



# Create your views here.



def createUser(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        email = request.POST['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        if user is not None:
            profile = Profile()
            profile.user = user
            profile.name = request.POST['name']
            profile.email = email
            profile.surname = request.POST['surname']
            profile.phone = request.POST['phone']
            profile.save()
            login(request, user)
            # Redirect to a success page.
            return redirect("/company/")
        # Return an 'invalid login' error message.
        return render(request,"main/login.html")
    else:
        return  HttpResponse('unknown method')

def login_page(request):
    if request.method == 'GET':
        return render(request,"main/login.html")
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect("/company/")
        # Return an 'invalid login' error message.
        return render(request,"main/login.html")
    else:
        return  HttpResponse('unknown method')

def registerUser(request):
        return render(request,"main/register.html")
        
 

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("/")

def profile(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=request.user.id)
        if request.method == "POST":
            profile.email = request.POST['email']
            profile.name = request.POST['name']
            profile.surname = request.POST['surname']
            profile.phone = request.POST['phone']
            profile.save()
        data = {"name": user.username, "lastlogin": user.last_login, "email": user.email, "profile": profile}
        return render(request,"main/profile.html", context=data)
    return  HttpResponse('unauthorized access!')

def companies(request):
    if request.user.is_authenticated:
        
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=request.user.id)
        #reset_queries() #отсекаем запросы которые были до этого
        if request.method == "POST":
            form = CompanyForm(request.POST) #Создаём экземпляр формы и заполняем данными из запроса
            if form.is_valid():
                #Сохранение компании в БД
                company = Company()
                company.name = form.cleaned_data['name']
                company.save()
                profile_company = ProfileCompany()
                profile_company.company_id = company.id
                profile_company.profile_id = profile.id
                profile_company.save()

                return redirect("/company/")
        else:
            form = CompanyForm() # GET метод - создаём пустую форму
        companies = ProfileCompany.objects.select_related("company").filter(profile_id=profile.id)
        #print(connection.queries) #выводим sql запросы которые генерирует orm
        print(companies.query)
        
        data = {"name": user.username, "lastlogin": user.last_login, "email": user.email, "profile": profile, "companies": companies, 'form': form}
        return render(request,"main/companies.html", context=data)
    return  HttpResponse('unauthorized access!')


def deleteCompany(request):
    if request.user.is_authenticated and request.method == "POST":
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=request.user.id)
        company_id = int(request.POST['company_id'])
        company = Company.objects.get(id=company_id)
        if company.profile_id != profile.id:#удалять можно только свои компании
            return  HttpResponse('unauthorized access!')
        with connection.cursor() as cursor:
            res_a = cursor.execute(f'''Delete from main_apartment where id in (SELECT a.id as a_id FROM main_company as c inner join main_house h on h.company_id = c.id inner join main_apartment a on a.house_id=h.id where c.id={company_id})''')
            print(f"удалено {res_a.rowcount} строк из таблицы main_apartment")
            res_h = cursor.execute(f'''Delete from main_house where id in (SELECT h.id as h_id FROM main_company as c inner join main_house h on h.company_id = c.id where c.id={company_id})''')
            print(f"удалено {res_h.rowcount} строк из таблицы main_house")
            res_c = cursor.execute(f'''Delete from main_company where id in ({company_id})''')
            print(f"удалено {res_c.rowcount} строк из таблицы main_company")
        return redirect("/company/")
    return  HttpResponse('unauthorized access!')

def houses(request, company_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = companyDetailsForm(request.POST)
            if form.is_valid():
                house = House()
                house.address = form.cleaned_data['address']
                house.company_id = company_id
                house.save()
                return redirect(f"/company/{company_id}")
        else:
            form = companyDetailsForm()

        houses = House.objects.filter(company_id=company_id)
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=request.user.id)

        #=======statistics===========
        reactions_by_h = Apartment.objects.raw(''' select total.id, total.house_id, total.address, total.total_reaction, neutral.neutral_reaction, positive.positive_reaction, negative.negative_reaction  FROM
(SELECT a.id, h.address, count(*) as total_reaction, a.house_id from main_apartment a inner join main_house h on a.house_id = h.id where a.reaction is not null GROUP BY a.house_id) as total
left  join 
(SELECT count(*) as neutral_reaction, house_id from main_apartment GROUP BY house_id, reaction having reaction=0)
as neutral on total.house_id = neutral.house_id left join 
(SELECT count(*) as positive_reaction, house_id from main_apartment GROUP BY house_id, reaction having reaction=1)
as positive on total.house_id = positive.house_id left join
(SELECT count(*) as negative_reaction, house_id from main_apartment GROUP BY house_id, reaction having reaction=2)
as negative on total.house_id = negative.house_id ''')
        
        reactions_by_house = []
        total_reactions = 0
        neutral_reactions = 0
        positive_reactions = 0
        negative_reactions = 0
        for i in reactions_by_h:
            reactions_by_house.append(ReactionItemHtmlModel(i.house_id, i.address, i.total_reaction, i.neutral_reaction, i.positive_reaction, i.negative_reaction))
            total_reactions = total_reactions + i.total_reaction
            if i.neutral_reaction is not None:
                neutral_reactions = neutral_reactions + i.neutral_reaction
            if i.positive_reaction is not None:
                positive_reactions = positive_reactions + i.positive_reaction
            if i.negative_reaction is not None:
                negative_reactions = negative_reactions + i.negative_reaction
        total_reactions = ReactionItemHtmlModel(None, None, total_reactions, neutral_reactions, positive_reactions, negative_reactions)

        opened_by_h = Apartment.objects.raw(''' select total.id, total.address, total.total_doors, total.house_id, opened.opened_doors, closed.closed_doors from 
(SELECT a.id, h.address, count(*) as total_doors, a.house_id from main_apartment a inner join main_house h on a.house_id = h.id GROUP BY a.house_id) as total
left join  (SELECT count(*) as opened_doors, house_id from main_apartment GROUP BY house_id, open having open=1) as opened
on total.house_id=opened.house_id
left JOIN (SELECT count(*) as closed_doors, house_id from main_apartment GROUP BY house_id, open having open=0) as closed
on total.house_id=closed.house_id ''')

        opened_by_house = []
        total_doors = 0
        opened_doors = 0
        closed_doors = 0
        for i in opened_by_h:
            opened_by_house.append(OpenItemHtmlModel(i.house_id, i.address, i.total_doors, i.opened_doors, i.closed_doors))
            total_doors = total_doors + i.total_doors
            if i.opened_doors is not None:
                opened_doors = opened_doors + i.opened_doors
            if i.closed_doors is not None:
                closed_doors = closed_doors + i.closed_doors

        total_opened = OpenItemHtmlModel(None, None, total_doors, opened_doors, closed_doors)

        contacts = Apartment.objects.raw(f'''SELECT a.id, count(*) as contacts from main_apartment a inner join main_house h on a.house_id = h.id where h.company_id={company_id} and a.name is NOT NULL and a.name is not "" ''')
        total_apartments = Apartment.objects.raw('''SELECT a.id, count(*) as "total_apartments" from main_apartment a inner join main_house h on a.house_id = h.id where h.company_id=1 ''')
        
        companyUsers = ProfileCompany.objects.select_related("profile").filter(company_id=company_id)

        profiles = Profile.objects.all()


        existed_profile_ids = list(ProfileCompany.objects.filter(company_id=company_id).values_list("profile_id", flat=True))
        profiles_orm = Profile.objects.exclude(id__in=existed_profile_ids)


        contacts_h = f"{round(contacts[0].contacts * 100/total_apartments[0].total_apartments)}%"
        contacts_total = contacts[0].contacts
        #============================
        data = {"name": user.username, "lastlogin": user.last_login, "email": user.email, "profile": profile, "houses": houses, "company_id":company_id, "reactions_by_house": reactions_by_house, "total_reactions":total_reactions, "opened_by_house":opened_by_house, "total_opened":total_opened, "contacts":contacts, "contacts_h":contacts_h, "contacts_total":contacts_total,"companyUsers":companyUsers, "profiles": profiles_orm}
        return render(request,"main/houses.html", context=data)
    return  HttpResponse('unauthorized access!')

def addUserToCompany(request, company_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            #сохранение в базу
            profile_company = ProfileCompany()
            profile_company.company_id = int(company_id)
            profile_company.profile_id = int(request.POST['user_select'])
            profile_company.save()
            return redirect(f"/company/{company_id}")
    return  HttpResponse('unauthorized access!')


def deleteHouse(request,company_id):
    if request.user.is_authenticated and request.method == "POST":
        houses = House.objects.get(id=int(request.POST['house_id']))
        with connection.cursor() as cursor:
            res = cursor.execute("DELETE from main_apartment WHERE house_id = %s", [int(request.POST['house_id'])])
            print(res)
        houses.delete()
        return redirect(f"/company/{company_id}")
    return  HttpResponse('unauthorized access!')

class ReactionItemHtmlModel:
    def __init__(self, houseId, houseAddress, total, neutral, positive, negative):
        self.houseId = houseId
        self.houseAddress = houseAddress
        self.total = total
        if neutral is not None:
            self.neutral = str(neutral)
        else:
            self.neutral = "-"
        if neutral is not None and total != 0:
            self.neutralPercent = f"{round(neutral * 100/total)}%"
        else:
            self.neutralPercent = "-"
        if positive is not None:
            self.positive = str(positive)
        else:
            self.positive = "-"
        if positive is not None and total != 0:
            self.positivePercent = f"{round(positive * 100/total)}%"
        else:
            self.positivePercent = "-"
        if negative is not None:
            self.negative = str(negative)
        else:
            self.negative = "-"
        if negative is not None and total != 0:
            self.negativePercent = f"{round(negative * 100/total)}%"
        else:
            self.negativePercent = "-"


class OpenItemHtmlModel:
    def __init__(self,houseId, houseAddress, total,opened, closed):
        self.houseId = houseId
        self.houseAddress = houseAddress
        self.total = total
        if opened is not None:
            self.opened = str(opened)
            self.openedPercent = f"{round(opened * 100/total)}%"
        else:
            self.opened = "-"
            self.openedPercent = "-"
        if closed is not None:
            self.closed = str(closed)
            self.closedPercent = f"{round(closed * 100/total)}%"
        else:
            self.closed = "-"
            self.closedPercent = "-"

    

def apartments(request,house_id,company_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = houseDetailsForm(request.POST)
            if form.is_valid():
                apartment = Apartment()
                apartment.number = form.cleaned_data['number']
                apartment.house_id = house_id
                apartment.open = form.cleaned_data['open']
                
                apartment.date_time = timezone.now()
                apartment.reaction = form.cleaned_data['reaction']
                apartment.name = form.cleaned_data['name']
                apartment.phone = form.cleaned_data['phone']
                apartment.comment = form.cleaned_data['comment']
                apartment.save()
                return redirect(f"/company/{company_id}/{house_id}")
        else:
            form = houseDetailsForm()

        apartments = Apartment.objects.filter(house_id=house_id)
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user_id=request.user.id)
        data = {"name": user.username, "lastlogin": user.last_login, "email": user.email, "profile": profile, "apartments": apartments, "house_id":house_id, "form": form, "company_id":company_id}
        return render(request,"main/apartments.html", context=data)
    return  HttpResponse('unauthorized access!')

    
def deleteApartment(request,house_id,company_id):
    if request.user.is_authenticated and request.method == "POST":
        apartment = Apartment.objects.get(id=int(request.POST['apartment_id']))
        apartment.delete()
        return redirect(f"/company/{company_id}/{house_id}")
    return  HttpResponse('unauthorized access!')
