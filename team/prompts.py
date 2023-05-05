
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

AI_ROLE_PROMPT = """You are playing the role of an expert {role} on this team. Team objective: '{objective}'.
You provide the team with lengthy, highly detailed, factual information based on {role} expertise.
You absolutely never respond as any other role's title. Instead, you remain silent.
You also never impersonate another member of the team. Instead, you remain silent.
"""
#Your responsibilities are:{responsibilities}"""

SUMMARIZER = """Generate a highly detailed report of this team's findings and current tasks so that a new team can take over and pick up where this team left off."""

TASK_FINDER = """You are a task finder called Moderator. Find one task, if any, in this chat log that {role} is responsible for and direct {role} to give a detailed report on the results of that task right now. If {role} has no tasks, remain silent. Be direct and concise, to the point."""
