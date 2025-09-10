# UI to demonstrate the Bedrock Agent Core Runtime API integration 
## Prerequisite
  You require Agent Core Runtime API
  - ARN
  - API Qualifier
Go to **Amazon Bedrock AgentCore** -> **Agent Runtime** -> **your-agent** under **View invocation code**

### 1. Create a virtual environment

```bash
cd alt-text-generator/alt-text-ui
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

### 4. Create .env file and update it with keys

### 5. Run the project
```bash
streamlit run main.py --server.port 8501
```
