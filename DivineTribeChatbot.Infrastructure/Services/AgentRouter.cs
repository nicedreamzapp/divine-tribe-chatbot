using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Enums;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class AgentRouter : IAgentRouter
{
    private readonly ILogger<AgentRouter> _logger;

    private readonly string[] _offTopicKeywords = new[]
    {
        "weather", "politics", "sports", "recipe", "movie", "music",
        "restaurant", "hotel", "flight", "car rental", "news"
    };

    private readonly string[] _troubleshootingKeywords = new[]
    {
        "broken", "not working", "problem", "issue", "fix", "help",
        "won't", "wont", "can't", "cant", "doesn't", "doesnt",
        "error", "wrong", "bad", "leaking", "resistance"
    };

    private readonly string[] _customerServiceKeywords = new[]
    {
        "return", "refund", "warranty", "shipping", "order", "delivery",
        "tracking", "cancel", "exchange", "damaged"
    };

    private readonly string[] _howToKeywords = new[]
    {
        "how to", "how do", "setup", "install", "use", "clean",
        "instructions", "guide", "tutorial"
    };

    public AgentRouter(ILogger<AgentRouter> logger)
    {
        _logger = logger;
    }

    public (QueryIntent intent, double confidence, string? rejectionReason) ClassifyIntent(
        string query,
        QueryPreprocessingResult preprocessingResult,
        ConversationContext context,
        bool hasCachedAnswer)
    {
        var queryLower = query.ToLower();

        // Signal 1: Off-topic detection (highest priority)
        if (IsOffTopic(queryLower))
        {
            _logger.LogInformation("Query classified as off-topic: {Query}", query);
            return (QueryIntent.OffTopic, 1.0, "This query is not related to Divine Tribe vaporizer products.");
        }

        // Signal 2: URL presence (confidence: 1.0)
        if (queryLower.Contains("ineedhemp.com"))
        {
            _logger.LogInformation("Query contains URL, classified as product info");
            return (QueryIntent.ProductInfo, 1.0, null);
        }

        // Signal 3: CAG cache match (confidence: 0.95)
        if (hasCachedAnswer)
        {
            _logger.LogInformation("Query has cached answer");
            return (QueryIntent.ProductInfo, 0.95, null);
        }

        // Signal 4: Customer service keywords (high priority)
        if (_customerServiceKeywords.Any(kw => queryLower.Contains(kw)))
        {
            _logger.LogInformation("Query classified as customer service");
            return (QueryIntent.CustomerService, 0.9, null);
        }

        // Signal 5: Troubleshooting keywords
        if (_troubleshootingKeywords.Any(kw => queryLower.Contains(kw)))
        {
            _logger.LogInformation("Query classified as troubleshooting");
            return (QueryIntent.Troubleshooting, 0.85, null);
        }

        // Signal 6: How-to keywords
        if (_howToKeywords.Any(kw => queryLower.Contains(kw)))
        {
            _logger.LogInformation("Query classified as how-to");
            return (QueryIntent.HowTo, 0.8, null);
        }

        // Signal 7: Product mention (confidence: 0.8)
        if (preprocessingResult.ExtractedEntities.Any())
        {
            if (preprocessingResult.IsComparison)
            {
                return (QueryIntent.ProductComparison, 0.8, null);
            }

            return (QueryIntent.ProductInfo, 0.8, null);
        }

        // Signal 8: Intent hints from preprocessing (confidence: 0.6)
        if (preprocessingResult.IntentHints.Contains("comparison"))
        {
            return (QueryIntent.ProductComparison, 0.7, null);
        }

        if (preprocessingResult.IntentHints.Contains("shopping"))
        {
            // Determine material type for routing
            if (preprocessingResult.MaterialType == MaterialType.Concentrate ||
                preprocessingResult.MaterialType == MaterialType.DryHerb)
            {
                return (QueryIntent.MaterialShopping, 0.75, null);
            }

            return (QueryIntent.ProductInfo, 0.7, null);
        }

        if (preprocessingResult.IntentHints.Contains("troubleshooting"))
        {
            return (QueryIntent.Troubleshooting, 0.7, null);
        }

        if (preprocessingResult.IntentHints.Contains("how_to"))
        {
            return (QueryIntent.HowTo, 0.7, null);
        }

        // Signal 9: Conversation context (confidence: 0.5)
        if (context.LastIntent.HasValue)
        {
            // If user is continuing a conversation, maintain the same intent type
            _logger.LogInformation("Using context-based intent: {Intent}", context.LastIntent);
            return (context.LastIntent.Value, 0.5, null);
        }

        // Default: General shopping/reasoning
        return (QueryIntent.Reasoning, 0.4, null);
    }

    private bool IsOffTopic(string query)
    {
        // Check for obvious off-topic keywords
        if (_offTopicKeywords.Any(kw => query.Contains(kw)))
        {
            // However, if it also mentions vaporizer/product keywords, it might be on-topic
            var productKeywords = new[] { "vape", "vaporizer", "dab", "concentrate", "divine", "tribe", "core", "v5" };

            if (!productKeywords.Any(kw => query.Contains(kw)))
            {
                return true;
            }
        }

        return false;
    }
}
