using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

/// <summary>
/// Simplified Vector Store using basic string similarity
/// For production, integrate ML.NET with sentence transformers ONNX model
/// </summary>
public class VectorStore : IVectorStore
{
    private readonly ILogger<VectorStore> _logger;
    private readonly Dictionary<Product, float[]> _embeddings = new();
    private List<Product> _products = new();

    public VectorStore(ILogger<VectorStore> logger)
    {
        _logger = logger;
    }

    public async Task BuildEmbeddingsAsync(List<Product> products)
    {
        _products = products;

        // Simplified: In production, use ML.NET with ONNX sentence transformer model
        // For now, create simple embeddings based on text features
        foreach (var product in products)
        {
            var embedding = CreateSimpleEmbedding(product);
            _embeddings[product] = embedding;
        }

        _logger.LogInformation("Built embeddings for {Count} products", products.Count);
        await Task.CompletedTask;
    }

    public List<(Product product, double score)> Search(string query, int topK = 10)
    {
        var queryEmbedding = GetEmbedding(query);

        var results = _products
            .Select(p => (product: p, score: CosineSimilarity(queryEmbedding, _embeddings[p])))
            .OrderByDescending(x => x.score)
            .Take(topK)
            .ToList();

        return results;
    }

    public float[] GetEmbedding(string text)
    {
        // Simplified embedding: TF-IDF-like approach
        // In production, use ML.NET with pre-trained sentence transformer
        var words = text.ToLower()
            .Split(new[] { ' ', ',', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);

        var embedding = new float[100]; // Simplified 100-dim vector

        foreach (var word in words)
        {
            var hash = Math.Abs(word.GetHashCode()) % 100;
            embedding[hash] += 1.0f;
        }

        // Normalize
        var magnitude = (float)Math.Sqrt(embedding.Sum(x => x * x));
        if (magnitude > 0)
        {
            for (int i = 0; i < embedding.Length; i++)
            {
                embedding[i] /= magnitude;
            }
        }

        return embedding;
    }

    private float[] CreateSimpleEmbedding(Product product)
    {
        var text = $"{product.Name} {product.Description} {string.Join(" ", product.Features)} {string.Join(" ", product.Keywords)}";
        return GetEmbedding(text);
    }

    private double CosineSimilarity(float[] a, float[] b)
    {
        if (a.Length != b.Length)
            return 0;

        double dotProduct = 0;
        double magnitudeA = 0;
        double magnitudeB = 0;

        for (int i = 0; i < a.Length; i++)
        {
            dotProduct += a[i] * b[i];
            magnitudeA += a[i] * a[i];
            magnitudeB += b[i] * b[i];
        }

        if (magnitudeA == 0 || magnitudeB == 0)
            return 0;

        return dotProduct / (Math.Sqrt(magnitudeA) * Math.Sqrt(magnitudeB));
    }
}
