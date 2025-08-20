def load_system_prompt():
    try:
        with open("src/prompts/system_prompts.md","r") as f:
            return f.read()
    except FileNotFoundError:
        return None
    