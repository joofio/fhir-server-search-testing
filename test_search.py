import pytest
import requests
from datetime import datetime
import json


BASE_URL = 'http://test.fhir.org/r4'
#BASE_URL="http://hapi.fhir.org/baseR4"


@pytest.fixture(scope="session", autouse=True)
def pytest_configure():
     # make conditional update for this
     f = open('test_objects.json')
 
     # returns JSON object as
     # a dictionary
     test_objects = json.load(f)
     headers = {
     'Content-Type': 'application/json'
     }
     # Iterating through the json
     # list
     res_ids=[]
     for i in test_objects:
          res=i["resourceType"]
      #    print(res)
          if res!="Patient":
               i["subject"]["reference"]="Patient/"+res_ids[0]
          r = requests.post(BASE_URL+"/"+res+"?_format=json", json=i,headers=headers)
       #   print(r.json())
          res_ids.append(r.json()["id"])
   #  print(res_ids)
     return res_ids

def test_server_alive():
     """test if server is alive"""
     response = requests.get(BASE_URL+"/metadata")
     assert response.status_code == 200

def test_search_patient():
     """search all patients"""
     response = requests.get(BASE_URL+"/Patient?_format=json")
     total=response.json()["total"]
     assert total== 671

def test_search_observation():
     """search all observations"""
     response = requests.get(BASE_URL+"/Observation?_format=json")
     total=response.json()["total"]
     assert total== 93

def test_search_sort_dates_ascending():
     """test if sort is ok, by sorting observation by effectiveDateTime"""
     dates=[]
     response = requests.get(BASE_URL+"/Observation?_format=json&_sort=date")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry["resource"])
          effectiveDateTime=entry["resource"].get("effectiveDateTime")
          rid=entry["resource"].get("id")
          dates.append(datetime.fromisoformat(effectiveDateTime))
          assert effectiveDateTime is not None      

     ddates=dates.copy()

     assert dates== sorted(ddates)

def test_search_sort_dates_descending():
     """test if sort is ok, by sorting observation by effectiveDateTime"""
     dates=[]
     response = requests.get(BASE_URL+"/Observation?_format=json&_sort=-date")
     assert  response.status_code== 200
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry["resource"])
          effectiveDateTime=entry["resource"].get("effectiveDateTime")
          rid=entry["resource"].get("id")
          dates.append(datetime.fromisoformat(effectiveDateTime))
          assert effectiveDateTime is not None  
     ddates=dates.copy()

     assert dates == sorted(ddates,reverse=True)

def test_search_reference():
     """test if search by reference is ok by searching Observation that mentions a patient"""
     subjects=[]
     response = requests.get(BASE_URL+"/Observation?subject=Patient/2081525&_format=json")
     print(response.json())
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry["resource"])
          subject=entry["resource"].get("subject")
          subjects.append(subject)
     assert len(subjects)== 5

def test_search_patient_by_id():
     """search patient by id"""
     response = requests.get(BASE_URL+"/Patient?_id=1545788&_format=json")
     total=response.json()["total"]
     #print(pat)
     assert total==1

def test_read_patient():
     """read patient by id"""
     ID="015140df-6732-4c39-9735-8d3e650faabc"
     response = requests.get(BASE_URL+"/Patient/"+ID+"?_format=json")
     _id=response.json()["id"]
     assert _id==ID


def test_post_search_id():
     """post a search for patient by id"""
     ID="015140df-6732-4c39-9735-8d3e650faabc"

     payload='_id='+ID+'&_format=json'
     headers = {
     'Content-Type': 'application/x-www-form-urlencoded'
     }
     response = requests.post(BASE_URL+"/Patient/_search",headers=headers, data=payload)
    # print(response.json())
     entries=response.json()["entry"]
     for entry in entries:
         # print(entry)
          _id=entry["resource"]["id"]
     assert _id==ID

def test_post_search_by_reference():
     """post a search for Observation with a patient reference"""
     subject="015140df-6732-4c39-9735-8d3e650faabc"

     payload='subject=Patient/'+subject+'&_format=json'
     headers = {
     'Content-Type': 'application/x-www-form-urlencoded'
     }
     response = requests.post(BASE_URL+"/Observation/_search",headers=headers, data=payload)
     #print(response.json())
     entries=response.json()["entry"]
     for entry in entries:
         # print(entry)
          out_subject=entry["resource"]["subject"]
     assert out_subject["reference"]=="Patient/"+subject


def test_post_search_by_name():
     """post a search by name for patient"""
     name="Practice"
     found=False
     payload='name='+name+'&_format=json'
     headers = {
     'Content-Type': 'application/x-www-form-urlencoded'
     }
     response = requests.post(BASE_URL+"/Patient/_search",headers=headers, data=payload)
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry)
          out_patient=entry["resource"]["name"]
          for names in out_patient:
               if names["family"]==name:
                    found=True
               for g in names.get("given",[]):
                    if g==name:
                         found=True
     assert found==True


def test_search_patient_name():
     """search patient by name"""
     name="Practice"
     found=False

     response = requests.get(BASE_URL+"/Patient?name="+name+"&_format=json")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry)
          out_patient=entry["resource"]["name"]
          for names in out_patient:
               if names["family"]==name:
                    found=True
               for g in names.get("given",[]):
                    if g==name:
                         found=True
     assert found==True


def test_search_by_gender():
     """search by gender"""
     gender="male"
     out_genders=[]
     response = requests.get(BASE_URL+"/Patient?gender="+gender+"&_format=json")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry)
          out_genders.append(entry["resource"]["gender"])
          
     assert all([v==gender for v in out_genders])

def test_search_by_not_gender():
     """search by not gender"""
     gender="male"
     out_genders=[]
     response = requests.get(BASE_URL+"/Patient?gender:not="+gender+"&_format=json")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry)
          out_genders.append(entry["resource"]["gender"])
          
     assert all([v!=gender for v in out_genders])

def test_search_by_date_lt():
     """test if search by date, lower  than"""
     dates=[]
     target_date="1991-05-07"
     date_time_target_date = datetime. strptime(target_date, '%Y-%m-%d')
     response = requests.get(BASE_URL+"/Patient?birthdate=lt"+target_date+"&_format=json")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry["resource"])
          birthdate=entry["resource"].get("birthDate")
          dates.append(datetime.fromisoformat(birthdate))
          assert birthdate is not None      


     assert all([d<date_time_target_date for d in dates])
### search operators: search patients above 65



def test_search_by_date_gt():
     """test if search by date, greater than"""
     dates=[]
     target_date="1991-05-07"
     date_time_target_date = datetime. strptime(target_date, '%Y-%m-%d')
     response = requests.get(BASE_URL+"/Patient?birthdate=gt"+target_date+"&_format=json")
     entries=response.json()["entry"]
     for entry in entries:
          #print(entry["resource"])
          birthdate=entry["resource"].get("birthDate")
          assert birthdate is not None      
          if len(birthdate)>12:
               dates.append(datetime.fromisoformat(birthdate))
          if len(birthdate)==7:
               dates.append(datetime.strptime(birthdate,'%Y-%m'))

     assert all([d>date_time_target_date for d in dates])


def test_chaining(pytest_configure):
     res_id=pytest_configure[0]
     """test chaining with searching a report with a certain name"""
     name="Maria"
     response = requests.get(BASE_URL+"/DiagnosticReport?subject:Patient.name="+name+"&_format=json")
     entries=response.json()["entry"]
     respose_ids=[]
     for entry in entries:
          respose_ids.append(entry["resource"].get("subject").get("reference"))
        #  print(res_id)
         # print(entr)
     print([ids.split("/")[-1] for ids in respose_ids])
     assert all([ids.split("/")[-1]==res_id for ids in respose_ids])



def test_search_marital_status():
     """ if this search returns something, the search is wrong"""
     response = requests.get(BASE_URL+"/Patient?_maritalStatus=M&_format=json")
     print(response.json())
     assert response.status_code==300

def test_text_search():
     """ text search by searching glucose on a observation
      Its about specific text search
     """
     response = requests.get(BASE_URL+"/Observation?_text=Glucose&_format=json")
     print(response.json())
     assert response.status_code==200


def test_reverse_chaining():
     #is this ok?
     """ reverse chaining testing"""
     response = requests.get(BASE_URL+"/Patient?_has:MedicationRequest:subject:intent=order&_format=json")
     print(response.json())
     assert response.status_code==300



def test_text_contains():
     """ text contains"""
     target_name="Search"
     response = requests.get(BASE_URL+"/Patient?given:contains="+target_name+"&_format=json")
     entries=response.json()["entry"]
     name_l=[]
     for entry in entries:
          #print(entry)
          names=entry["resource"].get("name")
          for name in names:
               name_l.extend(name["given"])
               #print(name)
          print(name_l)
          assert any([target_name in n  for n in name_l])==True 


def test_text_exact():
     """ text exact"""
     target_name="Test Search"
     response = requests.get(BASE_URL+"/Patient?given:exact="+target_name+"&_format=json")
     entries=response.json()["entry"]
     name_l=[]
     for entry in entries:
          #print(entry)
          names=entry["resource"].get("name")
          for name in names:
               name_l.extend(name["given"])
               #print(name)
          print(name_l)
          assert any([target_name==n  for n in name_l])==True 


def test_include():
     response = requests.get(BASE_URL+"/MedicationRequest?_include=MedicationRequest:patient&_format=json")
     entries=response.json()["entry"]
     patient_list=[]
     for entry in entries:
         # print(entry)
          res=entry["resource"].get("resourceType")
          patient=entry["resource"].get("subject",{}).get("reference")
          res_id=entry["resource"].get("id")
          if patient:
               patient_list.append(patient.split("/")[-1])
          print(patient,res)
          print(res_id,patient_list)
          if res=="Patient":
               assert res_id in patient_list


def test_revinclude(pytest_configure):
     res_id=pytest_configure[0]
     response = requests.get(BASE_URL+"/Patient?_id="+res_id+"&_revinclude=Observation:subject&_format=json")
     entries=response.json()["entry"]
     patient_list=[]
     for entry in entries:
         # print(entry)
          res=entry["resource"].get("resourceType")
          if res!="Patient":
               patient=entry["resource"].get("subject",{}).get("reference").split("/")[-1]
               assert patient==res_id


def test_revinclude2(pytest_configure):
     #is this ok??
     res_id=pytest_configure[0]
     response = requests.get(BASE_URL+"/Patient?_revinclude=Observation:subject&_format=json")
     entries=response.json()["entry"]
     patient_list=[]
     patient_refs=[]
     for entry in entries:
         # print(entry)
          res=entry["resource"].get("resourceType")
          if res=="Patient":
               patient_list.append(entry["resource"].get("id",{}))
          if res!="Patient":
               patient_refs.append(entry["resource"].get("subject",{}).get("reference").split("/")[-1])
     print(set(sorted(patient_list)),set(sorted(patient_refs)))
     assert set(sorted(patient_list))==set(sorted(patient_refs))

