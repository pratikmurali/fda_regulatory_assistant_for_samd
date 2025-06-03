---
title: FDA Regulatory Assistant For SaMD
emoji: 📊
colorFrom: yellow
colorTo: red
sdk: docker
pinned: true
license: apache-2.0
short_description: FDA Regulatory Assistant for Software as A Medical Device
---
# FDA Regulatory Assistant

A sophisticated AI-powered assistant for FDA regulatory compliance analysis, built with LangGraph multi-agent workflows and Chainlit for an interactive user experience.

## 🚀 Features

### 🤖 Multi-Agent System
- **Supervisor Agent**: Intelligent routing and response compilation as FDA auditor
- **Document Processor**: Advanced ZIP file extraction and document parsing
- **Cybersecurity Specialist**: FDA cybersecurity guidance and SOUP documentation analysis
- **Regulatory Affairs Expert**: CFR510K, PMA, and FDA regulatory compliance review
- **Compliance Auditor**: FDA Auditor like, Comprehensive gap analysis and readiness assessment
- **Report Generator**: Detailed compliance reports with actionable recommendations

### 💬 Interactive Capabilities
- **Intelligent Q&A**: Context-aware routing to appropriate specialist agents
- **Document Gap Analysis**: Upload ZIP files containing regulatory submission packages
- **Real-time Streaming**: Word-by-word response streaming with agent identification
- **Source References**: All responses include original FDA document citations
- **File Processing**: Support for PDF, Word, TXT, and ZIP file uploads

### 🏗️ Advanced Architecture
- **Simplified LangGraph Workflow**: Clean state management with message passing
- **15+ Specialized Tools**: Comprehensive toolkit for document processing and compliance analysis
- **RAG Integration**: Pre-warmed chains for instant access to FDA knowledge base
- **Streaming Configuration**: Word-by-word streaming with formatting preservation
- **Error Handling**: Graceful degradation and comprehensive error reporting
- **Evaluation Framework**: Dual evaluation system with RAGAS and LangSmith

## 🛠️ Technology Stack

- **Multi-Agent Framework**: LangGraph with simplified state management
- **UI Framework**: Chainlit for interactive chat interface with file uploads
- **LLM**: OpenAI GPT-4.1-mini with function calling
- **Vector Database**: Qdrant for efficient knowledge base storage and retrieval
- **Document Processing**: PyMuPDF (fitz) for PDF parsing, python-docx for Word documents
- **RAG System**: Custom chain manager with pre-warming and caching
- **Package Management**: UV for fast, reliable dependency management
- **Testing**: Pytest with comprehensive test suite
- **Code Quality**: Ruff for linting and code formatting
- **Monitoring**: LangSmith for tracing and performance monitoring
- **Evaluation**: RAGAS for automated RAG evaluation and quality assessment
- **Deployment**: Docker support with Hugging Face Spaces compatibility

## 📋 Prerequisites

- Python 3.12+
- OpenAI API key
- UV package manager (recommended) or pip

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fda-regulatory-assistant
   ```

2. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Initialize the knowledge base** (if needed)
   ```bash
   python setup_env.py
   ```

## 🚀 Usage

### Start the Application
```bash
chainlit run main.py -w
```

The application will be available at `http://localhost:8000`

### Using the Assistant

#### Question Answering
Simply ask questions about FDA regulations or cybersecurity requirements:
- "What are the FDA cybersecurity requirements for medical devices?"
- "How do I submit a 510(k) application?"
- "What are the SOUP requirements for medical device software?"

#### Document Analysis
1. Upload documents (PDF, TXT, or ZIP files)
2. Ask for compliance gap analysis
3. Receive detailed reports with findings and recommendations

### Example Interactions

**Cybersecurity Question:**
```
User: What are the key cybersecurity controls for Class II medical devices?
Assistant: Based on FDA guidance, Class II medical devices should implement...
```

**Gap Analysis:**
```
User: [Uploads device specification PDF]
User: Please analyze this document for regulatory compliance gaps
Assistant: **Cybersecurity Agent**: Analyzing cybersecurity compliance...
**Regulatory Agent**: Reviewing regulatory requirements...
**Auditor Agent**: Performing gap analysis...
**Report Generator**: Generating comprehensive report...
```

## 📁 Project Structure

```
fda-regulatory-assistant/
├── main.py                     # Chainlit application entry point
├── graph/                      # LangGraph multi-agent workflow
│   ├── agents.py              # 6 specialized agents with tool bindings
│   ├── graph.py               # Workflow orchestration and streaming
│   └── state.py               # Simplified state management
├── tools/                      # Comprehensive agent toolkit (15+ tools)
│   ├── __init__.py            # Tool exports
│   ├── tools.py               # Core tool implementations
│   ├── README.md              # Tool documentation
│   └── example_usage.py       # Usage examples
├── ragchains/                  # RAG chain implementations
│   ├── chain_manager.py       # Centralized chain management
│   ├── fda_cybersecurity_rag.py # Cybersecurity knowledge base
│   ├── fda_regulatory_rag.py  # Regulatory knowledge base
│   └── tools/                 # Legacy tool compatibility
├── evals/                      # Evaluation framework
│   ├── ragas_eval_for_cybersecurity_rag.py # RAGAS cybersecurity evaluation
│   ├── ragas_eval_for_regulatory_rag.py    # RAGAS regulatory evaluation
│   ├── langsmith_eval_for_cybersecurity_rag.py # LangSmith cybersecurity evaluation
│   ├── langsmith_eval_for_regulatory_rag.py    # LangSmith regulatory evaluation
│   ├── sdg_cybersecurity_rag.py # Synthetic data generation for cybersecurity
│   ├── sdg_regulatory_rag.py   # Synthetic data generation for regulatory
│   └── data/                   # Evaluation datasets
│       ├── cybersecurity/      # Cybersecurity evaluation data
│       └── fda/               # Regulatory evaluation data
├── utils/                      # Utility functions
│   ├── document_parsers.py    # Advanced document processing
│   ├── streaming_config.py    # Streaming configuration
│   └── langgraph_utils.py     # LangGraph helper functions
├── prompts/                    # LLM prompts and templates
├── tests/                      # Comprehensive test suite
├── examples/                   # Usage examples and demos
├── loaders/                    # Document loaders
├── cache/                      # Vector store cache
├── cybersecurity-cache/        # Cybersecurity-specific cache
├── Dockerfile                  # Docker deployment configuration
├── docker-compose.yml          # Docker Compose setup
├── ARCHITECTURE.md             # Detailed architecture documentation
├── DOCKER_DEPLOYMENT.md        # Docker deployment guide
└── pyproject.toml             # UV package configuration
```

## 🔄 Workflow Architecture

The application implements a **simplified LangGraph multi-agent system** with intelligent routing and streaming responses:

### 🎯 Workflow Types

**1. Question Answering Flow**
```
User Question → Supervisor → Route to Specialist → Tool Execution → Streaming Response
```

**2. Gap Analysis Flow**
```
ZIP Upload → Document Processor → Cybersecurity Agent →
Regulatory Agent → Auditor Agent → Report Generator → Final Report
```

### 🧠 Agent Specialization

1. **Supervisor Agent**:
   - Intelligent routing based on question keywords
   - Final response compilation as FDA auditor
   - Workflow orchestration and error handling

2. **Document Processor**:
   - ZIP file extraction and validation
   - Multi-format document parsing (PDF, Word, TXT)
   - Document chunking and metadata extraction

3. **Cybersecurity Specialist**:
   - FDA cybersecurity guidance analysis
   - SOUP (Software of Unknown Provenance) documentation
   - Vulnerability assessment and security controls

4. **Regulatory Affairs Expert**:
   - 510K submission requirements
   - PMA and regulatory compliance
   - FDA guidance interpretation

5. **Compliance Auditor**:
   - Gap analysis and readiness assessment
   - Compliance scoring and prioritization
   - Risk assessment and mitigation

6. **Report Generator**:
   - Comprehensive compliance reports
   - Executive summaries and recommendations
   - Actionable improvement plans

### 🔧 Key Architecture Features

- **Simplified State**: TypedDict with message passing using `operator.add`
- **Tool Integration**: 15+ specialized tools for document processing and analysis
- **Streaming Support**: Real-time word-by-word response streaming with 50ms delays
- **Error Handling**: Graceful degradation with recursion limits and enhanced termination logic
- **Source References**: Automatic extraction and formatting of source citations
- **Pre-warmed Chains**: Instant response times through chain pre-loading
- **Evaluation Framework**: Comprehensive quality assessment with RAGAS and LangSmith

## 🧪 Testing & Evaluation

### Unit Testing
Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_streaming_*.py
python -m pytest tests/test_tools_integration.py
python -m pytest tests/test_langgraph_workflow.py
```

### RAG Evaluation with RAGAS
Evaluate RAG chain quality using automated metrics:
```bash
# Evaluate cybersecurity RAG chain
python evals/ragas_eval_for_cybersecurity_rag.py

# Evaluate regulatory RAG chain
python evals/ragas_eval_for_regulatory_rag.py
```

**RAGAS Metrics**:
- LLM Context Recall
- Faithfulness
- Factual Correctness
- Response Relevancy
- Context Entity Recall
- Noise Sensitivity

### LangSmith Evaluation
Monitor and evaluate with LangSmith:
```bash
# Evaluate cybersecurity RAG with LangSmith
python evals/langsmith_eval_for_cybersecurity_rag.py

# Evaluate regulatory RAG with LangSmith
python evals/langsmith_eval_for_regulatory_rag.py
```

**LangSmith Evaluators**:
- QA Evaluator
- Contextual QA
- Chain of Thought
- Helpfulness Criteria

### Synthetic Data Generation
Generate evaluation datasets:
```bash
# Generate cybersecurity test datasets
python evals/sdg_cybersecurity_rag.py

# Generate regulatory test datasets
python evals/sdg_regulatory_rag.py
```

## 📊 Performance Features

### 🚀 Optimized Performance
- **Pre-warmed RAG Chains**: Instant response times after startup initialization
- **Streaming Responses**: Real-time word-by-word streaming with configurable delays
- **Concurrent Processing**: Thread-safe multi-agent execution
- **Memory Efficiency**: Shared vector stores and optimized document processing
- **Caching**: Intelligent caching of frequently accessed regulatory information

### 📈 Scalability Features
- **Session Isolation**: Independent user sessions with shared resources
- **Error Recovery**: Graceful degradation and automatic retry mechanisms
- **Resource Management**: Automatic cleanup and garbage collection
- **Load Balancing**: Efficient distribution of agent workloads

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
CHAINLIT_AUTH_SECRET=your_secret_here
LANGSMITH_API_KEY=your_langsmith_key  # For tracing and evaluation
LANGCHAIN_API_KEY=your_langchain_key  # For LangSmith evaluation
```

### Streaming Configuration
Customize streaming behavior in `utils/streaming_config.py`:

```python
# Word-by-word streaming configuration
WORD_DELAY = 0.05  # 50ms delay between words (configurable)

# Streaming function preserves formatting
async def stream_text_word_by_word(text: str, delay: float = WORD_DELAY):
    # Maintains numbered lists, line breaks, and text structure
    # Separate delays for words vs whitespace/formatting
```

### Agent Configuration
Customize agent behavior in `graph/agents.py`:

```python
# Enhanced routing keywords for intelligent agent selection
CYBERSECURITY_KEYWORDS = [
    "cybersecurity", "cyber security", "cyber-security",
    "SOUP", "software of unknown provenance",
    "vulnerability", "CVE", "CWE", "security", "threat",
    "malware", "encryption", "penetration testing",
    "authentication", "authorization"
]

REGULATORY_KEYWORDS = [
    "510K", "510(k)", "predicate device",
    "PMA", "premarket approval", "regulatory",
    "submission", "FDA approval", "compliance",
    "guidance documents", "regulatory pathway",
    "QSR", "quality system regulation"
]
```

### Tool Configuration
Adjust tool parameters in `tools/tools.py`:

```python
# Document processing settings
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 80

# Compliance analysis criteria
COMPLIANCE_CRITERIA = {
    "510k": ["predicate device identification", "substantial equivalence", ...],
    "pma": ["clinical data", "manufacturing information", ...],
    "qsr": ["design controls", "document controls", ...]
}
```

### Evaluation Configuration
Configure evaluation settings:

```python
# RAGAS evaluation settings
RAGAS_METRICS = [
    "LLMContextRecall", "Faithfulness", "FactualCorrectness",
    "ResponseRelevancy", "ContextEntityRecall", "NoiseSensitivity"
]

# LangSmith evaluation settings
LANGSMITH_EVALUATORS = [
    "qa", "context_qa", "cot_qa", "labeled_criteria"
]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions or issues:
1. Check the [Issues](../../issues) page
2. Review the test files for usage examples
3. Consult the architecture documentation in `ARCHITECTURE.md`

## 🔮 Roadmap

### ✅ Recently Completed
- [x] **Evaluation Framework**: Comprehensive RAGAS and LangSmith evaluation system
- [x] **Docker Deployment**: Full Docker support with Hugging Face Spaces compatibility
- [x] **Enhanced Architecture**: Simplified LangGraph implementation with improved performance
- [x] **Word-by-word Streaming**: Optimized streaming with formatting preservation
- [x] **Comprehensive Documentation**: Detailed architecture and deployment guides

### 🎯 Near-term Enhancements
- [ ] **Enhanced Document Support**: Excel, PowerPoint, and additional file formats
- [ ] **Advanced Analytics**: Compliance trend analysis and historical tracking
- [ ] **Batch Processing**: Multiple document package analysis with parallel processing
- [ ] **Custom Templates**: User-defined compliance checklists and report formats
- [ ] **Evaluation Dashboard**: Real-time evaluation metrics and performance monitoring

### 🚀 Future Features
- [ ] **FDA Database Integration**: Real-time access to FDA guidance updates
- [ ] **Visualization Dashboard**: Interactive compliance dashboards and charts
- [ ] **Multi-language Support**: Support for international regulatory frameworks (EU MDR, ISO 13485)
- [ ] **API Integration**: RESTful API for enterprise integration
- [ ] **Advanced AI Features**: Predictive compliance analysis and risk scoring
- [ ] **Automated Reporting**: Scheduled compliance reports and alerts

### 🔧 Technical Improvements
- [ ] **Performance Optimization**: Enhanced caching and parallel processing
- [ ] **Security Enhancements**: Advanced authentication and data encryption
- [ ] **Monitoring & Observability**: Comprehensive logging and metrics with Grafana/Prometheus
- [ ] **Cloud Deployment**: AWS/Azure deployment guides and infrastructure as code
- [ ] **Evaluation Automation**: Continuous evaluation pipeline with CI/CD integration

---

**Built with ❤️ using LangGraph, Chainlit, OpenAI, PyMuPDF, RAGAS, and LangSmith**

*Empowering regulatory compliance through intelligent multi-agent systems with comprehensive evaluation*

## 📚 Additional Resources

- **[Architecture Documentation](ARCHITECTURE.md)**: Detailed technical architecture and design patterns
- **[Docker Deployment Guide](DOCKER_DEPLOYMENT.md)**: Complete Docker deployment instructions
- **[Tool Documentation](tools/README.md)**: Comprehensive tool reference and usage examples
- **[Evaluation Framework](evals/)**: RAGAS and LangSmith evaluation implementations
- **[Example Usage](examples/)**: Code examples and integration patterns

## 🏆 Key Features Summary

✅ **6 Specialized Agents** with intelligent routing
✅ **15+ Comprehensive Tools** for compliance analysis
✅ **Dual Evaluation System** with RAGAS and LangSmith
✅ **Real-time Streaming** with word-by-word responses
✅ **Docker Deployment** ready for production
✅ **Comprehensive Testing** with automated evaluation
✅ **Source References** with every response
✅ **File Upload Support** for ZIP, PDF, DOCX, TXT

*Ready for deployment to Hugging Face Spaces, AWS, Azure, or local environments*