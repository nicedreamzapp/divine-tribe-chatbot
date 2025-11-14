using DivineTribeChatbot.Domain.Enums;

namespace DivineTribeChatbot.Domain.Models;

public class ConversationExchange
{
    public string UserMessage { get; set; } = string.Empty;
    public string BotResponse { get; set; } = string.Empty;
    public QueryIntent Intent { get; set; }
    public double Confidence { get; set; }
    public List<Product> ProductsShown { get; set; } = new();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? Feedback { get; set; }
}
