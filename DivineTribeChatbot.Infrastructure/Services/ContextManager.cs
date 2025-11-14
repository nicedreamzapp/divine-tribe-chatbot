using System.Collections.Concurrent;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Enums;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class ContextManager : IContextManager
{
    private readonly ConcurrentDictionary<string, ConversationContext> _sessions;
    private readonly ILogger<ContextManager> _logger;
    private readonly int _maxHistory;

    public ContextManager(ILogger<ContextManager> logger, int maxHistory = 10)
    {
        _sessions = new ConcurrentDictionary<string, ConversationContext>();
        _logger = logger;
        _maxHistory = maxHistory;
        _logger.LogInformation("Context Manager initialized (max {MaxHistory} exchanges per session)", maxHistory);
    }

    public ConversationContext GetContext(string sessionId)
    {
        return _sessions.GetOrAdd(sessionId, _ => new ConversationContext
        {
            SessionId = sessionId,
            ProductsMentioned = new List<Product>(),
            UserPreferences = new Dictionary<string, string>(),
            State = ConversationState.Initial,
            CreatedAt = DateTime.UtcNow,
            LastUpdated = DateTime.UtcNow
        });
    }

    public void UpdateContext(string sessionId, string userMessage, List<Product> productsShown)
    {
        var context = GetContext(sessionId);

        // Update products mentioned
        foreach (var product in productsShown)
        {
            if (!context.ProductsMentioned.Any(p => p.Url == product.Url))
            {
                context.ProductsMentioned.Add(product);
            }
        }

        // Update last product mentioned
        if (productsShown.Any())
        {
            context.LastProductMentioned = productsShown.First();
        }

        // Extract and update user preferences
        var preferences = ExtractPreferences(userMessage);
        foreach (var (key, value) in preferences)
        {
            context.UserPreferences[key] = value;
        }

        // Update conversation state based on message content
        UpdateConversationState(context, userMessage);

        context.ExchangeCount++;
        context.LastUpdated = DateTime.UtcNow;
    }

    public string ResolveFollowUpQuery(string query, ConversationContext context)
    {
        var queryLower = query.ToLower().Trim();

        var followUpIndicators = new[]
        {
            "it", "that", "this", "them", "those", "these",
            "what about", "tell me more", "how about",
            "the one", "that one", "this one"
        };

        var isFollowUp = followUpIndicators.Any(indicator => queryLower.Contains(indicator));

        if (!isFollowUp || context.LastProductMentioned == null)
        {
            return query;
        }

        // Replace pronouns with actual product name
        var resolvedQuery = query;

        if (queryLower.StartsWith("it ") || queryLower.StartsWith("that ") || queryLower.StartsWith("this "))
        {
            var words = query.Split(' ', 2);
            if (words.Length == 2)
            {
                resolvedQuery = $"{context.LastProductMentioned.Name} {words[1]}";
            }
        }
        else if (queryLower.Contains("what about") || queryLower.Contains("tell me more"))
        {
            resolvedQuery = $"{context.LastProductMentioned.Name} {query}";
        }

        _logger.LogInformation("Resolved follow-up query '{Original}' to '{Resolved}'", query, resolvedQuery);

        return resolvedQuery;
    }

    private Dictionary<string, string> ExtractPreferences(string query)
    {
        var queryLower = query.ToLower();
        var preferences = new Dictionary<string, string>();

        // Experience level
        if (new[] { "beginner", "new", "first time", "starter" }.Any(w => queryLower.Contains(w)))
        {
            preferences["experience_level"] = "beginner";
        }
        else if (new[] { "advanced", "experienced", "expert" }.Any(w => queryLower.Contains(w)))
        {
            preferences["experience_level"] = "advanced";
        }

        // Form factor
        if (new[] { "portable", "travel", "compact", "small" }.Any(w => queryLower.Contains(w)))
        {
            preferences["form_factor"] = "portable";
        }
        else if (new[] { "desktop", "home", "stationary" }.Any(w => queryLower.Contains(w)))
        {
            preferences["form_factor"] = "desktop";
        }

        // Priority features
        if (new[] { "flavor", "taste", "terp" }.Any(w => queryLower.Contains(w)))
        {
            preferences["priority"] = "flavor";
        }
        else if (new[] { "powerful", "strong", "potent" }.Any(w => queryLower.Contains(w)))
        {
            preferences["priority"] = "power";
        }
        else if (new[] { "easy", "simple", "convenient" }.Any(w => queryLower.Contains(w)))
        {
            preferences["priority"] = "ease_of_use";
        }
        else if (new[] { "cheap", "affordable", "budget" }.Any(w => queryLower.Contains(w)))
        {
            preferences["priority"] = "price";
        }

        // Material preference
        if (new[] { "dry herb", "flower", "bud" }.Any(w => queryLower.Contains(w)))
        {
            preferences["material"] = "dry_herb";
        }
        else if (new[] { "concentrate", "wax", "dab", "oil" }.Any(w => queryLower.Contains(w)))
        {
            preferences["material"] = "concentrate";
        }

        return preferences;
    }

    private void UpdateConversationState(ConversationContext context, string userMessage)
    {
        var messageLower = userMessage.ToLower();

        if (new[] { "vs", "versus", "compare", "difference", "better" }.Any(w => messageLower.Contains(w)))
        {
            context.State = ConversationState.Comparing;
        }
        else if (new[] { "broken", "not working", "problem", "issue", "fix" }.Any(w => messageLower.Contains(w)))
        {
            context.State = ConversationState.Troubleshooting;
        }
        else if (new[] { "buy", "purchase", "recommend", "best" }.Any(w => messageLower.Contains(w)))
        {
            context.State = ConversationState.Browsing;
        }
    }

    public void ClearSession(string sessionId)
    {
        _sessions.TryRemove(sessionId, out _);
        _logger.LogInformation("Cleared session {SessionId}", sessionId);
    }

    public void ClearOldSessions(TimeSpan maxAge)
    {
        var now = DateTime.UtcNow;
        var oldSessions = _sessions
            .Where(kvp => (now - kvp.Value.LastUpdated) > maxAge)
            .Select(kvp => kvp.Key)
            .ToList();

        foreach (var sessionId in oldSessions)
        {
            _sessions.TryRemove(sessionId, out _);
        }

        if (oldSessions.Any())
        {
            _logger.LogInformation("Cleared {Count} old sessions", oldSessions.Count);
        }
    }
}
