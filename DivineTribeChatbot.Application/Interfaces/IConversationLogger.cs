using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IConversationLogger
{
    Task LogConversationAsync(
        string sessionId,
        string userQuery,
        string botResponse,
        List<Product> productsShown,
        string intent,
        double confidence,
        string? feedback = null);
}
