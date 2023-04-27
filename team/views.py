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

fake_response = {'team': {'objective': 'Buy legal marijuana', 'description': '{\n  "Team Leader": [\n    "Research the legal requirements for purchasing marijuana in your state/country",\n    "Identify licensed dispensaries in your area",\n    "Create a budget for the purchase"\n  ],\n  "Purchasing Agent": [\n    "Visit the licensed dispensary",\n    "Present identification to prove legal age and residency",\n    "Select the desired strain and quantity of marijuana",\n    "Pay for the purchase using the allocated budget"\n  ],\n  "Transportation Coordinator": [\n    "Arrange for transportation of the purchased marijuana to the designated location",\n    "Ensure that the transportation method complies with legal requirements",\n    "Track the delivery to ensure it arrives safely"\n  ],\n  "Security Officer": [\n    "Ensure that the purchasing agent and transportation coordinator are safe during the transaction",\n    "Monitor the transportation of the marijuana to ensure it is not stolen or lost",\n    "Ensure that the marijuana is stored securely at the designated location"\n  ]\n}', 'roles': {'Team Leader': {'questions': '1. What are the specific legal requirements for purchasing marijuana in our state/country?\n2. How do we ensure that the licensed dispensaries we identify are reputable and trustworthy?\n3. What factors should we consider when creating a budget for the purchase?\n4. Are there any specific forms of identification that the purchasing agent should bring to the dispensary?\n5. What are the legal requirements for transporting marijuana in our state/country?\n6. How can we ensure the safety of the purchasing agent and transportation coordinator during the transaction?\n7. What measures should we take to ensure the marijuana is stored securely at the designated location?', 'guide': "# Team Leader Handbook\n\nWelcome to the role of Team Leader on our team! As the Team Leader, your main responsibilities will be to research the legal requirements for purchasing marijuana in our state/country, identify licensed dispensaries in our area, and create a budget for the purchase. Here are some answers to your specific questions:\n\n1. What are the specific legal requirements for purchasing marijuana in our state/country?\n   - The legal requirements for purchasing marijuana vary by state and country. In our state/country, you will need to be of legal age and have a valid form of identification to purchase marijuana. You should research the specific laws and regulations in our area to ensure that we are in compliance.\n\n2. How do we ensure that the licensed dispensaries we identify are reputable and trustworthy?\n   - You can research licensed dispensaries in our area by checking online reviews and ratings, asking for recommendations from friends or acquaintances who have purchased from dispensaries before, and checking with local authorities to ensure that the dispensary is licensed and in good standing.\n\n3. What factors should we consider when creating a budget for the purchase?\n   - When creating a budget for the purchase, you should consider the quantity and quality of the marijuana we want to purchase, the prices at different dispensaries, and any additional costs such as taxes or delivery fees.\n\n4. Are there any specific forms of identification that the purchasing agent should bring to the dispensary?\n   - The specific forms of identification required to purchase marijuana vary by state and country. In our area, a valid government-issued ID such as a driver's license or passport should be sufficient.\n\n5. What are the legal requirements for transporting marijuana in our state/country?\n   - The legal requirements for transporting marijuana vary by state and country. In our area, it is important to ensure that the transportation method complies with all applicable laws and regulations, such as keeping the marijuana in a sealed container and not transporting it across state lines.\n\n6. How can we ensure the safety of the purchasing agent and transportation coordinator during the transaction?\n   - To ensure the safety of the purchasing agent and transportation coordinator, it is important to choose a reputable and trustworthy dispensary, arrange for transportation in a safe and legal manner, and have a security officer present during the transaction.\n\n7. What measures should we take to ensure the marijuana is stored securely at the designated location?\n   - To ensure the marijuana is stored securely at the designated location, it should be kept in a locked container or safe, and only accessible to authorized personnel.\n\n## Typical Workday Guide\n\nAs the Team Leader, a typical workday may include:\n\n1. Researching the legal requirements for purchasing marijuana in our state/country.\n2. Identifying licensed dispensaries in our area and checking their reputations.\n3. Creating a budget for the purchase.\n4. Communicating with the Purchasing Agent to ensure they have the necessary identification and are prepared for the transaction.\n5. Communicating with the Transportation Coordinator to arrange for safe and legal transportation of the marijuana.\n6. Communicating with the Security Officer to ensure their presence during the transaction.\n7. Ensuring that the marijuana is stored securely at the designated location.\n\nRemember to communicate effectively with all members of the team and prioritize safety and compliance with all applicable laws and regulations. Good luck!", 'tasks': ['Research the legal requirements for purchasing marijuana in your state/country', 'Identify licensed dispensaries in your area', 'Create a budget for the purchase'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-L2npLZGwXElnbpJAncrA5qKh.png?st=2023-04-27T01%3A46%3A54Z&se=2023-04-27T03%3A46%3A54Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T02%3A37%3A17Z&ske=2023-04-28T02%3A37%3A17Z&sks=b&skv=2021-08-06&sig=LKKpeEstuQbgwW6kYKy1uZoKHFymPihw62SpyI7rATg%3D'}, 'Purchasing Agent': {'questions': '1. What are the legal requirements for purchasing marijuana in our state/country?\n2. What forms of identification do I need to prove legal age and residency at the licensed dispensary?\n3. How do I select the desired strain and quantity of marijuana?\n4. What is the allocated budget for the purchase?\n5. Are there any restrictions on the transportation method for the purchased marijuana?\n6. How do I ensure the safety of myself and the transportation coordinator during the transaction?\n7. How do I monitor the transportation of the marijuana to ensure it is not stolen or lost?\n8. What are the requirements for storing the marijuana securely at the designated location?', 'guide': "# Purchasing Agent Handbook\n\nWelcome to the team as a Purchasing Agent! Your role is crucial in ensuring that we are able to successfully buy legal marijuana. Here are some answers to your specific questions:\n\n1. What are the legal requirements for purchasing marijuana in our state/country?\n   - The legal requirements for purchasing marijuana vary by state and country. It is important to research and understand the specific laws and regulations in your area before making any purchases.\n\n2. What forms of identification do I need to prove legal age and residency at the licensed dispensary?\n   - Typically, a government-issued ID such as a driver's license or passport is required to prove legal age and residency at a licensed dispensary.\n\n3. How do I select the desired strain and quantity of marijuana?\n   - The licensed dispensary will have a variety of strains and quantities available. It is important to research and understand the different strains and their effects before making a selection. The dispensary staff can also provide guidance and recommendations.\n\n4. What is the allocated budget for the purchase?\n   - The Team Leader will provide you with the allocated budget for the purchase. It is important to stay within this budget to ensure that we are able to successfully complete the objective.\n\n5. Are there any restrictions on the transportation method for the purchased marijuana?\n   - Yes, there may be restrictions on the transportation method for the purchased marijuana depending on the specific laws and regulations in your area. It is important to research and understand these restrictions before arranging for transportation.\n\n6. How do I ensure the safety of myself and the transportation coordinator during the transaction?\n   - It is important to arrange for the transaction to take place in a safe and secure location. The Security Officer can provide guidance and support in ensuring the safety of everyone involved.\n\n7. How do I monitor the transportation of the marijuana to ensure it is not stolen or lost?\n   - The Transportation Coordinator will be responsible for tracking the delivery and ensuring that it arrives safely. It is important to communicate with the Transportation Coordinator and provide any necessary support.\n\n8. What are the requirements for storing the marijuana securely at the designated location?\n   - The Security Officer can provide guidance on the specific requirements for storing the marijuana securely at the designated location. It is important to follow these requirements to ensure the safety and security of the purchased marijuana.\n\n## Typical Workday Guide\n\nAs a Purchasing Agent, a typical workday may include the following steps:\n\n1. Research the legal requirements for purchasing marijuana in your state/country.\n2. Identify licensed dispensaries in your area.\n3. Communicate with the Team Leader to determine the allocated budget for the purchase.\n4. Visit the licensed dispensary and present identification to prove legal age and residency.\n5. Select the desired strain and quantity of marijuana within the allocated budget.\n6. Pay for the purchase using the allocated budget.\n7. Communicate with the Transportation Coordinator to arrange for transportation of the purchased marijuana to the designated location.\n8. Ensure that the transportation method complies with legal requirements.\n9. Communicate with the Security Officer to ensure the safety of everyone involved in the transaction.\n10. Monitor the transportation of the marijuana to ensure it arrives safely.\n11. Ensure that the marijuana is stored securely at the designated location.\n\nRemember to communicate with the rest of the team and ask for support or guidance whenever necessary. Good luck and have a successful workday!", 'tasks': ['Visit the licensed dispensary', 'Present identification to prove legal age and residency', 'Select the desired strain and quantity of marijuana', 'Pay for the purchase using the allocated budget'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-FPcSMCTUI2KE1ogPjM8dnSFm.png?st=2023-04-27T01%3A48%3A16Z&se=2023-04-27T03%3A48%3A16Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T02%3A45%3A52Z&ske=2023-04-28T02%3A45%3A52Z&sks=b&skv=2021-08-06&sig=gXfu8pPG6ERM%2BT72nlDSRquHyJsAqEL1LwsNjRjIIyo%3D'}, 'Transportation Coordinator': {'questions': '1. What are the legal requirements for transporting marijuana in our state/country?\n2. What transportation methods are allowed for transporting marijuana?\n3. Are there any specific regulations or permits required for transporting marijuana?\n4. How do we ensure the safety and security of the marijuana during transportation?\n5. How do we track the delivery of the marijuana to ensure it arrives safely?\n6. What should we do in case of any unforeseen circumstances during transportation?', 'guide': "# Transportation Coordinator Handbook\n\nWelcome to the team as the Transportation Coordinator! Your role is crucial in ensuring that the purchased marijuana is safely transported to the designated location. Here are some answers to your questions:\n\n## Legal Requirements for Transporting Marijuana\n\nThe legal requirements for transporting marijuana vary by state and country. It is important to research and understand the specific regulations in your area. Generally, marijuana must be transported in a sealed, odor-proof container and kept out of reach of the driver and passengers.\n\n## Allowed Transportation Methods for Marijuana\n\nThe allowed transportation methods for marijuana also vary by state and country. Some common methods include personal vehicles, delivery services, and courier services. It is important to ensure that the chosen method complies with legal requirements and that the marijuana is transported safely and securely.\n\n## Regulations and Permits for Transporting Marijuana\n\nSome states and countries require specific regulations and permits for transporting marijuana. It is important to research and understand these requirements and obtain any necessary permits before transporting the marijuana.\n\n## Safety and Security of Marijuana During Transportation\n\nEnsuring the safety and security of the marijuana during transportation is crucial. It is important to use a secure transportation method and keep the marijuana out of sight and reach of others. Additionally, it is important to track the delivery and monitor the transportation to ensure that the marijuana is not stolen or lost.\n\n## Tracking Delivery of Marijuana\n\nTracking the delivery of the marijuana is important to ensure that it arrives safely at the designated location. This can be done through various methods such as GPS tracking or regular check-ins with the driver.\n\n## Unforeseen Circumstances During Transportation\n\nIn case of any unforeseen circumstances during transportation, it is important to have a plan in place. This can include having a backup transportation method or contacting the appropriate authorities if necessary.\n\n## Typical Workday Guide\n\nAs the Transportation Coordinator, a typical workday may include the following steps:\n\n1. Confirm the pickup and delivery locations with the Purchasing Agent.\n2. Research and understand the legal requirements and regulations for transporting marijuana in your area.\n3. Choose a secure and legal transportation method.\n4. Ensure that the marijuana is securely packaged and stored in a sealed, odor-proof container.\n5. Track the delivery of the marijuana to ensure that it arrives safely at the designated location.\n6. Monitor the transportation to ensure that the marijuana is not stolen or lost.\n7. Communicate with the Security Officer to ensure that the marijuana is stored securely at the designated location.\n\nRemember to always prioritize safety and security when transporting marijuana. If you have any questions or concerns, don't hesitate to reach out to the team for support. Good luck!", 'tasks': ['Arrange for transportation of the purchased marijuana to the designated location', 'Ensure that the transportation method complies with legal requirements', 'Track the delivery to ensure it arrives safely'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-WJ6EwIsz3uPbqpcL7vKeEl9v.png?st=2023-04-27T01%3A49%3A22Z&se=2023-04-27T03%3A49%3A22Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T02%3A45%3A27Z&ske=2023-04-28T02%3A45%3A27Z&sks=b&skv=2021-08-06&sig=4Bka86jDtO4rMDULaEQ9ekUSy2RdV3avCplFjwE8nuA%3D'}, 'Security Officer': {'questions': '1. What are the legal requirements for transporting marijuana in our state/country?\n2. What measures should I take to ensure the safety of the purchasing agent and transportation coordinator during the transaction?\n3. What are the potential risks involved in transporting marijuana, and how can we mitigate them?\n4. How should I store the marijuana securely at the designated location?\n5. What should I do in case of an emergency or unexpected situation during the transportation or storage of the marijuana?', 'guide': "# Security Officer Handbook\n\nWelcome to the team as the Security Officer! Your role is crucial in ensuring the safety and security of the purchasing agent, transportation coordinator, and the marijuana during the transaction and transportation process. Here are some answers to your questions:\n\n## Legal Requirements for Transporting Marijuana\n\nThe legal requirements for transporting marijuana vary by state and country. It is important to research and understand the specific laws and regulations in your area. Generally, marijuana must be transported in a secure and locked container, and the transportation method must comply with all applicable laws and regulations.\n\n## Ensuring Safety of Purchasing Agent and Transportation Coordinator\n\nTo ensure the safety of the purchasing agent and transportation coordinator during the transaction, it is important to:\n\n- Choose a licensed dispensary with a good reputation\n- Meet in a public and well-lit area\n- Have a plan in case of an emergency or unexpected situation\n- Communicate regularly with the transportation coordinator to ensure their safety during transportation\n\n## Potential Risks and Mitigation Strategies\n\nThe potential risks involved in transporting marijuana include theft, loss, and damage. To mitigate these risks, it is important to:\n\n- Use a secure and locked container for transportation\n- Choose a reliable and trustworthy transportation method\n- Track the delivery to ensure it arrives safely\n- Have a backup plan in case of unexpected situations\n\n## Secure Storage of Marijuana\n\nTo store the marijuana securely at the designated location, it is important to:\n\n- Use a secure and locked container\n- Store the container in a safe and secure location\n- Limit access to the container to authorized personnel only\n\n## Emergency and Unexpected Situations\n\nIn case of an emergency or unexpected situation during the transportation or storage of the marijuana, it is important to:\n\n- Have a plan in place for different scenarios\n- Communicate with the team and relevant authorities as necessary\n- Follow all applicable laws and regulations\n\n## Typical Workday\n\nAs the Security Officer, a typical workday may include:\n\n- Reviewing the transportation plan and ensuring it complies with legal requirements\n- Communicating with the transportation coordinator to ensure their safety during transportation\n- Monitoring the transportation of the marijuana to ensure it arrives safely\n- Ensuring the marijuana is stored securely at the designated location\n- Conducting regular security checks to ensure the safety of the marijuana and personnel involved in the transaction and transportation process\n\nRemember, your role is crucial in ensuring the success of the team's objective to buy legal marijuana. If you have any questions or concerns, don't hesitate to communicate with the team and relevant authorities. Good luck!", 'tasks': ['Ensure that the purchasing agent and transportation coordinator are safe during the transaction', 'Monitor the transportation of the marijuana to ensure it is not stolen or lost', 'Ensure that the marijuana is stored securely at the designated location'], 'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-HjKdGLcSGTCfPFyh0qOtUTFN/user-3FEZp99GmcMlz7tVnqTRTZID/img-aiHQUpi61HISZkBKZv0JHJ4U.png?st=2023-04-27T01%3A50%3A26Z&se=2023-04-27T03%3A50%3A26Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-04-27T02%3A34%3A06Z&ske=2023-04-28T02%3A34%3A06Z&sks=b&skv=2021-08-06&sig=kNvTVVT5AepG%2BQg6m4hTDfDlhlG1J478WBVyevgBhdU%3D'}}}}

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
    if 'yes' in result.lower().strip():
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
            prompt = f"3D rendered cartoon avatar of {role}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT ugly, NOT bad"

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
