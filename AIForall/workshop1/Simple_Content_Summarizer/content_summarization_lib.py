import boto3

def get_summary(input_text):
    """
    Summarizes the provided text using Amazon Bedrock Claude model.
    
    Args:
        input_text (str): The text content to summarize
        
    Returns:
        str: The summarized content
    """
    
    message = {
        "role": "user",
        "content": [
            {
                "text": f"Please provide a concise summary of the following text:\n\n{input_text}"
            }
        ]
    }
    
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')
    
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=[message],
        inferenceConfig={
            "maxTokens": 1000,
            "temperature": 0
        },
    )
    
    return response['output']['message']['content'][0]['text']
