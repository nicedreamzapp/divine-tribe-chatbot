using DivineTribeChatbot.Domain.Enums;

namespace DivineTribeChatbot.Domain.Models;

public class QueryPreprocessingResult
{
    public string NormalizedQuery { get; set; } = string.Empty;
    public MaterialType MaterialType { get; set; } = MaterialType.Unknown;
    public List<string> IntentHints { get; set; } = new();
    public List<string> ExtractedEntities { get; set; } = new();
    public bool IsComparison { get; set; }
    public bool IsShopping { get; set; }
    public bool IsTroubleshooting { get; set; }
}
