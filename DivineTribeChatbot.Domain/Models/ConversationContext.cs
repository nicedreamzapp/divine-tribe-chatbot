using DivineTribeChatbot.Domain.Enums;

namespace DivineTribeChatbot.Domain.Models;

public class ConversationContext
{
    public string SessionId { get; set; } = string.Empty;
    public List<Product> ProductsMentioned { get; set; } = new();
    public Dictionary<string, string> UserPreferences { get; set; } = new();
    public ConversationState State { get; set; } = ConversationState.Initial;
    public QueryIntent? LastIntent { get; set; }
    public Product? LastProductMentioned { get; set; }
    public int ExchangeCount { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
}
