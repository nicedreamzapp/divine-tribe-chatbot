using System.Text.Json;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class ProductDatabase : IProductDatabase
{
    private readonly ILogger<ProductDatabase> _logger;
    private readonly IRagRetriever _ragRetriever;
    private readonly string _productsFilePath;
    private List<Product> _products = new();
    private Dictionary<string, Product> _productsByUrl = new();

    public ProductDatabase(
        ILogger<ProductDatabase> logger,
        IRagRetriever ragRetriever,
        string productsFilePath = "products_organized.json")
    {
        _logger = logger;
        _ragRetriever = ragRetriever;
        _productsFilePath = productsFilePath;
    }

    public async Task LoadProductsAsync()
    {
        try
        {
            if (!File.Exists(_productsFilePath))
            {
                _logger.LogWarning("Products file not found at {Path}", _productsFilePath);
                return;
            }

            var json = await File.ReadAllTextAsync(_productsFilePath);
            var productData = JsonSerializer.Deserialize<ProductDataFile>(json);

            if (productData?.Categories != null)
            {
                _products = productData.Categories
                    .SelectMany(cat => cat.Value.Products ?? new List<Product>())
                    .ToList();

                _productsByUrl = _products
                    .Where(p => !string.IsNullOrEmpty(p.Url))
                    .DistinctBy(p => p.Url)
                    .ToDictionary(p => p.Url, p => p);

                _logger.LogInformation("Loaded {Count} products from {Path}", _products.Count, _productsFilePath);

                // Initialize RAG retriever with products
                await _ragRetriever.LoadProductsAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading products from {Path}", _productsFilePath);
        }
    }

    public List<Product> Search(string query, int limit = 5)
    {
        // Use RAG retriever for intelligent search
        var results = _ragRetriever.Search(query, topK: limit);
        return results;
    }

    public List<Product> GetCategoryProducts(string category)
    {
        return _products
            .Where(p => p.Category.Equals(category, StringComparison.OrdinalIgnoreCase))
            .OrderBy(p => p.Priority)
            .ToList();
    }

    public Product? GetProductByUrl(string url)
    {
        _productsByUrl.TryGetValue(url, out var product);
        return product;
    }

    private class ProductDataFile
    {
        public Dictionary<string, CategoryData>? Categories { get; set; }
    }

    private class CategoryData
    {
        public string? DisplayName { get; set; }
        public int Priority { get; set; }
        public List<Product>? Products { get; set; }
    }
}
