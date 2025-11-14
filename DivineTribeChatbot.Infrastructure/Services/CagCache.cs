using System.Text.Json;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class CagCache : ICagCache
{
    private readonly ILogger<CagCache> _logger;
    private Dictionary<string, CachedAnswer> _cache = new();
    private readonly string _cacheFilePath;

    public CagCache(ILogger<CagCache> logger, string cacheFilePath = "Data/cag_cache.json")
    {
        _logger = logger;
        _cacheFilePath = cacheFilePath;
    }

    public void Load()
    {
        try
        {
            if (!File.Exists(_cacheFilePath))
            {
                _logger.LogWarning("CAG Cache file not found at {Path}. Creating empty cache.", _cacheFilePath);
                _cache = CreateDefaultCache();
                return;
            }

            var json = File.ReadAllText(_cacheFilePath);
            _cache = JsonSerializer.Deserialize<Dictionary<string, CachedAnswer>>(json)
                     ?? new Dictionary<string, CachedAnswer>();

            _logger.LogInformation("CAG Cache loaded with {Count} entries", _cache.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading CAG cache from {Path}", _cacheFilePath);
            _cache = CreateDefaultCache();
        }
    }

    public (bool found, string? response, List<Product>? products) GetCachedResponse(string query)
    {
        var queryLower = query.ToLower().Trim();

        foreach (var (key, answer) in _cache)
        {
            if (answer.Keywords.Any(keyword => queryLower.Contains(keyword.ToLower())))
            {
                var response = FormatResponse(answer);
                var products = ConvertToProducts(answer);

                _logger.LogInformation("CAG Cache hit for query: {Query} -> {Key}", query, key);

                return (true, response, products);
            }
        }

        return (false, null, null);
    }

    private string FormatResponse(CachedAnswer answer)
    {
        var parts = new List<string>();

        if (!string.IsNullOrEmpty(answer.FullName))
        {
            parts.Add($"# {answer.FullName}\n");
        }

        if (!string.IsNullOrEmpty(answer.Description))
        {
            parts.Add(answer.Description);
            parts.Add("");
        }

        if (answer.Features.Any())
        {
            parts.Add("**Key Features:**");
            parts.AddRange(answer.Features);
            parts.Add("");
        }

        if (!string.IsNullOrEmpty(answer.Price))
        {
            parts.Add($"**Price:** {answer.Price}");
            parts.Add("");
        }

        if (!string.IsNullOrEmpty(answer.Url))
        {
            parts.Add($"[View Product]({answer.Url})");
        }

        return string.Join("\n", parts);
    }

    private List<Product> ConvertToProducts(CachedAnswer answer)
    {
        if (string.IsNullOrEmpty(answer.Url))
        {
            return new List<Product>();
        }

        return new List<Product>
        {
            new Product
            {
                Name = answer.Name,
                FullName = answer.FullName,
                Description = answer.Description,
                Price = answer.Price,
                Url = answer.Url,
                Features = answer.Features.ToList()
            }
        };
    }

    private Dictionary<string, CachedAnswer> CreateDefaultCache()
    {
        // Create a minimal default cache with the most common products
        return new Dictionary<string, CachedAnswer>
        {
            ["v5_xl"] = new CachedAnswer
            {
                Name = "V5 XL",
                FullName = "V5 XL Extended Life Atomizer",
                Description = "Everything you love about the V5, but BIGGER! 30% larger cup means more concentrate per load and even better heat distribution.",
                Price = "$50-60",
                Features = new List<string>
                {
                    "🚀 30% larger SiC cup than regular V5",
                    "💨 Massive clouds and extended sessions",
                    "🔥 Same great SiC technology",
                    "⚡ Needs 35W+ mod",
                    "👑 The king of Divine Tribe atomizers"
                },
                Keywords = new List<string> { "v5 xl", "v5xl", "v 5 xl", "extra large", "bigger v5", "best for flavor", "best atomizer" },
                Url = "https://ineedhemp.com/product/v5-xl/"
            },
            ["core_deluxe"] = new CachedAnswer
            {
                Name = "Core 2.0 Deluxe",
                FullName = "Core 2.0 Deluxe Wireless Enail",
                Description = "The ultimate all-in-one e-rig. No mod needed! Built-in battery, water attachment included, and the same legendary SiC cup technology.",
                Price = "$199-249",
                Features = new List<string>
                {
                    "📱 Complete kit - nothing else needed",
                    "🔋 Built-in 3000mAh battery",
                    "💧 Glass bubbler included",
                    "🎯 Digital temp control (Bluetooth app)",
                    "✈️ Portable and discreet",
                    "🏆 Best value complete setup"
                },
                Keywords = new List<string> { "core", "core 2", "core deluxe", "e-rig", "enail", "wireless", "all in one", "complete setup", "beginner" },
                Url = "https://ineedhemp.com/product/core-2-0-deluxe/"
            },
            ["nice_dreamz"] = new CachedAnswer
            {
                Name = "Nice Dreamz",
                FullName = "Nice Dreamz Portable Flower Vaporizer",
                Description = "Premium dry herb vaporizer with true convection heating. Perfect for flower enthusiasts who want pure, flavorful vapor.",
                Price = "$129-149",
                Features = new List<string>
                {
                    "🌿 Designed for dry herb (flower)",
                    "🌡️ Precise temperature control",
                    "🔥 True convection heating",
                    "🔋 Long battery life",
                    "💨 Pure flavor, no combustion",
                    "📏 Compact and portable"
                },
                Keywords = new List<string> { "nice dreamz", "nicedreamz", "nice dreams", "flower", "dry herb", "herb vaporizer", "dry flower" },
                Url = "https://ineedhemp.com/product/nice-dreamz/"
            },
            ["ruby_twist"] = new CachedAnswer
            {
                Name = "Ruby Twist",
                FullName = "Ruby Twist Ball Vape",
                Description = "Premium ball vape for dry herb. Features ruby balls for superior heat retention and flavor.",
                Price = "$199-249",
                Features = new List<string>
                {
                    "🔴 Ruby balls for heat retention",
                    "🌿 Designed for dry herb",
                    "🔥 Superior flavor and efficiency",
                    "💨 Massive clouds",
                    "🏠 Desktop vaporizer"
                },
                Keywords = new List<string> { "ruby", "ruby twist", "ball vape", "dry herb desktop", "desktop vaporizer" },
                Url = "https://ineedhemp.com/product/ruby-twist/"
            }
        };
    }
}
