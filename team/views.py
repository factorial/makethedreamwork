from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.conf import settings

import os
import time
import openai
from dotenv import load_dotenv
import json

fake_response = {'team': {'objective': 'Get elected mayor of Atlanta', 'description': '{\n  "Campaign Manager": [\n    "Develop a campaign strategy and timeline",\n    "Recruit and manage campaign volunteers",\n    "Coordinate fundraising efforts",\n    "Organize campaign events and appearances",\n    "Oversee messaging and communication with the public"\n  ],\n  "Field Organizer": [\n    "Identify and target key voting precincts",\n    "Recruit and train volunteers for canvassing and phone banking",\n    "Organize and execute voter outreach efforts",\n    "Track and report on voter contact and engagement",\n    "Assist with voter registration and early voting efforts"\n  ],\n  "Fundraiser": [\n    "Develop a fundraising plan and timeline",\n    "Identify and cultivate potential donors",\n    "Organize fundraising events and solicit donations",\n    "Track and report on fundraising progress",\n    "Assist with donor outreach and communication"\n  ],\n  "Communications Director": [\n    "Develop and execute a communications plan",\n    "Craft messaging for the campaign and candidate",\n    "Manage social media and online presence",\n    "Coordinate with media outlets and journalists",\n    "Prepare the candidate for interviews and debates"\n  ],\n  "Volunteer Coordinator": [\n    "Recruit and manage campaign volunteers",\n    "Create and manage volunteer schedules",\n    "Train volunteers on campaign messaging and outreach",\n    "Organize and execute volunteer events and activities",\n    "Track and report on volunteer engagement and progress"\n  ]\n}', 'roles': {'Campaign Manager': {'questions': '1. What are the key issues that are important to the voters in Atlanta?\n2. Who are our main competitors in this election and what are their strengths and weaknesses?\n3. What is the budget for the campaign and how should we allocate our resources?\n4. How can we effectively target and engage with different demographics in Atlanta?\n5. What are the most effective campaign strategies and tactics that have worked in previous elections in Atlanta?\n6. How can we ensure that our messaging is consistent and resonates with the voters?\n7. What are the key milestones and deadlines that we need to meet in order to stay on track with our campaign timeline?\n8. How can we measure the success of our campaign efforts and make adjustments as needed?\n9. What kind of support can we expect from the party or other political organizations?\n10. How can we ensure that our campaign is ethical and transparent throughout the entire process?', 'guide': "# Campaign Manager Handbook\n\nWelcome to the team! As the Campaign Manager, your role is critical to the success of our campaign. Here are some answers to the questions you posed:\n\n## Key Issues\nIt's important to understand what issues are most important to the voters in Atlanta. We can gather this information through polling and focus groups. Some key issues that have been important in recent Atlanta elections include affordable housing, transportation, public safety, and education.\n\n## Competitors\nWe should research our competitors and their strengths and weaknesses. This can include looking at their previous campaigns, polling data, and public statements. It's also important to understand their base of support and how we can differentiate ourselves from them.\n\n## Budget\nWe should have a clear understanding of our budget and how we plan to allocate our resources. This can include fundraising goals, advertising spend, and staffing expenses. It's important to prioritize our spending based on the most effective strategies for reaching voters.\n\n## Targeting Demographics\nAtlanta is a diverse city, and it's important to understand how to effectively engage with different demographics. This can include targeted messaging and outreach efforts, as well as partnering with community leaders and organizations.\n\n## Effective Strategies\nThere are many effective campaign strategies and tactics that have worked in previous Atlanta elections. These can include door-to-door canvassing, phone banking, direct mail, and digital advertising. It's important to test different strategies and measure their effectiveness.\n\n## Consistent Messaging\nConsistent messaging is key to a successful campaign. We should develop a clear message that resonates with voters and use it consistently across all communication channels.\n\n## Milestones and Deadlines\nWe should develop a clear timeline with key milestones and deadlines. This can include fundraising goals, voter registration deadlines, and election day. It's important to stay on track and adjust our strategy as needed.\n\n## Measuring Success\nWe should track and measure the success of our campaign efforts. This can include tracking engagement on social media, polling data, and volunteer activity. We should use this data to make informed decisions and adjust our strategy as needed.\n\n## Party Support\nWe should reach out to the party and other political organizations for support. This can include endorsements, fundraising assistance, and access to voter data.\n\n## Ethics and Transparency\nWe should always conduct our campaign in an ethical and transparent manner. This includes following all campaign finance laws, being honest with voters, and avoiding negative campaigning.\n\n## Typical Workday\nAs Campaign Manager, your typical workday may include:\n- Developing and executing the campaign strategy\n- Managing the volunteer team\n- Coordinating fundraising efforts\n- Meeting with stakeholders and community leaders\n- Analyzing polling and voter data\n- Developing messaging and communication materials\n- Attending campaign events and appearances\n- Tracking and reporting on campaign progress\n- Adjusting strategy as needed based on data and feedback\n\nRemember, communication and collaboration with the team is key to our success. Good luck, and let's win this election!", 'tasks': ['Develop a campaign strategy and timeline', 'Recruit and manage campaign volunteers', 'Coordinate fundraising efforts', 'Organize campaign events and appearances', 'Oversee messaging and communication with the public'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-0VdJBfttCevU6h7RZDxiR1Gb.png?st=2023-04-27T18%3A27%3A15Z&se=2023-04-27T20%3A27%3A15Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T18%3A39%3A06Z&ske=2023-04-28T18%3A39%3A06Z&sks=b&skv=2021-08-06&sig=AhhqZc1XahonNZL4Ycp/Psva9fX9COXJTMeLvut9PY4%3D'}, 'Field Organizer': {'questions': '1. What are the key voting precincts in Atlanta and how do we identify them?\n2. What is the best approach for canvassing and phone banking, and how can we train volunteers effectively?\n3. What are the most effective voter outreach methods and how can we execute them successfully?\n4. How do we track and report on voter contact and engagement, and what metrics should we be tracking?\n5. What is the process for voter registration and early voting, and how can we assist with these efforts as a campaign team?', 'guide': '# Field Organizer Handbook\n\nWelcome to the team as our new Field Organizer! Your role is crucial to our success in getting our candidate elected as mayor of Atlanta. Here is a handbook to help you get started and answer any questions you may have.\n\n## Key Voting Precincts\n\nTo identify the key voting precincts in Atlanta, we will need to analyze past election data and demographic information. This will help us target areas with high voter turnout and support for our candidate. Our campaign manager will provide you with the necessary data and tools to identify these precincts.\n\n## Canvassing and Phone Banking\n\nCanvassing and phone banking are effective ways to reach voters and spread our campaign message. To train our volunteers effectively, we will provide them with a script and talking points to use when engaging with voters. We will also hold training sessions to practice and improve their communication skills. As a field organizer, you will be responsible for organizing and executing these training sessions.\n\n## Voter Outreach Methods\n\nThere are several voter outreach methods we can use, such as door-to-door canvassing, phone banking, and text messaging. We will need to tailor our approach based on the demographic and voting history of each precinct. As a field organizer, you will work closely with our volunteer coordinator to organize and execute these outreach efforts.\n\n## Tracking and Reporting\n\nTo track and report on voter contact and engagement, we will use a database or spreadsheet to record our interactions with voters. We will also track metrics such as the number of voters contacted and their level of support for our candidate. As a field organizer, you will be responsible for keeping accurate records and reporting on our progress.\n\n## Voter Registration and Early Voting\n\nVoter registration and early voting are crucial to our success in this election. We will need to assist voters in registering to vote and provide them with information on early voting locations and times. Our campaign manager will provide you with the necessary resources and tools to assist with these efforts.\n\n## Typical Workday\n\nAs a field organizer, your typical workday will include:\n\n1. Reviewing and analyzing data on key voting precincts.\n2. Organizing and executing training sessions for volunteers on canvassing and phone banking.\n3. Coordinating with the volunteer coordinator to organize voter outreach efforts.\n4. Keeping accurate records of voter contact and engagement.\n5. Assisting with voter registration and early voting efforts.\n6. Reporting on progress and making recommendations for improvement to the campaign manager.\n\nThank you for joining our team as our new Field Organizer. We look forward to working with you to get our candidate elected as mayor of Atlanta!', 'tasks': ['Identify and target key voting precincts', 'Recruit and train volunteers for canvassing and phone banking', 'Organize and execute voter outreach efforts', 'Track and report on voter contact and engagement', 'Assist with voter registration and early voting efforts'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-2EVIA0i1gCy6l7FKTWdJblLi.png?st=2023-04-27T18%3A28%3A21Z&se=2023-04-27T20%3A28%3A21Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T17%3A42%3A45Z&ske=2023-04-28T17%3A42%3A45Z&sks=b&skv=2021-08-06&sig=yP0vevoCkot1FEk3AMWu0MlTEhB2uqwSeKThiDrWZS8%3D'}, 'Fundraiser': {'questions': '1. What is the fundraising goal for the campaign?\n2. Who are the potential donors we should target and how do we reach out to them?\n3. What types of fundraising events have been successful in the past and how can we replicate them?\n4. How do we track and report on fundraising progress?\n5. What is the messaging we should use when soliciting donations?\n6. How can I assist with donor outreach and communication?\n7. What are the legal requirements and restrictions for campaign fundraising?', 'guide': "# Fundraiser Handbook\n\nWelcome to the team as our new Fundraiser! Your role is crucial to the success of our campaign to get elected mayor of Atlanta. Here is a handbook to help you get started and answer any questions you may have.\n\n## Fundraising Goals\n\nOur fundraising goal for the campaign is $1 million. This will cover the costs of events, advertising, and staff salaries.\n\n## Donor Outreach\n\nWe should target potential donors who have a history of supporting political campaigns, especially those who have contributed to campaigns in Atlanta. We can reach out to them through phone calls, emails, and direct mail. We can also attend local events and meet potential donors in person.\n\n## Successful Fundraising Events\n\nIn the past, successful fundraising events have included cocktail parties, dinners, and silent auctions. We should aim to replicate these events and make them unique to our campaign. For example, we could host a barbecue or a concert featuring local musicians.\n\n## Tracking Fundraising Progress\n\nWe will use a fundraising software to track and report on fundraising progress. This software will allow us to see how much money has been raised, where the donations are coming from, and which donors have contributed the most.\n\n## Messaging for Soliciting Donations\n\nWhen soliciting donations, we should emphasize the importance of our campaign and the positive impact it will have on Atlanta. We should also highlight the candidate's qualifications and experience. It's important to be transparent about how the donations will be used and to thank donors for their contributions.\n\n## Donor Outreach and Communication\n\nYou can assist with donor outreach and communication by sending thank-you notes, updating donors on the progress of the campaign, and answering any questions they may have. It's important to build relationships with donors and make them feel appreciated.\n\n## Legal Requirements and Restrictions\n\nCampaign fundraising is subject to legal requirements and restrictions. We must comply with Federal Election Commission (FEC) regulations and state and local laws. This includes reporting donations and expenditures, and not accepting donations from foreign nationals or corporations.\n\n## Typical Workday\n\nHere is a typical workday for a Fundraiser on our team:\n\n1. Check fundraising software for new donations and update records\n2. Reach out to potential donors via phone, email, or direct mail\n3. Plan and organize fundraising events\n4. Send thank-you notes to donors\n5. Assist with donor outreach and communication\n6. Attend meetings with other team members to discuss campaign strategy and progress\n\nWe hope this handbook has been helpful in answering your questions and providing guidance for your role as Fundraiser on our team. Let's work together to get elected mayor of Atlanta!", 'tasks': ['Develop a fundraising plan and timeline', 'Identify and cultivate potential donors', 'Organize fundraising events and solicit donations', 'Track and report on fundraising progress', 'Assist with donor outreach and communication'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-g3qPtlcZvlY1ePTP36Z9pNA3.png?st=2023-04-27T18%3A29%3A28Z&se=2023-04-27T20%3A29%3A28Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T18%3A29%3A40Z&ske=2023-04-28T18%3A29%3A40Z&sks=b&skv=2021-08-06&sig=jaMY6FZfuuLGS3PakaLMgQaHrwobIXBkWIkhWXI6gZg%3D'}, 'Communications Director': {'questions': "1. What are the key messages and values that the candidate wants to convey to the public?\n2. Who is our target audience and how can we effectively reach them through various communication channels?\n3. What are the main issues and concerns of the voters in Atlanta and how can we address them in our messaging?\n4. How can we effectively manage the candidate's public image and respond to any negative press or attacks from opponents?\n5. What are the best practices for managing social media accounts and creating engaging content to reach our audience?\n6. How can we effectively coordinate with other members of the campaign team, such as the campaign manager and field organizer, to ensure consistent messaging and outreach efforts?\n7. What are the rules and regulations around political advertising and messaging, and how can we ensure compliance with these laws?", 'guide': "# Communications Director Handbook\n\nWelcome to the role of Communications Director on our campaign team! As the Communications Director, your main responsibility is to develop and execute a communications plan that effectively conveys the candidate's messages and values to the public. Here are some key questions and answers to help you succeed in this role:\n\n## Key Messages and Values\n\n1. What are the key messages and values that the candidate wants to convey to the public?\n\nThe candidate's key messages and values should be the foundation of all our communication efforts. You should work closely with the campaign manager and the candidate to identify these messages and values. Some examples might include a commitment to social justice, a focus on economic development, or a dedication to improving public education.\n\n## Target Audience\n\n2. Who is our target audience and how can we effectively reach them through various communication channels?\n\nOur target audience will likely include a diverse range of voters in Atlanta, including different age groups, ethnicities, and socioeconomic backgrounds. You should work with the campaign manager and the field organizer to identify key voting precincts and demographics, and develop targeted messaging and outreach efforts for each group. We can reach our audience through various communication channels, including social media, email newsletters, direct mail, and phone banking.\n\n## Voter Concerns\n\n3. What are the main issues and concerns of the voters in Atlanta and how can we address them in our messaging?\n\nWe should conduct research and polling to identify the main issues and concerns of voters in Atlanta. Some common concerns might include affordable housing, public safety, and transportation. We can address these concerns in our messaging by highlighting the candidate's plans and policies to address these issues, as well as emphasizing the candidate's experience and qualifications.\n\n## Public Image\n\n4. How can we effectively manage the candidate's public image and respond to any negative press or attacks from opponents?\n\nAs the Communications Director, you should work closely with the campaign manager and the candidate to develop a strategy for managing the candidate's public image. This might include developing messaging around the candidate's background and experience, as well as responding quickly and effectively to any negative press or attacks from opponents. It's important to stay on top of media coverage and social media mentions, and respond promptly to any issues or concerns.\n\n## Social Media\n\n5. What are the best practices for managing social media accounts and creating engaging content to reach our audience?\n\nSocial media is a key communication channel for our campaign, and it's important to use best practices to effectively reach our audience. This might include developing a social media content calendar, using engaging visuals and videos, and responding promptly to comments and messages. You should also work closely with the campaign manager and the field organizer to ensure consistent messaging across all communication channels.\n\n## Coordination\n\n6. How can we effectively coordinate with other members of the campaign team, such as the campaign manager and field organizer, to ensure consistent messaging and outreach efforts?\n\nEffective coordination is key to a successful campaign, and you should work closely with the campaign manager and the field organizer to ensure consistent messaging and outreach efforts. This might include regular team meetings, shared communication calendars, and a clear division of responsibilities. You should also be open to feedback and input from other team members, and be willing to adjust your communication strategy as needed.\n\n## Rules and Regulations\n\n7. What are the rules and regulations around political advertising and messaging, and how can we ensure compliance with these laws?\n\nThere are strict rules and regulations around political advertising and messaging, and it's important to ensure compliance with these laws. You should familiarize yourself with the relevant regulations, such as those set by the Federal Election Commission and the Georgia Government Transparency and Campaign Finance Commission. You should also work closely with the campaign manager and the fundraiser to ensure that all fundraising efforts are compliant with these laws.\n\n## Typical Workday\n\nAs the Communications Director, your typical workday might include the following tasks:\n\n- Developing and executing a communications plan\n- Crafting messaging for the campaign and candidate\n- Managing social media and online presence\n- Coordinating with media outlets and journalists\n- Preparing the candidate for interviews and debates\n- Attending team meetings and coordinating with other team members\n- Responding to media inquiries and social media comments\n- Tracking and reporting on communication metrics and progress\n- Assisting with other campaign tasks as needed\n\nRemember, effective communication is key to a successful campaign, and your role as Communications Director is crucial to achieving our objective of getting elected mayor of Atlanta. Good luck!", 'tasks': ['Develop and execute a communications plan', 'Craft messaging for the campaign and candidate', 'Manage social media and online presence', 'Coordinate with media outlets and journalists', 'Prepare the candidate for interviews and debates'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-VHeeshIfOJFXEcbmtw4dJMEK.png?st=2023-04-27T18%3A31%3A11Z&se=2023-04-27T20%3A31%3A11Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T18%3A58%3A05Z&ske=2023-04-28T18%3A58%3A05Z&sks=b&skv=2021-08-06&sig=jkVTImzEa5S9Wx0lMTIgV2QSY20chgo3hahqOiGKHVI%3D'}, 'Volunteer Coordinator': {'questions': '1. What is the current volunteer base like, and what are their skills and interests?\n2. How can we effectively recruit new volunteers and expand our reach?\n3. What are the key messaging points and outreach strategies that volunteers should focus on?\n4. How can we ensure that volunteers are properly trained and equipped to engage with voters?\n5. What metrics should we be tracking to measure volunteer engagement and progress?\n6. What are some effective ways to recognize and incentivize volunteers for their contributions?\n7. How can we collaborate with other roles on the team to ensure a cohesive and effective campaign?', 'guide': "# Volunteer Coordinator Handbook\n\n## Introduction\nWelcome to the team as the Volunteer Coordinator! Your role is crucial to the success of our campaign to get elected mayor of Atlanta. As Volunteer Coordinator, you will be responsible for recruiting, managing, and training our campaign volunteers. This handbook will provide you with the necessary information to effectively carry out your tasks and collaborate with other roles on the team.\n\n## Questions and Answers\n1. What is the current volunteer base like, and what are their skills and interests?\n   - Our current volunteer base consists of individuals from diverse backgrounds and skill sets. Some volunteers have experience in political campaigns, while others are new to the process. It is important to identify their skills and interests to assign them to tasks that align with their strengths.\n\n2. How can we effectively recruit new volunteers and expand our reach?\n   - There are several ways to recruit new volunteers, including social media outreach, community events, and word-of-mouth. It is important to have a clear message and purpose for our campaign to attract volunteers who are passionate about our cause.\n\n3. What are the key messaging points and outreach strategies that volunteers should focus on?\n   - Our messaging should focus on our candidate's platform and how it will benefit the people of Atlanta. Volunteers should be trained to effectively communicate these points to potential voters. Outreach strategies can include canvassing, phone banking, and attending community events.\n\n4. How can we ensure that volunteers are properly trained and equipped to engage with voters?\n   - It is important to provide volunteers with training sessions that cover our messaging, outreach strategies, and best practices for engaging with voters. We can also provide them with materials such as flyers and talking points to assist them in their outreach efforts.\n\n5. What metrics should we be tracking to measure volunteer engagement and progress?\n   - We should track metrics such as the number of volunteers recruited, hours volunteered, and the number of voters contacted. This will allow us to measure the effectiveness of our outreach efforts and make adjustments as needed.\n\n6. What are some effective ways to recognize and incentivize volunteers for their contributions?\n   - Recognition can be as simple as a thank you note or shoutout on social media. We can also provide incentives such as campaign merchandise or tickets to campaign events. It is important to show our appreciation for their hard work and dedication.\n\n7. How can we collaborate with other roles on the team to ensure a cohesive and effective campaign?\n   - Communication is key to collaboration. It is important to regularly check in with other roles on the team and provide updates on volunteer engagement and progress. We can also coordinate with other roles to ensure that our messaging and outreach strategies are aligned.\n\n## Typical Workday\nAs Volunteer Coordinator, a typical workday may include the following tasks:\n1. Check and respond to emails and messages from volunteers.\n2. Review volunteer schedules and make any necessary adjustments.\n3. Conduct a training session for new volunteers.\n4. Follow up with volunteers who have not yet completed their assigned tasks.\n5. Attend a team meeting to provide updates on volunteer engagement and progress.\n6. Collaborate with other roles on the team to ensure a cohesive and effective campaign.\n7. Recognize and incentivize volunteers for their contributions.", 'tasks': ['Recruit and manage campaign volunteers', 'Create and manage volunteer schedules', 'Train volunteers on campaign messaging and outreach', 'Organize and execute volunteer events and activities', 'Track and report on volunteer engagement and progress'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-gex3sZwXrcBZAYtjcMKHQzWh.png?st=2023-04-27T18%3A32%3A23Z&se=2023-04-27T20%3A32%3A23Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T17%3A47%3A55Z&ske=2023-04-28T17%3A47%3A55Z&sks=b&skv=2021-08-06&sig=ZwckxiqBqrHZ8XLD%2Bcrc7WL1HTYUKXGjROE0jOaYfHc%3D'}}}}

OPENAI_API_KEY=settings.OPENAI_API_KEY

# Model: GPT, LLAMA, HUMAN, etc.
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")).lower()

# Model configuration
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.5))

# Configure OpenAI
openai.api_key = OPENAI_API_KEY
render_images = True


def openai_call(
      prompt: str,
      model: str = LLM_MODEL,
      temperature: float = OPENAI_TEMPERATURE,
      max_tokens: int = 100,
):
    while True:
        try:
            # Use chat completion API
            messages = [{"role": "system", "content": prompt}]
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None,
            )
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print(
                "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.Timeout:
            print(
                "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIError:
            print(
                "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIConnectionError:
            print(
                "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.InvalidRequestError:
            print(
                "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.ServiceUnavailableError:
            print(
                "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        else:
            break





def generate_team(OBJECTIVE):
    context = ""
    start_time = time.time()
    print(start_time)
    print(f'generating {OBJECTIVE} team')

    responses = {
        "team": {
            "objective": OBJECTIVE,
            "description": "",
            "roles": {},
        },
    }


    #return fake_response


    prompt = f'Yes or no: is the following objective offensive or inappropriate: "{OBJECTIVE}"? Answer with only yes or no.'
    result = openai_call(prompt, max_tokens=100)
    print("Offensive? "+ result)
    if 'yes' in result.lower():
        return False

    prompt = f"""
        OBJECTIVE: {OBJECTIVE}
        TASK: Write instructions for a team of humans to execute. Respond with a JSON object whose keys are
        unique role names on the team and each key contains a task list for that unique role.
        RESPONSE (JSON format only):"""
    result = openai_call(prompt, max_tokens=3000)
    print(result)

    responses["team"]["description"] = result
    context = prompt + result

    role_tasks = {}
    try:
        role_tasks = json.loads(f"{result}")
    except:
        print("Couldn't parse the team description this time.")



    valid_json = False
    while not valid_json:
        prompt = f"{context} List the roles on this team as a JavaScript array of strings. RESULT:["
        result = openai_call(prompt)
        print("["+ result)

        context = prompt + result

        try:
            roles = json.loads(f"[{result}")
            valid_json = True
        except:
            prompt = f"{context} That was not valid JavaScript array syntax. Try again:\n"

    for role in roles:

        loop_context = context
        prompt = f"""{loop_context}
        You are a new member on this team, assuming the role of {role}. List the questions you want to ask an
        expert in this role so they can give you the answers that will make you successful at your tasks and able to
        effectively collaborate toward the objective: {OBJECTIVE}."""
        result = openai_call(prompt, max_tokens=3000)
        print(result)

        responses["team"]["roles"][role] = { "questions" : result }
        loop_context = prompt + result

        prompt = f"""{loop_context}
                You are an expert in the role of {role} on this team. Generate a handbook for the new member in this
                role using Markdown format. In it, answer each of the new member's specific questions.
                Also include a guide which describes step-by-step a typical workday that the person in this role
                should expect to do."""
        result = openai_call(prompt, max_tokens=3000)
        print(result)
        responses["team"]["roles"][role]["guide"] =  result

        if role in role_tasks:
            if isinstance(role_tasks[role], list):
                responses["team"]["roles"][role]["tasks"] = role_tasks[role]
            else:
                responses["team"]["roles"][role]["tasks_string"] = role_tasks[role]

        if render_images:
            prompt = f"3D rendered cartoon avatar of {role}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

            while True:
                try:
                    response = openai.Image.create(
                        prompt=prompt,
                        n=1,
                        size="512x512"
                    )
                    break
                except:
                    print(f"***Error generating image for {role}, trying again.")
            image_url = response['data'][0]['url']
            print(image_url)
            responses["team"]["roles"][role]["image_url"] = image_url

    end_time = time.time()
    print(end_time)
    total_time_mins = (end_time - start_time)/60
    print(f"That took {total_time_mins} minutes.")
    return responses

@require_POST
def index(request):
    objective = request.POST.get('objective', "")
    context = {}

    if objective:
        context = generate_team(objective) or {}

    print(f"Rendering with this context: {context}")
    return TemplateResponse(request, "team.html", context)


def get(request):
    prompt = f"""
Reword these values while leaving the keys alone. Be as creative as you like. Brevity is the soul of wit.
{
"Title": "Teams Teams Teams!",
"Subtitle": "A tool for helping you accomplish a goal as a team with others.",
"Paragraph": "Teamwork makes the dream work. Use this tool to help you form a team of humans or get some boilerplate prompt language for your team of AI agents. The key is defining a small group of collaborative roles.",
"Intro": "This is your team. A possible version of it, anyway. Use the handbooks provided to kickstart discussion among human team members, or seed AI agents with context, or both. Then synchronize and execute in this dynamic and unpredictible world."
}"""
    context = {
            "Title": "Teams Teams Teams!",
            "Subtitle": "A tool for helping you accomplish a goal as a team with others.",
            "Paragraph": "Teamwork makes the dream work. Use this tool to help you form a team of humans or get some boilerplate prompt language for your team of AI agents. The key is defining a small group of collaborative roles.",
    }

    # todo - this would be fun but not for now
