using System.Collections.Concurrent;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class ConversationMemory : IConversationMemory
{
    private readonly int _maxHistory;
    private readonly ConcurrentDictionary<string, List<ConversationExchange>> _sessions;
    private readonly ILogger<ConversationMemory> _logger;

    public ConversationMemory(ILogger<ConversationMemory> logger, int maxHistory = 10)
    {
        _maxHistory = maxHistory;
        _sessions = new ConcurrentDictionary<string, List<ConversationExchange>>();
        _logger = logger;
        _logger.LogInformation("Conversation Memory initialized (max {MaxHistory} exchanges per session)", maxHistory);
    }

    public void AddExchange(string sessionId, ConversationExchange exchange)
    {
        var history = _sessions.GetOrAdd(sessionId, _ => new List<ConversationExchange>());

        lock (history)
        {
            history.Add(exchange);

            // Keep only the most recent exchanges
            if (history.Count > _maxHistory)
            {
                history.RemoveAt(0);
            }
        }
    }

    public List<ConversationExchange> GetHistory(string sessionId, int limit = 10)
    {
        if (!_sessions.TryGetValue(sessionId, out var history))
        {
            return new List<ConversationExchange>();
        }

        lock (history)
        {
            var count = Math.Min(limit, history.Count);
            return history.Skip(history.Count - count).ToList();
        }
    }

    public void RecordFeedback(string sessionId, int exchangeIndex, string feedback)
    {
        if (!_sessions.TryGetValue(sessionId, out var history))
        {
            _logger.LogWarning("Attempted to record feedback for non-existent session: {SessionId}", sessionId);
            return;
        }

        lock (history)
        {
            if (exchangeIndex >= 0 && exchangeIndex < history.Count)
            {
                history[exchangeIndex].Feedback = feedback;
                _logger.LogInformation("Feedback recorded for session {SessionId}, exchange {Index}",
                    sessionId, exchangeIndex);
            }
            else
            {
                _logger.LogWarning("Invalid exchange index {Index} for session {SessionId}",
                    exchangeIndex, sessionId);
            }
        }
    }

    public bool HasMentionedProduct(string sessionId, string productName)
    {
        var history = GetHistory(sessionId);
        var productLower = productName.ToLower();

        return history.Any(exchange =>
            exchange.ProductsShown.Any(p => p.Name.Contains(productLower, StringComparison.OrdinalIgnoreCase)) ||
            exchange.UserMessage.Contains(productLower, StringComparison.OrdinalIgnoreCase) ||
            exchange.BotResponse.Contains(productLower, StringComparison.OrdinalIgnoreCase));
    }

    public List<Product> GetContextProducts(string sessionId)
    {
        var history = GetHistory(sessionId);
        var productsDict = new Dictionary<string, Product>();

        foreach (var exchange in history)
        {
            foreach (var product in exchange.ProductsShown)
            {
                if (!productsDict.ContainsKey(product.Url))
                {
                    productsDict[product.Url] = product;
                }
            }
        }

        return productsDict.Values.ToList();
    }

    public bool IsFollowUpQuery(string sessionId, string currentQuery)
    {
        var queryLower = currentQuery.ToLower().Trim();

        var followUpWords = new[]
        {
            "it", "that", "this", "those", "them", "the same", "same one",
            "what about", "also", "and", "too", "as well",
            "yes", "no", "yeah", "nah", "yep", "nope",
            "ok", "okay", "thanks", "got it", "i see"
        };

        var startsWithFollowup = followUpWords.Any(word => queryLower.StartsWith(word));
        var isShort = queryLower.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length <= 3;
        var hasHistory = GetHistory(sessionId, limit: 1).Any();

        return hasHistory && (startsWithFollowup || isShort);
    }

    public void ClearSession(string sessionId)
    {
        _sessions.TryRemove(sessionId, out _);
        _logger.LogInformation("Cleared session {SessionId}", sessionId);
    }

    public int GetActiveSessionCount()
    {
        return _sessions.Count;
    }
}
