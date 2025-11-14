namespace DivineTribeChatbot.Domain.Models;

public class CachedAnswer
{
    public string Name { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Price { get; set; } = string.Empty;
    public List<string> Features { get; set; } = new();
    public List<string> Keywords { get; set; } = new();
    public string Url { get; set; } = string.Empty;
    public Dictionary<string, string> Metadata { get; set; } = new();
}
