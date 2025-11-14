using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace DivineTribeChatbot.Infrastructure.Services;

public class RagRetriever : IRagRetriever
{
    private readonly IVectorStore _vectorStore;
    private readonly ILogger<RagRetriever> _logger;
    private List<Product> _products = new();

    public RagRetriever(IVectorStore vectorStore, ILogger<RagRetriever> logger)
    {
        _vectorStore = vectorStore;
        _logger = logger;
    }

    public async Task LoadProductsAsync()
    {
        // Products are loaded from the products_organized.json file
        var productsPath = "products_organized.json";

        if (!File.Exists(productsPath))
        {
            _logger.LogWarning("Products file not found at {Path}", productsPath);
            return;
        }

        var json = await File.ReadAllTextAsync(productsPath);
        var productData = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(json);

        // Simplified loading - in production, properly deserialize the nested structure
        // For now, create some sample products
        _products = CreateSampleProducts();

        await _vectorStore.BuildEmbeddingsAsync(_products);

        _logger.LogInformation("RAG Retriever loaded {Count} products", _products.Count);
    }

    public List<Product> Search(string query, int topK = 10)
    {
        // Hybrid search: combine semantic and keyword search
        var semanticResults = SemanticSearch(query, topK * 2);
        var keywordResults = KeywordSearch(query, topK * 2);

        // Merge and deduplicate by URL
        var merged = MergeResults(semanticResults, keywordResults, topK);

        return merged;
    }

    public List<Product> SemanticSearch(string query, int topK = 10)
    {
        var results = _vectorStore.Search(query, topK);
        return results.Select(r => r.product).ToList();
    }

    public List<Product> KeywordSearch(string query, int topK = 10)
    {
        var queryLower = query.ToLower();
        var keywords = queryLower.Split(new[] { ' ', ',', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);

        var results = _products
            .Select(p => new
            {
                Product = p,
                Score = CalculateKeywordScore(p, keywords)
            })
            .Where(x => x.Score > 0)
            .OrderByDescending(x => x.Score)
            .Take(topK)
            .Select(x => x.Product)
            .ToList();

        return results;
    }

    private double CalculateKeywordScore(Product product, string[] keywords)
    {
        double score = 0;
        var searchText = $"{product.Name} {product.Description} {string.Join(" ", product.Keywords)}".ToLower();

        foreach (var keyword in keywords)
        {
            if (searchText.Contains(keyword))
            {
                score += 1.0;

                // Boost for name matches
                if (product.Name.ToLower().Contains(keyword))
                {
                    score += 2.0;
                }
            }
        }

        // Apply priority boost
        score *= product.SearchBoost;

        return score;
    }

    private List<Product> MergeResults(List<Product> semanticResults, List<Product> keywordResults, int limit)
    {
        var merged = new Dictionary<string, Product>();

        // Add semantic results first (higher weight)
        foreach (var product in semanticResults)
        {
            if (!string.IsNullOrEmpty(product.Url))
            {
                merged[product.Url] = product;
            }
        }

        // Add keyword results
        foreach (var product in keywordResults)
        {
            if (!string.IsNullOrEmpty(product.Url) && !merged.ContainsKey(product.Url))
            {
                merged[product.Url] = product;
            }
        }

        return merged.Values
            .OrderBy(p => p.Priority)
            .ThenByDescending(p => p.SearchBoost)
            .Take(limit)
            .ToList();
    }

    private List<Product> CreateSampleProducts()
    {
        // Sample products for initial testing
        return new List<Product>
        {
            new Product
            {
                Id = "v5_xl",
                Name = "V5 XL",
                FullName = "V5 XL Extended Life Atomizer",
                Description = "Everything you love about the V5, but BIGGER! 30% larger cup means more concentrate per load and even better heat distribution.",
                Price = "$50-60",
                Category = "main_products",
                Priority = 1,
                SearchBoost = 1.5,
                Url = "https://ineedhemp.com/product/v5-xl/",
                Features = new List<string> { "30% larger SiC cup", "Massive clouds", "Extended sessions" },
                Keywords = new List<string> { "v5", "xl", "concentrate", "atomizer", "flavor", "best" }
            },
            new Product
            {
                Id = "core_deluxe",
                Name = "Core 2.0 Deluxe",
                FullName = "Core 2.0 Deluxe Wireless Enail",
                Description = "The ultimate all-in-one e-rig. No mod needed!",
                Price = "$199-249",
                Category = "main_products",
                Priority = 1,
                SearchBoost = 1.3,
                Url = "https://ineedhemp.com/product/core-2-0-deluxe/",
                Features = new List<string> { "Complete kit", "Built-in battery", "Glass bubbler included" },
                Keywords = new List<string> { "core", "enail", "wireless", "complete", "beginner" }
            },
            new Product
            {
                Id = "nice_dreamz",
                Name = "Nice Dreamz",
                FullName = "Nice Dreamz Portable Flower Vaporizer",
                Description = "Premium dry herb vaporizer with true convection heating.",
                Price = "$129-149",
                Category = "main_products",
                Priority = 1,
                SearchBoost = 1.2,
                Url = "https://ineedhemp.com/product/nice-dreamz/",
                Features = new List<string> { "Dry herb", "Convection heating", "Portable" },
                Keywords = new List<string> { "nice", "dreamz", "flower", "dry herb", "portable" }
            }
        };
    }
}
