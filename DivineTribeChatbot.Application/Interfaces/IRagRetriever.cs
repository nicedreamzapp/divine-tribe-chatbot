using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IRagRetriever
{
    Task LoadProductsAsync();
    List<Product> Search(string query, int topK = 10);
    List<Product> SemanticSearch(string query, int topK = 10);
    List<Product> KeywordSearch(string query, int topK = 10);
}
