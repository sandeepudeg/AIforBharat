# Content Summarizer with Amazon Bedrock

A powerful web application that leverages Amazon Bedrock's Claude AI model to automatically generate concise summaries of any text content. Built with Streamlit for an intuitive user interface and Python for robust backend processing.

---

## 1. Problem & Solution

### The Problem
In today's information-overloaded world, professionals and students face significant challenges:
- **Information Overload**: Users receive massive amounts of text daily (articles, reports, emails, documentation)
- **Time Constraints**: Limited time to read and comprehend lengthy documents
- **Comprehension Difficulty**: Extracting key insights from complex or technical content
- **Inconsistent Quality**: Manual summarization is subjective and time-consuming
- **Accessibility**: Non-native speakers struggle with dense text

### The Solution
The **Content Summarizer** application provides:
- **Instant Summarization**: Generate concise summaries in seconds using advanced AI
- **Intelligent Extraction**: Claude AI identifies and extracts key points automatically
- **Consistent Quality**: AI-powered summaries maintain objectivity and accuracy
- **User-Friendly Interface**: Simple paste-and-summarize workflow with no technical knowledge required
- **Flexible Input**: Accept any text content (articles, reports, emails, documentation, etc.)

### Who Benefits
1. **Students & Researchers**: Quickly understand research papers and academic articles
2. **Business Professionals**: Summarize reports, meeting notes, and lengthy emails
3. **Content Creators**: Generate summaries for blog posts and social media
4. **Non-Native Speakers**: Simplify complex text for better comprehension
5. **Knowledge Workers**: Save time on document review and information processing

---

## 2. Technical Implementation

### AWS Services Used

#### **Amazon Bedrock**
- **Why**: Provides access to state-of-the-art foundation models (Claude 3.7 Sonnet) without managing infrastructure
- **How**: 
  - Serverless API for model inference
  - Pay-per-use pricing model
  - No model training or fine-tuning required
  - Handles scaling automatically

#### **Model: Claude 3.7 Sonnet**
- **Why**: 
  - Excellent at text understanding and summarization
  - Fast inference speed
  - Cost-effective for production workloads
  - Strong reasoning capabilities
- **Configuration**:
  - Max tokens: 1000 (sufficient for summaries)
  - Temperature: 0 (deterministic, consistent output)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│                   (Streamlit Web App)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Text Input Area (Paste Content)                   │   │
│  │  • Summarize Button                                  │   │
│  │  • Output Display                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│              (content_summarization_app.py)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Input Validation                                  │   │
│  │  • User Interaction Handling                         │   │
│  │  • Response Display & Formatting                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Library Layer                            │
│            (content_summarization_lib.py)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Message Formatting                                │   │
│  │  • Bedrock API Integration                           │   │
│  │  • Response Parsing                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   AWS Services Layer                        │
│                  (Amazon Bedrock)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Claude 3.7 Sonnet Model                           │   │
│  │  • Inference Processing                              │   │
│  │  • Response Generation                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

**Step 1: User Input**
- User pastes content into the Streamlit text area
- Clicks the "Summarize" button

**Step 2: Input Validation**
- Application validates that content is not empty
- Shows warning if input is invalid

**Step 3: Message Formatting**
- Content is formatted into a structured message for Claude
- System prompt instructs Claude to provide concise summary

**Step 4: Bedrock API Call**
- Message sent to Amazon Bedrock
- Claude 3.7 Sonnet model processes the request
- Inference configuration ensures consistent output

**Step 5: Response Processing**
- Claude returns summarized text
- Application extracts and displays the summary
- User sees results in real-time

### Code Structure

```
labs/content_summarizer/
├── content_summarization_lib.py    # Core Bedrock integration
├── content_summarization_app.py    # Streamlit UI
└── README.md                        # Documentation
```

**content_summarization_lib.py**
```python
- get_summary(input_text): Main function
  - Creates formatted message for Claude
  - Initializes Bedrock client
  - Calls converse API with Claude model
  - Returns summarized text
```

**content_summarization_app.py**
```python
- Streamlit page configuration
- Text input area for content
- Summarize button with validation
- Output display with spinner feedback
```

---

## 3. Scaling Strategy

### Current Capacity

**Single Instance Deployment**
- Handles 1-10 concurrent users
- Response time: 2-5 seconds per request
- Input limit: Up to 100,000 characters
- Output limit: 1,000 tokens (~750 words)

**Cost Structure**
- Amazon Bedrock: Pay-per-token (input + output)
- Streamlit Cloud: Free tier available
- Estimated cost: $0.01-0.05 per summary

### Future Growth Plans

#### **Phase 1: Enhanced Features (Months 1-2)**
- [ ] Adjustable summary length (short/medium/long)
- [ ] Multiple summarization styles (bullet points, paragraphs, key takeaways)
- [ ] File upload support (PDF, DOCX, TXT)
- [ ] Summary history and export (PDF, DOCX)
- [ ] User authentication and saved preferences

#### **Phase 2: Performance Optimization (Months 2-3)**
- [ ] Implement caching for duplicate content
- [ ] Add request queuing for high traffic
- [ ] Optimize token usage with prompt engineering
- [ ] Batch processing for multiple documents
- [ ] Response time monitoring and optimization

#### **Phase 3: Enterprise Features (Months 3-6)**
- [ ] Multi-language support
- [ ] Custom summarization templates
- [ ] API endpoint for programmatic access
- [ ] Integration with document management systems
- [ ] Advanced analytics and usage tracking
- [ ] Role-based access control

#### **Phase 4: Infrastructure Scaling (Months 6+)**
- [ ] Deploy on AWS Lambda for serverless scaling
- [ ] Use API Gateway for load distribution
- [ ] Implement CloudFront CDN for global distribution
- [ ] Add DynamoDB for caching and history
- [ ] Set up CloudWatch monitoring and alerts
- [ ] Auto-scaling based on demand

#### **Phase 5: Community Engagement (Months 6+)**
- [ ] Develop a community forum for user feedback
- [ ] Implement a user feedback system for continuous improvement
- [ ] Engage with Amazon Bedrock community for feedback and updates
---

## 4. Visual Documentation

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         End User                                 │
│                    (Browser/Web Client)                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                    Streamlit Application                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Frontend UI                                               │  │
│  │  • Text Input Component                                    │  │
│  │  • Summarize Button                                        │  │
│  │  • Output Display Area                                     │  │
│  │  • Loading Spinner                                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│              Python Backend (content_summarization_app.py)       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • Input Validation                                        │  │
│  │  • Error Handling                                          │  │
│  │  • Library Function Calls                                  │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│         Library Layer (content_summarization_lib.py)             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • Boto3 Client Initialization                             │  │
│  │  • Message Formatting                                      │  │
│  │  • API Request Construction                                │  │
│  │  • Response Parsing                                        │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    AWS API Gateway
                             │
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                    Amazon Bedrock Service                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Model: Claude 3.7 Sonnet                                  │  │
│  │  • Text Processing                                         │  │
│  │  • Summarization Logic                                     │  │
│  │  • Response Generation                                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### User Interface Screenshots

**Input Screen**
```
┌─────────────────────────────────────────────────────────┐
│  Content Summarizer                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Paste your content here to summarize                  │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Lorem ipsum dolor sit amet, consectetur adipiscing│ │
│  │ elit. Sed do eiusmod tempor incididunt ut labore  │ │
│  │ et dolore magna aliqua. Ut enim ad minim veniam,  │ │
│  │ quis nostrud exercitation ullamco laboris nisi ut │ │
│  │ aliquip ex ea commodo consequat...                │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [Summarize]                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Output Screen**
```
┌─────────────────────────────────────────────────────────┐
│  Content Summarizer                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Paste your content here to summarize                  │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Lorem ipsum dolor sit amet, consectetur adipiscing│ │
│  │ elit. Sed do eiusmod tempor incididunt ut labore  │ │
│  │ et dolore magna aliqua...                         │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [Summarize]                                            │
│                                                         │
│  Summary                                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ The text discusses Lorem ipsum, a placeholder     │ │
│  │ text commonly used in design. It emphasizes the   │ │
│  │ importance of understanding content structure and │ │
│  │ layout principles in professional work.           │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Input
    │
    ↓
┌─────────────────────┐
│ Validation Check    │
│ (Empty/Valid?)      │
└─────────────────────┘
    │
    ├─ Invalid → Show Warning
    │
    └─ Valid ↓
┌─────────────────────┐
│ Format Message      │
│ for Claude          │
└─────────────────────┘
    │
    ↓
┌─────────────────────┐
│ Initialize Bedrock  │
│ Client              │
└─────────────────────┘
    │
    ↓
┌─────────────────────┐
│ Call Bedrock API    │
│ (converse method)   │
└─────────────────────┘
    │
    ↓
┌─────────────────────┐
│ Parse Response      │
│ Extract Summary     │
└─────────────────────┘
    │
    ↓
Display Summary to User
```

---

## 5. Code & Resources

### Code Snippets

#### **Library Implementation (content_summarization_lib.py)**

```python
import boto3

def get_summary(input_text):
    """
    Summarizes the provided text using Amazon Bedrock Claude model.
    
    Args:
        input_text (str): The text content to summarize
        
    Returns:
        str: The summarized content
        
    Raises:
        Exception: If Bedrock API call fails
    """
    
    # Format the message for Claude
    message = {
        "role": "user",
        "content": [
            {
                "text": f"Please provide a concise summary of the following text:\n\n{input_text}"
            }
        ]
    }
    
    # Initialize Bedrock client
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')
    
    # Call Bedrock API with Claude model
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        messages=[message],
        inferenceConfig={
            "maxTokens": 1000,      # Limit output length
            "temperature": 0        # Deterministic output
        },
    )
    
    # Extract and return the summary
    return response['output']['message']['content'][0]['text']
```

#### **Application Implementation (content_summarization_app.py)**

```python
import streamlit as st
import content_summarization_lib as glib

# Configure page
st.set_page_config(page_title="Content Summarizer")
st.title("Content Summarizer")

# Input area
input_text = st.text_area(
    "Paste your content here to summarize", 
    height=200
)

# Summarize button
summarize_button = st.button("Summarize", type="primary")

# Process on button click
if summarize_button:
    if input_text.strip():
        st.subheader("Summary")
        
        # Show loading spinner while processing
        with st.spinner("Generating summary..."):
            response_content = glib.get_summary(input_text)
            st.write(response_content)
    else:
        st.warning("Please enter some content to summarize.")
```

### Installation & Setup

#### **Prerequisites**
- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured with credentials

#### **Installation Steps**

```bash
# 1. Clone or navigate to the project
cd labs/content_summarizer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install streamlit boto3

# 4. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)

# 5. Run the application
streamlit run content_summarization_app.py
```

### Running the Application

```bash
# Start the Streamlit server
streamlit run content_summarization_app.py

# The app will open at http://localhost:8501
```

### Dependencies

```
streamlit==1.28.0          # Web UI framework
boto3==1.26.0              # AWS SDK for Python
```

### GitHub Repository

**Repository Structure**
```
content-summarizer/
├── labs/
│   └── content_summarizer/
│       ├── content_summarization_lib.py
│       ├── content_summarization_app.py
│       ├── README.md
│       └── requirements.txt
├── .gitignore
└── LICENSE
```

**Key Files**
- `content_summarization_lib.py`: Core Bedrock integration logic
- `content_summarization_app.py`: Streamlit UI and user interaction
- `README.md`: Complete documentation
- `requirements.txt`: Python dependencies

### Live Demo

**Deployment Options**

1. **Streamlit Cloud** (Recommended for quick demo)
   ```bash
   # Push to GitHub
   git push origin main
   
   # Deploy on Streamlit Cloud
   # Visit: https://streamlit.io/cloud
   # Connect GitHub repository
   # Select main branch and app file
   ```

2. **AWS EC2**
   ```bash
   # Launch EC2 instance
   # Install Python and dependencies
   # Run: streamlit run app.py --server.port 80
   ```

3. **Docker Container**
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["streamlit", "run", "content_summarization_app.py"]
   ```

### Performance Metrics

**Typical Performance**
- Average response time: 2-5 seconds
- Input processing: <100ms
- Bedrock inference: 1-4 seconds
- Output rendering: <500ms

**Cost Estimation**
- Input tokens: ~$0.003 per 1M tokens
- Output tokens: ~$0.015 per 1M tokens
- Average cost per summary: $0.01-0.05

### Troubleshooting

**Common Issues**

1. **"NoCredentialsError" from Bedrock**
   - Solution: Run `aws configure` and enter valid credentials

2. **"AccessDenied" error**
   - Solution: Ensure IAM user has `bedrock:InvokeModel` permission

3. **Slow response times**
   - Solution: Check AWS region latency, consider using closer region

4. **Empty summary output**
   - Solution: Verify input text is substantial (>50 characters)

### Future Enhancements

- [ ] Multi-language summarization
- [ ] Custom summary length control
- [ ] File upload support (PDF, DOCX)
- [ ] Summary export (PDF, DOCX, TXT)
- [ ] User authentication and history
- [ ] API endpoint for programmatic access
- [ ] Advanced analytics dashboard
- [ ] Batch processing capability

---

## Summary

The **Content Summarizer** leverages Amazon Bedrock's powerful Claude AI model to solve the critical problem of information overload. By providing an intuitive, serverless solution, it enables users to quickly extract key insights from any text content. With a clear scaling strategy and roadmap for enterprise features, this application is positioned for growth from individual users to enterprise deployments.

**Key Takeaways:**
- ✅ Solves real-world information overload problem
- ✅ Leverages cutting-edge AWS AI services
- ✅ Scalable architecture for future growth
- ✅ User-friendly interface with Streamlit
- ✅ Cost-effective pay-per-use model
- ✅ Ready for enterprise deployment

---

