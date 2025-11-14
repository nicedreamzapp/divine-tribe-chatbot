using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IConversationMemory
{
    void AddExchange(string sessionId, ConversationExchange exchange);
    List<ConversationExchange> GetHistory(string sessionId, int limit = 10);
    void RecordFeedback(string sessionId, int exchangeIndex, string feedback);
}
