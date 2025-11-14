using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IVectorStore
{
    Task BuildEmbeddingsAsync(List<Product> products);
    List<(Product product, double score)> Search(string query, int topK = 10);
    float[] GetEmbedding(string text);
}
