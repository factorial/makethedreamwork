
CHECK_OFFENSE = 'Yes or no: is the following objective offensive or inappropriate: "{OBJECTIVE}"? Answer with only yes or no.'

DEFINE_TEAM = """
OBJECTIVE: {objective}
TASK: Write instructions for a team of humans to execute. Respond with a JSON object whose keys are
unique role names on the team and each key contains a task list for that unique role.
RESPONSE (JSON format only):"""

LIST_ROLES = "{context} List the roles on this team as a JavaScript array of strings. RESULT:["

JAVASCRIPT_ERROR = "{context} That was not valid JavaScript array syntax. Try again:\n"

NEW_MEMBER_QUESTIONS = """{context}
You are a new member on this team, assuming the role of {role}. List the questions you want to ask an
expert in this role so they can give you the answers that will make you successful at your tasks and able to
effectively collaborate toward the real-world objective: {objective}."""

GENERATE_HANDBOOK = """{context}
You are an expert in the role of {role} on this team. Generate a handbook for the new member in this
role using Markdown format. In it, answer the new member's specific questions in depth.
Also include in the handbook a guide which describes step-by-step a typical day in the life of a person in this role
on this team."""
    
AVATAR_FROM_CITY = "3D rendered cartoon avatar of {mascfem} {add} {role} from {city}, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

AVATAR = "3D rendered cartoon avatar of {mascfem} person, highlight hair, centered, studio lighting, looking at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, highly detailed glossy eyes, high detailed skin, skin pores, international, NOT ugly, NOT disfigured, NOT bad"

AI_ROLE_PROMPT = """You are an expert information-provider in the role of {role} on this team. Team objective: '{objective}'.
You have conducted all your necessary research.
You provide a detailed and factual response to a question, or you request information from another team member, or remain silent.
You must answer factually and in detail from your own expertise.
You require a human to do real-world tasks for you, but you can provide detailed instructions.
You ABSOLUTELY NEVER respond with another role's title. Instead, you stop responding.
You MUST NEVER impersonate another member of the team. Instead, you stop responding."""
#Your responsibilities are:{responsibilities}"""

SUMMARIZER = """Produce a list of detailed items that were stated as a fact and a list of tasks the team is executing.
{ending_message}
"""
# Ideas:
#summary_system_prompt = """You summarize a chat log into a project status recap. The recap always lists the top 5 tasks the team is working on as a todo list with assignees and the most important data points per task."""
#summary_system_prompt = f"""You summarize a chat log into a brief project status recap. The recap includes two short sections: * Answers to the important questions so far * the top 5 currently incomplete tasks the team is working on as a todo list with assignees """
#summary_system_prompt = """You summarize a meeting log into a list of precisely what actions each team member will take before the next meeting and factoids discovered by the team."""
