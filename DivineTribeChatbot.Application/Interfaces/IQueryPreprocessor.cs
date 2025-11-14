using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IQueryPreprocessor
{
    QueryPreprocessingResult Preprocess(string query);
}
