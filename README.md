# alt-text-generator
Langgraph based GenAI project for generating alt-text

# Project Setup

## Test Environment Setup

Follow the steps below to set up and run the project:

### 1. Create a virtual environment
```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment
- **On macOS/Linux**
  ```bash
  source .venv/bin/activate
  ```
- **On Windows**
  ```bash
  venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the project
```bash
python3 test.py
```


# Project Setup

## Test Environment Setup

Follow the steps below to set up and run the project:

### 1. Create a virtual environment
```bash
python -m venv venv
```

### 2. Activate the virtual environment
- **On macOS/Linux**
  ```bash
  source venv/bin/activate
  ```
- **On Windows**
  ```bash
  venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the project
```bash
python text.py
```

---

## Run on Amazon Bedrock Core Runtime

Follow these steps to containerize and push your project to AWS:

### 1. Set up AWS CLI
1. Install AWS CLI (v2 recommended):  
   [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
   
2. Configure AWS CLI with your credentials:
```bash
aws configure
```
   Provide:
   - AWS Access Key ID  
   - AWS Secret Access Key  
   - Default region (e.g., `us-east-1`)  
   - Output format (`json`, `text`, or `table`)  

3. Verify configuration:
```bash
aws sts get-caller-identity
```

### 2. Create an Access Key
1. Log in to the **AWS Management Console**.  
2. Navigate to **IAM → Users → Your User → Security Credentials**.  
3. Under **Access keys**, click **Create access key**.  
4. Download the key file or copy the Access Key ID and Secret Access Key.  
   *(Use these when running `aws configure`.)*

### 3. Authenticate Docker with ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ecr-image-repository
```

Replace **`ecr-image-repository`** with your actual Amazon ECR registry URI, e.g.:  
```
123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### 4. Build and Push Docker Image (ARM64)
```bash
docker buildx build \
  --platform linux/arm64 \
  -t ecr-image-repository/agent-core/alt-text:latest \
  --push .
```

- `--platform linux/arm64` → ensures compatibility with AWS Graviton/Bedrock runtime  
- `-t` → tags the image with your ECR repo name and project identifier  
- `--push` → pushes the image directly to ECR  

---

✅ Once pushed, you can use this image in Amazon Bedrock Core Runtime or ECS task definitions.


### 5. Host on Amazon Bedrock Core Runtime
1. Navigate to **Amazon Bedrock AgentCore**  
2. Under **Agent Runtime**, click **Host agent**  
3. Choose **image** and provide the ECR image URI you pushed in step 4.   
4. Under **Advanced configurations** provide env variables
