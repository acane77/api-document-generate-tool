## 1. 大语言模型

### 1.1. 自然语言问答

#### 向LLM Query

```
POST /api/completions
```

* **请求**

```json
{
    "query": "",
    "temperature": 0.01,
    "model": "gpt4",
    "session_id": 0,
    "kb_info": [
        {
            "kb_name": "",
            "recall": 3
        }
    ]
}
```

说明：

|名称|类型|必需|默认值|含义|
|----|----|----|----|----|
|query|string|Yes| |用户Prompt|
|temperature|float|No|0.01|LLM Temperature|
|model|string|No|gpt4|LLM模型名称|
|session_id|int|No|0|多轮对话会话ID|
|kb_info|object[]|Yes| |见kb_info的说明|


.kb_info说明：

|名称|类型|必需|默认值|含义|
|----|----|----|----|----|
|kb_name|string|Yes| |知识库名称|
|recall|int|No|3|召回条数|





* **响应**

```json
{
    "answer": "",
    "session_id": 0
}
```

说明：

|名称|类型|含义|
|----|----|----|
|answer|string|LLM答案|
|session_id|int|会话ID|





