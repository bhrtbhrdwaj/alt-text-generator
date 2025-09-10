### 1. Create a virtual environment

```bash
cd alt-text-workflow
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

### 5. Test locally
Open a terminal window and start your agent with the following command:
```bash
python3 alt_text_main.py
```
Test your agent by opening another terminal window and enter the following command:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"user_input": "A group of four engineers in hard hats and safety vests discuss blueprints at a construction site."}'
```

### 6. Deploy on Agent Core runtime
Configure the agent. Use the default values:
```bash
agentcore configure -e alt_text_main.py
```
Host your agent in AgentCore Runtime:
```bash
agentcore launch
```

### 7. Host on Amazon Bedrock Core Runtime
1. Navigate to **Amazon Bedrock AgentCore**  
2. Under **Agent Runtime**, click **Your agent**
4. Click on **Update hosting**  
3. Under **Advanced configurations** provide env variables
```python
AWS_BEARER_TOKEN_BEDROCK=
REGION_NAME=
LIGHT_WEIGHT_MODEL=
DEFAULT_MODEL=
```
After setting it up you can test it on AWS testing environment using **Test endpoint** under **Endpoint** section.
Basic testing payload:
```python 
{"user_input": "A group of four engineers in hard hats and safety vests discuss blueprints at a construction site."} 
```
