# With Function tool
from agents import function_tool

# Setup Semantic Search Tool
userDB = [{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "notes": "John Doe is a software engineer at Google"
}, {
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "notes": "Jane Smith is a software engineer at Apple"
}]

@function_tool
def find_user(name):
    print(f"2. Searching: {name}")
    for user in userDB:
        if user["name"].lower() == name.lower():
            return str(user)
    return f"No user of {name} found"

# find_user_json = {
#     "name": "find_user",
#     "description": "Always use this tool to find a user in the user database",
#     "parameters": {
#         "type": "object",
#         "properties": {"name": {"type": "string", "description": "The name of the user to find"}},
#         "required": ["name"],
#         "additionalProperties": False
#     }
# }