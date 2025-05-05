from llama_cpp import Llama

def main():
    # Prompt user for the path to the .gguf model
    model_path = "D:\mistral-7b-instruct-v0.1.Q4_K_M (1).gguf"
    # Load the model
    llm = Llama(model_path=model_path, n_ctx=4096)

    # Get user input for the conspiracy topic
    topic = input("Enter the topic for the ASMR conspiracy: ")

    # Build the ASMR-style prompt
    prompt = f"""

Write a fictional story that explores a long-buried conspiracy surrounding {topic}.

The narrative should feel atmospheric and immersive, gradually uncovering chilling secrets hidden from the public eye. Use vivid sensory descriptions to evoke a sense of mystery and unease—abandoned corridors, flickering lights, classified documents, and forgotten witnesses.

Incorporate elements like:

Hidden files and cryptic notes

Shadowy figures or secret organizations

Anonymous sources or whistleblowers

Suppressed evidence or erased records

Strange sounds, encrypted messages, or unexplainable events

Structure the story to build suspense, with each reveal deepening the reader’s sense that something vast and sinister lies just beneath the surface.

End with a haunting twist or unresolved question that leaves the reader wondering what’s real… and what’s been kept from them.


"""

    # Generate the script
    output = llm(
        prompt,
        max_tokens=4000,
        temperature=0.8,
        top_p=0.95,
        stop=None
    )
    generated_script = output["choices"][0]["text"].strip()

    # Save to a .txt file
    filename = f"asmr_conspiracy_{topic.replace(' ', '_').lower()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(generated_script)
    print(f"ASMR script saved to {filename}")

if __name__ == "__main__":
    main()
