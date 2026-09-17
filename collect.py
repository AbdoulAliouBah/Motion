import requests
import json
import sqlite3
import time 

url = "https://remoteok.com/api"
response = requests.get(url, timeout=10)

data_remoteok = response.json()

#print(data_remoteok[2])

#print (type(data))
#print (data[1])

url = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"

response = requests.get(url,timeout=10)
data_greenhouse = response.json()
data_greenhouse = data_greenhouse["jobs"]

#print (data["jobs"][1])

def normalize_remoteok(job): 
    

    normalized = {
            "title" : job.get("position"),
            "company": job.get("company"),
            "location": job.get("location"),
            "url":job.get("url"),
            "source": "remoteok",
            "description": job.get("description")
        }
  
    return normalized



#remotejob = data_remoteok[1]
#print(normalize_remoteok(job))

def fetch_greenhouse_description(job_id):
    print(f"Fetching description for job {job_id}")
    url = f"https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/{job_id}"
    try: 
         response = requests.get(url, timeout=10)
         data = response.json()
         return data.get("content")
    except: 
        print('this request timedout')
        return None 
    
   
    

def normalize_greenhouse(job): 
    
    normalized= { 
        "title": job.get("title"),
        "company": job.get("company_name"),
        "location" :job.get("location",{}).get("name"),
        "url":job.get("absolute_url"),
        "source" : "greenhouse", 
        "description" : fetch_greenhouse_description(job.get("id"))
    }

    return normalized

"""def remoteok_list(job): 
 for job in range (len(data_remoteok)): 
    normalize_remoteok(job)
 return remoteok_list.append(normalize_remoteok(job))"""

def remoteok_list(): 
   result = []

   for job in data_remoteok[1:]: 
       
       normalized =normalize_remoteok(job)
       result.append(normalized )
   return result 
remoteok_jobs = remoteok_list()

def greenhouse_list (): 
    result = []

    for job in (data_greenhouse):
        normalized = normalize_greenhouse(job)
        result.append(normalized)
        time.sleep(1)
    return result 
greenhouse_jobs = greenhouse_list()

#print (len(greenhouse_jobs))
#print(data_greenhouse[0])
#remoteok_jobs= remoteok_list()
#print(len(remoteok_jobs))
#job=(data["jobs"][1])
#print(normalize_greenhouse(job))

all_jobs = []

all_jobs.extend(remoteok_jobs)
all_jobs.extend(greenhouse_jobs)
print(len(remoteok_jobs))
print(len(greenhouse_jobs))
print(len(all_jobs))

with open("jobs.json", "w") as f:
    json.dump(all_jobs, f)
    
print(f"Fetched {len(all_jobs)} jobs")
print(f"remoteOK: {len(remoteok_jobs)},Grenhouse: {len(greenhouse_jobs)}")
print (f"Saved to jobs.json")

"""for job in all_jobs[:3]: 
    print (job.get("title"))
    print(job.get("company"))
    print(job.get("location"))
    print(job.get("url"))
    print(job.get("source"))"""

for i , job in enumerate (all_jobs[:10], start=1): 
    print(f"{i}. {job.get('title')} , {job.get('company')} , {job.get('location')},{job.get('source')},{job.get('url')},{job.get('description')}")

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS ALLJOBS ( 
                   URL PRIMARY KEY, 
                   TITLE TEXT, 
                   COMPANY TEXT , 
                   LOCATION TEXT,
                   SOURCE TEXT,
                   DESCRIPTION TEXT

               )""")
tuple((job['url'], job['title'],job['company'],job['location'],job['source']))

jobs_to_insert = []
for job in all_jobs: 
    jobs_to_insert.append((job['url'], job['title'],job['company'],job['location'],job['source'],job['description']))
cursor.executemany("INSERT OR IGNORE INTO ALLJOBS VALUES (?, ?, ?, ?, ?, ?)", jobs_to_insert)
conn.commit()
cursor.execute("SELECT COUNT(*) FROM ALLJOBS")
print(cursor.fetchone())






