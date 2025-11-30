import boto3

def read_file(file_name):
    with open(file_name, "r") as f:
        return f.read()

def get_context_list():
    return [
        "Prompt engineering basics",
        "Content creation",
        "Summarization",
        "Question and answer",
        "Translation",
        "Analysis: Positive email",
        "Analysis: Negative email",
        "Code",
        "Advanced techniques: Claude"
    ]

def get_context(lab):
    if lab == "Prompt engineering basics":
        return read_file("basics.txt")
    elif lab == "Summarization":
        return read_file("summarization_content.txt")
    elif lab == "Question and answer":
        return read_file("qa.txt")
    elif lab == "Analysis: Positive email":
        return read_file("analysis_positive.txt")
    elif lab == "Analysis: Negative email":
        return read_file("analysis_negative.txt")
    elif lab in ["Content creation", "Translation"]:
        return read_file("qa.txt")
    elif lab == "Code":
        return ""
    elif lab == "Advanced techniques: Claude":
        return read_file("summarization_content.txt")
    return ""

def get_prompt(template, context=None):
    if not template or not template.strip():
        return None
    if "{context}" in template and context:
        return template.format(context=context)
    return template

def get_text_response(model_id, temperature, template, context=None):
    session = boto3.Session()
    bedrock = session.client(service_name="bedrock-runtime")

    prompt = get_prompt(template, context)
    if not prompt:
        return "Error: Prompt text cannot be empty."

    message = {
        "role": "user",
        "content": [{"text": prompt}]
    }

    try:
        response = bedrock.converse(
            modelId=model_id,
            messages=[message],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": temperature,
                "topP": 0.9,
                "stopSequences": []
            },
        )
        return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        return f"Error calling Bedrock: {e}"
