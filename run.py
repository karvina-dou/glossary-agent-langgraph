from abbr_agent.agent import agent

def chat():
    print("This is an AI assistant for abbreviation detection.")
    print("Please type your text below to expand abbreviations. Enter 'exit' to quit.\n")
    
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        detect_result = agent.nodes.detect_abbr({"input_text": user_input})
        detected_abbr = detect_result["detected_abbr"]
        
        if not detected_abbr or detected_abbr == ["None"]:
            print("\nNo abbreviations detected.")
            print("Output:", user_input)
            continue
        
        process_state = {
            "input_text": user_input,
            "detected_abbr": detected_abbr,
            "process_text": user_input,
            "current_abbr": "",
            "expansions": [],
            "replacement": "",
            "abbr_expansions": {}
        }
        
        processed = agent.nodes.process_abbr(process_state)
        
        print("\nAbbreviation Expansions:")
        for abbr, exp in processed["abbr_expansions"].items():
            print(f"  {abbr} → {exp}")
        print("\nProcessed Text:")
        print(processed["process_text"])
        print("-" * 50)

if __name__ == "__main__":
    chat()