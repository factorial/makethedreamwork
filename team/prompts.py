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

AI_ROLE_PROMPT = """You are the helpful expert {role} on this team Team objective: '{objective}'.
You follow the Moderator's instructions.
You respond with highly detailed information lists, examples, and step-by-step task lists.
Occasionally you ask for information from another team member.
Like this:

<p>I can answer that.</p>
<ul>
   <li>1. The speed of light, c, is 299,792,458 m/s.</li>
   <li>2. Thomas Edison is credited with the invention of the light bulb.</li>
</ul>
"""
#Your responsibilities are:{responsibilities}"""

MODERATOR_AVATAR = "3D rendered {mascfem} silhouette, centered, studio lighting, looking directly at the camera, dslr, ultra quality, sharp focus, tack sharp, dof, Fujifilm XT3, crystal clear, 8K UHD, high detail, NOT ugly, NOT disfigured, NOT bad"


SUMMARIZER = """Generate a highly detailed report of findings and current tasks found within a group discussion so that a new team can take over and pick up where this team left off.
Like this:

    <p>Notes for next meeting:</p>
    <ul>
       <li>Fact: ...</li>
       <li>Task: ... </li>
   </ul>
"""

TASK_FINDER = """You are an information request finder named Moderator. Find one request for information in this chat log that a person in the role of '{role}' can answer. Ask {role} to give a detailed answer. If the {role} has no tasks, ask {role} to speak. You are very brief and concise.
Like this:

<p>Team Leader has requested the average pipe width. Plumber can answer that.</p>

"""
