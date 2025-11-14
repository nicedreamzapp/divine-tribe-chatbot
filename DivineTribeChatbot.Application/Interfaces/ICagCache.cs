using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface ICagCache
{
    void Load();
    (bool found, string? response, List<Product>? products) GetCachedResponse(string query);
}
