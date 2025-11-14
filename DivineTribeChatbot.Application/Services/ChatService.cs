using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Enums;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Application.Services;

public class ChatService
{
    private readonly IQueryPreprocessor _queryPreprocessor;
    private readonly ICagCache _cagCache;
    private readonly IAgentRouter _agentRouter;
    private readonly IContextManager _contextManager;
    private readonly IConversationMemory _conversationMemory;
    private readonly IConversationLogger _conversationLogger;
    private readonly IProductDatabase _productDatabase;
    private readonly IMistralClient _mistralClient;
    private readonly ILogger<ChatService> _logger;

    public ChatService(
        IQueryPreprocessor queryPreprocessor,
        ICagCache cagCache,
        IAgentRouter agentRouter,
        IContextManager contextManager,
        IConversationMemory conversationMemory,
        IConversationLogger conversationLogger,
        IProductDatabase productDatabase,
        IMistralClient mistralClient,
        ILogger<ChatService> logger)
    {
        _queryPreprocessor = queryPreprocessor;
        _cagCache = cagCache;
        _agentRouter = agentRouter;
        _contextManager = contextManager;
        _conversationMemory = conversationMemory;
        _conversationLogger = conversationLogger;
        _productDatabase = productDatabase;
        _mistralClient = mistralClient;
        _logger = logger;
    }

    public async Task<ChatResponse> ProcessMessageAsync(ChatRequest request)
    {
        try
        {
            var sessionId = string.IsNullOrEmpty(request.SessionId)
                ? Guid.NewGuid().ToString()
                : request.SessionId;

            // Step 1: Get conversation context
            var context = _contextManager.GetContext(sessionId);

            // Step 2: Resolve follow-up queries (handle "it", "that one", etc.)
            var resolvedQuery = _contextManager.ResolveFollowUpQuery(request.Message, context);

            // Step 3: Preprocess query
            var preprocessingResult = _queryPreprocessor.Preprocess(resolvedQuery);

            // Step 4: Check CAG cache for instant answers
            var (hasCachedAnswer, cachedResponse, cachedProducts) = _cagCache.GetCachedResponse(resolvedQuery);

            // Step 5: Classify intent using Agent Router
            var (intent, confidence, rejectionReason) = _agentRouter.ClassifyIntent(
                resolvedQuery,
                preprocessingResult,
                context,
                hasCachedAnswer);

            // Step 6: Handle off-topic queries
            if (intent == QueryIntent.OffTopic)
            {
                var offTopicResponse = "I'm here to help with Divine Tribe vaporizer products! " +
                    "I can assist with product recommendations, comparisons, troubleshooting, " +
                    "and questions about our vaporizers. How can I help you today?";

                await _conversationLogger.LogConversationAsync(
                    sessionId,
                    request.Message,
                    offTopicResponse,
                    new List<Product>(),
                    intent.ToString(),
                    confidence);

                return new ChatResponse
                {
                    Response = offTopicResponse,
                    Status = "success",
                    SessionId = sessionId,
                    Intent = intent.ToString(),
                    Confidence = confidence
                };
            }

            // Step 7: Return cached answer if available
            if (hasCachedAnswer && cachedResponse != null)
            {
                _contextManager.UpdateContext(sessionId, request.Message, cachedProducts ?? new List<Product>());

                var exchange = new ConversationExchange
                {
                    UserMessage = request.Message,
                    BotResponse = cachedResponse,
                    Intent = intent,
                    Confidence = confidence,
                    ProductsShown = cachedProducts ?? new List<Product>()
                };
                _conversationMemory.AddExchange(sessionId, exchange);

                await _conversationLogger.LogConversationAsync(
                    sessionId,
                    request.Message,
                    cachedResponse,
                    cachedProducts ?? new List<Product>(),
                    intent.ToString(),
                    confidence);

                return new ChatResponse
                {
                    Response = cachedResponse,
                    Status = "success",
                    SessionId = sessionId,
                    ProductsShown = cachedProducts,
                    Intent = intent.ToString(),
                    Confidence = confidence
                };
            }

            // Step 8: Handle customer service queries
            if (intent == QueryIntent.CustomerService)
            {
                var customerServiceResponse = await GenerateCustomerServiceResponseAsync(resolvedQuery, context);

                _contextManager.UpdateContext(sessionId, request.Message, new List<Product>());

                var exchange = new ConversationExchange
                {
                    UserMessage = request.Message,
                    BotResponse = customerServiceResponse,
                    Intent = intent,
                    Confidence = confidence,
                    ProductsShown = new List<Product>()
                };
                _conversationMemory.AddExchange(sessionId, exchange);

                await _conversationLogger.LogConversationAsync(
                    sessionId,
                    request.Message,
                    customerServiceResponse,
                    new List<Product>(),
                    intent.ToString(),
                    confidence);

                return new ChatResponse
                {
                    Response = customerServiceResponse,
                    Status = "success",
                    SessionId = sessionId,
                    Intent = intent.ToString(),
                    Confidence = confidence
                };
            }

            // Step 9: Search for relevant products
            var products = _productDatabase.Search(resolvedQuery, limit: 5);

            // Step 10: Generate AI response with product context
            var aiResponse = await GenerateAiResponseAsync(
                resolvedQuery,
                intent,
                products,
                context,
                preprocessingResult);

            // Step 11: Update context and memory
            _contextManager.UpdateContext(sessionId, request.Message, products);

            var aiExchange = new ConversationExchange
            {
                UserMessage = request.Message,
                BotResponse = aiResponse,
                Intent = intent,
                Confidence = confidence,
                ProductsShown = products
            };
            _conversationMemory.AddExchange(sessionId, aiExchange);

            // Step 12: Log conversation for training
            await _conversationLogger.LogConversationAsync(
                sessionId,
                request.Message,
                aiResponse,
                products,
                intent.ToString(),
                confidence);

            return new ChatResponse
            {
                Response = aiResponse,
                Status = "success",
                SessionId = sessionId,
                ProductsShown = products,
                Intent = intent.ToString(),
                Confidence = confidence
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat message");
            return new ChatResponse
            {
                Response = "I apologize, but I encountered an error. Please try again.",
                Status = "error",
                SessionId = request.SessionId
            };
        }
    }

    private async Task<string> GenerateCustomerServiceResponseAsync(string query, ConversationContext context)
    {
        var systemPrompt = @"You are a customer service representative for Divine Tribe Vaporizers (ineedhemp.com).
Provide helpful, professional responses to customer service inquiries about:
- Returns and refunds
- Warranty information
- Order status and shipping
- General inquiries

Be polite, empathetic, and direct customers to matt@ineedhemp.com for specific account issues.";

        var conversationHistory = _conversationMemory.GetHistory(context.SessionId, limit: 3);
        var historyText = string.Join("\n", conversationHistory.Select(e =>
            $"User: {e.UserMessage}\nAssistant: {e.BotResponse}"));

        var userPrompt = string.IsNullOrEmpty(historyText)
            ? query
            : $"Previous conversation:\n{historyText}\n\nCurrent question: {query}";

        return await _mistralClient.GenerateResponseAsync(systemPrompt, userPrompt);
    }

    private async Task<string> GenerateAiResponseAsync(
        string query,
        QueryIntent intent,
        List<Product> products,
        ConversationContext context,
        QueryPreprocessingResult preprocessingResult)
    {
        var systemPrompt = BuildSystemPrompt(intent, preprocessingResult);
        var productContext = BuildProductContext(products);

        var conversationHistory = _conversationMemory.GetHistory(context.SessionId, limit: 3);
        var historyText = string.Join("\n", conversationHistory.Select(e =>
            $"User: {e.UserMessage}\nAssistant: {e.BotResponse}"));

        var userPrompt = $@"{productContext}

{(string.IsNullOrEmpty(historyText) ? "" : $"Previous conversation:\n{historyText}\n\n")}Current question: {query}

Provide a helpful, concise response (2-3 sentences max). Include relevant product URLs when mentioning products.";

        return await _mistralClient.GenerateResponseAsync(systemPrompt, userPrompt);
    }

    private string BuildSystemPrompt(QueryIntent intent, QueryPreprocessingResult preprocessingResult)
    {
        var basePrompt = @"You are a knowledgeable sales assistant for Divine Tribe Vaporizers (ineedhemp.com).
You help customers find the perfect vaporizer for their needs. Be concise, friendly, and focus on product benefits.";

        return intent switch
        {
            QueryIntent.MaterialShopping when preprocessingResult.MaterialType == MaterialType.Concentrate =>
                basePrompt + "\n\nFocus on concentrate devices. The V5 XL offers best flavor, Core Deluxe is most versatile.",

            QueryIntent.MaterialShopping when preprocessingResult.MaterialType == MaterialType.DryHerb =>
                basePrompt + "\n\nFocus on dry herb devices. Ruby Twist and Gen 2 DC Ceramic are our top recommendations.",

            QueryIntent.ProductComparison =>
                basePrompt + "\n\nProvide clear, objective comparisons highlighting key differences and use cases.",

            QueryIntent.Troubleshooting =>
                basePrompt + "\n\nProvide clear troubleshooting steps. Be empathetic and solution-focused.",

            QueryIntent.HowTo =>
                basePrompt + "\n\nProvide clear, step-by-step instructions. Be patient and thorough.",

            _ => basePrompt
        };
    }

    private string BuildProductContext(List<Product> products)
    {
        if (!products.Any())
            return "No specific products found for this query.";

        var productInfo = products.Select(p =>
            $"- {p.Name} ({p.Price}): {p.Description}\n  URL: {p.Url}");

        return $"Relevant products:\n{string.Join("\n\n", productInfo)}";
    }

    public async Task RecordFeedbackAsync(string sessionId, int exchangeIndex, string feedback)
    {
        _conversationMemory.RecordFeedback(sessionId, exchangeIndex, feedback);
        _logger.LogInformation("Feedback recorded for session {SessionId}, exchange {Index}",
            sessionId, exchangeIndex);
    }
}
