using System.Text.RegularExpressions;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Enums;
using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Infrastructure.Services;

public class QueryPreprocessor : IQueryPreprocessor
{
    private readonly string[] _concentrateKeywords = new[]
    {
        "wax", "concentrate", "dabs", "dab", "oil", "shatter", "budder",
        "rosin", "sauce", "crumble", "distillate", "live resin", "hash oil"
    };

    private readonly string[] _dryHerbKeywords = new[]
    {
        "flower", "dry herb", "herb", "bud", "nugs"
    };

    private readonly string[] _hempKeywords = new[]
    {
        "hemp", "shirt", "clothing", "clothes", "hoodie", "boxer",
        "apparel", "tank", "t-shirt", "tshirt"
    };

    private readonly string[] _comparisonWords = new[]
    {
        "vs", "versus", "compare", "difference between", "better than"
    };

    private readonly string[] _shoppingWords = new[]
    {
        "buy", "purchase", "recommend", "best", "top", "which"
    };

    private readonly string[] _troubleshootingWords = new[]
    {
        "broken", "not working", "problem", "issue", "fix", "help",
        "won't", "wont", "can't", "cant", "doesn't", "doesnt",
        "error", "wrong", "bad"
    };

    private readonly string[] _howToWords = new[]
    {
        "how to", "how do", "setup", "install", "use", "clean"
    };

    private readonly Dictionary<string, string[]> _productPatterns = new()
    {
        ["v5"] = new[] { "v5", "v 5", "version 5", "divine crossing v5" },
        ["v5_xl"] = new[] { "v5 xl", "v5xl", "xl v5", "v5 extra large" },
        ["core"] = new[] { "core", "core 2.0", "core deluxe" },
        ["tug"] = new[] { "tug", "tug 2.0", "tug deluxe" },
        ["lightning"] = new[] { "lightning pen", "lightning" },
        ["fogger"] = new[] { "fogger", "nice dreamz", "nicedreamz" },
        ["ruby"] = new[] { "ruby", "ruby twist", "ball vape" },
        ["gen2"] = new[] { "gen 2", "gen2", "generation 2" }
    };

    public QueryPreprocessingResult Preprocess(string query)
    {
        var queryLower = query.ToLower().Trim();

        var result = new QueryPreprocessingResult
        {
            NormalizedQuery = queryLower,
            MaterialType = DetectMaterialType(queryLower),
            IntentHints = ExtractIntentHints(queryLower).ToList(),
            ExtractedEntities = DetectProducts(queryLower).ToList(),
            IsComparison = _comparisonWords.Any(w => queryLower.Contains(w)),
            IsShopping = _shoppingWords.Any(w => queryLower.Contains(w)),
            IsTroubleshooting = _troubleshootingWords.Any(w => queryLower.Contains(w))
        };

        return result;
    }

    private MaterialType DetectMaterialType(string query)
    {
        var hasConcentrate = _concentrateKeywords.Any(kw => query.Contains(kw));
        var hasDryHerb = _dryHerbKeywords.Any(kw => query.Contains(kw));
        var hasHemp = _hempKeywords.Any(kw => query.Contains(kw));

        if (hasHemp)
            return MaterialType.Hemp;

        if (hasConcentrate && !hasDryHerb)
            return MaterialType.Concentrate;

        if (hasDryHerb && !hasConcentrate)
            return MaterialType.DryHerb;

        return MaterialType.Unknown;
    }

    private IEnumerable<string> DetectProducts(string query)
    {
        var products = new List<string>();

        foreach (var (product, patterns) in _productPatterns)
        {
            if (patterns.Any(pattern => query.Contains(pattern)))
            {
                products.Add(product);
            }
        }

        return products;
    }

    private IEnumerable<string> ExtractIntentHints(string query)
    {
        var hints = new List<string>();

        // Support queries (high priority)
        if (_troubleshootingWords.Any(w => query.Contains(w)))
            hints.Add("troubleshooting");

        if (_howToWords.Any(w => query.Contains(w)))
            hints.Add("how_to");

        // Comparison
        if (_comparisonWords.Any(w => query.Contains(w)))
            hints.Add("comparison");

        // Shopping
        if (_shoppingWords.Any(w => query.Contains(w)))
            hints.Add("shopping");

        return hints;
    }

    private string? ExtractUrl(string query)
    {
        var urlPattern = @"https?://(?:www\.)?ineedhemp\.com/[^\s]+";
        var match = Regex.Match(query, urlPattern);
        return match.Success ? match.Value : null;
    }
}
