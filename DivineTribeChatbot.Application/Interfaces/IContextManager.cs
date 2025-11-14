using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IContextManager
{
    ConversationContext GetContext(string sessionId);
    void UpdateContext(string sessionId, string userMessage, List<Product> productsShown);
    string ResolveFollowUpQuery(string query, ConversationContext context);
}
