#import libraries

import tweepy
import json
import sys
import jsonpickle
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from nltk.tokenize import WordPunctTokenizer
import seaborn as sns 


# Set plotting parameters
get_ipython().magic(u'matplotlib inline')
params = {'legend.fontsize': 'x-large',
         'figure.figsize': (9,6),
         'axes.labelsize': 'large',
         'axes.titlesize': 'x-large',
          }
plt.rcParams.update(params)


# Step I: Extract Tweets from Twitter API


# twitter API key
consumer_key="**************"
consumer_secret="********************"
access_token="***********************"
access_token_secret="***********************"

auth=tweepy.OAuthHandler(consumer_key,consumer_secret)

auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit =True,
                wait_on_rate_limit_notify =True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)


# Create a dictionary to hold the extracted data
dict_tweet = {'user': [], 'text': [],
             'retweet_count':[],
             'bio':[],'id':[]}

# Set the twitter extraction query parameters
searchQuery = '"Artificial%20Intelligence"%20OR%20AI&lang=en'
maxTweets = 70000
tweetsPerQry = 100
fName = 'tweets_aiAI_uncleaned.txt'
sinceId = None #no lower limit, go as far back as API allows
max_id = -1L #no lower limit, go as far back as API allows

#Initiate the count
tweetCount = 0


# search for tweets
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang='en') # added lang to next several lines, ESC
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang='en',
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang='en',
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang='en',
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            for tweet in new_tweets:
                dict_tweet['user'].append(tweet.user.screen_name)
                dict_tweet['text'].append(tweet.text)
                dict_tweet['retweet_count'].append(tweet.retweet_count)
                dict_tweet['bio'].append(tweet.user.description)
                dict_tweet['id'].append(tweet.user.id_str)
             
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                f.write(jsonpickle.encode(tweet._json, unpicklable =False)+ 
                       '\n')
            tweetCount += len(new_tweets)
            print("Download {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
            
        except tweepy.TweepError as e:
          
            print("some error:" + str(e))
            break
print("Download {0} tweets, saved to {1}". format(tweetCount, fName))

#Convert dictionary to data frame
tweet_df = pd.DataFrame(dict_tweet)
tweet_df.head(5)


# Preprocess data
tok = WordPunctTokenizer()
part1 = r'@[A-Za-z0-9]+' 
part2 = r'https?://[A-Za-z0-9./]+' 
combined_pat = r'|'.join((part1,part2))

min_df = pd.DataFrame(tweet_df,columns=['bio','id'])
min_df['id'].min()

def tweet_cleaner(text):
    soup = BeautifulSoup(text, 'lxml')
    souped = soup.get_text()
    stripped = re.sub(combined_pat, '', souped)
    try:
        clean = stripped.decode("utf-8-sig").replace(u"\ufffd", "?")
    except:
        clean = stripped
    letters_only = re.sub("[^a-zA-Z]", " ", clean)
    lower_case = letters_only.lower()
   
    words = tok.tokenize(lower_case)
    return (" ".join(words)).strip()

all_tweets = tweet_df.text
text_cleaned = []
for t in all_tweets:
    text_cleaned.append(tweet_cleaner(t))
    
len(text_cleaned)
text_clean = pd.Series(text_cleaned)
tweet_df['text_clean'] = text_clean.values

tweet_df['text_clean'] = tweet_df['text_clean'].str.replace('rt', '')

#Save cleaned tweets to csv
tweet_df.to_csv('aiAI_first_cleaned.csv', sep=',', encoding='utf-8')


# keywords that computer professionals' ['bio'] contains
condStr = """information security analyst|IT manager|computer system analyst
|computer network architect|security engineer|technical solutions consultant|technical program manager
|technical solutions engineer|test engineer|android engineer|computer engineering|software test engineer
|java developer|computer vision scientist|computer architechture|cloud engineer|full stack engineer
|Python|python cloud engineer||linux|Linux|python software engineer|image acquisition|bioinformatics
|scala|java|Java|voice assistant|application developer|systems architect|PHP|Go|games system engineer
|backend engineer|bot|Chatbot|Blockchain|robotics|automation|driverless car|CyberSecurity|DigitalTransformation
|cs|VR|AR|geek|virtual realitysoftware|Software|software developer|Software Developer|AI|ai|artificial intelligence
|programmer|Programmer|data science|Data Science|data mining|DataScience|data scientist|data engineer|big data
|machine learning|ml|ML|Machine Learning|NLP|nlp|natural language processing|Natural Language Processing|deep learning
|Deep Learning|web designer|Web Designer
"""

#kw = ['a','b','c','d']
#'|'.join(kw)

tweet_df['engi_occu'] = tweet_df['bio'].str.contains(condStr)

# keywords that laypeople's ['bio'] contains
conStrLay = """lawyer|teacher|student|singer|politician|product manager|gardener
|shop|chef|dentist|physician|nurse|statistician|orthodontist|therapist|surgeon|psychiatrist|marketing manager|actuary|mathematician|HR
|business operations manager|mechanical engineer|accountant|financial advisor|civil engineer|financial manager|massage therapist|pharmacist
|plumber|cost estimator|retail marketing|program manager|consultant|manufacturing business manager|account strategist|industry manager
|analytical consultant|visual designer|painter|actor|actress|animation lead|interaction designer|customer support specialist|marketing operations manager
|brand designer|journalist|tradesperson|retail salesperson|cashier|office clerk|waiter|customer service representative|mover|secretary
|administrative assistant|stock clerk|truck driver|manufacturing sales representative|auditor|security guard|business operation specialist
|cook|maid|food preparation worker|construction laborer|supervisor|packer|packager|sheriff|carpenter|childcare worker|technician|mechanic teller
|medical assistant|electrician|dishwasher|bartender|bus driver|pipefitter|machinist|hairdresser|hairstylist|cosmetologist|pharmacy|sales|solder
|firefighter|artist|reporter|biomedical engineer|medical|attorney|musician|director|photographer|farm owner|farmer|tailor|gold smith|jeweller
|pianist|singer|violinist|librarian|freelancer|writer|host|charity|paster|minister|priest|preacher|novelist|poet|media operator|product manager
|Author|broadcaster|humanist|Able Seamen|Account Collector|Accounting Specialist|Adjustment Clerk|Administrative Assistant|Administrative Law Judge
|Administrative Service Manager|Admiralty Lawyer|Adult Literacy |Remedial Education Teachers|Advertising Account Executive|Advertising Agency Coordinator
|Aeronautical|Aerospace Engineer|Aerospace Engineering Technician|Agricultural Crop Farm Manager|Agricultural Engineer|Agricultural Equipment Operator
|Agricultural Inspector|Agricultural Product Sorter|Agricultural Sciences Professor|Agricultural Technician|Air Crew Member|Air Crew Officer|Air Traffic Controller
|Aircraft Assembler|Aircraft Body |Bonded Structure Repairer|Aircraft Cargo Handling Supervisor|Aircraft Examiner|Aircraft Launch|Recovery Officer
|Aircraft Launch|Recovery Specialist|Aircraft Mechanic|Airfield Operations Specialist|Airline Flight Attendant|Airline Flight Control Administrator
|Airline Flight Operations Administrator|Airline Flight Reservations Administrator|Airport Administrator|Airport Design Engineer|Alcohol Abuse Assistance Coordinator
|Drug Abuse Assistance Coordinator|Alumni Relations Coordinator|Ambulance Drivers|Amusement Park  Recreation Attendants|Anesthesiologist|Animal Breeder|Animal Control Worker
|Animal Husbandry Worker Supervisor|Animal Keepers |Groomers|Animal Kennel Supervisor|Animal Scientist|Animal Trainer|Animation Cartoonist
|Answering Service Operator|Anthropology |Archeology Professor|Anti Terrorism Intelligence Agent|Appeals Referee|Aquaculturist|Fish Farmer|Aquarium Curator|Architecture Professor
|Area Ethnic|Cultural Studies Professor|Armored Assault Vehicle Crew Member|Armored Assault Vehicle Officer|Art Appraiser|Art Director|Art Restorer|Art Therapist|Art  Drama  
|Music Professor|Artillery |Missile Crew Member|Artillery |Missile Officer|Artists Agent|Athletes' Business Manager|Athletic Coach
|Athletic Director|Athletic Trainer|ATM Machine Servicer|Atmospheric |Space Scientist|Audio Visual Collections Specialist|Audiovisual Production Specialist|Automobile Mechanic
|Automotive Body Repairer|Automotive Engineer|Automotive Glass Installer|Avionics Technician|Baggage Porters |Bellhops|Baker|Ballistics Expert|Bank |Branch Managers|Bank Examiner
|Bank Teller|Benefits Manager|Bicycle Mechanic|Billing Specialist|Bindery Machine Set Up Operators|Bindery Machine Tender|Biological Technician|Biology Professor|Biomedical Engineer
|Biomedical Equipment Technician|Boat Builder|Book Editor|Border Patrol Agent|Brattice Builder|Bridge |Lock Tenders|Broadcast News Analyst|Broadcast Technician|Broker's Floor Representative
|Brokerage Clerk|Budget Accountant|Budget Analyst|Building Inspector|Building Maintenance Mechanic|Grader Operator|Bus |Truck Mechanics|Bus Boy|Bus Girl|Bus Driver School|Bus Driver Transit
|Business Professor|Business Service Specialist|Cabinet Maker|Camp Director|Caption Writer|Cardiologist|Cardiopulmonary Technologist|Career Counselor|Cargo |Freight Agents|Carpenter's Assistant
|Carpet Installer|Cartographer|Cartographic Technician|Cartoonist|Casino Cage Worker|Casino Cashier|Casino Dealer|Casino Floor Person|Casino Manager|Casino Pit Boss|Casino Slot Machine Mechanic
|Casino Surveillance Officer|Casting Director|Catering Administrator|Ceiling Tile Installer|Cement Mason|Ceramic Engineer|Certified Public Accountant|Chaplain|Chemical Engineer|Chemical Equipment Operator
|Chemical Plant Operator|Chemical Technicians|Chemistry Professor|Chief Financial Officer|Child Care Center Administrator|Child Care Worker|Child Life Specialist|Child Support Investigator|Child Support Services Worker
|City Planning Aide|Civil Drafter|Civil Engineer|Civil Engineering Technician|Clergy Member|Religious Leader|Clinical Dietitian|Clinical Psychologist|Clinical Sociologist|Coatroom |Dressing Room Attendants
|College|University Professor|Commercial Designer|Commercial Diver|Commercial Fisherman|Communication Equipment Mechanic|Communications Professor|Community Health Nurse|Community Organization Worker
|Community Welfare Worker |Compensation Administrator|Compensation Specialist|Compliance Officer|Congressional Aide
|Conservation Scientist|Construction Driller|Construction Laborer|Construction Manager|Construction Trades Supervisor
|Contract Administrator|Contract Specialist|Control Center Specialist|Controller|Cook|Cook Fast Food|Cook Private Household
|Cook Restaurant|Cook Short Order|Copy Writer|Corporation Lawyer|Correction Officer|Correspondence Clerk|Cosmetologist
|Cost Accountant|Cost Analysis Engineer|Cost Estimator|Costume Attendant|Counseling Psychologist|Counter |Rental Clerks
|County or City Auditor|Couriers |Messengers|Court Administrator|Court Clerk|Court Reporter|Craft Artist|Crane Operator
|Credit Adjuster|Credit Analyst|Credit Reporter|Criminal Investigator|Detective|Criminal Justice Professor|Criminal Lawyer
|Crop Workers Supervisor|Crossing Guard|Custom Tailor|Customer Service Representative|Customer Service Supervisor
|Customs Inspector|Cutting Machine Operators|Dairy Technologist|Database Administrator|Deaf Students Teacher|Delivery Driver
|Demonstrators |Product Promoters|Orthodontic Office Administrator|Dental Assistant|Dental Hygienist
|Dental Laboratory Technician|Dentist|Dermatologist|Desktop Publishing Specialist|Developmental Psychologist
|Die Cutter Operator|Dietetic Technician|Dietitian |Nutritionist|Directory Assistance Operator|Disabled Students Teacher
|Disk Jockey|Dispatcher|Door To Door Salesmen|Dry Wall Installer|Economics Professor|Editorial Writer  Newspapers  Magazines
|Education |Training Administrator|Education Professor|Educational Administrator|Educational Psychologist
|Educational Resource Coordinator|Educational Therapist|EEG Technician|Technologist|Electric Meter Installer
|Electric Motor Mechanic|Electrical |Electronic Inspector|Electrical Drafter|Electrical Engineers
|Electrical Parts Reconditioner|Electrical Technician|Electro Mechanical Technicians|Electromechanical Equipment Assembler
|Electronic Drafter|Electronics Engineer|Electronics Technician|Elementary School Administrator|Elementary School Teacher
|Elevator Mechanic|Emergency Management Specialist|Emergency Medical Technician|Employee Benefits Analyst
|Employee Training Instructor|Employment Administrator|Employment |Placement Specialist|Employment Interviewer|Engine
|Machine Assemblers|Engineering Managers|Engineering Professor|English Language |Literature Professor
|Environmental Compliance Inspector|Environmental Disease Analyst|Environmental Engineer|Environmental Planner
|Environmental Research Analyst|Environmental Science Technician|Environmental Science Professor|Environmental Technician
|Equal Opportunity Representative|Etchers |Engravers|Excavating Machine Operator|Excavating Supervisor|Executive Secretary
|Exercise Physiologist|Exhibit Artist|Exhibit Designer|Experimental Psychologist|Explosives Worker|Export Agent|Fabric
|Apparel Patternmakers|Facilities Planner|Factory Layout Engineer|Family Caseworker|Family Pract|Farm Equipment Mechanic
|Farm Hand|Farm Labor Contractor|Farm Manager|Farm Products Purchasing Agent|Fashion Artist|Fashion Coordinator
|Fashion Designer|Fashion Model|Fence Installer|Field Contractor|Field Health Officer|File Clerk|Film Editor
|Film Laboratory Technician|Finance Manager|Financial Aid Counselor|Financial Analyst|Financial Examiner|Financial Planner
|Financial Services Sales Agent|Fine Artist|Fire Inspector|Fire Investigator|Fire Prevention Engineer
|Fire Protection Engineer|Fire Protection Engineering Technician|Fish Game Warden|Fish Hatchery Specialist
|Fishery Worker Supervisor|Fitness Trainer|Flight Engineers|Floral Designer|Food Drug Inspector|Food Batchmaker
|Food Preparation Worker|Food Science Technicians|Food Technologist|Foreign Exchange Trader|Foreign Language Interpreter
|Foreign Language Teacher|Foreign Language Translator|Foreign Service Officer|Foreign Service Peacekeeping Specialist
|Foreign Student Adviser|Forensic Science Technicians|Forensics Psychologist|Forest |Conservation Technician|Forest Engineer
|Forest Fire Prevention Supervisor|Forest Fire Inspector|Forestry |Conservation Professor|Forging Machine Operator|Forklift
|Industrial Truck Operators|Fraud Investigator|Freight |Stock Handler|Fund Raiser|Funds Development Administrator
|Funeral Attendant|Funeral Director|Furniture Designer|Furniture Finishers|Gas Plant Operator|General |Operations Managers
|General Farmworkers|General Internists|Geography Professor|Geological Data Technicians|Geological Technician|Glass Blower
|Gluing Machine Operators|Golf Course Superintendent|Government Budget Analyst|Government Property Inspectors
|Government Service Executives|Graduate Teaching Assistant|Graphic Designer|Greenhouse |Nursery Manager|Gynecologist
|Portable Tool Mechanic|H|Sewer|Harbor Master|Harbor  Lake  Waterways Police|Hardwood Floor Finisher
|Hazardous Materials Removal Worker|Hazardous Waste Management Analyst|Health Care Facilities Inspector|Health Case Manager
|Health Educators|Health Psychologist|Hearing Officer|Heating|Refrigeration Technician|Heavy Equipment Mechanic
|High School Administrator|High School Guidance Counselor|High School Teacher|Highway Maintenance Worker|Highway Patrol Pilot
|Historic Site Administrator|Historical Archivist|History Professor|Home Appliance Installer|Home Appliance Repairer
|Home Economics Teacher|Home Economist|Home Entertainment System Installer|Home Health Aide|Home Health Technician
|Horticultural Worker Supervisor|Horticulture Therapist|Horticulturist|Hospital Administrator|Hospital Nurse|Hosts
|Hostesses|Hotel Convention|Events Coordinator|Hotel Manager|Housekeeping Supervisors|Human Factors Psychologist
|Human Resources Management Advisor|Human Resources Management Consultant|Hydraulic Engineer|Immigration Inspector
|Industrial Air Pollution Analyst|Industrial Arts Teacher|Industrial Designer|Industrial Engineer
|Industrial Engineering Technician|Industrial Health Engineer|Industrial Hygienist|Industrial Machinery Mechanics
|Industrial Relations Analyst|Industrial Relations Specialist|Industrial Therapist|Industrial Waste Inspector
|Industrial Organizational Psychologist|Infantry Officers|Instructional Coordinators|Instructor Police Canine Services
|Instrument Technician|Insulation Installer|Insurance Adjuster|Insurance Agent|Insurance Appraiser|Insurance Claim Examiner
|Insurance Claims Adjuster|Insurance Claims Clerks|Insurance Estate Planner|Insurance Lawyer
|Insurance Policy Processing Clerk|Insurance Underwriter|Intelligence Specialist Government|Interior Designer
|Internal Auditor|Interpreter for the Hearing Impaired|Irradiated Fuel Handlers|Irrigation Engineer|Janitorial Supervisors
|Job Analyst|Job Development Specialist|Job Printer|Kindergarten Teacher|Labor Relations Advisor|Laboratory Tester
|Surveyor|Landscape Architect|Landscape Contractor|Lathe Operator|Law Clerks|Law Professor|Legal Assistant|Legal Secretary
|Legislative Assistant|Library Assistant|Library Consultant|Library Science Professor|Library Technician|License Clerk
|Licensed Practical Nurse|Livestock Commission Agent|Loan Counselor|Loan Interviewers |Clerks|Loan Officer
|Locomotive Engineers|Log Graders|Scalers|Logging Tractor Operator|Logging Worker Supervisor|Machine Feeders
|Offbearers|Mail Clerk|Mail Machine Operators|Maintenance Supervisor|Makeup Artists|Theatrical|Management Consultant Analyst
|Manicurists |Pedicurists|Manual Arts Therapist|Mapping Technician|Marina Boat Charter Administrator|Marine
|Aquatic Biologist|Marine Architect|Marine Cargo Surveyor|Marine Drafter|Marine Engineer|Marine Surveyor
|Marine Engineer|Port Engineer|Market Research Analyst|Marketing Managers|Marking Clerk|Marriage|Family Therapists
|Massage Therapist|Materials Engineer|Materials Inspector|Materials Scientist|Math Professor|Mathematical Technician
|Meat Packers|Meat  Poultry  |Fish Trimmers|Mechanical Drafter|Mechanical Engineer|Mechanical Engineering Technician
|Mechanical Inspector|Medical Administrative Assistant|Medical |Public Health Social Workers|Medical |Scientific Illustrator
|Medical Appliance Technician|Medical Assistant|Medical Equipment Preparer|Medical Examiner|Coroner
|Medical Insurance Claims Analyst|Medical Laboratory Technician|Medical Photographer|Medical Records Administrator
|Medical Records Technician|Medical Secretary|Medical Technologist|Medical Transcriptionist|Mental Health Counselor
|Mentally Retarded Students Teacher|Merchandise Displayer|Metal Casting Machine Operator|Metal Fabricator
|Meter Mechanic|Middle School Administrator|Middle School Guidance Counselor|Middle School Teacher|Military Analyst
|Military Officer|Military Enlisted Personnel|Mill Worker|Mine Cutting Machine Operator|Mine Inspector|Mining Engineer
|Mining Machine Operator|Mining Shovel Machine Operator|Missing Person Investigator|Missionary Worker|Model Maker
|Model Makers  Metal |Plastic|Motion Picture Director|Motion Picture Projectionist|Motor Vehicle Inspector
|Motorboat Mechanic|Motorcycle Mechanic|Municipal Fire Fighting Supervisor|Museum Curator|Museum Technicians
|Conservators|Music Arrangers |Orchestrators|Music Director|Music Teacher|Music Therapist|Musical Instrument Tuner
|Narcotics Investigator|New Accounts Clerk|Newspaper Editor|Newspaper Writer|Non Retail Sales Supervisor|Nuclear Engineer
|Nuclear Equipment Operation Technician|Nuclear Fuels Research Engineer|Nuclear Medicine Technologist
|Nuclear Monitoring Technician|Nuclear Power Reactor Operator|Nuclear Technicians|Numerical Tool Programmer
|Nurse Practitioner|Nurse's Aide|Nursery Workers|Nursing Professor|Obstetrician|Occupational Analyst|Occupational Physician
|Occupational Safety  Health Inspector|Occupational Therapist|Occupational Therapy Assistant|Oceanographic Assistant
|Office Clerk|Office Machine Mechanic|Office Supervisor|Offset Press Operators|Operating Engineers
|Operations Management Analyst|Ophthalmic Laboratory Technician|Ophthalmologist|Oral |Maxillofacial Surgeons|Order Clerk
|Order Fillers  Wholesale |Retail Sales|Ordinary Seamen|Ornamental Metalwork Designer|Orthodontic Assistant
|Orthodontic Laboratory Technician|Orthodontist|Outdoor Education Teacher|Overhead Door Installer|Package Designer
|Packaging Machine Operator|Packers |Packagers  Hand|Painter|Painters  Construction |Maintenance
|Painters Transportation Equipment|Park Naturalist|Parking Enforcement Officer|Parking Lot Attendant
|Parole Officer|Parts Salesperson|Paste Up Worker|Patent Agent|Patent Lawyer|Pathologist|Payroll |Timekeeping Clerk
|PBX Installer |Repairer|Peace Corps Worker|Pediatric Dentist|Pediatrician|Personal Service Supervisor
|Personnel Administrator|Personnel Assistant|Personnel Recruiter|Pest Control Workers|Pesticide Handlers|Petroleum Engineer
|Petroleum Geologist|Petroleum Laboratory Assistant|Petroleum Refinery Operator|Petroleum Technician|Pharmacy Aides
|Philosophy |Religion Professor|Photo Optics Technician|Photoengravers|Photogrammetric Engineer
|Photographic Equipment Mechanic|Photographic Process Workers|Physical Education Instructor|Physical Therapist
|Physical Therapist Aides|Physical Therapy Assistant|Physician's Assistant|Physician's Office Nurse|Physics Professor
|Pilot|Plant Breeder|Plant Manager|Plasterers |Stucco Masons|Plastic Surgeon|Graphic Arts|Plumber Plumbing Contractor
|Police |Detectives Supervisor|Police Artist|Police Identification |Records Officers|Police Officer
|Political Science Professor|Political Scientist|Postal Service Clerks|Postal Service Mail Carriers
|Postal Service Mail Sorter|Postmasters |Mail Superintendents|Power Plant Operators|Power Line Installer |Mechanic
|Precision Devices Inspectors |Testers|Preschool Administrator|Preschool Teacher|Pressing Machine Operator
|Pressure Vessel Inspectors|Printing|Graphic Arts Reproduction Technician|Printmaker|Private Detectives |Investigators
|Private Nurse|Private Sector Executives|Probate Lawyer|Probation Officer|Procurement Clerks|Product Planner
|Product Safety Engineer|Production Planner|Production Clerk|Professional Sports Scout|Proofreader|Copy Marker
|Property Accountant|Property Assessor|Property Managers|Props |Lighting Technicians|Prosthetic Technician
|Psychiatric Aide|Psychiatric Technician|Psychiatrist|Psychology Professor|Public Health Service Officer
|Public Relations Manager|Public Relations Specialist|Public Transportation Inspector|Publications Editor
|Purchasing Agent|Purchasing Manager|Quality Control Coordinator|Quality Control Engineer|Quality Control Inspector
|Quality Control Technician|Quarry Worker|Radar |Sonar Technicians|Radiation Protection Engineer|Radiation Therapists
|Radio TV Announcer|Radio TV News Commentator|Radio TV Newscaster|Radio TV Producer|Radio TV Program Director
|Radio TV Sports Announcer|Radio TV Station Administrator|Radio TV Talk Show Host|Radio Mechanics|Radio Operators
|Radiologic Technicians|Radiologic Technologist|Radiologist|Rail Yard Engineers|Railroad Conductors |Yardmasters
|Railroad Engineer|Railroad Inspector|Range Manager|Real Estate Appraiser|Real Estate Assessor|Real Estate Broker
|Real Estate Lawyer|Real Estate Sales Agents|Recreation Leader|Recreational Protective Service Worker
|Recreational Therapist|Recreational Vehicle Mechanic|Referee|Refuse |Recyclable Material Collectors
|Registrar Administrator|Reliability Engineer|Religious Institution Education Coordinator|Reservation Ticket Agent
|Residence Counselor|Resource Recovery Engineer|Resource Teacher|Respiratory Care Technician|Respiratory Therapist
|Respiratory Therapy Technician|Restaurant Food Coordinator|Restaurant Manager|Retail Buyer
|Retail Customer Service Representative|Retail Inventory Control Analyst|Retail Sales Department Supervisor
|Retail Salespersons|Retail Store Manager|Revenue Agent|Safety Inspector|Sales Engineers|Sales Floor Stock Clerk
|Sales Managers|Sales Promoter|Sales Representative Aircraft|Sales Representative Drugs|Sales Representative Graphic Arts
|Sales Representative Hotel Furnishings|Sales Representative Medical Equipment|Sales Representative Printed Advertising
|Sales Representative Radio|TV Time|Sales Representative Telecommunications|Sales Representative Teleconferencing
|Sales Representative Education Programs|Sales Representatives Agricultural Products|Sales Representatives Instruments
|Sales Representatives Mechanical Equipment|Sales Representitive Psychological Tests|Sanitary Engineer
|Sawing Machine Operator|Scanner Operators|School Nurse|School Plant Consultant|School Psychologist|Scientific Linguist
|Scientific Photographer|Screen Printing Machine Operators|Screen Writer|Script Editor|Securities Broker|Security 
|Fire Alarm Systems Installers|Security Guard|Self Enrichment Education Teachers|Septic Tank |Sewer Servicers
|Service Station Attendants|Set Designer|Set Illustrator|Sewing Machine Operators|Sheet Metal Workers|Ship Carpenters
|Joiners|Ship Engineers|Ship Master|Ship Mate|Ship Pilot|Shipping  Receiving  |Traffic Clerks|Shoe Machine Operators
|Signal Switch Repairer|Skin Care Specialists|Small Engine Mechanics|Social |Community Service Manager|Social
|Human Service Assistants|Social Psychologist|Social Science Research Assistants|Social Service Volunteer
|Social Welfare Administrator|Social Work Professor|Social Worker|Sociology Professor|Soil Conservation Technician
|Soil Conservationist|Soil Engineer|Soil Scientist|Solar Energy Systems Designer|Solid Waste Disposal Administrator
|Sound Engineering Technicians|Special Education Administrator|Special Forces|Special Forces Officers|Speech Pathologist
|Speech Writer|Sport Psychologist|Sport's|Entertainment Agent  Manager|Sports Agent|Sports Events Business Manager
|Sports Physician|Sportswriter|Stained Glass Artist|Standards Engineer|Statement Clerks|Stationary Engineers
|Statistical Assistants|Steel Workers|Storage |Distribution Manager|Stress Analyst Engineer|Structural Drafter
|Structural Engineer|Student Admissions Administrator|Student Affairs Administrator|Student Financial Aid Administrator
|Substance Abuse Counselor|Subway |Streetcar Conductor|Surgeon|Surgical Technician|Technologist|Survey Researchers
|Surveying Technicians|Switchboard Operator|Systems Accountant|Systems Analyst  Data Processing|Tax Accountant|Tax Auditor
|Tax Collector|Tax Examiner|Tax Lawyer|Tax Preparer|Taxi Drivers |Chauffeurs|Teacher of the Blind|Team Assemblers
|Technical Scientific Publications Editor|Technical Director|Technical Illustrator|Technical Publications Writer
|Technological Espionage Intelligence Agent|Telecommunications Line Installers |Repairers
|Telecommunications Maintenance Worker|Telecommunications Technician|Telephone Station Installers|Textile Bleaching
|Dyeing Machine Operators|Textile Cutting Machine Operators|Textile Designer|Tile |Marble Setters|Title Examiner
|Title Searchers|Tool Machine Designer|Tool |Die Makers| Sharpener|Tour Guide|Town Clerk|Traffic Administrator
|Traffic Agent|Traffic Technicians|Transit |Railroad Police|Transportation Attendants|Transportation Systems Design Engineer
|Travel Agent|Travel Clerk|Travel Counselor|Travel Writer|Treasurer|Treatment Plant Operators|Tree Trimmers |Pruners
|Truck Driver|Ultrasound Technologist|Unemployment Inspector|Urban |Regional Planner|Ushers |Lobby Attendants
|Utility Meter Reader|Vending Machine Mechanic|Veterinarian|Veterinarian Technician|Veterinary Assistant|Video Engineer
|Vocational Education Instructors College|Vocational Education Teachers  Middle School|Vocational Rehabilitation Counselor
|Voice Pathologist|Waiters |Waitresses|Warehouse Stock Clerk|Watch Repairers|Water Pollution Control Inspector
|Weather Observer|Web Art Director|Weighers |Measurers|Welder|Welfare Eligibility Workers |Interviewers|Wholesale Buyers
|Wildlife Biologist|Wildlife Control Agent|Windows Draperies Treatment Specialist|Woodworking Machine Operators
|Word Processing Specialist|Writer|Author|Zoo Veterinarian|Zoologist
"""

tweet_df['layp_occu'] = tweet_df['bio'].str.contains(conStrLay)

# Save computer professional tweets
tweet_df.to_csv('aiAI_engi_cleaned.csv', sep=',', encoding='utf-8')

# Save laypeople tweets
tweet_df.to_csv('aiAI_layp_cleaned.csv', sep=',', encoding='utf-8')
tweet_df['has_occu'] = tweet_df['bio'] != ""

# save tweets from both groups into one document
tweet_df.to_csv('aiAI_tweets_cleaned.csv', sep=',', encoding='utf-8')


# Create a column that categorizes all columns
tweet_df['occu_cat'] = ''
tweet_df.loc[tweet_df['has_occu'] == False, 'occu_cat'] = 'none'
tweet_df.loc[tweet_df['engi_occu'] == True, 'occu_cat'] = 'engi_occu'
tweet_df.loc[tweet_df['layp_occu'] == True, 'occu_cat'] = 'layp_occu'
tweet_df.loc[tweet_df['occu_cat'] == '', 'occu_cat'] = 'other'


# Step II: Use bipolar sentiment lexicon to calculate positive and negative word ratio of tweets

# read sentiment lexicon data
posWW = open('positive.txt').read()
negWW = open('negative.txt').read()

positive_words = posWW.split('\n')
negative_words = negWW.split('\n')

# the column to count total number of words in each tweet
tweet_df['word_count'] = tweet_df['text_clean'].str.split().str.len()
tweet_df.head(5)

# Count the number of positive words
positive_counts = []
negative_counts = []
tweet_length = []
for tweet in tweet_df['text_clean']:
    positive_counter = 0
    negative_counter = 0
    tweet_length.append(len(words))
    for word in words:
        if word in positive_words:
            positive_counter = positive_counter + 1
        if word in negative_words:
            negative_counter = negative_counter + 1
    positive_counts.append(positive_counter)
    negative_counts.append(negative_counter)
    
# Add those counts to the data frame
tweet_df['pos_count'] = positive_counts
tweet_df['neg_count'] = negative_counts

# Calculate ratios
tweet_df['pos_ratio'] = tweet_df['pos_count']/tweet_df['word_count']
tweet_df['neg_ratio'] = tweet_df['neg_count']/tweet_df['word_count']

# Save 
tweet_df.to_csv('aiAI_tweets_cleaned.csv', sep=',', encoding='utf-8')


# Step III: Clean the data again

# Load data
tweet_df = pd.read_csv('aiAI_tweets_cleaned.csv',index_col = 0)

#Remove the rows that pos_ratio > 1.0
tweet_df = tweet_df.drop(tweet_df[tweet_df.pos_ratio>1.0].index)

# Delete rows with index 'other'
indexNames = tweet_df[ tweet_df['occu_cat'] == "other" ].index
tweet_df.drop(indexNames , inplace=True)

#Remove rows with NaN
tweet_df = tweet_df[np.isfinite(tweet_df['pos_ratio'])]

#Delete rows with RT
tweet_df=tweet_df[~tweet_df.text.str.contains("RT")]

#Reset the index of tweet_df
tweet_df = tweet_df.reset_index(drop=True)

#Save removed  data to occu-other_ratio_remove.csv
tweet_df.to_csv('remove.csv', sep=',', encoding='utf-8')


# Step IV: Sampling


# Load data
tweet_df = pd.read_csv('abnormal_pos_ratio_remove.csv',index_col = 0)

# Subset the data to only Engineer and Laypeople tweets
tweet_df_EL = tweet_df[(tweet_df['occu_cat'] == 'engi_occu') | (tweet_df['occu_cat'] == 'layp_occu')]

# Check if there are balanced data between engi and lap categories
tweet_df_EL['occu_cat'].value_counts()

# split the data into a engineer (EN) and laypeople (LA) set
tweet_df_EN = tweet_df_EL[(tweet_df_EL['occu_cat'] == 'engi_occu')] 
tweet_df_LA = tweet_df_EL[(tweet_df_EL['occu_cat'] == 'layp_occu')]

# Confirm how many rows are in LA, the smaller sample
LA_tweet_count = len(tweet_df_LA)
print(LA_tweet_count) 

# Sample the same number of tweets from EN
tweet_df_EN_sample = tweet_df_EN.sample(n = LA_tweet_count)
len(tweet_df_EN_sample) 


# Step V: Descriptive Statistics

from numpy import inf

# positive and negative ratios from each occupation
EN_pos = np.asarray(tweet_df_EN_sample.pos_ratio,dtype=np.float)
EN_neg = np.asarray(tweet_df_EN_sample.neg_ratio,dtype=np.float)
LA_pos = np.asarray(tweet_df_LA.pos_ratio,dtype=np.float)
LA_neg = np.asarray(tweet_df_LA.neg_ratio,dtype=np.float)

# Convert inf to 0 for each
EN_pos[EN_pos == inf] = 0
EN_neg[EN_neg == inf] = 0
LA_pos[LA_pos == inf] = 0
LA_neg[LA_neg == inf] = 0
EN_pos[EN_pos == inf] = 0
EN_neg[EN_neg == inf] = 0
LA_pos[LA_pos == inf] = 0
LA_neg[LA_neg == inf] = 0

# find NaN indices
EN_pos_NaN = np.argwhere(np.isnan(EN_pos))
EN_neg_NaN = np.argwhere(np.isnan(EN_neg))
LA_pos_NaN = np.argwhere(np.isnan(LA_pos))
LA_neg_NaN = np.argwhere(np.isnan(LA_neg))

# set NaN to zero
EN_pos[EN_pos_NaN] = 0
EN_neg[EN_neg_NaN] = 0
LA_pos[LA_pos_NaN] = 0
LA_neg[LA_neg_NaN] = 0


# Positive ratio, engineer group
# mean, median, range, st. deviation, each rounded to 3 decimal places
EN_pos_mean = round(EN_pos.mean(), 3)
EN_pos_median = round(np.median(EN_pos), 3)
EN_pos_sd = round(np.std(EN_pos), 3)
EN_pos_max = round(max(EN_pos), 3)
EN_pos_min = round(min(EN_pos), 3)

# Negative ratio, engineer group
# mean, median, range, st. deviation, each rounded to 3 decimal places
EN_neg_mean = round(EN_neg.mean(), 3)
EN_neg_median = round(np.median(EN_neg), 3)
EN_neg_sd = round(np.std(EN_neg), 3)
EN_neg_max = round(max(EN_neg), 3)
EN_neg_min = round(min(EN_neg), 3)

# Positive ratio, laypeople group
# mean, median, range, st. deviation, each rounded to 3 decimal places
LA_pos_mean = round(LA_pos.mean(), 3)
LA_pos_median = round(np.median(LA_pos), 3)
LA_pos_sd = round(np.std(LA_pos), 3)
LA_pos_max = round(max(LA_pos), 3)
LA_pos_min = round(min(LA_pos), 3)

# Negative ratio, laypeople group
# mean, median, range, st. deviation, each rounded to 3 decimal places
LA_neg_mean = round(LA_neg.mean(), 3)
LA_neg_median = round(np.median(LA_neg), 3)
LA_neg_sd = round(np.std(LA_neg), 3)
LA_neg_max = round(max(LA_neg), 3)
LA_neg_min = round(min(LA_neg), 3)


# Summarize mean and s.d.
comp_pos = 'Pos ratio: EN mean %f (s.d. %f); LA mean %f (s.d. %f)' % (EN_pos_mean, EN_pos_sd, LA_pos_mean, LA_pos_sd)
comp_neg = 'Neg ratio: EN mean %f (s.d. %f); LA mean %f (s.d. %f)' % (EN_neg_mean, EN_neg_sd, LA_neg_mean, LA_neg_sd)
print(comp_pos)
print(comp_neg)


# Step VI: Visualize the Distributions of Samples


# Positive ratio is not normal
LA_pos_plot = sns.distplot(tweet_df_LA.pos_ratio, hist = False).set_title('Prop. of positive tweets, Laypeople')


EN_pos_plot = sns.distplot(tweet_df_EN_sample.pos_ratio, hist = False).set_title('Prop. of positive tweets, Engineer')


# negative ratio is not normal
LA_neg_plot = sns.distplot(tweet_df_LA.neg_ratio, hist = False).set_title('Prop. of negative tweets, Laypeople')


# negative ratio is not normal
EN_neg_plot = sns.distplot(tweet_df_EN_sample.neg_ratio, hist = False).set_title('Prop. of negative tweets, Engineer')


# Step VII: Run Wilcox test for Each Dependent Variable


# Import test function
from scipy.stats import mannwhitneyu

# positive ratio test
mannwhitneyu(tweet_df_LA.pos_ratio, tweet_df_EN_sample.pos_ratio)

pos_means = 'Laypeople positive mean: %f; Engineer positive mean: %f' % (LA_pos_mean, EN_pos_mean)
print(neg_means)


# negative test ratio
mannwhitneyu(tweet_df_LA.neg_ratio, tweet_df_EN_sample.neg_ratio)

neg_means = 'Laypeople negative mean: %f; Engineer negative mean: %f' % (LA_neg_mean, EN_neg_mean)
print(neg_means)


# Step VIII: Run Basic Linear Regression

import statsmodels.api as sm
import scipy
from scipy import stats


# Convert tweets whose counted words divided by zero-sentiment word to inf
tweet_df_EL.pos_ratio[np.argwhere(np.isinf(tweet_df_EL.pos_ratio))] = 0
tweet_df_EL.neg_ratio[np.argwhere(np.isinf(tweet_df_EL.neg_ratio))] = 0

# find NaN indices
EL_pos_NaN = np.argwhere(np.isnan(tweet_df_EL.pos_ratio))
EL_neg_NaN = np.argwhere(np.isnan(tweet_df_EL.neg_ratio))

# set NaN to zero
tweet_df_EL.pos_ratio[EL_pos_NaN] = 0
tweet_df_EL.neg_ratio[EL_neg_NaN] = 0


# Step IX: Remove Outliers

# The measure used to assess outliers is the z-score
# Create new columns for pos_ratio and neg_ratio that are z-transformed
tweet_df_EL['pos_ratio_z'] = scipy.stats.zscore(tweet_df_EL['pos_ratio'])
tweet_df_EL['neg_ratio_z'] = scipy.stats.zscore(tweet_df_EL['neg_ratio'])


# the distribution of z-scores: a few points are > 3
sns.distplot(tweet_df_EL.pos_ratio_z, hist = False).set_title('Z-scores, positive ratio') 

# the distribution of z-scores: few points are > 3
sns.distplot(tweet_df_EL.neg_ratio_z, hist = False).set_title('Z-scores, negative ratio') 

# save the data as a separate object
tweet_df_EL_saver = tweet_df_EL

# Restrict the main data frame (tweet_df_NT) to only z-scores < 3 or > -3
tweet_df_EL = tweet_df_EL[(tweet_df_EL['pos_ratio_z'] < 3) & (tweet_df_EL['pos_ratio_z'] > -3)] 
tweet_df_EL = tweet_df_EL[(tweet_df_EL['neg_ratio_z'] < 3) & (tweet_df_EL['neg_ratio_z'] > -3)] 


#  Step X Positive Ratio Model

# indepdendent and dependent variables
x_pos = tweet_df_EL['occu_cat']    

# the proportion of all the data that falls into each category
num_rows = tweet_df_EL.shape[0] 
cat_counts = tweet_df_EL['occu_cat'].value_counts() 
cat_counts / num_rows

tweet_df_EL['weighted_occu'] = 0
tweet_df_EL.loc[tweet_df_EL.occu_cat == 'layp_occu', 'weighted_occu'] = 0.67
tweet_df_EL.loc[tweet_df_EL.occu_cat == 'engi_occu', 'weighted_occu'] = -0.33

tweet_df_EL.weighted_occu.value_counts()

# Set weighted row to dependent variable
x_pos = tweet_df_EL.weighted_occu

# Dependent variable is the positive word ratio of each tweet. 
y_pos = tweet_df_EL['pos_ratio']   

# Fit the model
pos_model = sm.OLS(y_pos, x_pos)
pos_model2 = pos_model.fit()
print(pos_model2.summary())


# Step XI: Negative Ratio Model

# Dependent variable, negative ratio
y_neg = tweet_df_EL['neg_ratio']   
x_neg = x_pos

# Fit the model
neg_model = sm.OLS(y_neg, x_neg)
neg_model2 = neg_model.fit()
print(neg_model2.summary())

# Plot positive ratio and negative ratio
tweet_df.boxplot(column=['pos_ratio', 'neg_ratio'], by=['occu_cat'])

