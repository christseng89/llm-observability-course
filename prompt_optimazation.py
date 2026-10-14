def optimize_prompt(prompt: str) -> str:
    """
    Apply common prompt optimizations.

    NOT a replacement for manual review - just catches obvious bloat.
    """

    # Remove common filler phrases
    fillers = [
        "I want you to",
        "You are a highly intelligent",
        "Please note that",
        "It's important to remember that",
        "In your response, make sure to",
        "As an AI assistant,",
    ]

    result = prompt
    for filler in fillers:
        result = result.replace(filler, "")

    # Remove excessive whitespace
    result = " ".join(result.split())

    # Remove repeated instructions
    lines = result.split(".")
    seen = set()
    unique_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            sentence = line.strip()
            unique_lines.append(sentence[0].upper() + sentence[1:])

    optimized = ". ".join(unique_lines).rstrip(".")
    return optimized + "." if optimized else optimized


if __name__ == "__main__":
    # Example usage
    original_prompt = """
    I want you to act as a prompt optimizer. You are a highly intelligent AI assistant. 
    Please note that your task is to improve the clarity and conciseness of prompts. 
    It's important to remember that the goal is to make prompts more effective. 
    In your response, make sure to provide clear instructions. 
    As an AI assistant, you should also consider the context of the prompt.
    """

    optimized_prompt = optimize_prompt(original_prompt)
    print("\033[92mOriginal Prompt:\033[0m")
    print(original_prompt)
    print("\033[93m\nOptimized Prompt:\033[0m")
    print(optimized_prompt)
