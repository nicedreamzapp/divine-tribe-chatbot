# Divine Tribe Chatbot - .NET C# Version

This is a complete conversion of the Divine Tribe AI Chatbot from Python to .NET C# 8, following Clean Architecture principles.

## Architecture

The solution is organized into 4 projects:

### 1. **DivineTribeChatbot.Domain** (Core Layer)
- Domain models (Product, ChatRequest, ChatResponse, etc.)
- Enums (QueryIntent, ConversationState, MaterialType)
- No dependencies on other projects

### 2. **DivineTribeChatbot.Application** (Application Layer)
- Service interfaces (ICagCache, IAgentRouter, IRagRetriever, etc.)
- Main ChatService orchestration logic
- Depends on: Domain

### 3. **DivineTribeChatbot.Infrastructure** (Infrastructure Layer)
- Service implementations
- External API clients (MistralClient)
- Data access (JSON file loading, conversation logging)
- Depends on: Application, Domain

### 4. **DivineTribeChatbot.Api** (Presentation Layer)
- ASP.NET Core Web API
- REST endpoints (/api/chat, /api/chat/feedback)
- Swagger/OpenAPI documentation
- Depends on: All other projects

## Features Converted

✅ **Query Preprocessing** - Intent detection, material type classification
✅ **CAG Cache** - Fast lookup for 426+ frequently asked questions
✅ **Agent Router** - 5-signal intent classification
✅ **Context Manager** - Conversation history tracking
✅ **Conversation Memory** - Session-based memory (10 exchanges max)
✅ **Conversation Logger** - Daily JSON logs for RLHF training
✅ **Product Database** - Product catalog management
✅ **Vector Store** - Semantic search (simplified version)
✅ **RAG Retriever** - Hybrid semantic + keyword search
✅ **Mistral AI Client** - LLM integration for response generation

## Prerequisites

- .NET 8.0 SDK or later
- Mistral AI API key
- (Optional) Visual Studio 2022 or VS Code

## Setup Instructions

### 1. Install .NET 8.0 SDK

Download from: https://dotnet.microsoft.com/download/dotnet/8.0

Verify installation:
```bash
dotnet --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/axionmak/divine-tribe-chatbot.git
cd divine-tribe-chatbot
```

### 3. Configure API Keys

Edit `DivineTribeChatbot.Api/appsettings.json`:

```json
{
  "Mistral": {
    "ApiKey": "YOUR_MISTRAL_API_KEY_HERE",
    "Model": "mistral-medium-latest"
  }
}
```

### 4. Restore Dependencies

```bash
dotnet restore
```

### 5. Build the Solution

```bash
dotnet build
```

### 6. Run the Application

```bash
cd DivineTribeChatbot.Api
dotnet run
```

The API will start on: **http://localhost:5001**

## API Endpoints

### POST /api/chat
Send a chat message and receive AI-generated response.

**Request:**
```json
{
  "message": "What's the best vaporizer for concentrates?",
  "sessionId": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "<p>I recommend the <strong>V5 XL</strong>...</p>",
  "status": "success",
  "sessionId": "abc123",
  "productsShown": [
    {
      "name": "V5 XL",
      "url": "https://ineedhemp.com/product/v5-xl/",
      "price": "$50-60"
    }
  ],
  "intent": "MaterialShopping",
  "confidence": 0.85
}
```

### POST /api/chat/feedback
Submit feedback on a chatbot response.

**Request:**
```json
{
  "sessionId": "abc123",
  "exchangeIndex": 0,
  "feedback": "helpful"
}
```

### GET /api/chat/health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T10:30:00Z",
  "version": "1.0.0"
}
```

## Project Structure

```
DivineTribeChatbot/
├── DivineTribeChatbot.sln
├── DivineTribeChatbot.Api/
│   ├── Controllers/
│   │   └── ChatController.cs
│   ├── Program.cs
│   ├── appsettings.json
│   └── DivineTribeChatbot.Api.csproj
├── DivineTribeChatbot.Application/
│   ├── Interfaces/
│   │   ├── ICagCache.cs
│   │   ├── IAgentRouter.cs
│   │   ├── IRagRetriever.cs
│   │   └── ... (10 interfaces)
│   ├── Services/
│   │   └── ChatService.cs
│   └── DivineTribeChatbot.Application.csproj
├── DivineTribeChatbot.Domain/
│   ├── Models/
│   │   ├── Product.cs
│   │   ├── ChatRequest.cs
│   │   ├── ChatResponse.cs
│   │   └── ... (10 models)
│   ├── Enums/
│   │   ├── QueryIntent.cs
│   │   ├── ConversationState.cs
│   │   └── MaterialType.cs
│   └── DivineTribeChatbot.Domain.csproj
└── DivineTribeChatbot.Infrastructure/
    ├── Services/
    │   ├── QueryPreprocessor.cs
    │   ├── CagCache.cs
    │   ├── AgentRouter.cs
    │   ├── ContextManager.cs
    │   ├── ConversationMemory.cs
    │   ├── ConversationLogger.cs
    │   ├── ProductDatabase.cs
    │   ├── VectorStore.cs
    │   ├── RagRetriever.cs
    │   └── MistralClient.cs
    └── DivineTribeChatbot.Infrastructure.csproj
```

## Development

### Running in Development Mode

```bash
dotnet run --project DivineTribeChatbot.Api --environment Development
```

### Running Tests (Coming Soon)

```bash
dotnet test
```

### Swagger UI

When running in Development mode, access Swagger UI at:
**http://localhost:5001/swagger**

## Differences from Python Version

### Improvements

1. **Clean Architecture** - Clear separation of concerns across 4 layers
2. **Dependency Injection** - Built-in DI container, better testability
3. **Strongly Typed** - Compile-time type safety
4. **Async/Await** - Native async support for better performance
5. **Swagger/OpenAPI** - Auto-generated API documentation

### Simplified Components

1. **Vector Store** - Uses basic cosine similarity instead of sentence-transformers
   - For production: Integrate ML.NET with ONNX sentence transformer models
2. **Image Generation** - Not yet implemented (ComfyUI integration)
3. **Telegram Integration** - Not yet implemented

### Migration Path for Advanced Features

To implement full sentence-transformer embeddings:

1. Install ML.NET packages:
```bash
dotnet add package Microsoft.ML
dotnet add package Microsoft.ML.OnnxRuntime
```

2. Download ONNX model (e.g., all-MiniLM-L6-v2)
3. Update VectorStore.cs to use ML.NET prediction engine

## Configuration

### appsettings.json

```json
{
  "Mistral": {
    "ApiKey": "your-key-here",
    "Model": "mistral-medium-latest"
  },
  "ChatSettings": {
    "MaxConversationHistory": 10,
    "DefaultResponseLength": 500,
    "LogDirectory": "conversation_logs"
  }
}
```

### Environment Variables

Alternatively, configure via environment variables:

```bash
export Mistral__ApiKey="your-key-here"
export Mistral__Model="mistral-medium-latest"
```

## Logging

Logs are written to:
- **Console** - Real-time logging during development
- **conversation_logs/** - Daily JSON files for training data

Example log entry:
```json
{
  "chatId": "session_123_20251114_143022_123456",
  "sessionId": "session_123",
  "timestamp": "2025-11-14T14:30:22.123Z",
  "userQuery": "best for wax",
  "botResponse": "I recommend...",
  "productsShown": ["V5 XL", "Core Deluxe"],
  "intent": "MaterialShopping",
  "confidence": 0.85
}
```

## Deployment

### Docker (Coming Soon)

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0
COPY bin/Release/net8.0/publish/ App/
WORKDIR /App
ENTRYPOINT ["dotnet", "DivineTribeChatbot.Api.dll"]
```

### Azure App Service

1. Publish the app:
```bash
dotnet publish -c Release
```

2. Deploy to Azure:
```bash
az webapp up --name divine-tribe-chatbot --runtime "DOTNET|8.0"
```

### Linux/Windows Server

1. Publish self-contained:
```bash
dotnet publish -c Release -r linux-x64 --self-contained
```

2. Run:
```bash
./DivineTribeChatbot.Api
```

## Performance

Expected performance metrics:

- **CAG Cache Hits**: <100ms
- **RAG Search**: 300-500ms
- **AI Response Generation**: 1-3 seconds (depends on Mistral API)
- **Memory Usage**: ~200MB baseline
- **Concurrent Requests**: Supports 100+ concurrent sessions

## Contributing

Contributions are welcome! Areas for improvement:

1. ML.NET integration for proper embeddings
2. Unit test coverage
3. Telegram bot integration
4. Image generation (FLUX/ComfyUI)
5. Performance optimizations
6. Caching layer (Redis)

## License

Same as the original Python version.

## Support

For issues or questions:
- Email: matt@ineedhemp.com
- GitHub Issues: https://github.com/axionmak/divine-tribe-chatbot/issues

## Credits

Original Python version by Divine Tribe team.
C# conversion completed November 2025.

---

**Built with:** .NET 8, ASP.NET Core, Markdig, System.Text.Json
**AI Integration:** Mistral AI API
**Architecture:** Clean Architecture / Onion Architecture
