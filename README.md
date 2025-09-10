# alt-text-generator

Langgraph based Multi-agent project for generating alt-text.
It contains multiple agents:
- Complexity Analysis Agent: Categorizes the input content by complexity (Simple, Moderate, Complex).
- Alt-Text Generation Agent: Generates alt-text tailored to the complexity level.
- Evaluation & Feedback Agent: That takes the Subject Matter Experts (SMEs) review and correct the generated alt-text to ensure quality and compliance.

This project is structured into Backed/ Langgraph workflow and Streamlit based UI for demonstration
- alt-text-workflow
- alt-text-ui

![Alt text](./images/ui.png)

# Backend setup for Agent core runtime

### Prerequisite
- Python 3
- AWS CLI set up for pushing project Agent Core Runtime

### We will be using N. Virginia(us-east-1) region as per Agent Core runtime is currently availablity. 

## To use Amazon Bedrock and models, you need both a **Bedrock API Key** and a **Model ID**.

### Amazon Bedrock Key
1. Go to the **Amazon Bedrock**.  
2. Navigate to **API Keys** under **Discover**.  
3. Generate a new key:  
   - **Long-term** → for production or repeated use.  

### Model Key
1. In the **Amazon Bedrock**, go to **Model Catalogue**.  
2. Select the model you want to use.  
3. Go to **Model Access** and click **Request Access**.  
4. Once your request is approved, you will see the model’s **Inference ID** under **Cross-region inference**.  
5. Use this **Inference profile ID** as your **model key** when calling the API.


### Configure AWS CLI with your credentials:
Credhelper extension: https://chromewebstore.google.com/detail/cloudkeeper-credential-he/mpljkpamdjfdjmfcpnlmhhakbjigjjcd?hl=en-US&pli=1
- Copy aws creds
- Open a terminal and paste the cred 
```bash
cd ~/.aws
vim credentials
```
- Also provide **region=use-east-1*** in the cred file

### Refer to alt-text-workflow's readme to push image to Agent Core Runtime