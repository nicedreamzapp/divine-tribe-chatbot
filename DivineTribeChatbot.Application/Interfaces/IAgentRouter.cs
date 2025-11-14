using DivineTribeChatbot.Domain.Enums;
using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IAgentRouter
{
    (QueryIntent intent, double confidence, string? rejectionReason) ClassifyIntent(
        string query,
        QueryPreprocessingResult preprocessingResult,
        ConversationContext context,
        bool hasCachedAnswer);
}
